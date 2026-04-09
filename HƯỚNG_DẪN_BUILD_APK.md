# MedReminder - Hướng Dẫn Build APK Hoàn Chỉnh

## 📋 Tổng Quan

Dự án **MedReminder** đã được chuẩn bị sẵn sàng để build thành APK với các file cấu hình đã được tạo.

### Các File Đã Tạo

| File | Mục đích |
|------|----------|
| `buildozer.spec` | Cấu hình Buildozer cho Android |
| `requirements.txt` | Danh sách Python dependencies |
| `BUILD_GUIDE.py` | Hướng dẫn chi tiết đầy đủ |
| `build_apk.py` | Script kiểm tra và hướng dẫn nhanh |

### Cấu Trúc Project

```
App1/
├── main.py                      # Entry point ✅
├── buildozer.spec               # ✅ ĐÃ TẠO
├── requirements.txt             # ✅ ĐÃ TẠO
├── BUILD_GUIDE.py               # ✅ Hướng dẫn đầy đủ
├── build_apk.py                 # ✅ Script kiểm tra
├── kv/                         # UI files ✅
├── screens/                    # Logic ✅
├── services/                   # Alarm service ✅
├── ai_core/                   # AI agent ✅
├── data/                      # Mock data ✅
├── assets/
│   ├── icons/medications/     # 78 icons (SVG+PNG) ✅
│   ├── icons/medications_png/ # 42 PNG icons ✅
│   └── sounds/                # 33 MP3 ringtones ✅
└── __init__.py files          # 5 packages ✅
```

---

## 🚀 Cách Build Đơn Giản Nhất: Google Colab

### Bước 1: Mở Google Colab

Truy cập: **https://colab.research.google.com**

### Bước 2: Tạo Notebook mới và chạy các cell sau

```python
# Cell 1: Cài đặt hệ thống
!apt-get update
!apt-get install -y python3-pip build-essential git python3-dev \
    ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev \
    libsdl2-ttf-dev libffi-dev openjdk-17-jdk zlib1g-dev \
    libgstreamer1.0-dev gstreamer1.0-plugins-base \
    autoconf libtool swig unzip
```

```python
# Cell 2: Cài đặt Python packages
!pip install buildozer==1.5.0 kivy==2.3.0 kivymd==1.2.0 Pillow pygame
```

```python
# Cell 3: Upload code (hoặc clone từ GitHub)
# Cách 1: Upload thủ công
from google.colab import files
uploaded = files.upload()  # Upload thư mục App1 đã nén thành ZIP
```

```python
# Cell 4: Giải nén và build
import os
import zipfile
import shutil

# Giải nén nếu upload ZIP
# shutil.unpack_archive('App1.zip', '/content/')

%cd /content/App1

# Build debug APK
!buildozer android debug
```

### Bước 3: Tải APK về

```python
from google.colab import files
import shutil

# Copy APK ra thư mục gốc
shutil.copy('/content/App1/bin/medreminder-1.0.0-arm64-v8a_armeabi-v7a-debug.apk',
            '/content/medreminder.apk')

# Tải về
files.download('/content/medreminder.apk')
```

---

## 🖥️ Cách 2: Build trên WSL2 Ubuntu (Khuyến nghị cho Windows)

### Yêu cầu

- Windows 10/11 với WSL2 đã bật
- 15GB+ dung lượng đĩa
- RAM: 8GB+

### Các bước

#### 1. Bật WSL2 (nếu chưa có)

Mở **PowerShell (Admin)**:

```powershell
wsl --install -d Ubuntu-22.04
```

#### 2. Cài đặt dependencies trong Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-dev ffmpeg libavcodec-extra \
    libsdl2-dev libsqlite3-dev libffi-dev zlib1g-dev \
    libgstreamer1.0-dev gstreamer1.0-plugins-base \
    autoconf libtool swig unzip git openjdk-17-jdk
