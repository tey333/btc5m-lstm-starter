import pandas as pd
import glob

def read_any(path: str) -> pd.DataFrame:
    if path.lower().endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path)

def ensure_regular_5m(df: pd.DataFrame, tz_source: str, tz_target: str) -> pd.DataFrame:
    ts = pd.to_datetime(df["timestamp"])
    if ts.dt.tz is None:
        ts = ts.dt.tz_localize(tz_source)
    ts = ts.dt.tz_convert(tz_target)
    df = df.copy()
    df["timestamp"] = ts
    df = df.sort_values("timestamp").set_index("timestamp")

    full = pd.DataFrame(index=pd.date_range(df.index[0], df.index[-1], freq="5min", tz=tz_target))
    df = full.join(df, how="left")

    for c in ["open","high","low","close"]:
        if c in df:
            df[c] = df[c].ffill()
    if "volume" in df:
        df["volume"] = df["volume"].fillna(0)

    df = df.dropna(subset=["close"])
    return df.reset_index().rename(columns={"index":"timestamp"})

def load_all(raw_glob: str, tz_source: str, tz_target: str, ensure_regular: bool=True) -> pd.DataFrame:
    files = sorted(glob.glob(raw_glob))
    if not files:
        raise FileNotFoundError(f"No files matched: {raw_glob}")
    dfs = []
    for f in files:
        df = read_any(f)
        need = {"timestamp","open","high","low","close","volume"}
        miss = need - set(df.columns)
        if miss:
            raise ValueError(f"{f} missing columns: {miss}")
        if ensure_regular:
            df = ensure_regular_5m(df, tz_source, tz_target)
        else:
            ts = pd.to_datetime(df["timestamp"])
            if ts.dt.tz is None:
                ts = ts.dt.tz_localize(tz_source)
            df = df.copy()
            df["timestamp"] = ts.dt.tz_convert(tz_target)
            df = df.sort_values("timestamp")
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True).sort_values("timestamp")
    return data
