from app.services.tv_session_manager import get_tv_instance

from fastapi import APIRouter, HTTPException, Depends
from tvDatafeed import TvDatafeed, Interval
from app.utils.rsi_utils import calcular_rsi
from app.utils.divergence_utils import detectar_divergencias, consolidar_analise_divergencias
from app.config import Settings, get_settings
import pandas as pd
from typing import Dict, Any

router = APIRouter()

interval_map = {
    "15m": Interval.in_15_minute,
    "30m": Interval.in_30_minute,
    "1h": Interval.in_1_hour,
    "4h": Interval.in_4_hour,
    "1d": Interval.in_daily,
    "1w": Interval.in_weekly
}

@router.get("/analise-divergencia-rsi", 
            summary="Análise de Divergências do RSI/IFR", 
            tags=["Análise Técnica"])
def get_all_divergences(settings: Settings = Depends(get_settings)):
    try:
        tv = get_tv_instance()
        result = {"divergencias": {}}
        todas_divergencias = {}

        for key, interval in interval_map.items():
            try:
                # Obtém mais candles para ter dados suficientes para a análise
                df = tv.get_hist(symbol="BTCUSDT", exchange="BINANCE", interval=interval, n_bars=500)

                if not isinstance(df, pd.DataFrame) or df.empty:
                    raise ValueError(f"Sem dados retornados para o intervalo {key}")

                # Calcular RSI
                df = calcular_rsi(df, periodo=14)
                
                # Detectar divergências com janela de análise mais ampla
                analise = detectar_divergencias(df, janela_extremos=3, janela_analise=120)
                
                # Adicionar informações de debug para timeframes específicos
                if key in ["1d", "4h"]:
                    # Encontra topos e fundos 
                    df_debug = df.tail(50).copy()
                    df_debug['extremos_preco'] = pd.Series(0, index=df_debug.index)
                    
                    # Marca extremos manualmente para debug
                    for i in range(3, len(df_debug) - 3):
                        # Verificar topo
                        if df_debug['close'].iloc[i] == max(df_debug['close'].iloc[i-3:i+4]):
                            df_debug.loc[df_debug.index[i], 'extremos_preco'] = 1
                        # Verificar fundo
                        elif df_debug['close'].iloc[i] == min(df_debug['close'].iloc[i-3:i+4]):
                            df_debug.loc[df_debug.index[i], 'extremos_preco'] = -1
                    
                    # Extrair pontos extremos para debug
                    topos = df_debug[df_debug['extremos_preco'] == 1][['close', 'RSI']].tail(3)
                    fundos = df_debug[df_debug['extremos_preco'] == -1][['close', 'RSI']].tail(3)
                    
                    # Adicionar informações de debug 
                    analise["debug"] = {
                        "total_candles": len(df),
                        "topos_recentes": {
                            idx.strftime("%Y-%m-%d %H:%M"): {
                                "preco": round(row["close"], 2),
                                "rsi": round(row["RSI"], 2)
                            } for idx, row in topos.iterrows()
                        },
                        "fundos_recentes": {
                            idx.strftime("%Y-%m-%d %H:%M"): {
                                "preco": round(row["close"], 2),
                                "rsi": round(row["RSI"], 2)
                            } for idx, row in fundos.iterrows()
                        }
                    }
                
                result["divergencias"][key] = analise
                todas_divergencias[key] = analise

            except Exception as e:
                result["divergencias"][key] = {
                    "divergencia_detectada": False,
                    "erro": str(e)
                }

        # Adicionar análise consolidada
        result["consolidado"] = consolidar_analise_divergencias(todas_divergencias)
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar com TradingView: {str(e)}")