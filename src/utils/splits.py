import numpy as np
import pandas as pd

def time_splits(df: pd.DataFrame, train_m: int, valid_m: int, test_m: int, step_m: int):
    ts = pd.to_datetime(df["timestamp"], utc=True)
    cur = ts.min().normalize() + pd.Timedelta(days=1)
    end = ts.max()
    while cur + pd.DateOffset(months=train_m+valid_m+test_m) <= end:
        t0 = cur
        t1 = t0 + pd.DateOffset(months=train_m)
        v1 = t1 + pd.DateOffset(months=valid_m)
        s1 = v1 + pd.DateOffset(months=test_m)
        tr = (ts>=t0)&(ts<t1)
        va = (ts>=t1)&(ts<v1)
        te = (ts>=v1)&(ts<s1)
        yield (tr.to_numpy().nonzero()[0], va.to_numpy().nonzero()[0], te.to_numpy().nonzero()[0])
        cur = cur + pd.DateOffset(months=step_m)
