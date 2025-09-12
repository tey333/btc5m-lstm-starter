import numpy as np
import pandas as pd

def make_triple_barrier_labels(df: pd.DataFrame, atr_mult_tp: float, atr_mult_sl: float, max_holding: int, min_move_bps: int=0) -> pd.Series:
    """
    ให้ป้ายกำกับ 3 ชั้น: -1 (short), 0 (flat), +1 (long)
    แบบกระชับ: ใช้ผลตอบแทนล่วงหน้าในกรอบ max_holding เป็น proxy (ลดคอมพิวต์),
    โดยตั้งเกณฑ์ minimum move (bps) เพื่อกันสัญญาณจิ๋ว
    """
    close = df["close"].to_numpy()
    n = len(df)
    tgt = np.zeros(n, dtype=np.int8)
    min_move = (min_move_bps/1e4) * close

    for i in range(n - max_holding - 1):
        c0 = close[i]
        fwd = close[i+max_holding] - c0
        if abs(fwd) < min_move[i]:
            tgt[i] = 0
        else:
            tgt[i] = 1 if fwd > 0 else -1

    return pd.Series(tgt, index=df.index, name="target")
