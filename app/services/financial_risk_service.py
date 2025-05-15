from bs4 import BeautifulSoup
import httpx
import datetime
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
            
            # Extração dos valores
            supplied_value = self._extract_supplied_asset_value(soup)
            net_asset_value = self._extract_net_asset_value(soup)
            health_factor = self._extract_health_factor(soup)
            
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
    
    def _extract_supplied_asset_value(self, soup) -> float:
        try:
            # Encontrando o valor de "Supplied Asset Value" na página
            elements = soup.find_all("div", {"class": "grid-item"})
            for element in elements:
                heading = element.find("div", {"class": "item-label"})
                if heading and "Supplied Asset Value" in heading.text:
                    value_text = element.find("div", {"class": "item-value"}).text.strip()
                    # Remover $ e , e converter para float
                    return float(value_text.replace("$", "").replace(",", ""))
            # Se não encontrou o elemento específico, tenta método alternativo
            value_element = soup.select_one("div.supplied-value")
            if value_element:
                return float(value_element.text.strip().replace("$", "").replace(",", ""))
            return 10000  # Valor fallback
        except Exception as e:
            print(f"Erro ao extrair Supplied Asset Value: {e}")
            return 10000  # Valor fallback
    
    def _extract_net_asset_value(self, soup) -> float:
        try:
            # Encontrando o valor de "Net Asset Value" na página
            elements = soup.find_all("div", {"class": "grid-item"})
            for element in elements:
                heading = element.find("div", {"class": "item-label"})
                if heading and "Net Asset Value" in heading.text:
                    value_text = element.find("div", {"class": "item-value"}).text.strip()
                    # Remover $ e , e converter para float
                    return float(value_text.replace("$", "").replace(",", ""))
            # Se não encontrou o elemento específico, tenta método alternativo
            value_element = soup.select_one("div.net-asset-value")
            if value_element:
                return float(value_element.text.strip().replace("$", "").replace(",", ""))
            return 5000  # Valor fallback
        except Exception as e:
            print(f"Erro ao extrair Net Asset Value: {e}")
            return 5000  # Valor fallback
    
    def _extract_health_factor(self, soup) -> float:
        try:
            # Encontrando o valor de "Health Factor" na página
            elements = soup.find_all("div", {"class": "grid-item"})
            for element in elements:
                heading = element.find("div", {"class": "item-label"})
                if heading and "Health Factor" in heading.text:
                    value_text = element.find("div", {"class": "item-value"}).text.strip()
                    # Converter para float
                    return float(value_text)
            # Se não encontrou o elemento específico, tenta método alternativo
            hf_element = soup.select_one("div.health-factor")
            if hf_element:
                return float(hf_element.text.strip())
            return 2.0  # Valor fallback
        except Exception as e:
            print(f"Erro ao extrair Health Factor: {e}")
            return 2.0  # Valor fallback
    
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