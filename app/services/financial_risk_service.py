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
        self.cache = None
        self.last_fetch = None
        self.cache_duration = datetime.timedelta(minutes=10)  # Cache válido por 10 minutos
    
    async def fetch_financial_data(self) -> Dict[str, Any]:
        """Busca dados financeiros da carteira na AAVE v3 via APIs oficiais da AAVE"""
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
            
            # Tentar obter dados usando múltiplos métodos com fallback automático
            result = self.get_aave_data_with_fallback()
            
            if "error" in result:
                logger.error(f"Erro ao buscar dados financeiros: {result['error']}")
                return {
                    "health_factor": 0,
                    "alavancagem": 0,
                    "supplied_asset_value": 0,
                    "net_asset_value": 0,
                    "error": result["error"],
                    "timestamp": current_time.isoformat()
                }
            
            # Extrair dados do resultado
            health_factor = result["health_factor"]
            total_collateral = result["total_collateral_usd"]
            total_debt = result["total_debt_usd"]
            nav = result["net_asset_value_usd"]
            wbtc_supplied_value = result.get("wbtc_supplied_value_usd", 0)
            
            # Se nav for zero, use total_collateral para evitar divisão por zero
            if nav <= 0 and total_collateral > 0:
                nav = total_collateral
            
            # Calcular alavancagem
            leverage = total_collateral / nav if nav > 0 else 0
            
            logger.info(f"Health Factor: {health_factor}")
            logger.info(f"Total Collateral: ${total_collateral}")
            logger.info(f"Total Debt: ${total_debt}")
            logger.info(f"NAV: ${nav}")
            logger.info(f"Leverage: {leverage}x")
            logger.info(f"WBTC Supplied Value: ${wbtc_supplied_value}")
            
            # Resultado
            data = {
                "health_factor": health_factor,
                "alavancagem": round(leverage, 2),
                "supplied_asset_value": total_collateral,
                "wbtc_supplied_value": wbtc_supplied_value,
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
    
    def get_aave_data_with_fallback(self) -> Dict[str, Any]:
        """
        Tentar obter dados usando múltiplos métodos com fallback automático
        """
        # Primeiro método: API Oficial AAVE v1
        result = self.get_aave_data_official_api()
        if "error" not in result:
            logger.info("Dados obtidos com sucesso usando API oficial v1")
            return result
        
        logger.warning(f"Falha no método API oficial v1: {result.get('error')}")
        
        # Segundo método: API Alternativa AAVE v3
        result_alt = self.get_aave_data_alternative()
        if "error" not in result_alt:
            logger.info("Dados obtidos com sucesso usando API alternativa v3")
            return result_alt
        
        logger.warning(f"Falha no método API alternativa v3: {result_alt.get('error')}")
        
        # Terceiro método: API UI da AAVE
        result_ui = self.get_aave_data_ui_api()
        if "error" not in result_ui:
            logger.info("Dados obtidos com sucesso usando UI API")
            return result_ui
        
        logger.warning(f"Falha no método UI API: {result_ui.get('error')}")
        
        # Se todos os métodos falharem, retorna erro
        return {"error": "Não foi possível obter dados da posição AAVE com nenhum método"}
    
    def get_aave_data_official_api(self) -> Dict[str, Any]:
        """
        Obter dados da AAVE v3 na Arbitrum usando a API oficial da AAVE
        """
        # ID da rede Arbitrum
        network_id = 42161
        
        # Endpoint da API oficial da AAVE para v3
        url = f"https://app.aave.com/api/v1/data/user-summary?address={self.wallet_address}&network={network_id}"
        
        try:
            logger.info(f"Consultando API oficial AAVE: {url}")
            response = requests.get(url)
            
            if response.status_code != 200:
                logger.error(f"Erro ao acessar API oficial: {response.status_code} - {response.text}")
                return {"error": f"Erro ao acessar API: {response.status_code}"}
                
            data = response.json()
            logger.debug(f"Resposta da API oficial: {json.dumps(data, indent=2)}")
            
            # Verificar se há dados relevantes
            if not data or "error" in data:
                if "error" in data:
                    logger.error(f"Erro retornado pela API: {data['error']}")
                else:
                    logger.warning("API retornou objeto vazio ou sem dados")
                return {"error": "Posição não encontrada ou erro na API"}
                
            # Estrutura esperada da resposta
            wbtc_supplied_value = 0
            health_factor = float('inf')
            net_asset_value = 0
            
            # Processar health factor
            if "healthFactor" in data:
                try:
                    health_factor = float(data["healthFactor"])
                    logger.info(f"Health factor encontrado: {health_factor}")
                except (ValueError, TypeError):
                    logger.warning("Health factor não é um número válido, definindo como infinito")
                    health_factor = float('inf')
                    
            # Processar net asset value (totalCollateralUSD - totalDebtUSD)
            total_collateral = float(data.get("totalCollateralUSD", 0))
            total_debt = float(data.get("totalDebtUSD", 0))
            net_asset_value = total_collateral - total_debt
            
            logger.info(f"Collateral: ${total_collateral}, Debt: ${total_debt}, NAV: ${net_asset_value}")
            
            # Buscar valor específico de WBTC fornecido
            supplies = data.get("supplies", [])
            for asset in supplies:
                if asset.get("symbol") == "WBTC":
                    wbtc_supplied_value = float(asset.get("amountUSD", 0))
                    logger.info(f"WBTC fornecido: ${wbtc_supplied_value}")
                    break
                    
            return {
                "health_factor": health_factor,
                "wbtc_supplied_value_usd": wbtc_supplied_value,
                "net_asset_value_usd": net_asset_value,
                "total_collateral_usd": total_collateral,
                "total_debt_usd": total_debt
            }
            
        except Exception as e:
            logger.exception(f"Erro ao processar dados da API oficial: {e}")
            return {"error": f"Erro ao processar dados: {str(e)}"}
    
    def get_aave_data_alternative(self) -> Dict[str, Any]:
        """
        Endpoint alternativo da API AAVE para dados de usuário
        """
        url = f"https://api.aave.com/data/v3/users/{self.wallet_address}/summary?networkId=42161"
        
        try:
            logger.info(f"Consultando API alternativa AAVE v3: {url}")
            response = requests.get(url)
            
            if response.status_code != 200:
                logger.error(f"Erro ao acessar API alternativa: {response.status_code} - {response.text}")
                return {"error": f"Erro ao acessar API alternativa: {response.status_code}"}
                
            data = response.json()
            logger.debug(f"Resposta da API alternativa: {json.dumps(data, indent=2)}")
            
            # Processar dados
            health_factor = data.get("healthFactor")
            # Converter para float, tratando 'Infinity' ou outros valores não numéricos
            try:
                health_factor = float(health_factor) if health_factor is not None else float('inf')
            except (ValueError, TypeError):
                health_factor = float('inf')
            
            if health_factor == 0:
                health_factor = float('inf')
                
            total_collateral_usd = float(data.get("totalCollateralMarketReferenceCurrency", 0))
            total_debt_usd = float(data.get("totalBorrowsMarketReferenceCurrency", 0))
            net_asset_value = total_collateral_usd - total_debt_usd
            
            logger.info(f"Alternativo - HF: {health_factor}, Collateral: ${total_collateral_usd}, Debt: ${total_debt_usd}")
            
            # Encontrar WBTC nos ativos
            wbtc_supplied_value = 0
            for asset in data.get("userReservesData", []):
                if asset.get("reserve", {}).get("symbol") == "WBTC":
                    wbtc_supplied_value = float(asset.get("underlyingBalanceUSD", 0))
                    logger.info(f"WBTC fornecido (alternativo): ${wbtc_supplied_value}")
                    break
                    
            return {
                "health_factor": health_factor,
                "wbtc_supplied_value_usd": wbtc_supplied_value,
                "net_asset_value_usd": net_asset_value,
                "total_collateral_usd": total_collateral_usd,
                "total_debt_usd": total_debt_usd
            }
            
        except Exception as e:
            logger.exception(f"Erro ao processar dados alternativos: {e}")
            return {"error": f"Erro ao processar dados alternativos: {str(e)}"}
    
    def get_aave_data_ui_api(self) -> Dict[str, Any]:
        """
        Obtém dados do usuário usando a API UI da AAVE
        """
        try:
            # Primeiro, obter dados gerais do pool
            ui_api_url = "https://app.aave.com/api/v1/ui-pool-data?networkId=42161&lendingPoolAddressProvider=0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb"
            
            logger.info(f"Consultando UI API para dados de pool: {ui_api_url}")
            response = requests.get(ui_api_url)
            
            if response.status_code != 200:
                logger.error(f"Erro ao acessar UI API (pool data): {response.status_code}")
                return {"error": f"Erro ao acessar UI API (pool): {response.status_code}"}
                
            pool_data = response.json()
            
            # Agora obter os dados específicos do usuário
            user_api_url = f"https://app.aave.com/api/v1/user-data?networkId=42161&userAddress={self.wallet_address}"
            
            logger.info(f"Consultando UI API para dados do usuário: {user_api_url}")
            user_response = requests.get(user_api_url)
            
            if user_response.status_code != 200:
                logger.error(f"Erro ao acessar UI API (user data): {user_response.status_code}")
                return {"error": f"Erro ao acessar UI API (user): {user_response.status_code}"}
                
            user_data = user_response.json()
            logger.debug(f"Resposta da UI API (user): {json.dumps(user_data, indent=2)}")
            
            if not user_data:
                logger.warning("UI API retornou dados vazios para o usuário")
                return {"error": "Sem dados de usuário na UI API"}
                
            # Extrair Health Factor
            health_factor = float('inf')  # Valor padrão se não houver empréstimos
            if "healthFactor" in user_data and user_data["healthFactor"] is not None:
                try:
                    health_factor = float(user_data["healthFactor"])
                    if health_factor == 0:
                        health_factor = float('inf')  # 0 significa "sem empréstimos"
                except (ValueError, TypeError):
                    logger.warning(f"Valor inválido para healthFactor: {user_data['healthFactor']}")
            
            # Calcular valores totais
            total_collateral_usd = float(user_data.get("totalLiquidityUSD", 0))
            total_debt_usd = float(user_data.get("totalBorrowsUSD", 0))
            net_asset_value = total_collateral_usd - total_debt_usd
            
            # Buscar valor de WBTC
            wbtc_supplied_value = 0
            for asset in user_data.get("reserves", []):
                if asset.get("symbol") == "WBTC" and "underlyingBalanceUSD" in asset:
                    wbtc_supplied_value = float(asset["underlyingBalanceUSD"])
                    break
            
            logger.info(f"UI API - HF: {health_factor}, Collateral: ${total_collateral_usd}, Debt: ${total_debt_usd}")
            
            return {
                "health_factor": health_factor,
                "wbtc_supplied_value_usd": wbtc_supplied_value,
                "net_asset_value_usd": net_asset_value,
                "total_collateral_usd": total_collateral_usd,
                "total_debt_usd": total_debt_usd
            }
            
        except Exception as e:
            logger.exception(f"Erro ao processar dados da UI API: {e}")
            return {"error": f"Erro ao processar dados da UI API: {str(e)}"}
    
    def calculate_financial_risk(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula o score de risco financeiro baseado nos indicadores"""
        
        hf = financial_data["health_factor"]
        leverage = financial_data["alavancagem"]
        
        # Verificação para health factor infinito (sem empréstimos)
        is_infinite_hf = (hf == float('inf') or hf > 1000)
        
        # Cálculo do score para Health Factor (inversamente proporcional)
        if is_infinite_hf:
            hf_score = 1.0  # Risco mínimo (sem empréstimos)
            hf_classification = "Sem empréstimos"
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
        if hf < 1.5 and not is_infinite_hf:
            alertas.append(f"HF crítico: {hf:.2f}")
        if leverage > 3.0:
            alertas.append(f"Alavancagem elevada: {leverage}x")
        
        # Se não houver alertas, adicionar um neutro
        if not alertas:
            if is_infinite_hf:
                alertas.append("Sem empréstimos ativos")
            else:
                alertas.append(f"HF saudável: {hf:.2f}")
        
        # Formatar health factor para exibição
        hf_display = "∞" if is_infinite_hf else hf
        
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