#!/bin/bash
# =============================================================================
# Build APK Script - Chi build APK thoi
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo -e "\033[1;36m"
echo "========================================"
echo "  Build APK - MedReminder"
echo "========================================"
echo -e "\033[0m"

# Kich hoat virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Cau hinh JAVA
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Xoa cache cu (neu can)
# rm -rf .buildozer/

# Build APK - tu dong tra loi 'y'
echo ""
echo "[*] Bat dau build APK..."
echo "[*] Thoi gian: 5-15 phut"
echo ""

echo "y" | buildozer -f "${SCRIPT_DIR}/buildozer.spec" android debug

# Kiem tra ket qua
if [ -f "bin/"*.apk ]; then
    echo ""
    echo -e "\033[1;32m========================================"
    echo "  BUILD THANH CONG!"
    echo -e "\033[1;32m========================================"
    echo ""
    echo "APK da tao:"
    ls -lh bin/*.apk
    echo ""
    echo "Copy APK ve may Windows:"
    echo "  scp root@YOUR_VPS_IP:/root/App1/bin/*.apk C:\Users\YourName\Downloads\"
else
    echo ""
    echo -e "\033[1;31mBuild that bai![0m"
    echo "Xem log de biet chi tiet loi."
    exit 1
fi
