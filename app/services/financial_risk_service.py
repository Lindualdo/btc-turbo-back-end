from bs4 import BeautifulSoup
import httpx
import datetime
import re
from typing import Dict, Any, List, Optional

class FinancialRiskService:
    def __init__(self):
        self.defi_address = "0x2A81EdB7C75BfdCcB7a156de3152C61D00247d62"
        self.defisim_url = f"https://defisim.xyz/?address={self.defi_address}"
        self.cache = None
        self.last_fetch = None
        self.cache_duration = datetime.timedelta(minutes=10)  # Cache válido por 10 minutos
    
    async def fetch_financial_data(self) -> Dict[str, Any]:
        """Executa o scraping dos dados financeiros do DeFiSim"""
        current_time = datetime.datetime.now()
        
        # Verifica se o cache é válido
        if self.cache and self.last_fetch and (current_time - self.last_fetch < self.cache_duration):
            return self.cache
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"Fazendo requisição para: {self.defisim_url}")
                response = await client.get(self.defisim_url)
                response.raise_for_status()
                
                # Parsear o HTML com BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                html_content = str(soup)
                
                # Extração dos valores diretamente do HTML
                health_factor = None  # Vai ser atualizado abaixo
                supplied_value = None
                net_asset_value = None
                
                # 1. Buscar o Health Factor diretamente pelo data-testid
                try:
                    health_factor_div = soup.find("div", {"data-testid": "health-factor"})
                    if health_factor_div:
                        # Extrair o valor numérico usando regex
                        text_content = health_factor_div.text.strip()
                        hf_match = re.search(r'[\d.]+', text_content)
                        if hf_match:
                            health_factor = float(hf_match.group())
                            print(f"Health Factor encontrado via data-testid: {health_factor}")
                except Exception as e:
                    print(f"Erro ao buscar Health Factor por data-testid: {e}")
                
                # 2. Se não encontrou, buscar em classes específicas do Mantine
                if not health_factor:
                    try:
                        # Buscar em todos os spans do Mantine que podem conter valores
                        mantine_texts = soup.find_all("span", {"class": lambda x: x and "mantine-Text-root" in x})
                        for text_elem in mantine_texts:
                            text = text_elem.text.strip()
                            # Verificar se é apenas um número (possível health factor)
                            if re.match(r'^[\d.]+$', text):
                                health_factor = float(text)
                                print(f"Health Factor encontrado via classes Mantine: {health_factor}")
                                break
                    except Exception as e:
                        print(f"Erro ao buscar Health Factor por classes Mantine: {e}")
                
                # 3. Método mais genérico - buscar tabelas ou grid de dados
                if not health_factor or not supplied_value or not net_asset_value:
                    try:
                        # Buscar em todas as divs que possam conter grid de dados
                        data_items = soup.find_all("div", {"class": lambda x: x and ("grid" in x or "card" in x)})
                        for item in data_items:
                            item_text = item.text.strip()
                            
                            # Buscar Health Factor
                            if not health_factor and "Health Factor" in item_text:
                                hf_match = re.search(r'[\d.]+', item_text.split("Health Factor")[-1])
                                if hf_match:
                                    health_factor = float(hf_match.group())
                                    print(f"Health Factor encontrado via grid: {health_factor}")
                            
                            # Buscar Supplied Asset Value
                            if not supplied_value and "Supplied Asset" in item_text:
                                val_match = re.search(r'\$[\d,]+(?:\.\d+)?', item_text)
                                if val_match:
                                    supplied_value = float(val_match.group().replace("$", "").replace(",", ""))
                                    print(f"Supplied Asset Value encontrado: {supplied_value}")
                            
                            # Buscar Net Asset Value
                            if not net_asset_value and "Net Asset" in item_text:
                                val_match = re.search(r'\$[\d,]+(?:\.\d+)?', item_text)
                                if val_match:
                                    net_asset_value = float(val_match.group().replace("$", "").replace(",", ""))
                                    print(f"Net Asset Value encontrado: {net_asset_value}")
                    except Exception as e:
                        print(f"Erro ao buscar dados via listas/grids: {e}")
                
                # 4. Último recurso - salvar o HTML completo para diagnóstico
                if not health_factor or not supplied_value or not net_asset_value:
                    print("Não foi possível encontrar todos os valores necessários")
                    if not health_factor:
                        print("Não foi possível encontrar Health Factor, usando valor padrão")
                        health_factor = 0  # Valor zero para indicar falha na extração
                    if not supplied_value:
                        print("Não foi possível encontrar Supplied Asset Value, usando valor padrão")
                        supplied_value = 0  # Valor zero para indicar falha na extração
                    if not net_asset_value:
                        print("Não foi possível encontrar Net Asset Value, usando valor padrão")
                        net_asset_value = 0  # Valor zero para indicar falha na extração
                
                # Cálculo da alavancagem
                leverage = supplied_value / net_asset_value if net_asset_value > 0 else 0  # Zero em caso de erro
                
                # Preparar resposta
                data = {
                    "health_factor": health_factor,
                    "alavancagem": round(leverage, 2),
                    "supplied_asset_value": supplied_value,
                    "net_asset_value": net_asset_value,
                    "timestamp": current_time.isoformat()
                }
                
                # Atualiza o cache
                self.cache = data
                self.last_fetch = current_time
                
                return data
                
        except Exception as e:
            print(f"Erro ao fazer scraping: {e}")
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