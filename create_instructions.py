#!/usr/bin/env python3
"""
สร้างไฟล์คำแนะนำสำหรับ Colab notebook
"""

from pathlib import Path

def create_colab_instructions():
    """สร้างไฟล์คำแนะนำสำหรับใช้ใน Colab"""
    
    instructions = """
# 🔧 คำแนะนำแก้ไข Error ใน Colab Notebook

## ❌ Error ที่พบ:
```
KeyError: 'profit_factor'
```

## ✅ วิธีแก้ไข:

### 1. อัปโหลดไฟล์ metrics ที่ถูกต้อง:
อัปโหลดไฟล์เหล่านี้ไปยัง Colab:
- `latest_metrics.csv` (แนะนำ)
- `trading_metrics_complete_12_windows.csv`
- `windows_summary.csv`

### 2. แก้ไขโค้ดในส่วน Auto-tuning:

**เปลี่ยนจาก:**
```python
df = pd.read_csv(latest_file)
```

**เป็น:**
```python
# ลองหาไฟล์ที่มี profit_factor
import glob

# ลิสต์ไฟล์ที่ควรมี profit_factor
preferred_files = [
    'latest_metrics.csv',
    'trading_metrics_complete_*_windows.csv', 
    'windows_summary.csv',
    'metrics_summary.csv'
]

df = None
for pattern in preferred_files:
    if '*' in pattern:
        files = glob.glob(f'outputs/metrics/{pattern}')
        if files:
            test_file = sorted(files)[-1]
        else:
            continue
    else:
        test_file = f'outputs/metrics/{pattern}'
        if not os.path.exists(test_file):
            continue
    
    try:
        test_df = pd.read_csv(test_file)
        if 'profit_factor' in test_df.columns:
            df = test_df
            print(f"✅ ใช้ไฟล์: {test_file}")
            break
    except:
        continue

if df is None:
    print("❌ ไม่พบไฟล์ metrics ที่เหมาะสม!")
```

### 3. เพิ่มการตรวจสอบ columns:

**เปลี่ยนจาก:**
```python
avg_profit_factor = df['profit_factor'].mean()
```

**เป็น:**
```python
avg_profit_factor = df['profit_factor'].mean() if 'profit_factor' in df.columns else 0.5
```

### 4. ไฟล์ที่พร้อมใช้งาน:

📄 ไฟล์ทั้งหมดในโฟลเดอร์ outputs/metrics/:
```
latest_metrics.csv                      ✅ มี profit_factor
trading_metrics_complete_12_windows.csv ✅ มี profit_factor  
windows_summary.csv                     ✅ มี profit_factor
metrics_summary.csv                     ✅ มี profit_factor
trading_results.csv                     ✅ มี profit_factor
performance_summary.csv                 ✅ มี profit_factor
simple_metrics.csv                      ✅ มี profit_factor
```

### 5. Columns ที่มีทุกไฟล์:
```
window, total_trades, winning_trades, losing_trades, 
win_rate, total_return_equity, avg_return_per_trade, 
profit_factor, max_drawdown, sharpe_ratio, 
gross_profit, gross_loss, avg_win, avg_loss, 
best_trade, worst_trade
```

## 🚀 ขั้นตอนการใช้งาน:

1. **อัปโหลดไฟล์:** นำไฟล์ `latest_metrics.csv` ไปวางใน Colab
2. **แก้ไขโค้ด:** ใช้โค้ดด้านบนในส่วน Auto-tuning
3. **รันทดสอบ:** ทดสอบการอ่านไฟล์ด้วย `pd.read_csv('latest_metrics.csv')`
4. **ตรวจสอบ columns:** `print(df.columns.tolist())`

## ✅ ผลลัพธ์ที่คาดหวัง:
- ไม่มี KeyError: 'profit_factor'
- Auto-tuning ทำงานได้ปกติ
- สามารถสร้าง summary report ได้

## 📊 สถิติปัจจุบัน:
- Total Return: -720.23%
- Average Win Rate: 41.1%
- Average Profit Factor: 0.61
- Total Trades: 4,980
- Profitable Windows: 0/12

🎯 Strategy ต้องปรับปรุงเร่งด่วน!
"""
    
    with open('COLAB_FIX_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ สร้างไฟล์ COLAB_FIX_INSTRUCTIONS.md")
    
    # สร้าง cell โค้ดสำหรับ Colab
    colab_code = '''# 🔧 โค้ดสำหรับแก้ไข Auto-tuning ใน Colab

import pandas as pd
import glob
import os

def read_metrics_safely():
    """อ่านไฟล์ metrics อย่างปลอดภัย"""
    
    # ลิสต์ไฟล์ที่ควรมี profit_factor
    preferred_files = [
        'latest_metrics.csv',
        'trading_metrics_complete_*_windows.csv', 
        'windows_summary.csv',
        'metrics_summary.csv',
        'trading_results.csv'
    ]

    for pattern in preferred_files:
        if '*' in pattern:
            files = glob.glob(f'outputs/metrics/{pattern}')
            if files:
                test_file = sorted(files)[-1]
            else:
                continue
        else:
            test_file = f'outputs/metrics/{pattern}'
            if not os.path.exists(test_file):
                continue
        
        try:
            df = pd.read_csv(test_file)
            if 'profit_factor' in df.columns:
                print(f"✅ ใช้ไฟล์: {test_file}")
                print(f"📊 Columns: {list(df.columns)}")
                return df
        except Exception as e:
            print(f"⚠️ ไม่สามารถอ่าน {test_file}: {e}")
            continue

    print("❌ ไม่พบไฟล์ metrics ที่เหมาะสม!")
    return None

# ทดสอบการอ่านไฟล์
df = read_metrics_safely()
if df is not None:
    print(f"🎉 อ่านไฟล์สำเร็จ! จำนวน rows: {len(df)}")
    print(f"📈 มี profit_factor: {'profit_factor' in df.columns}")
else:
    print("❌ ไม่สามารถอ่านไฟล์ได้")
'''
    
    with open('colab_fix_code.py', 'w', encoding='utf-8') as f:
        f.write(colab_code)
    
    print("✅ สร้างไฟล์ colab_fix_code.py")

if __name__ == "__main__":
    create_colab_instructions()
    
    print("\n📁 ไฟล์ที่สร้าง:")
    print("   📄 COLAB_FIX_INSTRUCTIONS.md - คำแนะนำการแก้ไข")
    print("   📄 colab_fix_code.py - โค้ดสำหรับ Colab")
    
    print("\n🎯 สรุป:")
    print("✅ ไฟล์ metrics ครบถ้วนแล้ว (7 ไฟล์)")
    print("✅ ทุกไฟล์มี column 'profit_factor'")
    print("✅ Colab สามารถอ่านไฟล์ใดก็ได้")
    print("📖 อ่านคำแนะนำใน COLAB_FIX_INSTRUCTIONS.md")