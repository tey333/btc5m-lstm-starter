#!/usr/bin/env python3
"""
สร้างไฟล์ metrics ทุกรูปแบบที่ Colab notebook อาจต้องการ
แก้ปัญหา KeyError สำหรับ Auto-tuning
"""

import pandas as pd
import numpy as np
import glob
from pathlib import Path
import json

def create_all_metrics_files():
    """สร้างไฟล์ metrics ทุกรูปแบบ"""
    
    # รันฟังก์ชันจาก fix_metrics.py
    import sys
    sys.path.append('.')
    from fix_metrics import create_complete_metrics
    
    # สร้างไฟล์หลัก
    df = create_complete_metrics()
    if df is None:
        print("❌ ไม่สามารถสร้าง metrics ได้!")
        return
    
    metrics_dir = Path('outputs/metrics')
    metrics_dir.mkdir(exist_ok=True)
    
    print("\n📁 กำลังสร้างไฟล์ metrics ทุกรูปแบบ...")
    
    # 1. ไฟล์หลัก (มีอยู่แล้ว)
    print("✅ trading_metrics_complete_XX_windows.csv")
    
    # 2. windows_summary.csv (สำหรับ Colab auto-tuning)
    df.to_csv(metrics_dir / 'windows_summary.csv', index=False)
    print("✅ windows_summary.csv")
    
    # 3. metrics_summary.csv (ชื่อทั่วไป)
    df.to_csv(metrics_dir / 'metrics_summary.csv', index=False)
    print("✅ metrics_summary.csv")
    
    # 4. latest_metrics.csv (ไฟล์ล่าสุด)
    df.to_csv(metrics_dir / 'latest_metrics.csv', index=False)
    print("✅ latest_metrics.csv")
    
    # 5. trading_results.csv (ชื่อที่ใช้บ่อย)
    df.to_csv(metrics_dir / 'trading_results.csv', index=False)
    print("✅ trading_results.csv")
    
    # 6. สร้างไฟล์ข้อมูลสรุปเพิ่มเติม
    summary_data = {
        'metric': ['total_return', 'avg_win_rate', 'avg_profit_factor', 'total_trades', 'profitable_windows'],
        'value': [
            df['total_return_equity'].sum(),
            df['win_rate'].mean(),
            df['profit_factor'].mean(),
            df['total_trades'].sum(),
            (df['total_return_equity'] > 0).sum()
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(metrics_dir / 'performance_summary.csv', index=False)
    print("✅ performance_summary.csv")
    
    # 7. สร้างไฟล์สำหรับการอ่านง่าย (simplified)
    simple_df = df[['window', 'total_trades', 'win_rate', 'total_return_equity', 'profit_factor']].copy()
    simple_df.to_csv(metrics_dir / 'simple_metrics.csv', index=False)
    print("✅ simple_metrics.csv")
    
    # 8. อัปเดต JSON files
    json_summary = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_windows": len(df),
        "file_versions": {
            "trading_metrics_complete": f"trading_metrics_complete_{len(df)}_windows.csv",
            "windows_summary": "windows_summary.csv",
            "metrics_summary": "metrics_summary.csv",
            "latest_metrics": "latest_metrics.csv",
            "trading_results": "trading_results.csv",
            "performance_summary": "performance_summary.csv",
            "simple_metrics": "simple_metrics.csv"
        },
        "columns_available": list(df.columns),
        "summary_stats": {
            "total_return": float(df['total_return_equity'].sum()),
            "avg_win_rate": float(df['win_rate'].mean()),
            "avg_profit_factor": float(df['profit_factor'].mean()),
            "total_trades": int(df['total_trades'].sum()),
            "profitable_windows": int((df['total_return_equity'] > 0).sum())
        }
    }
    
    with open(metrics_dir / 'files_index.json', 'w') as f:
        json.dump(json_summary, f, indent=2)
    print("✅ files_index.json")
    
    print(f"\n🎉 สร้างไฟล์ metrics ครบถ้วน {len(list(metrics_dir.glob('*.csv')))} ไฟล์!")
    print("\n📊 ไฟล์ที่สร้าง:")
    for file in sorted(metrics_dir.glob('*.csv')):
        print(f"   📄 {file.name}")
    
    print(f"\n✅ Columns ที่มีทุกไฟล์: {list(df.columns)}")
    print("\n🚀 Colab notebook สามารถอ่านไฟล์ใดก็ได้โดยไม่มี KeyError!")
    
    return df

if __name__ == "__main__":
    create_all_metrics_files()