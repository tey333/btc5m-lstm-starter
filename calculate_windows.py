#!/usr/bin/env python3
"""
คำนวณจำนวน Windows ที่จะเทรนจาก Configuration
ใช้สำหรับการคำนวณ Walk-Forward Analysis windows
"""

import yaml
import pandas as pd
from pathlib import Path
import sys
import os

# เพิ่ม src ใน Python path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from utils.splits import time_splits
    USE_REAL_SPLITS = True
except ImportError:
    print("⚠️ ไม่สามารถ import time_splits ได้ จะใช้การคำนวณแบบประมาณ")
    USE_REAL_SPLITS = False

def calculate_windows_accurate(config_path="configs/config.yaml", data_path=None):
    """คำนวณจำนวน windows แบบแม่นยำจาก config"""
    
    # โหลด config
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    
    print("🔧 Configuration:")
    print(f"  📅 Train months: {cfg['split']['train_months']}")
    print(f"  ✅ Valid months: {cfg['split']['valid_months']}")
    print(f"  🧪 Test months: {cfg['split']['test_months']}")
    print(f"  ➡️ Step months: {cfg['split']['step_months']}")
    print()
    
    # ตรวจสอบไฟล์ข้อมูล
    if data_path is None:
        # หาไฟล์ข้อมูลที่เตรียมแล้ว
        prepared_dir = Path("data/prepared")
        if prepared_dir.exists():
            data_files = list(prepared_dir.glob("*.parquet"))
            if data_files:
                data_path = data_files[0]
            else:
                # หาไฟล์ข้อมูลดิบ
                raw_dir = Path("data/raw")
                if raw_dir.exists():
                    raw_files = list(raw_dir.glob("*.csv")) + list(raw_dir.glob("*.parquet"))
                    if raw_files:
                        print(f"⚠️ ไม่พบข้อมูลที่เตรียมแล้ว กรุณารัน: python -m scripts.preprocess")
                        print(f"📁 พบข้อมูลดิบ: {raw_files[0]}")
                        return None
    
    if data_path is None or not Path(data_path).exists():
        print("❌ ไม่พบไฟล์ข้อมูล!")
        print("กรุณาตรวจสอบ:")
        print("  1. วางไฟล์ข้อมูลใน data/raw/")
        print("  2. รัน python -m scripts.preprocess")
        return None
    
    print(f"📊 กำลังโหลดข้อมูลจาก: {data_path}")
    
    # โหลดข้อมูล
    if str(data_path).endswith('.csv'):
        df = pd.read_csv(data_path)
    else:
        df = pd.read_parquet(data_path)
    
    print(f"📈 ข้อมูลทั้งหมด: {len(df):,} รายการ")
    
    # แปลง timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    start_date = df['timestamp'].min()
    end_date = df['timestamp'].max()
    
    print(f"📅 ระยะเวลาข้อมูล: {start_date.strftime('%Y-%m-%d')} ถึง {end_date.strftime('%Y-%m-%d')}")
    total_days = (end_date - start_date).days
    total_months = total_days / 30.44  # เฉลี่ย
    print(f"⏱️ รวม: {total_days} วัน ({total_months:.1f} เดือน)")
    print()
    
    if USE_REAL_SPLITS:
        # คำนวณ windows แบบแม่นยำ
        print("🔄 กำลังคำนวณ Walk-Forward Windows แบบแม่นยำ...")
        
        windows = list(time_splits(
            df, 
            cfg['split']['train_months'], 
            cfg['split']['valid_months'], 
            cfg['split']['test_months'], 
            cfg['split']['step_months']
        ))
        
        # กรอง windows ที่มีข้อมูลเพียงพอ
        seq_len = cfg.get('train', {}).get('seq_len', 96)
        valid_windows = []
        
        for i, (tr, va, te) in enumerate(windows):
            if len(tr) >= seq_len and len(va) >= seq_len and len(te) >= seq_len:
                valid_windows.append((i, tr, va, te))
                
                # แสดงรายละเอียด window แรกไม่กี่อัน
                if i < 3:
                    tr_start = df.iloc[tr[0]]['timestamp'].strftime('%Y-%m-%d')
                    tr_end = df.iloc[tr[-1]]['timestamp'].strftime('%Y-%m-%d')
                    te_start = df.iloc[te[0]]['timestamp'].strftime('%Y-%m-%d')
                    te_end = df.iloc[te[-1]]['timestamp'].strftime('%Y-%m-%d')
                    
                    print(f"  [Window {i}] Train: {len(tr):,} samples ({tr_start} → {tr_end})")
                    print(f"               Valid: {len(va):,} samples")
                    print(f"               Test:  {len(te):,} samples ({te_start} → {te_end})")
                    print()
        
        # แสดงสรุป
        print("=" * 60)
        print(f"🎯 สรุปผลการคำนวณ (แม่นยำ):")
        print(f"  📊 จำนวน Windows ทั้งหมด: {len(windows)}")
        print(f"  ✅ Windows ที่ใช้งานได้: {len(valid_windows)}")
        print(f"  ❌ Windows ที่ข้อมูลไม่พอ: {len(windows) - len(valid_windows)}")
        print()
        
        if valid_windows:
            print(f"🚀 การเทรนจะแสดง: [Window 0] ถึง [Window {len(valid_windows)-1}]")
            print(f"⏱️ คาดว่าใช้เวลา: {len(valid_windows) * 10:.0f}-{len(valid_windows) * 25:.0f} นาที")
            print(f"   (ประมาณ 10-25 นาทีต่อ Window ขึ้นอยู่กับ GPU)")
        else:
            print("❌ ไม่มี Window ที่ใช้งานได้!")
            print("💡 ลองปรับลด train_months, valid_months, test_months")
        
        return len(valid_windows)
    
    else:
        # คำนวณ windows โดยประมาณ
        return calculate_windows_approximate(cfg, total_months)

