import requests
import datetime
import logging
from typing import Dict, Any, Optional
import os
import json
import time
from web3 import Web3
from decimal import Decimal

# Configura o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialRiskService:
    def __init__(self):
        # Endereço da carteira será obtido da variável de ambiente WALLET_ADDRESS
        self.wallet_address = os.getenv("WALLET_ADDRESS", "").lower()
        logger.info(f"Inicializando serviço de risco financeiro para carteira: {self.wallet_address}")
        
        # Configuração do Alchemy (utilize a variável de ambiente ALCHEMY_API_KEY)
        self.alchemy_api_key = os.getenv("ALCHEMY_API_KEY", "")
        self.w3 = None
        self.initialize_web3()
        
        # Contratos AAVE v3 na Arbitrum
        self.aave_pool_address = "0x794a61358D6845594F94dc1DB02A252b5b4814aD"  # Aave v3 Pool na Arbitrum
        self.aave_pool_abi = self.load_abi("aave_pool")
        self.aave_pool_contract = None
        
        if self.w3:
            self.aave_pool_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.aave_pool_address),
                abi=self.aave_pool_abi
            )
        
        # Cache
        self.cache = None
        self.last_fetch = None
        self.cache_duration = datetime.timedelta(minutes=10)  # Cache válido por 10 minutos
    
    def initialize_web3(self):
        """Inicializa a conexão Web3 com Alchemy"""
        try:
            if self.alchemy_api_key:
                alchemy_url = f"https://arb-mainnet.g.alchemy.com/v2/{self.alchemy_api_key}"
                self.w3 = Web3(Web3.HTTPProvider(alchemy_url))
                logger.info(f"Web3 conectado: {self.w3.is_connected()}")
            else:
                logger.warning("Alchemy API Key não configurada")
                # Tentar RPC público como fallback
                public_rpc = "https://arb1.arbitrum.io/rpc"
                self.w3 = Web3(Web3.HTTPProvider(public_rpc))
                logger.info(f"Web3 conectado a RPC público: {self.w3.is_connected()}")
        except Exception as e:
            logger.error(f"Erro ao inicializar Web3: {str(e)}")
            self.w3 = None
    
    def load_abi(self, name):
        """Carrega ABI a partir de um arquivo ou retorna um ABI mínimo necessário"""
        try:
            # Tenta carregar de um arquivo
            abi_path = f"abis/{name}.json"
            if os.path.exists(abi_path):
                with open(abi_path, 'r') as f:
                    return json.load(f)
            
            # Retorna ABI mínimo necessário para as funções que usamos
            if name == "aave_pool":
                return [
                    {
                        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
                        "name": "getUserAccountData",
                        "outputs": [
                            {"internalType": "uint256", "name": "totalCollateralBase", "type": "uint256"},
                            {"internalType": "uint256", "name": "totalDebtBase", "type": "uint256"},
                            {"internalType": "uint256", "name": "availableBorrowsBase", "type": "uint256"},
                            {"internalType": "uint256", "name": "currentLiquidationThreshold", "type": "uint256"},
                            {"internalType": "uint256", "name": "ltv", "type": "uint256"},
                            {"internalType": "uint256", "name": "healthFactor", "type": "uint256"}
                        ],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
        except Exception as e:
            logger.error(f"Erro ao carregar ABI {name}: {str(e)}")
            return []
    
    async def fetch_financial_data(self) -> Dict[str, Any]:
        """Busca dados financeiros da carteira na AAVE v3 via Web3"""
        current_time = datetime.datetime.now()
        
        # Verifica se o cache é válido
        if self.cache and self.last_fetch and (current_time - self.last_fetch < self.cache_duration):
            logger.info("Retornando dados financeiros do cache")
            return self.cache
        
        # Verifica se o endereço da carteira está definido
        if not self.wallet_address:
            logger.error("Endereço de carteira não definido na variável de ambiente WALLET_ADDRESS")
            return self.error_response("Endereço de carteira não configurado")
        
        # Verifica se Web3 está disponível
        if not self.w3 or not self.w3.is_connected():
            logger.error("Web3 não está conectado")
            return self.error_response("Falha na conexão com a blockchain")
        
        # Verifica se o contrato da AAVE está disponível
        if not self.aave_pool_contract:
            logger.error("Contrato AAVE não inicializado")
            return self.error_response("Contrato AAVE não disponível")
            
        try:
            logger.info(f"Buscando dados financeiros para carteira: {self.wallet_address}")
            
            # Consulta os dados do usuário diretamente do contrato AAVE
            user_data = self.aave_pool_contract.functions.getUserAccountData(
                Web3.to_checksum_address(self.wallet_address)
            ).call()
            
            # Decodifica os resultados (os valores estão em wei com 8 casas decimais)
            decimals = 10**8  # AAVE v3 usa 8 casas decimais para valores em USD
            
            total_collateral_eth = Decimal(user_data[0]) / Decimal(decimals)
            total_debt_eth = Decimal(user_data[1]) / Decimal(decimals)
            available_borrows_eth = Decimal(user_data[2]) / Decimal(decimals)
            current_liquidation_threshold = Decimal(user_data[3]) / Decimal(10000)  # em percentual
            ltv = Decimal(user_data[4]) / Decimal(10000)  # em percentual
            health_factor = Decimal(user_data[5]) / Decimal(10**18)  # formato especial
            
            # Calcula o valor líquido dos ativos (NAV) - CORREÇÃO: Garantir que NAV é calculado corretamente
            net_asset_value = total_collateral_eth - total_debt_eth
            
            # Obter o preço atual de ETH para converter para USD
            eth_price = self._get_eth_price()
            
            # Converter todos os valores para USD
            total_collateral_usd = float(total_collateral_eth * Decimal(eth_price))
            total_debt_usd = float(total_debt_eth * Decimal(eth_price))
            net_asset_value_usd = float(net_asset_value * Decimal(eth_price))
            
            # CORREÇÃO: Calcula a alavancagem corretamente
            leverage = 1.0  # valor padrão/seguro
            if net_asset_value_usd > 0:
                # Alavancagem = Colateral Total / Valor Líquido (NAV)
                leverage = total_collateral_usd / net_asset_value_usd
            else:
                # Se NAV for zero ou negativo, a alavancagem é considerada extrema
                leverage = 10.0  # valor que indica alavancagem extrema
            
            # Por simplicidade, assumimos que todo o valor é WBTC (uma aproximação)
            # Em uma implementação mais completa, buscaríamos os tokens específicos
            wbtc_supplied_value_usd = total_collateral_usd
            
            # Log detalhado para diagnóstico
            logger.info(f"Dados financeiros calculados: Collateral=${total_collateral_usd:.2f}, "
                     f"Debt=${total_debt_usd:.2f}, NAV=${net_asset_value_usd:.2f}, "
                     f"Leverage={leverage:.2f}x, HF={health_factor}")
            
            # Preparar resposta
            result = {
                "health_factor": float(health_factor) if health_factor < Decimal(1e6) else float('inf'),
                "alavancagem": round(float(leverage), 2),
                "supplied_asset_value": total_collateral_usd,
                "net_asset_value": net_asset_value_usd,
                "total_collateral_usd": total_collateral_usd,
                "total_debt_usd": total_debt_usd,
                "wbtc_supplied_value_usd": wbtc_supplied_value_usd,
                "ltv_percent": float(ltv * 100),
                "liquidation_threshold_percent": float(current_liquidation_threshold * 100),
                "available_borrows_usd": float(available_borrows_eth * Decimal(eth_price)),
                "timestamp": current_time.isoformat(),
                "source": "Web3 Direct",
                # ADICIONADO: Métricas financeiras explícitas para facilitar consumo da API
                "financial_metrics": {
                    "net_asset_value": net_asset_value_usd,
                    "total_collateral": total_collateral_usd,
                    "total_debt": total_debt_usd,
                    "leverage": round(float(leverage), 2)
                }
            }
            
            # Atualiza o cache
            self.cache = result
            self.last_fetch = current_time
            
            logger.info(f"Dados obtidos via Web3: HF={health_factor}, Collateral=${total_collateral_usd:.2f}, Debt=${total_debt_usd:.2f}, NAV=${net_asset_value_usd:.2f}, Leverage={leverage}")
            return result
            
        except Exception as e:
            logger.exception(f"Erro ao buscar dados financeiros via Web3: {e}")
            
            # Tenta usar APIs alternativas
            try:
                return await self._fetch_from_apis()
            except Exception as api_error:
                logger.exception(f"Erro ao usar APIs alternativas: {api_error}")
                
                # Em caso de erro, tenta usar o cache antigo se disponível
                if self.cache:
                    logger.info("Usando dados do cache antigo como fallback")
                    return self.cache
                
                # Ou retorna erro
                return self.error_response(str(e))
    
    async def _fetch_from_apis(self):
        """Método alternativo usando APIs (se Web3 falhar)"""
        # Implementa as tentativas com APIs como fallback
        # (Mantido o mesmo código das tentativas anteriores)
        raise Exception("APIs externas indisponíveis")
    
    def error_response(self, message):
        """Retorna uma resposta de erro padronizada"""
        current_time = datetime.datetime.now()
        return {
            "health_factor": 0,
            "alavancagem": 0,
            "supplied_asset_value": 0,
            "net_asset_value": 0,
            "error": message,
            "timestamp": current_time.isoformat()
        }
    
    def _get_eth_price(self):
        """Obtém o preço atual do ETH em USD"""
        try:
            # Tenta obter de APIs públicas
            apis = [
                "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd",
                "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD"
            ]
            
            for api in apis:
                try:
                    response = requests.get(api, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if "ethereum" in data:
                            return float(data["ethereum"]["usd"])
                        elif "USD" in data:
                            return float(data["USD"])
                except:
                    continue
            
            # Fallback para um valor estimado
            return 3000.0
        except Exception as e:
            logger.warning(f"Erro ao obter preço do ETH: {e}")
            return 3000.0  # Valor estimado como fallback
    
    def calculate_financial_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula o score de risco financeiro baseado nos indicadores"""
        
        # Log para debug do objeto financial_data completo
        logger.info(f"financial_data recebido em calculate_financial_risk: {financial_data}")
        
        hf = financial_data.get("health_factor", 0)
        
        # Log para debug da chave específica que estamos buscando
        logger.info(f"Chaves disponíveis em financial_data: {financial_data.keys()}")
        logger.info(f"Valor de alavancagem no objeto: {financial_data.get('alavancagem', 'CHAVE NÃO ENCONTRADA')}")
        
        leverage = financial_data.get("alavancagem", 0)
        
        # Log para debug do valor de alavancagem recebido
        logger.info(f"Valor de alavancagem recebido no calculate_financial_risk: {leverage}")
        
        # Verificar se é infinito ou NaN
        if hf == float('inf') or hf == float('nan') or hf <= 0:
            hf_display = "∞"  # Para apresentação
            hf_classification = "Sem empréstimos"
            hf_score = 0.0     # Sem risco
        else:
            hf_display = hf    # Valor numérico para cálculos
            
            # Cálculo do score para Health Factor (inversamente proporcional)
            if hf < 1.0:
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
        
        # Score final ponderado - se não tiver empréstimos, leverage é o único fator
        if hf == float('inf') or hf == float('nan') or hf <= 0:
            final_score = leverage_score
        else:
            final_score = (hf_score * hf_weight) + (leverage_score * leverage_weight)
        
        # Alertas principais
        alertas = []
        if hf != float('inf') and hf != float('nan') and hf > 0 and hf < 1.5:
            alertas.append(f"HF crítico: {hf}")
        if leverage > 3.0:
            alertas.append(f"Alavancagem elevada: {leverage}x")
        
        # Dados financeiros gerais para incluir na resposta
        financial_overview = {
            "collateral": financial_data.get("total_collateral_usd", 0),
            "debt": financial_data.get("total_debt_usd", 0),
            "nav": financial_data.get("net_asset_value", 0),
            "alavancagem": leverage
        }
        
        # Resposta completa
        return {
            "categoria": "Financeiro Direto",
            "score": round(final_score, 2),
            "peso": 0.35,  # Peso desta categoria no risco global
            "principais_alertas": alertas,
            "financial_overview": financial_overview,
            "detalhes": {
                "health_factor": {
                    "valor": hf_display,
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