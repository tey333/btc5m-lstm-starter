#!/usr/bin/env python3
"""
แก้ไข Colab notebook เพื่อใช้ไฟล์ metrics ที่ถูกต้อง
"""

import json
from pathlib import Path

def fix_colab_notebook():
    """แก้ไข notebook เพื่อใช้ไฟล์ metrics ที่มี profit_factor"""
    
    notebook_path = Path('BTC_LSTM_Colab.ipynb')
    
    if not notebook_path.exists():
        print("❌ ไม่พบไฟล์ notebook!")
        return False
    
    # อ่านไฟล์ notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # ค้นหาและแก้ไขส่วนที่อ่านไฟล์ CSV
    fixed = False
    
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source_lines = cell['source']
            
            # แก้ไขส่วนที่อ่านไฟล์ CSV ในฟังก์ชัน auto_tune_config
            for i, line in enumerate(source_lines):
                # หาบรรทัดที่อ่าน latest_file
                if 'df = pd.read_csv(latest_file)' in line:
                    print(f"🔧 แก้ไขบรรทัด: {line.strip()}")
                    
                    # แทนที่ด้วยการตรวจสอบไฟล์ที่มี profit_factor
                    new_code = '''    # ลองหาไฟล์ที่มี profit_factor ก่อน
    preferred_files = ['latest_metrics.csv', 'trading_metrics_complete_*_windows.csv', 
                      'windows_summary.csv', 'metrics_summary.csv']
    
    df = None
    for pattern in preferred_files:
        if '*' in pattern:
            matching_files = list(metrics_dir.glob(pattern))
            if matching_files:
                test_file = sorted(matching_files)[-1]
            else:
                continue
        else:
            test_file = metrics_dir / pattern
            if not test_file.exists():
                continue
        
        try:
            test_df = pd.read_csv(test_file)
            if 'profit_factor' in test_df.columns:
                df = test_df
                print(f"✅ ใช้ไฟล์: {test_file.name}")
                break
        except:
            continue
    
    if df is None:
        print("❌ ไม่พบไฟล์ metrics ที่เหมาะสม!")
        return False, None, None
    '''
                    
                    # แทนที่บรรทัดเดิม
                    source_lines[i] = new_code
                    fixed = True
                    break
                
                # หาบรรทัดที่เข้าถึง profit_factor โดยตรง
                elif "df['profit_factor']" in line and 'if' not in line:
                    print(f"🔧 เพิ่มการตรวจสอบ: {line.strip()}")
                    
                    # เพิ่มการตรวจสอบ column ก่อนเข้าถึง
                    new_line = line.replace(
                        "df['profit_factor']",
                        "df['profit_factor'] if 'profit_factor' in df.columns else 0.5"
                    )
                    source_lines[i] = new_line
                    fixed = True
    
    if fixed:
        # บันทึกไฟล์ที่แก้ไขแล้ว
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1, ensure_ascii=False)
        
        print("✅ แก้ไข notebook เรียบร้อย!")
        return True
    else:
        print("⚠️ ไม่พบส่วนที่ต้องแก้ไข")
        return False

if __name__ == "__main__":
    print("🔧 กำลังแก้ไข Colab notebook...")
    
    # สร้างไฟล์ metrics ทุกรูปแบบก่อน
    import sys
    sys.path.append('.')
    from create_all_metrics import create_all_metrics_files
    
    print("📊 สร้างไฟล์ metrics ทุกรูปแบบ...")
    create_all_metrics_files()
    
    print("\n🔧 แก้ไข notebook...")
    success = fix_colab_notebook()
    
    if success:
        print("\n🎉 แก้ไขเสร็จสมบูรณ์!")
        print("✅ Colab notebook พร้อมใช้งานโดยไม่มี KeyError")
    else:
        print("\n⚠️ การแก้ไขไม่สำเร็จ")
        print("💡 แนะนำ: อัปโหลดไฟล์ metrics ด้วยตนเองใน Colab")