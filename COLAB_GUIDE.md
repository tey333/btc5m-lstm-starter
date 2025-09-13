# คำแนะนำการใช้งานใน Google Colab

## 🚀 วิธีการเทรนใน Google Colab

### 1. เตรียมความพร้อม
1. เปิด Google Colab: https://colab.research.google.com/
2. Upload ไฟล์ `BTC_LSTM_Colab.ipynb` 
3. หรือใช้ลิงก์: `https://colab.research.google.com/github/tey333/btc5m-lstm-starter/blob/main/BTC_LSTM_Colab.ipynb`

### 2. ขั้นตอนการเทรน
1. **Setup Environment**: รันเซลล์ตั้งแต่ต้นเพื่อ clone repo และติดตั้ง dependencies
2. **Upload Data**: อัพโหลดไฟล์ข้อมูล BTC 5m ของคุณ
3. **Preprocessing**: รันการประมวลผลข้อมูล
4. **Training**: เริ่มการเทรน model
5. **Download Results**: ดาวน์โหลดผลลัพธ์

### 3. การปรับแต่งสำหรับ Colab

#### สำหรับ GPU T4 (15GB):
```yaml
train:
  batch_size: 512
  max_epochs: 25
  device: "cuda"
```

#### สำหรับ GPU L4 (24GB):
```yaml
train:
  batch_size: 1024  # หรือ 1536 สำหรับประสิทธิภาพสูงสุด
  max_epochs: 25
  device: "cuda"
```

#### สำหรับการทดสอบเร็ว:
```yaml
split:
  train_months: 3
  valid_months: 1
  test_months: 1

train:
  batch_size: 256
  max_epochs: 5
```

#### หาก GPU Memory หมด:
```yaml
train:
  batch_size: 256  # หรือ 128
  device: "cuda"
```

#### สำหรับ CPU เท่านั้น:
```yaml
train:
  batch_size: 128
  max_epochs: 5
  device: "cpu"
```

### 4. ข้อมูลที่ต้องการ
- **Format**: CSV หรือ Parquet
- **Columns**: timestamp, open, high, low, close, volume
- **Timeframe**: 5 นาที
- **Size**: แนะนำ 6+ เดือนสำหรับผลลัพธ์ที่ดี

### 5. ผลลัพธ์ที่จะได้
- **Models**: ไฟล์ .pt ของโมเดลที่เทรนแล้ว
- **Trades**: ผลการ backtest แต่ละ window
- **Metrics**: สถิติประสิทธิภาพรวม
- **Config**: การตั้งค่าที่ใช้

### 6. เทคนิคประหยัด GPU
1. ใช้ **Runtime > Restart and run all** เมื่อ memory หมด
2. ลด `batch_size` หาก Out of Memory
3. ใช้ `max_epochs: 5-10` สำหรับการทดสอบ
4. ปิด tab อื่นๆ เพื่อประหยัด RAM

### 7. การตีความผลลัพธ์

#### Good Performance:
- Win Rate > 35% (เพื่อกำไรจาก RR 1:2)
- Sharpe Ratio > 1.0
- Max Drawdown < 15%
- Profit Factor > 1.2

#### Poor Performance:
- Win Rate < 30%
- Sharpe Ratio < 0.5
- Max Drawdown > 25%
- Profit Factor < 1.0

### 8. Troubleshooting

#### หาก Clone ไม่ได้:
```bash
!git clone https://github.com/tey333/btc5m-lstm-starter.git
```

#### หาก Install แพคเกจไม่ได้:
```bash
!pip install torch pandas numpy scikit-learn pyyaml tqdm
```

#### หาก GPU ไม่เจอ:
ไปที่ Runtime > Change runtime type > Hardware accelerator > GPU

#### หาก Memory หมด:
1. Runtime > Restart runtime
2. ลด batch_size ในไฟล์ config
3. ปิดการเปิดหลายๆ notebook

### 9. แนะนำสำหรับมือใหม่
1. **เริ่มด้วยการทดสอบ**: ใช้ train_months: 3, max_epochs: 5
2. **ตรวจสอบข้อมูล**: ให้แน่ใจว่าข้อมูลครบถ้วนและถูกต้อง
3. **เริ่มจากเล็ก**: ทดสอบกับข้อมูลเล็กๆ ก่อน
4. **อดทน**: การเทรนเต็มจะใช้เวลา 1-3 ชั่วโมง

### 10. เก็บงาน
- Download ไฟล์ zip ผลลัพธ์ทุกครั้ง
- เซฟ config ที่ได้ผลดี
- บันทึกค่า metrics สำคัญ

---

## 🎯 พร้อมเทรนแล้ว!

อัพโหลด `BTC_LSTM_Colab.ipynb` ไปยัง Google Colab และเริ่มเทรน! 🚀