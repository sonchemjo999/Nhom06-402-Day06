#!/bin/bash
# =============================================================================
# MedReminder - Build APK Script cho Ubuntu 22.04 VPS
# =============================================================================
# Chạy từ thư mục gốc project:  bash packaging/build_on_vps.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo '========================================'
echo '  MedReminder APK Builder - Ubuntu 22.04'
echo '========================================'
echo -e "${NC}"

# BUOC 1: Cap nhat he thong
step1() {
    echo -e "${YELLOW}[1/7]${NC} Cap nhat he thong..."
    sudo apt update && sudo apt upgrade -y
    echo -e "${GREEN} Hoan tat${NC}"
}

# BUOC 2: Cai dat cac goi
step2() {
    echo -e "${YELLOW}[2/7]${NC} Cai dat cac goi..."
    sudo apt install -y python3-pip python3-dev python3-venv ffmpeg libavcodec-extra libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libffi-dev zlib1g-dev libgstreamer1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good autoconf libtool swig unzip git openjdk-17-jdk cmake ninja-build ccache zip openjdk-17-jdk-headless
    echo -e "${GREEN} Hoan tat${NC}"
}

# BUOC 3: Cau hinh Java
step3() {
    echo -e "${YELLOW}[3/7]${NC} Cau hinh Java..."
    export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
    export PATH=$JAVA_HOME/bin:$PATH
    if ! grep -q 'JAVA_HOME=' ~/.bashrc; then
        echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
        echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
    fi
    java -version
    echo -e "${GREEN} Java OK: $JAVA_HOME${NC}"
}

# BUOC 4: Tao swap
step4() {
    echo -e "${YELLOW}[4/7]${NC} Kiem tra RAM..."
    TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
    echo "   RAM: ${TOTAL_MEM}MB"
    if [ "$TOTAL_MEM" -lt 8000 ]; then
        echo -e "${YELLOW}   Tao swap 4GB...${NC}"
        if [ ! -f /swapfile ]; then
            sudo fallocate -l 4G /swapfile
            sudo chmod 600 /swapfile
            sudo mkswap /swapfile
            sudo swapon /swapfile
            echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
        fi
        echo -e "${GREEN} Swap OK${NC}"
    else
        echo -e "${GREEN} RAM du${NC}"
    fi
}

# BUOC 5: Cai Python
step5() {
    echo -e "${YELLOW}[5/7]${NC} Cai Python packages..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install Cython==0.29.36 kivy==2.3.0 kivymd==1.2.0 Pillow docutils pygments buildozer==1.5.0
    echo -e "${GREEN} Python packages OK${NC}"
}

# BUOC 6: Kiem tra code
step6() {
    echo -e "${YELLOW}[6/7]${NC} Kiem tra source code..."
    if [ ! -f "main.py" ]; then
        echo -e "${RED} Chua co source code!${NC}"
        echo 'Upload App1.zip len VPS roi chay: unzip App1.zip && cd App1 && ./build_on_vps.sh'
        exit 1
    fi
    echo -e "${GREEN} Code OK${NC}"
}

# BUOC 7: Build APK
step7() {
    echo -e "${YELLOW}[7/7]${NC} Build APK..."
    source venv/bin/activate
    export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
    export PATH=$JAVA_HOME/bin:$PATH
    buildozer -f "$SCRIPT_DIR/buildozer.spec" android debug
    echo -e "${GREEN}========================================"
    echo '  BUILD HOAN TAN!'
    echo -e "${GREEN}========================================"
    echo 'APK trong: bin/'
    ls -la bin/*.apk 2>/dev/null
}

# CHAY
echo ''
echo 'Bat dau build APK (20-45 phut lan dau)...'
echo ''
step1
step2
step3
step4
step5
step6
step7
echo -e "${GREEN} Chuc mung!${NC}"
