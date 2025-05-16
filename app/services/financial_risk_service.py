import requests
import datetime
import logging
from typing import Dict, Any, Optional
import os
import json

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
                id
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
            
            logger.debug(f"Query GraphQL: {query}")
            
            # Enviar requisição POST
            response = requests.post(
                self.subgraph_url,
                json={'query': query}
            )
            
            # Verificar resposta
            if response.status_code != 200:
                logger.error(f"API retornou código de status {response.status_code}: {response.text}")
                raise Exception(f"API retornou código de status {response.status_code}")
            
            data = response.json()
            logger.debug(f"Resposta da API: {json.dumps(data, indent=2)}")
            
            if data.get('errors'):
                logger.error(f"Erro na consulta GraphQL: {data.get('errors')}")
                return {
                    "health_factor": 0,
                    "alavancagem": 0,
                    "supplied_asset_value": 0,
                    "net_asset_value": 0,
                    "error": f"Erro na consulta GraphQL: {data.get('errors')}",
                    "timestamp": current_time.isoformat()
                }
            
            if data.get('data', {}).get('user') is None:
                # O endereço pode estar em um formato diferente, vamos tentar com '0x' em minúsculo
                if self.wallet_address.startswith("0X"):
                    corrected_address = "0x" + self.wallet_address[2:]
                    logger.info(f"Tentando novamente com endereço corrigido: {corrected_address}")
                    self.wallet_address = corrected_address
                    return await self.fetch_financial_data()
                
                logger.warning(f"Posição não encontrada para o endereço da carteira: {self.wallet_address}")
                
                # Tentando verificar se o endereço existe com outra consulta
                verify_query = """
                {
                  users(where: {id: "%s"}) {
                    id
                  }
                }
                """ % self.wallet_address
                
                verify_response = requests.post(
                    self.subgraph_url,
                    json={'query': verify_query}
                )
                
                verify_data = verify_response.json()
                logger.debug(f"Verificação de endereço: {json.dumps(verify_data, indent=2)}")
                
                # Para fins de depuração, vamos verificar uma lista de usuários recentes
                sample_query = """
                {
                  users(first: 5) {
                    id
                  }
                }
                """
                
                sample_response = requests.post(
                    self.subgraph_url,
                    json={'query': sample_query}
                )
                
                sample_data = sample_response.json()
                logger.info(f"Amostra de usuários recentes: {json.dumps(sample_data.get('data', {}).get('users', []), indent=2)}")
                
                return {
                    "health_factor": 0,
                    "alavancagem": 0,
                    "supplied_asset_value": 0,
                    "net_asset_value": 0,
                    "error": "Posição não encontrada",
                    "timestamp": current_time.isoformat(),
                    "debug_info": {
                        "wallet_address": self.wallet_address,
                        "verify_response": verify_data
                    }
                }
            
            user_data = data['data']['user']
            logger.info(f"Dados do usuário encontrados: {json.dumps(user_data, indent=2)}")
            
            # Extrair Health Factor
            health_factor = 0
            if user_data.get('healthFactor') and user_data['healthFactor'] != "0":
                health_factor = float(user_data['healthFactor'])
                # Na AAVE v3, o health factor pode vir em diferentes formatos
                # Se for um valor muito grande, provavelmente precisa ser dividido por 10^18
                if health_factor > 100000:
                    health_factor = health_factor / 1e18
            
            # Calcular valores para todos os ativos
            supplied_assets = 0
            asset_details = []
            
            for reserve in user_data.get('reserves', []):
                symbol = reserve['reserve']['symbol']
                decimals = int(reserve['reserve']['decimals'])
                price_usd = float(reserve['reserve']['price']['priceInUSD'])
                balance = float(reserve['currentATokenBalance']) / (10 ** decimals)
                usd_value = balance * price_usd
                
                asset_details.append({
                    "symbol": symbol,
                    "balance": balance,
                    "usd_value": usd_value
                })
                
                supplied_assets += usd_value
                
                logger.info(f"Asset {symbol}: {balance} tokens = ${usd_value}")
            
            # Calcular NAV (Net Asset Value)
            total_collateral = float(user_data.get('totalCollateralUSD', 0))
            total_debt = float(user_data.get('totalDebtUSD', 0))
            
            # Verificar se os valores precisam ser ajustados (divisão por 10^8)
            if total_collateral > 1e8:
                total_collateral = total_collateral / 1e8
            
            if total_debt > 1e8:
                total_debt = total_debt / 1e8
                
            nav = total_collateral - total_debt
            
            # Calcular alavancagem
            leverage = total_collateral / nav if nav > 0 else 0
            
            logger.info(f"Health Factor: {health_factor}")
            logger.info(f"Total Collateral: ${total_collateral}")
            logger.info(f"Total Debt: ${total_debt}")
            logger.info(f"NAV: ${nav}")
            logger.info(f"Leverage: {leverage}x")
            
            # Resultado
            data = {
                "health_factor": health_factor,
                "alavancagem": round(leverage, 2),
                "supplied_asset_value": supplied_assets if supplied_assets > 0 else total_collateral,
                "net_asset_value": nav,
                "total_collateral_usd": total_collateral,
                "total_debt_usd": total_debt,
                "asset_details": asset_details,
                "timestamp": current_time.isoformat()
            }
            
            # Atualiza o cache
            self.cache = data
            self.last_fetch = current_time
            
            logger.info(f"Dados financeiros obtidos com sucesso: HF={health_factor}, NAV=${nav}")
            return data
            
        except Exception as e:
            logger.exception(f"Erro ao buscar dados financeiros: {e}")
            # Em caso de erro, tenta usar o cache antigo se disponível
            if self.cache:
                return self.cache
            # Ou retorna valores de fallback
            return {
                "health_factor": 0,
                "alavancagem": 0,
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