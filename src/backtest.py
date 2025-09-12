import numpy as np
import pandas as pd

def run_backtest(prices: pd.DataFrame, proba: np.ndarray, thr: float, fee_bps: float, slippage_bps: float, atr_tp: float, atr_sl: float, max_holding: int):
    fee = fee_bps/1e4
    slp = slippage_bps/1e4

    close = prices["close"].to_numpy()
    atr = prices["atr"].to_numpy()
    ts = prices["timestamp"].to_numpy()

    longs = proba[:,2]
    shorts = proba[:,0]

    i = 0
    N = len(close)
    trades = []
    while i < N-1:
        long_sig = (longs[i]>=thr) and (longs[i]>shorts[i])
        short_sig= (shorts[i]>=thr) and (shorts[i]>longs[i])
        if not (long_sig or short_sig):
            i += 1
            continue
        side = 1 if long_sig else -1
        px_in = close[i]*(1+slp if side==1 else 1-slp)
        tp = px_in*(1 + (atr_tp*atr[i]/px_in)) if side==1 else px_in*(1 - (atr_tp*atr[i]/px_in))
        sl = px_in*(1 - (atr_sl*atr[i]/px_in)) if side==1 else px_in*(1 + (atr_sl*atr[i]/px_in))

        hit = None
        for j in range(i+1, min(i+1+max_holding, N)):
            px = close[j]
            if side==1 and (px>=tp or px<=sl): hit=j; break
            if side==-1 and (px<=tp or px>=sl): hit=j; break
        if hit is None: hit = min(i+max_holding, N-1)

        px_out = close[hit]*(1 - slp if side==1 else 1 + slp)
        ret = (px_out/px_in - 1)*side - 2*fee
        trades.append({"t_in":ts[i], "t_out":ts[hit], "side":side, "ret":ret})
        i = hit + 1

    if not trades:
        return {"trades": 0}, pd.DataFrame()
    df_t = pd.DataFrame(trades)
    wins = (df_t["ret"]>0).sum()
    losses = (df_t["ret"]<0).sum()
    wr = wins/len(df_t)
    pf = (df_t.loc[df_t["ret"]>0,"ret"].sum())/(-df_t.loc[df_t["ret"]<0,"ret"].sum()) if losses>0 else float("inf")
    avg_win = df_t.loc[df_t["ret"]>0,"ret"].mean() if wins>0 else 0.0
    avg_loss= -df_t.loc[df_t["ret"]<0,"ret"].mean() if losses>0 else 0.0
    rr = (avg_win/avg_loss) if avg_loss>0 else 0.0
    eq = (1+df_t["ret"]).cumprod()
    dd = float((eq/eq.cummax()-1).min())
    metrics = {
        "trades": int(len(df_t)),
        "win_rate": float(wr),
        "profit_factor": float(pf),
        "rr": float(rr),
        "total_return_equity": float(eq.iloc[-1]-1),
        "max_drawdown": dd
    }
    return metrics, df_t
