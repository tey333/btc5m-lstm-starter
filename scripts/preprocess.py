import yaml
from pathlib import Path
from src.data.load import load_all

def main():
    cfg = yaml.safe_load(open("configs/config.yaml", encoding="utf-8"))
    df = load_all(
        cfg["data"]["raw_glob"],
        cfg["data"]["tz_source"],
        cfg["data"]["tz_target"],
        ensure_regular=cfg["data"]["ensure_regular_5m"]
    )
    Path("data/prepared").mkdir(parents=True, exist_ok=True)
    out = "data/prepared/btc_5m_clean.parquet"
    df.to_parquet(out)
    print("Saved:", out, "| shape:", df.shape, "| range:", df["timestamp"].min(), "→", df["timestamp"].max())

if __name__ == "__main__":
    main()