```

#### 3. Set JAVA_HOME

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

#### 4. Copy project vào Linux filesystem

```bash
cp -r /mnt/g/AI_THUC_CHIEN_20K_2026_K1/test_app/App1 ~/
cd ~/App1
```

**QUAN TRỌNG**: Không build trong `/mnt/g/` - phải copy vào home directory!

#### 5. Cài Python dependencies

```bash
pip3 install -r requirements.txt
pip3 install buildozer==1.5.0
```

#### 6. Build APK

```bash
buildozer android debug
```

⏱️ **Thời gian**: 20-45 phút (lần đầu tiên)

#### 7. Copy APK về Windows

```bash
cp ~/App1/bin/*.apk /mnt/g/AI_THUC_CHIEN_20K_2026_K1/test_app/
```

---

## 📱 Cách 3: Build trên Termux (Android)

### Yêu cầu

- Android 7.0+
- 10GB+ bộ nhớ trong
- Termux từ F-Droid (KHÔNG phải Google Play)

### Các bước

#### 1. Cài đặt Termux

Tải từ F-Droid: https://f-droid.org/packages/com.termux/

#### 2. Cài dependencies

```bash
pkg update && pkg upgrade -y
pkg install python buildozer git
pkg install termux-api
termux-setup-storage
```

#### 3. Copy project

```bash
cp -r /sdcard/Download/App1 ~/
cd ~/App1
```

#### 4. Cài Python packages

```bash
pip install -r requirements.txt
pip install buildozer==1.5.0
```

#### 5. Build

```bash
buildozer android debug
```

⏱️ **Thời gian**: 30-60 phút

#### 6. Copy APK ra thẻ nhớ

```bash
cp ~/App1/bin/*.apk /sdcard/
```

---

## 🔧 Khắc Phục Lỗi Thường Gặp

### ❌ Lỗi: "sdk not found"

```bash
# Buildozer sẽ tự tải SDK, chỉ cần chạy lại
buildozer android debug --verbose
```

### ❌ Lỗi: "Java not found"

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

### ❌ Lỗi: "Operation not permitted" (WSL)

**NGUYÊN NHÂN**: Đang build trong `/mnt/g/` (Windows filesystem)

**GIẢI PHÁP**: Copy project vào home directory:

```bash
cp -r /mnt/g/AI_THUC_CHIEN_20K_2026_K1/test_app/App1 ~/
cd ~/App1
# Bây giờ mới build
buildozer android debug
```

### ❌ Lỗi: Build quá chậm / bị kill

**NGUYÊN NHÂN**: Thiếu RAM

**GIẢI PHÁP**:
- Tăng RAM VM lên 8GB+
- Trong WSL2, tạo file `%USERPROFILE%\.wslconfig`:

```
[wsl2]
memory=8GB
processors=4
```

### ❌ Lỗi: Import PIL không được

```bash
pip install --force-reinstall Pillow
```

### ❌ Lỗi: "fcntl not available"

**ĐÂY KHÔNG PHẢI LỖI!** - Module này chỉ dùng trên Unix, app đã có try-except xử lý.

---

## 📲 Cài Đặt APK lên Điện Thoại

### Cách 1: Qua USB

1. Bật **Developer Options** + **USB Debugging** trên điện thoại
2. Kết nối USB
3. Copy file `.apk` vào điện thoại
4. Tap vào file APK để cài

### Cách 2: Qua Google Drive

1. Upload APK lên Google Drive
2. Mở Drive trên điện thoại
3. Tap vào file `.apk` để cài

### Cách 3: Qua ADB

```bash
adb install medreminder-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### LƯU Ý QUAN TRỌNG

Cần bật **"Install from unknown sources"** trong:
**Settings** > **Security** > **Unknown sources**

---

## 📊 Thông Tin APK Sau Build

| Thông số | Giá trị |
|----------|---------|
| Tên ứng dụng | MedReminder |
| Package | org.medreminder |
| Version | 1.0.0 |
| Kiến trúc hỗ trợ | armeabi-v7a (32-bit), arm64-v8a (64-bit) |
| SDK tối thiểu | Android 5.0 (API 21) |
| Quyền | VIBRATE, WAKE_LOCK, INTERNET, RECEIVE_BOOT_COMPLETED |

---

## 📚 Tài Liệu Tham Khảo

- **Buildozer Docs**: https://buildozer.readthedocs.io
- **python-for-android**: https://github.com/kivy/python-for-android
- **KivyMD Docs**: https://kivymd.readthedocs.io
- **Kivy Docs**: https://kivy.org/doc/stable/

---

## ❓ Cần Hỗ Trợ Thêm?

Nếu gặp lỗi không có trong danh sách trên, hãy:

1. Chạy với flag `--verbose` để xem chi tiết lỗi:
   ```bash
   buildozer android debug --verbose
   ```

2. Kiểm tra log trong `.buildozer/` directory

3. Đảm bảo đã copy project vào Linux filesystem (không phải `/mnt/g/`)

---

**Chúc bạn build APK thành công! 🎉**
