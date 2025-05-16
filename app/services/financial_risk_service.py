import requests
import datetime
import logging
from typing import Dict, Any, Optional
import os

# Configura o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialRiskService:
    def __init__(self):
        # Endereço da carteira será obtido da variável de ambiente WALLET_ADDRESS
        self.wallet_address = os.getenv("WALLET_ADDRESS", "").lower()
        self.subgraph_url = "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-arbitrum"
        self.cache = None
        self.last_fetch = None
        self.cache_duration = datetime.timedelta(minutes=10)  # Cache válido por 10 minutos
    
    async def fetch_financial_data(self) -> Dict[str, Any]:
        """Busca dados financeiros da carteira na AAVE v3 via The Graph API"""
        current_time = datetime.datetime.now()
        
        # Verifica se o cache é válido
        if self.cache and self.last_fetch and (current_time - self.last_fetch < self.cache_duration):
            logger.info("Retornando dados financeiros do cache")
            return self.cache
        
        # Verifica se o endereço da carteira está definido
        if not self.wallet_address:
            logger.error("Endereço de carteira não definido na variável de ambiente WALLET_ADDRESS")
            return {
                "health_factor": 0,
                "alavancagem": 0,
                "supplied_asset_value": 0,
                "net_asset_value": 0,
                "error": "Endereço de carteira não configurado",
                "timestamp": current_time.isoformat()
            }
            
        try:
            logger.info(f"Buscando dados financeiros para carteira: {self.wallet_address}")
            
            # Consulta GraphQL para AAVE v3 Arbitrum
            query = """
            {
              user(id: "%s") {
                healthFactor
                totalCollateralUSD
                totalDebtUSD
                reserves(where: {usageAsCollateralEnabledOnUser: true}) {
                  reserve {
                    symbol
                    decimals
                    price {
                      priceInUSD
                    }
                  }
                  currentATokenBalance
                }
              }
            }
            """ % self.wallet_address
            
            # Enviar requisição POST
            response = requests.post(
                self.subgraph_url,
                json={'query': query}
            )
            
            # Verificar resposta
            if response.status_code != 200:
                logger.error(f"Erro na API: código {response.status_code}, resposta: {response.text}")
                raise Exception(f"API retornou código de status {response.status_code}")
            
            data = response.json()
            logger.debug(f"Resposta da API: {data}")
            
            if data.get('data', {}).get('user') is None:
                logger.warning(f"Posição não encontrada para o endereço da carteira: {self.wallet_address}")
                return {
                    "health_factor": 0,
                    "alavancagem": 0,
                    "supplied_asset_value": 0,
                    "net_asset_value": 0,
                    "error": f"Posição não encontrada para carteira {self.wallet_address}",
                    "timestamp": current_time.isoformat()
                }
            
            user_data = data['data']['user']
            
            # Extrair Health Factor (dividir por 10^18)
            health_factor = float(user_data.get('healthFactor', 0)) if user_data.get('healthFactor') else 0
            if health_factor > 0:
                health_factor = health_factor / 1e18
            
            # Calcular valores para WBTC
            wbtc_balance = 0
            wbtc_usd_value = 0
            
            for reserve in user_data.get('reserves', []):
                if reserve['reserve']['symbol'] == 'WBTC':
                    decimals = int(reserve['reserve']['decimals'])
                    price_usd = float(reserve['reserve']['price']['priceInUSD'])
                    wbtc_balance = float(reserve['currentATokenBalance']) / (10 ** decimals)
                    wbtc_usd_value = wbtc_balance * price_usd
            
            # Calcular NAV (Net Asset Value)
            total_collateral = float(user_data.get('totalCollateralUSD', 0)) if user_data.get('totalCollateralUSD') else 0
            total_debt = float(user_data.get('totalDebtUSD', 0)) if user_data.get('totalDebtUSD') else 0
            
            if total_collateral > 0:
                total_collateral = total_collateral / 1e8
            if total_debt > 0:
                total_debt = total_debt / 1e8
                
            nav = total_collateral - total_debt
            
            # Calcular alavancagem
            leverage = total_collateral / nav if nav > 0 else 0
            
            # Resultado
            data = {
                "health_factor": health_factor,
                "alavancagem": round(leverage, 2),
                "supplied_asset_value": wbtc_usd_value if wbtc_usd_value > 0 else total_collateral,
                "net_asset_value": nav,
                "total_collateral_usd": total_collateral,
                "total_debt_usd": total_debt,
                "timestamp": current_time.isoformat()
            }
            
            # Atualiza o cache
            self.cache = data
            self.last_fetch = current_time
            
            logger.info(f"Dados financeiros obtidos com sucesso: HF={health_factor}, NAV=${nav}")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados financeiros: {e}")
            # Em caso de erro, tenta usar o cache antigo se disponível
            if self.cache:
                return self.cache
            # Ou retorna valores de fallback
            return {
                "health_factor": 0,  # Valor zero para indicar falha na extração
                "alavancagem": 0,    # Valor zero para indicar falha na extração
                "supplied_asset_value": 0,
                "net_asset_value": 0,
                "error": str(e),
                "timestamp": current_time.isoformat()
            }
    
    def calculate_financial_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula o score de risco financeiro baseado nos indicadores"""
        
        hf = financial_data["health_factor"]
        leverage = financial_data["alavancagem"]
        
        # Cálculo do score para Health Factor (inversamente proporcional)
        if hf < 1.0:
            hf_score = 10.0  # Risco máximo
        elif hf < 1.2:
            hf_score = 9.0   # Risco crítico
        elif hf < 1.5:
            hf_score = 7.0   # Risco elevado
        elif hf < 2.0:
            hf_score = 5.0   # Risco moderado
        elif hf < 3.0:
            hf_score = 3.0   # Risco baixo
        else:
            hf_score = 1.0   # Risco mínimo
        
        # Classificação de Health Factor
        if hf < 1.0:
            hf_classification = "Liquidação Iminente"
        elif hf < 1.2:
            hf_classification = "Crítico"
        elif hf < 1.5:
            hf_classification = "Elevado"
        elif hf < 2.0:
            hf_classification = "Moderado"
        else:
            hf_classification = "Seguro"
            
        # Cálculo do score para Alavancagem
        if leverage > 5.0:
            leverage_score = 10.0  # Risco extremo
        elif leverage > 3.0:
            leverage_score = 7.0   # Risco elevado
        elif leverage > 2.0:
            leverage_score = 5.0   # Risco moderado
        elif leverage > 1.5:
            leverage_score = 3.0   # Risco controlado
        else:
            leverage_score = 1.0   # Risco baixo
        
        # Classificação de Alavancagem
        if leverage > 5.0:
            leverage_classification = "Extrema"
        elif leverage > 3.0:
            leverage_classification = "Elevada"
        elif leverage > 2.0:
            leverage_classification = "Moderada"
        elif leverage > 1.5:
            leverage_classification = "Controlada"
        else:
            leverage_classification = "Baixa"
        
        # Pesos dos indicadores
        hf_weight = 0.7
        leverage_weight = 0.3
        
        # Score final ponderado
        final_score = (hf_score * hf_weight) + (leverage_score * leverage_weight)
        
        # Alertas principais
        alertas = []
        if hf < 1.5:
            alertas.append(f"HF crítico: {hf}")
        if leverage > 3.0:
            alertas.append(f"Alavancagem elevada: {leverage}x")
        
        # Resposta completa
        return {
            "categoria": "Financeiro Direto",
            "score": round(final_score, 2),
            "peso": 0.35,  # Peso desta categoria no risco global
            "principais_alertas": alertas,
            "detalhes": {
                "health_factor": {
                    "valor": hf,
                    "classificacao": hf_classification,
                    "score": hf_score,
                    "peso": hf_weight
                },
                "alavancagem": {
                    "valor": leverage,
                    "classificacao": leverage_classification,
                    "score": leverage_score,
                    "peso": leverage_weight
                }
            }
        }