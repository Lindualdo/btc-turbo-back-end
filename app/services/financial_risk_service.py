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
        
        # Lista de possíveis endpoints para o AAVE v3 Arbitrum
        self.endpoints = [
            "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-arbitrum",
            "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-arbitrum-one",
            "https://api.studio.thegraph.com/query/24660/aave-v3-arbitrum/version/latest",
            "https://gateway-arbitrum.network.thegraph.com/api/subgraphs/name/aave/protocol-v3",
            "https://gateway.thegraph.com/api/subgraphs/name/aave/protocol-v3-arbitrum",
            "https://thegraph.com/hosted-service/subgraph/aave/protocol-v3-arbitrum"
        ]
        
        # Vamos determinar o endpoint funcionando no momento da primeira consulta
        self.working_endpoint = None
        
        self.cache = None
        self.last_fetch = None
        self.cache_duration = datetime.timedelta(minutes=10)  # Cache válido por 10 minutos
    
    def find_working_endpoint(self):
        """Testa os endpoints disponíveis para encontrar um que funcione"""
        if self.working_endpoint:
            return self.working_endpoint
        
        # Consulta básica para verificar se o endpoint responde
        query = '{users(first: 1) {id}}'
        
        for endpoint in self.endpoints:
            try:
                logger.info(f"Testando endpoint: {endpoint}")
                response = requests.post(endpoint, json={'query': query}, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and not 'errors' in data:
                        logger.info(f"✅ Endpoint funcionando: {endpoint}")
                        self.working_endpoint = endpoint
                        return endpoint
                    else:
                        logger.warning(f"⚠️ {endpoint} - Responde mas com erros: {json.dumps(data)}")
                else:
                    logger.warning(f"❌ {endpoint} - Erro HTTP {response.status_code}")
            except Exception as e:
                logger.error(f"❌ {endpoint} - Erro: {str(e)}")
        
        # Se nenhum endpoint funcionou
        logger.error("Não foi possível encontrar um endpoint funcionando para The Graph AAVE v3")
        return None
    
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
            return self.create_default_response("Endereço de carteira não configurado")
            
        try:
            # Encontra um endpoint funcionando
            endpoint = self.find_working_endpoint()
            if not endpoint:
                return self.create_default_response("Nenhum endpoint AAVE v3 disponível")
            
            logger.info(f"Buscando dados financeiros para carteira: {self.wallet_address}")
            
            # Consulta GraphQL para obter reservas do usuário
            query = """
            {
              userReserves(where: {user: "%s"}) {
                reserve {
                  symbol
                  decimals
                  price {
                    priceInUSD
                  }
                  usageAsCollateralEnabled
                }
                currentATokenBalance
                currentStableDebt
                currentVariableDebt
                usageAsCollateralEnabledOnUser
              }
              user(id: "%s") {
                id
                healthFactor
                totalCollateralUSD
                totalDebtUSD
              }
            }
            """ % (self.wallet_address, self.wallet_address)
            
            logger.debug(f"Query GraphQL: {query}")
            
            # Enviar requisição POST
            response = requests.post(endpoint, json={'query': query})
            
            # Verificar resposta
            if response.status_code != 200:
                logger.error(f"API retornou código de status {response.status_code}: {response.text}")
                return self.create_default_response(f"API retornou código de status {response.status_code}")
            
            data = response.json()
            logger.debug(f"Resposta da API: {json.dumps(data, indent=2)}")
            
            if data.get('errors'):
                logger.error(f"Erro na consulta GraphQL: {data.get('errors')}")
                return self.create_default_response(f"Erro na consulta GraphQL: {data.get('errors')}")
            
            user_reserves = data.get('data', {}).get('userReserves', [])
            if not user_reserves:
                logger.warning(f"Usuário não encontrado ou sem posições na AAVE v3: {self.wallet_address}")
                
                # Tentar uma consulta para todos os usuários recentes para verificar se a API está retornando dados
                sample_query = """
                {
                  users(first: 5) {
                    id
                    healthFactor
                    totalCollateralUSD
                    totalDebtUSD
                  }
                }
                """
                
                sample_response = requests.post(endpoint, json={'query': sample_query})
                sample_data = sample_response.json()
                
                if 'data' in sample_data and sample_data['data'].get('users'):
                    users = sample_data['data']['users']
                    logger.info(f"Exemplos de usuários com posições: {json.dumps(users, indent=2)}")
                    
                    # Verificar se o formato do endereço está correto
                    example_user = users[0]['id']
                    if example_user.startswith("0x") and self.wallet_address.startswith("0x"):
                        logger.info("O formato do endereço parece correto (0x...)")
                    else:
                        logger.warning(f"Formato de endereço diferente. Exemplo API: {example_user}, Seu endereço: {self.wallet_address}")
                
                return self.create_default_response("Posição não encontrada")
            
            user_data = data.get('data', {}).get('user', {})
            
            # Extrair Health Factor (pode ser None, infinity ou um número)
            health_factor = 0
            
            if user_data and user_data.get('healthFactor'):
                if user_data['healthFactor'] == "0" or user_data['healthFactor'] == 0:
                    health_factor = float('inf')  # Sem dívidas = risco zero = HF infinito
                else:
                    health_factor = float(user_data['healthFactor'])
                    # Na AAVE v3, o health factor geralmente precisa ser ajustado
                    if health_factor > 100:
                        health_factor = health_factor / 1e18
            else:
                health_factor = float('inf')  # Se não tem dados de HF, provavelmente não tem empréstimos
            
            # Processar reservas para calcular valores
            supplied_assets = 0
            debt_amount = 0
            asset_details = []
            
            for reserve in user_reserves:
                symbol = reserve['reserve']['symbol']
                decimals = int(reserve['reserve']['decimals'])
                price_usd = float(reserve['reserve']['price']['priceInUSD'])
                
                # Saldos e dívidas
                a_token_balance = float(reserve['currentATokenBalance']) / (10 ** decimals)
                stable_debt = float(reserve['currentStableDebt']) / (10 ** decimals)
                variable_debt = float(reserve['currentVariableDebt']) / (10 ** decimals)
                
                # Valor em USD
                supplied_value = a_token_balance * price_usd
                debt_value = (stable_debt + variable_debt) * price_usd
                
                # Só adiciona como colateral se estiver habilitado para tal
                collateral_enabled = reserve.get('usageAsCollateralEnabledOnUser', False)
                collateral_value = supplied_value if collateral_enabled else 0
                
                asset_details.append({
                    "symbol": symbol,
                    "supplied_balance": a_token_balance,
                    "supplied_value_usd": supplied_value,
                    "debt_balance": stable_debt + variable_debt,
                    "debt_value_usd": debt_value,
                    "collateral_enabled": collateral_enabled,
                    "collateral_value_usd": collateral_value
                })
                
                supplied_assets += supplied_value
                debt_amount += debt_value
                
                logger.info(f"Asset {symbol}: {a_token_balance} supplied = ${supplied_value}, {stable_debt + variable_debt} borrowed = ${debt_value}")
            
            # Calcular NAV (Net Asset Value)
            total_collateral = 0
            total_debt = 0
            
            if user_data:
                total_collateral = float(user_data.get('totalCollateralUSD', 0))
                total_debt = float(user_data.get('totalDebtUSD', 0))
                
                # Verificar se os valores precisam ser ajustados
                if total_collateral > 1e8:
                    total_collateral = total_collateral / 1e8
                
                if total_debt > 1e8:
                    total_debt = total_debt / 1e8
            else:
                # Usar os valores calculados se não temos dados do usuário
                total_collateral = supplied_assets
                total_debt = debt_amount
                
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
                "supplied_asset_value": total_collateral,
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
            return self.create_default_response(str(e))
    
    def create_default_response(self, error_message="Erro desconhecido"):
        """Cria uma resposta padrão em caso de erro"""
        return {
            "health_factor": 0,
            "alavancagem": 0,
            "supplied_asset_value": 0,
            "net_asset_value": 0,
            "error": error_message,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def calculate_financial_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula o score de risco financeiro baseado nos indicadores"""
        
        hf = financial_data["health_factor"]
        leverage = financial_data["alavancagem"]
        
        # Tratamento para health factor infinito (sem empréstimos)
        if hf == float('inf'):
            hf_classification = "Sem empréstimos"
            hf_score = 1.0  # Risco mínimo
        # Cálculo do score para Health Factor (inversamente proporcional)
        elif hf < 1.0:
            hf_score = 10.0  # Risco máximo
            hf_classification = "Liquidação Iminente"
        elif hf < 1.2:
            hf_score = 9.0   # Risco crítico
            hf_classification = "Crítico"
        elif hf < 1.5:
            hf_score = 7.0   # Risco elevado
            hf_classification = "Elevado"
        elif hf < 2.0:
            hf_score = 5.0   # Risco moderado
            hf_classification = "Moderado"
        elif hf < 3.0:
            hf_score = 3.0   # Risco baixo
            hf_classification = "Baixo"
        else:
            hf_score = 1.0   # Risco mínimo
            hf_classification = "Seguro"
            
        # Cálculo do score para Alavancagem
        if leverage > 5.0:
            leverage_score = 10.0  # Risco extremo
            leverage_classification = "Extrema"
        elif leverage > 3.0:
            leverage_score = 7.0   # Risco elevado
            leverage_classification = "Elevada"
        elif leverage > 2.0:
            leverage_score = 5.0   # Risco moderado
            leverage_classification = "Moderada"
        elif leverage > 1.5:
            leverage_score = 3.0   # Risco controlado
            leverage_classification = "Controlada"
        else:
            leverage_score = 1.0   # Risco baixo
            leverage_classification = "Baixa"
        
        # Pesos dos indicadores
        hf_weight = 0.7
        leverage_weight = 0.3
        
        # Score final ponderado
        final_score = (hf_score * hf_weight) + (leverage_score * leverage_weight)
        
        # Alertas principais
        alertas = []
        if hf != float('inf') and hf < 1.5:
            alertas.append(f"HF crítico: {hf}")
        if leverage > 3.0:
            alertas.append(f"Alavancagem elevada: {leverage}x")
        
        # Se não há alertas, adicione uma mensagem positiva
        if not alertas:
            if hf == float('inf'):
                alertas.append("Sem empréstimos ativos")
            else:
                alertas.append(f"Position saudável: HF = {hf}")
        
        # Resposta completa
        return {
            "categoria": "Financeiro Direto",
            "score": round(final_score, 1),
            "peso": 0.35,  # Peso desta categoria no risco global
            "principais_alertas": alertas,
            "detalhes": {
                "health_factor": {
                    "valor": float('inf') if hf == float('inf') else round(hf, 2),
                    "classificacao": hf_classification,
                    "score": hf_score,
                    "peso": hf_weight
                },
                "alavancagem": {
                    "valor": round(leverage, 2),
                    "classificacao": leverage_classification,
                    "score": leverage_score,
                    "peso": leverage_weight
                }
            }
        }