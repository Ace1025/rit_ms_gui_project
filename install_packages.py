#!/usr/bin/env python3
"""
RIT-MS GUI 프로젝트 패키지 자동 설치 스크립트
"""

import subprocess
import sys
import os

def install_package(package):
    """패키지를 설치하는 함수"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 설치 완료")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {package} 설치 실패")
        return False

def check_package(package_name):
    """패키지가 이미 설치되어 있는지 확인"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    print("🚀 RIT-MS GUI 프로젝트 패키지 설치를 시작합니다...\n")
    
    # 필요한 패키지 목록
    packages = [
        ("pandas", "pandas>=1.3.0"),
        ("matplotlib", "matplotlib>=3.4.0"), 
        ("PyQt5", "pyqt5>=5.15.0"),
        ("openpyxl", "openpyxl>=3.0.0")
    ]
    
    installed_count = 0
    
    for import_name, pip_name in packages:
        print(f"📦 {pip_name} 확인 중...")
        
        if check_package(import_name):
            print(f"✅ {import_name}이 이미 설치되어 있습니다.\n")
            installed_count += 1
        else:
            print(f"⚠️  {import_name}이 설치되지 않았습니다. 설치 중...")
            if install_package(pip_name):
                installed_count += 1
            print()
    
    print("=" * 50)
    print(f"설치 완료: {installed_count}/{len(packages)} 패키지")
    
    if installed_count == len(packages):
        print("🎉 모든 패키지가 성공적으로 설치되었습니다!")
        print("이제 다음 명령어로 GUI를 실행할 수 있습니다:")
        print("python main_layer1_gui.py")
    else:
        print("⚠️  일부 패키지 설치에 실패했습니다.")
        print("수동으로 다음 명령어를 실행해보세요:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()