def calculate_windows_approximate(cfg, total_months):
    """คำนวณจำนวน windows โดยประมาณ"""
    
    print("🔄 กำลังคำนวณ Walk-Forward Windows (ประมาณ)...")
    
    window_size = cfg['split']['train_months'] + cfg['split']['valid_months'] + cfg['split']['test_months']
    step_size = cfg['split']['step_months']
    
    # จำนวน windows = (total_months - window_size) / step_size + 1
    num_windows = max(0, int((total_months - window_size) / step_size) + 1)
    
    # แสดงสรุป
    print("=" * 60)
    print(f"🎯 สรุปผลการคำนวณ (ประมาณ):")
    print(f"  📊 Window size: {window_size} เดือน")
    print(f"  ➡️ Step size: {step_size} เดือน")
    print(f"  ✅ จำนวน Windows: {num_windows}")
    print()
    
    if num_windows > 0:
        print(f"🚀 การเทรนจะแสดง: [Window 0] ถึง [Window {num_windows-1}]")
        print(f"⏱️ คาดว่าใช้เวลา: {num_windows * 10:.0f}-{num_windows * 25:.0f} นาที")
        print(f"   (ประมาณ 10-25 นาทีต่อ Window ขึ้นอยู่กับ GPU)")
    else:
        print("❌ ไม่มี Window ที่ใช้งานได้!")
        print("💡 ลองปรับลด train_months, valid_months, test_months")
    
    print("=" * 60)
    
    return num_windows

def show_strategy_comparison():
    """แสดงการเปรียบเทียบ strategies ต่างๆ"""
    
    print("\n🎯 การเปรียบเทียบ Strategies:")
    print("=" * 60)
    
    strategies = [
        {
            "name": "Conservative",
            "rr": "1:1.2",
            "target_wr": "60%+",
            "risk": "ต่ำ",
            "return": "ปานกลาง",
            "suitable": "มือใหม่"
        },
        {
            "name": "Balanced", 
            "rr": "1:1.5",
            "target_wr": "50%+",
            "risk": "ปานกลาง",
            "return": "ดี",
            "suitable": "ทั่วไป"
        },
        {
            "name": "Aggressive",
            "rr": "1:2.0",
            "target_wr": "40%+", 
            "risk": "สูง",
            "return": "สูง",
            "suitable": "มีประสบการณ์"
        },
        {
            "name": "Scalping",
            "rr": "1:1.0",
            "target_wr": "70%+",
            "risk": "ต่ำมาก",
            "return": "เสถียร",
            "suitable": "High Frequency"
        }
    ]
    
    for strategy in strategies:
        print(f"📈 {strategy['name']}:")
        print(f"   RR: {strategy['rr']}, Target WR: {strategy['target_wr']}")
        print(f"   Risk: {strategy['risk']}, Return: {strategy['return']}")
        print(f"   เหมาะสำหรับ: {strategy['suitable']}")
        print()

def main():
    """ฟังก์ชันหลักสำหรับ command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='คำนวณจำนวน Windows สำหรับ Walk-Forward Analysis')
    parser.add_argument('--config', '-c', default='configs/config.yaml', 
                       help='Path to config file (default: configs/config.yaml)')
    parser.add_argument('--data', '-d', default=None,
                       help='Path to data file (default: auto-detect)')
    parser.add_argument('--strategies', '-s', action='store_true',
                       help='แสดงการเปรียบเทียบ strategies')
    
    args = parser.parse_args()
    
    if args.strategies:
        show_strategy_comparison()
        return
    
    num_windows = calculate_windows_accurate(args.config, args.data)
    
    if num_windows is not None and num_windows > 0:
        print(f"\n🎉 พร้อมเทรน {num_windows} Windows!")
    else:
        print("\n❌ ไม่สามารถคำนวณ Windows ได้")
        sys.exit(1)

if __name__ == "__main__":
    main()