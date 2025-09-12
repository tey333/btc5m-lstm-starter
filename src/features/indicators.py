import numpy as np
import pandas as pd
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

def add_features(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    df = df.copy()

    # log returns
    df["logret"] = np.log(df["close"]).diff()
    for h in cfg["feature"]["return_lags"]:
        df[f"logret_lag_{h}"] = df["logret"].shift(1).rolling(h).sum()

    # ATR & normalized
    atr = AverageTrueRange(df["high"], df["low"], df["close"], window=cfg["feature"]["atr_period"])
    df["atr"] = atr.average_true_range()
    df["atr_norm"] = df["atr"] / df["close"]

    # EMA gaps
    for p in cfg["feature"]["ema_periods"]:
        ema = EMAIndicator(df["close"], window=p).ema_indicator()
        df[f"ema_{p}_gap"] = (df["close"] - ema) / df["close"]

    # RSI (0..1)
    rsi = RSIIndicator(df["close"], window=cfg["feature"]["rsi_period"]).rsi()
    df["rsi"] = (rsi/100.0).clip(0,1)

    # Candle/body & range
    body = (df["close"] - df["open"])
    rng = (df["high"] - df["low"]).replace(0, np.nan)
    df["body_norm"] = (body / rng).clip(-5,5).fillna(0)
    df["hl_range"] = rng / df["close"]

    # Time features
    ts = pd.to_datetime(df["timestamp"], utc=True)
    minute = ts.dt.minute + ts.dt.hour * 60
    df["tod_sin"] = np.sin(2*np.pi*minute/1440)
    df["tod_cos"] = np.cos(2*np.pi*minute/1440)
    dow = ts.dt.dayofweek
    df["dow_sin"] = np.sin(2*np.pi*dow/7)
    df["dow_cos"] = np.cos(2*np.pi*dow/7)

    return df.dropna()
