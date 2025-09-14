# 🔧 โค้ดสำหรับแก้ไข Auto-tuning ใน Colab

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
