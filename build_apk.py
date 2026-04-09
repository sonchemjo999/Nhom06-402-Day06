# -*- coding: utf-8 -*-
"""
MedReminder - APK Build Script
用于在 Windows 上检查依赖是否已安装
实际构建需要在 WSL2 / Linux / Google Colab / Termux 中执行
"""

import subprocess
import sys


def check_dependencies():
    """检查 Python 依赖是否已安装"""
    print("=" * 50)
    print("MedReminder - APK Build Check")
    print("=" * 50)

    deps = [
        ("kivy", "Kivy framework"),
        ("kivymd", "KivyMD UI components"),
        ("PIL", "Pillow image library"),
        ("pygame", "Pygame audio library"),
    ]

    all_ok = True
    for module, name in deps:
        try:
            __import__(module)
            print(f"✅ {name} - OK")
        except ImportError:
            print(f"❌ {name} - MISSING")
            all_ok = False

    print("=" * 50)
    if all_ok:
        print("✅ 所有依赖已安装！可以运行 `python main.py` 测试应用")
        print("")
        print("⚠️  APK 构建需要在以下环境之一进行：")
        print("   1. WSL2 + Ubuntu (推荐)")
        print("   2. Google Colab (最简单)")
        print("   3. Termux on Android")
        print("   4. Linux 虚拟机")
    else:
        print("❌ 缺少依赖，请先安装：")
        print(f"   pip install -r requirements.txt")
    print("=" * 50)
    return all_ok


def build_apk_info():
    """显示 APK 构建说明"""
    print("""
📱 APK 构建指南
==============

在你的项目目录 (App1) 中，有两个配置文件已准备好：

  ✅ buildozer.spec  - Buildozer 构建配置
  ✅ requirements.txt - Python 依赖列表

==========================================
构建步骤（选择一种方式）：
==========================================

方法 1️⃣  Google Colab（最简单，零配置）
------------------------------------------
1. 打开 https://colab.research.google.com
2. 创建新 Notebook
3. 执行以下命令：

!apt-get install -y python3-pip build-essential git python3-dev \\
    ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev \\
    libsdl2-ttf-dev libffi-dev openjdk-8-jdk zlib1g-dev \\
    libgstreamer1.0-dev gstreamer1.0-plugins-base

!pip install buildozer kivy==2.3.0 kivymd==1.2.0 pillow pygame

# 上传你的 App1 文件夹到 Colab
# 然后进入 App1 目录执行：

!buildozer android debug

# APK 将生成在 bin/ 目录下


方法 2️⃣  WSL2 Ubuntu（推荐用于 Windows 用户）
-----------------------------------------------
1. 打开 PowerShell，以管理员身份运行：
   wsl --install

2. 进入 Ubuntu 终端，安装依赖：

sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-dev ffmpeg libavcodec-extra \\
    libsdl2-dev libsqlite3-dev libffi-dev zlib1g-dev \\
    libgstreamer1.0-dev gstreamer1.0-plugins-base \\
    autoconf libtool swig unzip git openjdk-17-jdk

3. 复制你的 App1 文件夹到 WSL：
   cp -r /mnt/g/AI_THUC_CHIEN_20K_2026_K1/test_app/App1 ~/

4. 进入目录，安装 Python 依赖：
   cd ~/App1
   pip3 install -r requirements.txt
   pip3 install buildozer

5. 初始化 Buildozer：
   buildozer init

6. 构建 APK：
   buildozer android debug

APK 将生成在 /root/.buildozer/apk/.../bin/ 目录下


方法 3️⃣  Termux on Android（直接用手机构建）
--------------------------------------------
1. 安装 Termux (F-Droid 版本)
2. 安装 Termux:API

3. 在 Termux 中执行：

pkg update && pkg upgrade
pkg install python buildozer
pkg install git

cd /sdcard
# 将 App1 文件夹放到 /sdcard/

cd App1
buildozer init
buildozer android debug


方法 4️⃣  虚拟机 (VirtualBox + Ubuntu)
--------------------------------------
1. 下载 Ubuntu Desktop ISO
2. 创建虚拟机，安装 Ubuntu
3. 在虚拟机中安装 Buildozer
4. 复制项目文件，构建 APK

==========================================
注意事项：
==========================================

⚠️  APK 构建过程需要下载 Android SDK（约 1-2GB）
⚠️  首次构建可能需要 10-30 分钟（取决于网速）
⚠️  确保有足够的磁盘空间（至少 5GB）

📦 构建完成后，APK 文件可用于：
  - 安装到 Android 手机测试
  - 分发给用户
  - 发布到 Google Play Store
""")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_dependencies()
    else:
        build_apk_info()
