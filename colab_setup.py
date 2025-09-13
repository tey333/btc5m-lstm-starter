# Google Colab Setup for BTC 5m LSTM Trading
# ใช้สำหรับติดตั้งและเตรียม environment ใน Colab

import os
import subprocess
import sys

def install_requirements():
    """ติดตั้ง packages ที่จำเป็น"""
    print("🔧 Installing required packages...")
    
    # อ่าน requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            packages = f.read().strip().split('\n')
        
        for package in packages:
            if package and not package.startswith('#'):
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    except FileNotFoundError:
        print("requirements.txt not found, installing manually...")
        packages = [
            'torch',
            'pandas',
            'numpy',
            'scikit-learn',
            'pyyaml',
            'tqdm'
        ]
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def setup_directories():
    """สร้าง directories ที่จำเป็น"""
    print("📁 Setting up directories...")
    
    dirs = [
        'data/prepared',
        'data/raw',
        'data/sample',
        'outputs/models',
        'outputs/trades',
        'outputs/metrics'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created: {dir_path}")

def check_gpu():
    """ตรวจสอบ GPU"""
    print("🎯 Checking GPU availability...")
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"✅ GPU available: {gpu_name}")
            print(f"GPU Memory: {gpu_memory:.1f} GB")
            
            # แนะนำ batch_size ตาม GPU memory
            if gpu_memory < 8:
                recommended_batch = 256
            elif gpu_memory < 16:
                recommended_batch = 512
            elif gpu_memory < 24:
                recommended_batch = 1024
            else:
                recommended_batch = 1536  # สำหรับ GPU L4 24GB หรือดีกว่า
            
            print(f"💡 แนะนำ batch_size: {recommended_batch}")
            
            return True
        else:
            print("⚠️ No GPU available, will use CPU")
            return False
    except ImportError:
        print("⚠️ PyTorch not installed yet")
        return False

def download_sample_data():
    """ดาวน์โหลดข้อมูลตัวอย่าง (ถ้ามี)"""
    print("📊 Checking for sample data...")
    
    sample_file = 'data/sample/btc5m_sample.csv'
    if os.path.exists(sample_file):
        print(f"✅ Sample data found: {sample_file}")
    else:
        print("⚠️ No sample data found. Please upload your BTC 5m data to data/raw/")

def main():
    """ฟังก์ชันหลักสำหรับ setup"""
    print("🚀 Setting up BTC 5m LSTM Trading for Google Colab")
    print("=" * 50)
    
    # Setup directories
    setup_directories()
    
    # Install packages
    install_requirements()
    
    # Check GPU
    has_gpu = check_gpu()
    
    # Check sample data
    download_sample_data()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed!")
    print("\nNext steps:")
    print("1. Upload your BTC 5m data to 'data/raw/' folder")
    print("2. Run preprocessing: !python -m scripts.preprocess")
    print("3. Run training: !python -m scripts.run_train")
    
    if not has_gpu:
        print("\n⚠️ GPU not available. Consider:")
        print("   - Reduce batch_size in config.yaml (256-512)")
        print("   - Reduce max_epochs (5-10 for testing)")
        print("   - Change device to 'cpu' in config.yaml")

if __name__ == "__main__":
    main()