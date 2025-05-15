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
                response = await client.get(self.defisim_url)
                response.raise_for_status()
                
                # Parsear o HTML com BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extração dos valores diretamente do HTML
                health_factor = 2.0  # Valor default
                supplied_value = 10000  # Valor default
                net_asset_value = 5000  # Valor default
                
                # Buscar os valores visíveis na página usando seletores específicos
                try:
                    # Localizar o Health Factor por classe específica do Mantine
                    health_factor_elements = soup.find_all("div", {"data-testid": "health-factor"})
                    if health_factor_elements:
                        for elem in health_factor_elements:
                            # Procurar por elementos numéricos dentro deste contenedor
                            value_text = elem.text.strip()
                            match = re.search(r'\d+(\.\d+)?', value_text)
                            if match:
                                health_factor = float(match.group())
                                break
                    
                    if health_factor == 2.0:  # Se ainda não encontrou, tente outros seletores
                        # Buscar por spans específicos que possam conter o valor
                        spans = soup.find_all("span", {"class": lambda x: x and "mantine" in x})
                        for span in spans:
                            if span.text and re.match(r'^\d+(\.\d+)?$', span.text.strip()):
                                health_factor = float(span.text.strip())
                                break
                    
                    # Buscar os valores de Supplied e Net Asset
                    grid_items = soup.find_all("div", {"class": lambda x: x and "grid" in x})
                    for item in grid_items:
                        item_text = item.text.strip()
                        if "Supplied Asset Value" in item_text:
                            match = re.search(r'\$([0-9,.]+)', item_text)
                            if match:
                                supplied_value = float(match.group(1).replace(",", ""))
                        elif "Net Asset Value" in item_text:
                            match = re.search(r'\$([0-9,.]+)', item_text)
                            if match:
                                net_asset_value = float(match.group(1).replace(",", ""))
                                
                except Exception as e:
                    print(f"Erro no parsing detalhado: {e}")
                    
                # Cálculo da alavancagem
                leverage = supplied_value / net_asset_value if net_asset_value > 0 else float('inf')
                
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
            # Em caso de erro, tenta usar o cache antigo se disponível
            if self.cache:
                return self.cache
            # Ou retorna valores de fallback
            return {
                "health_factor": 2.0,  # Valor conservador
                "alavancagem": 2.0,    # Valor conservador
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