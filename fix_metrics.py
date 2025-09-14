#!/usr/bin/env python3
"""
สร้างไฟล์ metrics CSV ที่สมบูรณ์จากข้อมูลการเทรด
แก้ปัญหา KeyError ใน Colab notebook
"""

import pandas as pd
import numpy as np
import glob
from pathlib import Path
import json

def create_complete_metrics():
    """สร้างไฟล์ metrics ที่สมบูรณ์จากข้อมูลการเทรด"""
    
    trades_dir = Path('outputs/trades')
    if not trades_dir.exists():
        print("❌ ไม่พบโฟลเดอร์ trades!")
        return None
    
    trade_files = list(trades_dir.glob("trades_w*.parquet"))
    if not trade_files:
        print("❌ ไม่พบไฟล์ trades!")
        return None
    
    print("📊 กำลังสร้างไฟล์ metrics ที่สมบูรณ์...")
    
    metrics_list = []
    
    for file in trade_files:
        try:
            # แยกหมายเลข window
            window_num = int(file.stem.split('_w')[1])
            
            # โหลดข้อมูลการเทรด
            df = pd.read_parquet(file)
            
            if len(df) == 0:
                print(f"⚠️ Window {window_num}: ไม่มีข้อมูลการเทรด")
                continue
            
            # คำนวณ metrics พื้นฐาน
            total_trades = len(df)
            winning_trades = (df['ret'] > 0).sum()
            losing_trades = (df['ret'] < 0).sum()
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
            total_return = df['ret'].sum()
            avg_return_per_trade = df['ret'].mean()
            
            # คำนวณ Profit Factor
            gross_profit = df[df['ret'] > 0]['ret'].sum() if winning_trades > 0 else 0.0
            gross_loss = abs(df[df['ret'] < 0]['ret'].sum()) if losing_trades > 0 else 0.0001
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 10.0
            
            # คำนวณ Drawdown
            equity_curve = (1 + df['ret']).cumprod()
            running_max = equity_curve.expanding().max()
            drawdown = (equity_curve - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # คำนวณ Sharpe Ratio
            returns_std = df['ret'].std()
            sharpe_ratio = avg_return_per_trade / returns_std if returns_std > 0 else 0.0
            
            # คำนวณ Average Win/Loss
            avg_win = df[df['ret'] > 0]['ret'].mean() if winning_trades > 0 else 0.0
            avg_loss = df[df['ret'] < 0]['ret'].mean() if losing_trades > 0 else 0.0
            
            # สร้าง metrics dictionary
            metrics = {
                'window': window_num,
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_return_equity': total_return,
                'avg_return_per_trade': avg_return_per_trade,
                'profit_factor': profit_factor,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'gross_profit': gross_profit,
                'gross_loss': gross_loss,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'best_trade': df['ret'].max(),
                'worst_trade': df['ret'].min()
            }
            
            metrics_list.append(metrics)
            print(f"✅ Window {window_num}: {total_trades} trades, Return={total_return:.2%}")
            
        except Exception as e:
            print(f"⚠️ ข้ามไฟล์ {file}: {e}")
    
    if not metrics_list:
        print("❌ ไม่สามารถสร้าง metrics ได้!")
        return None
    
    # สร้าง DataFrame
    metrics_df = pd.DataFrame(metrics_list)
    metrics_df = metrics_df.sort_values('window')
    
    # บันทึกเป็น CSV
    metrics_dir = Path('outputs/metrics')
    metrics_dir.mkdir(exist_ok=True)
    
    csv_filename = f'trading_metrics_complete_{len(metrics_df)}_windows.csv'
    csv_path = metrics_dir / csv_filename
    
    metrics_df.to_csv(csv_path, index=False)
    
    print(f"\n✅ สร้างไฟล์ {csv_filename} เรียบร้อย!")
    print(f"📊 จำนวน Windows: {len(metrics_df)}")
    print(f"📊 Columns: {list(metrics_df.columns)}")
    
    # หา best/worst windows (ใช้วิธีที่ง่ายและปลอดภัย)
    total_returns = metrics_df['total_return_equity'].tolist()
    windows = metrics_df['window'].tolist()
    
    max_return_idx = total_returns.index(max(total_returns))
    min_return_idx = total_returns.index(min(total_returns))
    
    best_window_val = windows[max_return_idx]
    worst_window_val = windows[min_return_idx]
    
    # สร้างรายงานสรุป JSON
    summary = {
        "summary": {
            "total_windows": len(metrics_df),
            "avg_win_rate": float(metrics_df['win_rate'].mean()),
            "avg_profit_factor": float(metrics_df['profit_factor'].mean()),
            "avg_return": float(metrics_df['total_return_equity'].mean()),
            "total_return": float(metrics_df['total_return_equity'].sum()),
            "max_drawdown": float(metrics_df['max_drawdown'].min()),
            "total_trades": int(metrics_df['total_trades'].sum()),
            "profitable_windows": int((metrics_df['total_return_equity'] > 0).sum()),
            "best_window": best_window_val,
            "worst_window": worst_window_val
        },
        "detailed_metrics": metrics_df.to_dict('records')
    }
    
    json_path = metrics_dir / 'complete_metrics_summary.json'
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ สร้างไฟล์ JSON summary เรียบร้อย!")
    
    return metrics_df

def display_summary(df):
    """แสดงสรุปผลลัพธ์"""
    
    print("\n📊 สรุปผลลัพธ์การเทรด")
    print("=" * 80)
    
    # สถิติรวม
    total_return = df['total_return_equity'].sum()
    avg_win_rate = df['win_rate'].mean()
    avg_profit_factor = df['profit_factor'].mean()
    total_trades = df['total_trades'].sum()
    profitable_windows = (df['total_return_equity'] > 0).sum()
    
    print(f"🎯 สถิติรวม:")
    print(f"   📈 Total Return: {total_return:.2%}")
    print(f"   📈 Average Win Rate: {avg_win_rate:.1%}")
    print(f"   📈 Average Profit Factor: {avg_profit_factor:.2f}")
    print(f"   📊 Total Trades: {total_trades:,}")
    print(f"   ✅ Profitable Windows: {profitable_windows}/{len(df)} ({profitable_windows/len(df):.1%})")
    print(f"   📉 Max Drawdown: {df['max_drawdown'].min():.2%}")
    
    # ประเมินผล
    print(f"\n🎯 การประเมินผล:")
    
    if total_return > 0:
        print("✅ Strategy ทำกำไรโดยรวม!")
    else:
        print("❌ Strategy ขาดทุนโดยรวม")
    
    if avg_profit_factor > 1.0:
        print("✅ Profit Factor > 1.0 - มีศักยภาพ")
    else:
        print("❌ Profit Factor < 1.0 - ต้องปรับปรุง")
    
    if avg_win_rate > 0.5:
        print("✅ Win Rate > 50% - ดี")
    else:
        print("⚠️ Win Rate < 50% - ต้องปรับปรุง")

if __name__ == "__main__":
    # สร้างไฟล์ metrics
    df = create_complete_metrics()
    
    if df is not None:
        # แสดงสรุป
        display_summary(df)
        
        print(f"\n📁 ไฟล์ที่สร้าง:")
        print(f"   📊 outputs/metrics/trading_metrics_complete_{len(df)}_windows.csv")
        print(f"   📄 outputs/metrics/complete_metrics_summary.json")
        print(f"\n🚀 ไฟล์พร้อมใช้ใน Colab notebook แล้ว!")
    else:
        print("❌ ไม่สามารถสร้างไฟล์ metrics ได้")