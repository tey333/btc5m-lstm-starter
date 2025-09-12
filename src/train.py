import yaml, json
from pathlib import Path
import numpy as np
import pandas as pd
from tqdm import tqdm
import torch
from torch.utils.data import DataLoader
import torch.nn as nn
import torch.optim as optim

from .features.indicators import add_features
from .labeling.triple_barrier import make_triple_barrier_labels
from .utils.dataset import RollingStandardScaler, SeqDataset
from .utils.splits import time_splits
from .models.lstm import LSTMClf
from .backtest import run_backtest

def softmax_np(logits: np.ndarray) -> np.ndarray:
    m = logits.max(axis=1, keepdims=True)
    ex = np.exp(logits - m)
    return ex / ex.sum(axis=1, keepdims=True)

def train_one_window(cfg: dict, df: pd.DataFrame, feat_cols: list, tr_idx, va_idx, te_idx):
    device = torch.device(cfg["train"]["device"] if (cfg["train"]["device"]=="cuda" and torch.cuda.is_available()) else "cpu")
    seq_len = cfg["train"]["seq_len"]

    X = df[feat_cols].to_numpy()
    y = df["target"].to_numpy()

    scaler = RollingStandardScaler().fit(X[tr_idx])
    Xtr, Xva, Xte = scaler.transform(X[tr_idx]), scaler.transform(X[va_idx]), scaler.transform(X[te_idx])
    ds_tr = SeqDataset(Xtr, y[tr_idx], seq_len)
    ds_va = SeqDataset(Xva, y[va_idx], seq_len)
    ds_te = SeqDataset(Xte, y[te_idx], seq_len)

    dl_tr = DataLoader(ds_tr, batch_size=cfg["train"]["batch_size"], shuffle=True, num_workers=0)
    dl_va = DataLoader(ds_va, batch_size=4096, shuffle=False, num_workers=0)
    dl_te = DataLoader(ds_te, batch_size=4096, shuffle=False, num_workers=0)

    model = LSTMClf(in_ch=len(feat_cols), hidden=64, layers=2, num_classes=3).to(device)
    class_w = torch.tensor(cfg["train"]["class_weights"], dtype=torch.float32, device=device)
    crit = nn.CrossEntropyLoss(weight=class_w)
    opt = optim.Adam(model.parameters(), lr=cfg["train"]["lr"])

    best_acc=-1; best_state=None; bad=0
    for ep in range(cfg["train"]["max_epochs"]):
        model.train()
        for xb,yb in dl_tr:
            xb,yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            logits = model(xb)
            loss = crit(logits, yb)
            loss.backward()
            opt.step()
        # valid accuracy
        model.eval(); corr=0; tot=0
        with torch.no_grad():
            for xb,yb in dl_va:
                xb,yb = xb.to(device), yb.to(device)
                pred = model(xb).argmax(1)
                corr += (pred==yb).sum().item(); tot += len(yb)
        acc = corr/tot if tot>0 else 0.0
        if acc>best_acc:
            best_acc=acc; best_state={k:v.cpu().clone() for k,v in model.state_dict().items()}; bad=0
        else:
            bad+=1
            if bad>=cfg["train"]["early_stop_patience"]:
                break

    # load best
    model.load_state_dict(best_state)
    model.eval()

    # logits on test
    all_logits=[]
    with torch.no_grad():
        for xb,_ in dl_te:
            xb = xb.to(device)
            all_logits.append(model(xb).cpu().numpy())
    logits = np.concatenate(all_logits, axis=0)
    proba = softmax_np(logits)
    return model.cpu(), scaler, proba

def run(cfg_path="configs/config.yaml"):
    cfg = yaml.safe_load(open(cfg_path))

    # Load prepared data
    df = pd.read_parquet("data/prepared/btc_5m_clean.parquet").sort_values("timestamp")

    # Features & labels
    df = add_features(df, cfg)
    df["target"] = make_triple_barrier_labels(
        df,
        cfg["label"]["atr_mult_tp"],
        cfg["label"]["atr_mult_sl"],
        cfg["label"]["max_holding"],
        cfg["label"].get("min_move_bps", 0)
    )
    df = df.dropna().reset_index(drop=True)

    drop_cols = {"timestamp","open","high","low","close","volume","target"}
    feat_cols = [c for c in df.columns if c not in drop_cols]

    out_models = Path("outputs/models"); out_models.mkdir(parents=True, exist_ok=True)
    out_metrics= Path("outputs/metrics"); out_metrics.mkdir(parents=True, exist_ok=True)
    out_trades = Path("outputs/trades"); out_trades.mkdir(parents=True, exist_ok=True)

    all_metrics = []
    k=0
    for tr,va,te in time_splits(df, cfg["split"]["train_months"], cfg["split"]["valid_months"], cfg["split"]["test_months"], cfg["split"]["step_months"]):
        if len(tr)<cfg["train"]["seq_len"] or len(va)<cfg["train"]["seq_len"] or len(te)<cfg["train"]["seq_len"]:
            continue

        print(f"[Window {k}] train={len(tr)} valid={len(va)} test={len(te)}")
        model, scaler, proba = train_one_window(cfg, df, feat_cols, tr, va, te)

        # align test indices with proba (account for seq_len-1 offset)
        te_idx_adj = te[cfg["train"]["seq_len"]-1:]
        prices_te = df.loc[te_idx_adj, ["timestamp","close","atr"]].reset_index(drop=True)

        metrics, trades = run_backtest(
            prices_te, proba,
            thr=cfg["trade"]["proba_threshold"],
            fee_bps=cfg["trade"]["fee_bps"],
            slippage_bps=cfg["trade"]["slippage_bps"],
            atr_tp=cfg["trade"]["atr_mult_tp"],
            atr_sl=cfg["trade"]["atr_mult_sl"],
            max_holding=cfg["trade"]["max_holding"],
        )
        metrics["window"] = k
        all_metrics.append(metrics)

        # save artifacts
        torch.save(model.state_dict(), out_models / f"lstm_w{k}.pt")
        np.save(out_models / f"scaler_mean_w{k}.npy", scaler.mean_)
        np.save(out_models / f"scaler_std_w{k}.npy", scaler.std_)
        trades.to_parquet(out_trades / f"trades_w{k}.parquet", index=False)
        k += 1

    if not all_metrics:
        print("No windows produced metrics. Check config date coverage & data size.")
        return

    with open(out_metrics / "metrics_windows.json", "w") as f:
        json.dump(all_metrics, f, indent=2)

    # summary
    dfm = pd.DataFrame(all_metrics)
    summary = {
        "windows": int(len(dfm)),
        "median_win_rate": float(dfm["win_rate"].median()),
        "median_profit_factor": float(dfm["profit_factor"].median()),
        "sum_trades": int(dfm["trades"].sum()),
        "median_total_return_equity": float(dfm["total_return_equity"].median()),
        "median_max_drawdown": float(dfm["max_drawdown"].median()),
    }
    with open(out_metrics / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Summary:", summary)
