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
        
        # Configuração do Web3
        self.w3 = None
        self.initialize_web3()
        
        # Contratos AAVE v3 na Arbitrum
        self.aave_pool_address = "0x794a61358D6845594F94dc1DB02A252b5b4814aD"  # Aave v3 Pool na Arbitrum
        self.aave_pool_abi = self.load_abi("aave_pool")
        self.aave_pool_contract = None
        
        if self.w3:
            try:
                self.aave_pool_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(self.aave_pool_address),
                    abi=self.aave_pool_abi
                )
                logger.info("Contrato AAVE Pool inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar contrato AAVE: {str(e)}")
        
        # Cache
        self.cache = None
        self.last_fetch = None
        self.cache_duration = datetime.timedelta(minutes=10)  # Cache válido por 10 minutos
    
    def initialize_web3(self):
        """Inicializa a conexão Web3 com RPC público"""
        try:
            # Tenta vários RPC públicos disponíveis
            rpc_endpoints = [
                "https://arb1.arbitrum.io/rpc",
                "https://arbitrum-one.public.blastapi.io",
                "https://endpoints.omniatech.io/v1/arbitrum/one/public",
                "https://arbitrum.blockpi.network/v1/rpc/public"
            ]
            
            for rpc_url in rpc_endpoints:
                try:
                    logger.info(f"Tentando conectar ao RPC: {rpc_url}")
                    self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 30}))
                    if self.w3.is_connected():
                        logger.info(f"Web3 conectado com sucesso: {rpc_url}")
                        return
                except Exception as e:
                    logger.warning(f"Falha ao conectar a {rpc_url}: {str(e)}")
            
            logger.error("Não foi possível conectar a nenhum RPC público")
            self.w3 = None
        except Exception as e:
            logger.error(f"Erro ao inicializar Web3: {str(e)}")
            self.w3 = None
    
    def load_abi(self, name):
        """Carrega ABI a partir de um arquivo ou retorna um ABI mínimo necessário"""
        try:
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
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar ABI {name}: {str(e)}")
            return []
    
    async def fetch_financial_data(self) -> Dict[str, Any]:
        """Busca dados financeiros da carteira na AAVE v3 via Web3 ou APIs de fallback"""
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
            
            # Primeiro tentar via Web3 diretamente (mais confiável)
            if self.w3 and self.aave_pool_contract and self.w3.is_connected():
                try:
                    result = await self.get_data_from_web3()
                    if result and "error" not in result:
                        # Atualiza o cache
                        self.cache = result
                        self.last_fetch = current_time
                        return result
                except Exception as e:
                    logger.warning(f"Falha ao obter dados via Web3: {str(e)}")
            
            # Se Web3 falhar, tentar via APIs
            logger.info("Web3 falhou ou não está disponível, tentando APIs alternativas")
            
            # Tentar obter dados via Debank API
            data = self._get_debank_protocol_data(self.wallet_address)
            
            # Se não conseguir via Debank, tentar via APIs oficiais da AAVE (fallback)
            if not data or "error" in data:
                logger.warning(f"Falha na API Debank: {data.get('error', 'Erro desconhecido')}")
                data = self._get_aave_data_with_fallback(self.wallet_address)
            
            if "error" in data:
                logger.error(f"Erro ao obter dados financeiros: {data.get('error')}")
                if self.cache:  # Use o cache se disponível
                    return self.cache
                return {
                    "health_factor": 0,
                    "alavancagem": 0,
                    "supplied_asset_value": 0,
                    "net_asset_value": 0,
                    "error": data.get("error", "Erro desconhecido"),
                    "timestamp": current_time.isoformat()
                }
            
            # Processar os dados obtidos
            health_factor = data.get("health_factor", 0)
            
            # Calcular NAV (Net Asset Value)
            total_collateral = data.get("total_collateral_usd", 0)
            total_debt = data.get("total_debt_usd", 0)
            nav = total_collateral - total_debt
            
            # Calcular alavancagem
            leverage = 1.0
            if nav > 0 and total_collateral > 0:
                leverage = total_collateral / nav
            
            # Calcular valor de ativos fornecidos 
            supplied_asset_value = total_collateral
            
            # Constrói o resultado
            result = {
                "health_factor": health_factor,
                "alavancagem": round(leverage, 2),
                "supplied_asset_value": supplied_asset_value,
                "net_asset_value": nav,
                "total_collateral_usd": total_collateral,
                "total_debt_usd": total_debt,
                "timestamp": current_time.isoformat()
            }
            
            # Adiciona detalhes de assets se disponíveis
            if "asset_details" in data:
                result["asset_details"] = data["asset_details"]
            
            # Atualiza o cache
            self.cache = result
            self.last_fetch = current_time
            
            logger.info(f"Dados financeiros obtidos com sucesso: HF={health_factor}, NAV=${nav}")
            return result
            
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
    
    async def get_data_from_web3(self):
        """Obtém dados diretamente dos contratos via Web3"""
        try:
            logger.info(f"Consultando contrato AAVE via Web3 para carteira: {self.wallet_address}")
            
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
            health_factor_raw = Decimal(user_data[5]) / Decimal(10**18)  # formato especial
            
            # Tratar health factor infinito
            if health_factor_raw > Decimal(10**10) or total_debt_eth == 0:
                health_factor = float('inf')
            else:
                health_factor = float(health_factor_raw)
            
            # Calcula o valor líquido dos ativos (NAV)
            net_asset_value = float(total_collateral_eth - total_debt_eth)
            
            # Calcula a alavancagem (se collateral for 0, alavancagem é 1.0)
            leverage = 1.0
            if net_asset_value > 0 and float(total_collateral_eth) > 0:
                leverage = float(total_collateral_eth) / net_asset_value
            
            # Note: valores já estão em USD na resposta do contrato AAVE v3
            total_collateral_usd = float(total_collateral_eth)
            total_debt_usd = float(total_debt_eth)
            
            # Não temos dados específicos de tokens, então assumimos que todo valor é WBTC
            # Em uma implementação mais completa, precisaríamos consultar cada token separadamente
            wbtc_supplied_value_usd = total_collateral_usd
            
            logger.info(f"Dados obtidos via Web3: HF={health_factor}, Collateral=${total_collateral_usd}, Debt=${total_debt_usd}")
            
            return {
                "health_factor": health_factor,
                "wbtc_supplied_value_usd": wbtc_supplied_value_usd,
                "net_asset_value_usd": net_asset_value,
                "total_collateral_usd": total_collateral_usd,
                "total_debt_usd": total_debt_usd,
                "ltv": float(ltv * 100),  # Convertido para percentual
                "liquidation_threshold": float(current_liquidation_threshold * 100),  # Convertido para percentual
                "source": "web3_direct"
            }
            
        except Exception as e:
            logger.warning(f"Falha ao obter dados via Web3: {str(e)}")
            return {"error": f"Falha ao consultar contrato: {str(e)}"}
    
    def _get_aave_data_official_api(self, wallet_address):
        """Obter dados da AAVE v3 na Arbitrum usando a API oficial da AAVE"""
        try:
            logger.info("Tentando método API oficial v1 da AAVE")
            # ID da rede Arbitrum
            network_id = 42161
            
            # Endpoint da API oficial da AAVE para v3
            url = f"https://app.aave.com/api/v1/data/user-summary?address={wallet_address}&network={network_id}"
            
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return {"error": f"Erro ao acessar API: {response.status_code}"}
                
            data = response.json()
            
            # Verificar se há dados relevantes
            if not data or "error" in data:
                return {"error": "Posição não encontrada ou erro na API"}
                
            # Verificar se temos o campo necessário
            if "healthFactor" not in data or "totalCollateralUSD" not in data:
                return {"error": "Dados incompletos na resposta da API"}
                
            # Estrutura esperada da resposta
            wbtc_supplied_value = 0
            health_factor = float('inf')
            net_asset_value = 0
            
            # Processar health factor
            if "healthFactor" in data:
                try:
                    health_factor = float(data["healthFactor"])
                    if health_factor == 0:
                        health_factor = float('inf')
                except (ValueError, TypeError):
                    health_factor = float('inf')
                    
            # Processar net asset value (totalCollateralUSD - totalDebtUSD)
            total_collateral = float(data.get("totalCollateralUSD", 0))
            total_debt = float(data.get("totalDebtUSD", 0))
            net_asset_value = total_collateral - total_debt
            
            # Buscar valor específico de WBTC fornecido
            supplies = data.get("supplies", [])
            asset_details = []
            
            for asset in supplies:
                if asset.get("symbol") == "WBTC":
                    wbtc_supplied_value = float(asset.get("amountUSD", 0))
                
                asset_details.append({
                    "symbol": asset.get("symbol", ""),
                    "balance": float(asset.get("amount", 0)),
                    "usd_value": float(asset.get("amountUSD", 0))
                })
                    
            logger.info(f"Método API oficial v1 bem sucedido. HF={health_factor}, Total Collateral=${total_collateral}")
                    
            return {
                "health_factor": health_factor,
                "wbtc_supplied_value_usd": wbtc_supplied_value,
                "net_asset_value_usd": net_asset_value,
                "total_collateral_usd": total_collateral,
                "total_debt_usd": total_debt,
                "asset_details": asset_details
            }
            
        except Exception as e:
            logger.warning(f"Falha no método API oficial v1: {str(e)}")
            return {"error": f"Erro ao processar dados: {str(e)}"}
    
    def _get_aave_data_alternative(self, wallet_address):
        """Endpoint alternativo da API AAVE para dados de usuário"""
        try:
            logger.info("Tentando método API alternativa v3 da AAVE")
            url = f"https://api.aave.com/data/v3/users/{wallet_address}/summary?networkId=42161"
            
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return {"error": f"Erro ao acessar API alternativa: {response.status_code}"}
                
            data = response.json()
            
            # Processar dados
            health_factor = float(data.get("healthFactor", "inf"))
            if health_factor == 0:
                health_factor = float('inf')
                
            total_collateral_usd = float(data.get("totalCollateralMarketReferenceCurrency", 0))
            total_debt_usd = float(data.get("totalBorrowsMarketReferenceCurrency", 0))
            net_asset_value = total_collateral_usd - total_debt_usd
            
            # Detalhes dos ativos
            asset_details = []
            wbtc_supplied_value = 0
            
            for asset in data.get("userReservesData", []):
                if asset.get("reserve", {}).get("symbol") == "WBTC":
                    wbtc_supplied_value = float(asset.get("underlyingBalanceUSD", 0))
                
                asset_details.append({
                    "symbol": asset.get("reserve", {}).get("symbol", ""),
                    "balance": float(asset.get("underlyingBalance", 0)),
                    "usd_value": float(asset.get("underlyingBalanceUSD", 0))
                })
                    
            logger.info(f"Método API alternativa v3 bem sucedido. HF={health_factor}, Total Collateral=${total_collateral_usd}")
                    
            return {
                "health_factor": health_factor,
                "wbtc_supplied_value_usd": wbtc_supplied_value,
                "net_asset_value_usd": net_asset_value,
                "total_collateral_usd": total_collateral_usd,
                "total_debt_usd": total_debt_usd,
                "asset_details": asset_details
            }
            
        except Exception as e:
            logger.warning(f"Falha no método API alternativa v3: {str(e)}")
            return {"error": f"Erro ao processar dados alternativos: {str(e)}"}

    def _get_ui_api_data(self, wallet_address):
        """Obter dados via UI API"""
        try:
            logger.info("Tentando método UI API da AAVE")
            # URL para dados do pool
            pool_api_url = "https://app.aave.com/api/v1/ui-pool-data?networkId=42161&lendingPoolAddressProvider=0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb"
            response = requests.get(pool_api_url, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Erro ao acessar UI API (pool data): {response.status_code}")
                return {"error": f"Erro ao acessar UI API (pool): {response.status_code}"}
                
            pool_data = response.json()
            
            # URL para dados do usuário
            user_api_url = f"https://app.aave.com/api/v1/user-data?networkId=42161&lendingPoolAddressProvider=0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb&userAddress={wallet_address}"
            user_response = requests.get(user_api_url, timeout=10)
            
            if user_response.status_code != 200:
                logger.error(f"Erro ao acessar UI API (user data): {user_response.status_code}")
                return {"error": f"Erro ao acessar UI API (user): {user_response.status_code}"}
                
            user_data = user_response.json()
            
            # Extrair health factor
            health_factor = float('inf')
            if user_data.get("healthFactor") and user_data["healthFactor"] != "0":
                health_factor = float(user_data["healthFactor"])
                
            # Extrair dados de colateral e dívidas
            total_collateral_usd = float(user_data.get("totalCollateralUSD", 0))
            total_debt_usd = float(user_data.get("totalBorrowsUSD", 0))
            net_asset_value = total_collateral_usd - total_debt_usd
            
            # Extrair detalhes dos ativos
            asset_details = []
            wbtc_supplied_value = 0
            
            for reserve in user_data.get("reservesData", []):
                if reserve.get("symbol") == "WBTC" and float(reserve.get("underlyingBalanceUSD", 0)) > 0:
                    wbtc_supplied_value = float(reserve.get("underlyingBalanceUSD", 0))
                
                if float(reserve.get("underlyingBalance", 0)) > 0:
                    asset_details.append({
                        "symbol": reserve.get("symbol", ""),
                        "balance": float(reserve.get("underlyingBalance", 0)),
                        "usd_value": float(reserve.get("underlyingBalanceUSD", 0))
                    })
                    
            logger.info(f"Método UI API bem sucedido. HF={health_factor}, Total Collateral=${total_collateral_usd}")
                    
            return {
                "health_factor": health_factor,
                "wbtc_supplied_value_usd": wbtc_supplied_value,
                "net_asset_value_usd": net_asset_value,
                "total_collateral_usd": total_collateral_usd,
                "total_debt_usd": total_debt_usd,
                "asset_details": asset_details
            }
            
        except Exception as e:
            logger.warning(f"Falha no método UI API: {str(e)}")
            return {"error": f"Erro ao processar dados UI API: {str(e)}"}

    def _get_debank_protocol_data(self, wallet_address):
        """
        Obter dados da AAVE v3 na Arbitrum via Debank API
        Esta API é pública e confiável, sendo usada por várias carteiras e aplicações
        """
        try:
            logger.info("Tentando método Debank API")
            
            # Endpoint para protocolos específicos
            url = f"https://openapi.debank.com/v1/user/protocol?id={wallet_address.lower()}&protocol_id=aave3-arbitrum"
            
            # Headers para evitar bloqueio
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json"
            }
            
            # Fazer a requisição
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"Erro ao acessar Debank API (protocol): {response.status_code}")
                return {"error": f"Erro ao acessar Debank API: {response.status_code}"}
            
            data = response.json()
            
            # Verificar se encontrou protocolo
            if not data or not isinstance(data, dict) or "error_code" in data:
                logger.warning(f"Protocolo AAVE v3 Arbitrum não encontrado via Debank")
                return {"error": "Protocolo AAVE v3 Arbitrum não encontrado"}
            
            # Dados do protocolo
            total_collateral_usd = 0
            total_debt_usd = 0
            asset_details = []
            wbtc_supplied_value = 0
            
            # Os dados do Debank são organizados em "portfolio_item_list"
            for item in data.get("portfolio_item_list", []):
                # Verificar se é um supply ou borrow
                if "detail" in item:
                    token_symbol = item.get("detail", {}).get("symbol", "")
                    token_price = float(item.get("detail", {}).get("price", 0))
                    token_amount = float(item.get("balance", 0))
                    usd_value = token_amount * token_price
                    
                    if "Supply" in item.get("name", "") or "Collateral" in item.get("name", ""):
                        total_collateral_usd += usd_value
                        
                        if token_symbol == "WBTC":
                            wbtc_supplied_value = usd_value
                        
                        asset_details.append({
                            "symbol": token_symbol,
                            "balance": token_amount,
                            "usd_value": usd_value,
                            "type": "supply"
                        })
                    
                    elif "Borrow" in item.get("name", ""):
                        total_debt_usd += usd_value
                        
                        asset_details.append({
                            "symbol": token_symbol,
                            "balance": token_amount,
                            "usd_value": usd_value,
                            "type": "borrow"
                        })
            
            # Health factor - o Debank não fornece diretamente, então precisamos calcular
            # ou usar outra API só para esse valor
            
            # Verificar se há divida para calcular health factor
            health_factor = float('inf')
            if total_debt_usd > 0:
                # Vamos tentar obter health factor
                try:
                    # Usando a API alternativa da AAVE só para o healthFactor
                    hf_url = f"https://aave-api-v2.aave.com/data/users/{wallet_address}/arbitrum/0xa97684ead0e402dc232d5a977953df7ecbab3cdb"
                    hf_response = requests.get(hf_url, timeout=10)
                    
                    if hf_response.status_code == 200:
                        hf_data = hf_response.json()
                        if "healthFactor" in hf_data:
                            health_factor = float(hf_data["healthFactor"])
                    else:
                        # Aproximação baseada na fórmula (LTV ajustado)
                        health_factor = (total_collateral_usd * 0.8) / total_debt_usd
                except:
                    # Aproximação como fallback final
                    health_factor = (total_collateral_usd * 0.8) / total_debt_usd if total_debt_usd > 0 else float('inf')
            
            # Net asset value
            net_asset_value = total_collateral_usd - total_debt_usd
            
            logger.info(f"Método Debank API bem sucedido. HF={health_factor}, Total Collateral=${total_collateral_usd}")
            
            return {
                "health_factor": health_factor,
                "wbtc_supplied_value_usd": wbtc_supplied_value,
                "net_asset_value_usd": net_asset_value,
                "total_collateral_usd": total_collateral_usd,
                "total_debt_usd": total_debt_usd,
                "asset_details": asset_details,
                "source": "debank"
            }
            
        except Exception as e:
            logger.warning(f"Falha no método Debank API: {str(e)}")
            return {"error": f"Erro ao processar dados Debank: {str(e)}"}

    def _get_aave_data_with_fallback(self, wallet_address):
        """
        Tentar obter dados usando vários métodos diferentes com fallback
        """
        # Primeiro método - API oficial
        result = self._get_aave_data_official_api(wallet_address)
        if "error" not in result:
            return result
        
        # Segundo método - API alternativa
        result_alt = self._get_aave_data_alternative(wallet_address)
        if "error" not in result_alt:
            return result_alt
        
        # Terceiro método - UI API
        result_ui = self._get_ui_api_data(wallet_address)
        if "error" not in result_ui:
            return result_ui
        
        # Se todos falharem
        return {"error": "Não foi possível obter dados da posição AAVE com nenhum método"}
    
    def calculate_financial_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula o score de risco financeiro baseado nos indicadores"""
        
        hf = financial_data.get("health_factor", 0)
        leverage = financial_data.get("alavancagem", 1.0)
        
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
        
        # Resposta completa
        return {
            "categoria": "Financeiro Direto",
            "score": round(final_score, 2),
            "peso": 0.35,  # Peso desta categoria no risco global
            "principais_alertas": alertas,
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