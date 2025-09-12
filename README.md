# BTC 5m LSTM Starter Kit

ชุดสตาร์ทเตอร์สำหรับสร้างโมเดล **LSTM เทรด Bitcoin TF 5 นาที** ด้วยข้อมูลย้อนหลังหลายปี
- เตรียมข้อมูล → เติมกริดเวลาให้สม่ำเสมอ (5m) → ฟีเจอร์เทคนิคอล → ติดฉลาก (triple-barrier แบบกระชับ)  
- แบ่ง **sliding walk-forward** (Train 12m → Valid 3m → Test 3m; เลื่อน 3m)
- เทรน LSTM + Early stopping ด้วย Valid accuracy
- Backtest บนช่วง Test พร้อม ATR SL/TP, ค่าธรรมเนียม, สลิปเพจ

## โครงสร้าง
```
btc5m-lstm-starter/
├─ data/
│  ├─ raw/                 # วางไฟล์ 5m ที่นี่ (CSV/Parquet)
│  ├─ prepared/            # ไฟล์ parquet หลังเติมกริดและจัดรูป
│  └─ sample/              # ตัวอย่างไฟล์เล็ก ๆ
├─ outputs/
│  ├─ models/              # น้ำหนักโมเดลและ scaler ต่อ window
│  ├─ metrics/             # metrics_windows.json, summary.json
│  └─ trades/              # trades_w{k}.parquet ต่อ window
├─ configs/config.yaml
├─ src/                    # โมดูลหลัก
└─ scripts/                # entrypoints
```

## วิธีเริ่มต้น
1) ติดตั้งไลบรารี
```bash
pip install -r requirements.txt
```
2) วางไฟล์ราคา 5 นาที (คอลัมน์: `timestamp,open,high,low,close,volume`) ที่ `data/raw/`  
   - ถ้า timestamp ไม่ได้ใส่ timezone จะใช้ `tz_source` ใน config เพื่อจัดการให้
3) เตรียมข้อมูล (ทำความสะอาด + เติมกริด 5m)
```bash
python -m scripts.preprocess
```
4) เทรน + Backtest แบบ walk-forward
```bash
python -m scripts.run_train
```
ผลลัพธ์:
- `outputs/metrics/metrics_windows.json` และ `summary.json`
- `outputs/trades/trades_w{k}.parquet` ต่อหน้าต่าง
- โมเดลและสเกลเลอร์ใน `outputs/models/`

> ปรับค่าใน `configs/config.yaml` ตามสภาพตลาด/โบรกเกอร์ และเครื่องของคุณ

## หมายเหตุ
- ชุดนี้ออกแบบ **ไม่มีข้อมูลรั่ว (leakage)**: EMA/RSI/ATR และสเกลเลอร์ fit เฉพาะ train window
- โปรดตั้ง `fee_bps` และ `slippage_bps` ให้สอดคล้องตลาดจริง
- หากข้อมูลมีช่องว่างเวลา ชุดนี้จะเติมกริด 5 นาทีและ forward-fill ราคา (volume=0)
