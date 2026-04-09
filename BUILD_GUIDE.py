# -*- coding: utf-8 -*-
"""
================================================================================
  MEDREMINDER - HƯỚNG DẪN BUILD APK ĐẦY ĐỦ
================================================================================
  Phiên bản: 1.0.0
  Framework: Kivy 2.3.0 + KivyMD 1.2.0
  Target: Android APK

================================================================================
 MỤC LỤC
================================================================================
  1. Tổng quan
  2. Yêu cầu hệ thống
  3. Chuẩn bị code cho Android
  4. Cách 1: Build trên Google Colab (Khuyến nghị - Đơn giản nhất)
  5. Cách 2: Build trên WSL2 Ubuntu
  6. Cách 3: Build trên Termux (Android)
  7. Cách 4: Build trên máy ảo Linux
  8. Khắc phục lỗi thường gặp
  9. Cài đặt APK lên điện thoại
  10. Tối ưu hóa và đóng gói Google Play

================================================================================
 1. TỔNG QUAN
================================================================================
  MedReminder là ứng dụng nhắc nhở uống thuốc viết bằng Python + Kivy/KivyMD.
  Để tạo file APK cài đặt trên Android, bạn cần biên dịch code Python thành
  bytecode Android sử dụng Buildozer + python-for-android.

  Buildozer là công cụ chuẩn để đóng gói ứng dụng Kivy cho Android.

================================================================================
 2. YÊU CẦU HỆ THỐNG
================================================================================
  A. CHO MÁY TÍNH WINDOWS (WSL2):
     - Windows 10/11 với WSL2 enabled
     - Ubuntu 20.04 hoặc 22.04 trong WSL
     - 15GB+ dung lượng đĩa trống
     - RAM: 8GB+ (cho Android SDK + build)

  B. CHO GOOGLE COLAB:
     - Tài khoản Google
     - Dung lượng Drive để lưu APK (~100MB)

  C. CHO TERMUX (ĐIỆN THOẠI ANDROID):
     - Android 7.0+
     - 10GB+ bộ nhớ trong
     - Termux + Termux:API

================================================================================
 3. CHUẨN BỊ CODE CHO ANDROID
================================================================================
  Đã thực hiện sẵn các bước sau:

  ✅ buildozer.spec - File cấu hình build đã tạo
  ✅ requirements.txt - Danh sách dependencies
  ✅ __init__.py - Đã có trong tất cả các package

  CẦN THỰC HIỆN THÊM:

  a) Tạo icon ứng dụng (512x512 PNG):
     - Thiết kế icon bằng Canva/Photoshop/Figma
     - Lưu vào App1/icon.png

  b) Tạo presplash image (800x600 PNG):
     - Màn hình chờ khi app khởi động
     - Lưu vào App1/presplash.png

  c) Kiểm tra file sound (đã có sẵn):
     - Đảm bảo tất cả file .mp3 trong assets/sounds/


================================================================================
 4. CÁCH 1: BUILD TRÊN GOOGLE COLAB (KHUYẾN NGHỊ)
================================================================================
  Đây là cách đơn giản và nhanh nhất, không cần cài đặt gì trên máy.

  BƯỚC 1: Mở Google Colab
  ------------------------
  Truy cập: https://colab.research.google.com
  Tạo Notebook mới

  BƯỚC 2: Cài đặt dependencies
  -----------------------------
  Trong cell đầu tiên, chạy:

  ```python
  !apt-get update
  !apt-get install -y python3-pip build-essential git python3-dev \\
      ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev \\
      libsdl2-ttf-dev libffi-dev openjdk-17-jdk zlib1g-dev \\
      libgstreamer1.0-dev gstreamer1.0-plugins-base \\
      autoconf libtool swig unzip
  ```

  BƯỚC 3: Cài đặt Python packages
  -------------------------------
  ```python
  !pip install buildozer==1.5.0 kivy==2.3.0
  !pip install kivymd==1.2.0 Pillow pygame
  ```

  BƯỚC 4: Upload code lên Colab
  -----------------------------
  Cách 1 - Upload thủ công:
  ```python
  from google.colab import files
  import zipfile
  import os

  # Upload thư mục App1 (nén thành ZIP trước)
  uploaded = files.upload()

  # Giải nén
  for fn in uploaded.keys():
      if fn.endswith('.zip'):
          with zipfile.ZipFile(fn, 'r') as zip_ref:
              zip_ref.extractall('/content/App1')
  ```

  Cách 2 - Từ Google Drive:
  ```python
  from google.colab import drive
  drive.mount('/content/drive')

  # Copy từ Drive vào Colab
  !cp -r /content/drive/MyDrive/App1 /content/
  ```

  BƯỚC 5: Build APK
  -----------------
  ```python
  %cd /content/App1

  # Initialize buildozer (nếu chưa có buildozer.spec)
  # !buildozer init

  # Build debug APK
  !buildozer android debug
  ```

  ⏱️ Thời gian: 15-30 phút (lần đầu tiên, download Android SDK)

  BƯỚC 6: Tải APK về
  -------------------
  ```python
  # APK nằm trong thư mục bin/
  from google.colab import files
  import shutil

  # Copy APK ra thư mục gốc
  shutil.copy('/content/App1/bin/' + 
              [f for f in os.listdir('/content/App1/bin/') 
               if f.endswith('.apk')][0],
              '/content/medreminder.apk')

  files.download('/content/medreminder.apk')
  ```

================================================================================
 5. CÁCH 2: BUILD TRÊN WSL2 UBUNTU
================================================================================
  Phù hợp nếu bạn muốn build trên máy Windows đã cài WSL2.

  BƯỚC 1: Cài đặt WSL2 (nếu chưa có)
  ---------------------------------
  Mở PowerShell (Admin) và chạy:
  ```powershell
  wsl --install -d Ubuntu-22.04
  ```

  Khởi động lại máy tính.

  BƯỚC 2: Cài đặt Java JDK + System packages
  ------------------------------------------
  Trong Ubuntu terminal:

  ```bash
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y python3-pip python3-dev ffmpeg libavcodec-extra \\
      libsdl2-dev libsqlite3-dev libffi-dev zlib1g-dev \\
      libgstreamer1.0-dev gstreamer1.0-plugins-base \\
      autoconf libtool swig unzip git openjdk-17-jdk \\
      cmake ninja-build
  ```

  BƯỚC 3: Set JAVA_HOME
  ---------------------
  ```bash
  export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
  export PATH=$JAVA_HOME/bin:$PATH
  echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
  echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
  ```

  BƯỚC 4: Copy project vào WSL
  ----------------------------
  Trong PowerShell:
  ```powershell
  # Copy thư mục App1 vào WSL home
  wsl -d Ubuntu-22.04 -- cp -r G:\\AI_THUC_CHIEN_20K_2026_K1\\test_app\\App1 ~/App1
  ```

  Hoặc trong Ubuntu:
  ```bash
  cp -r /mnt/g/AI_THUC_CHIEN_20K_2026_K1/test_app/App1 ~/
  cd ~/App1
  ```

  BƯỚC 5: Cài Python dependencies
  -------------------------------
  ```bash
  pip3 install -r requirements.txt
  pip3 install buildozer==1.5.0
  ```

  BƯỚC 6: Verify buildozer
  ------------------------
  ```bash
  buildozer version
  # Nên hiển thị: 1.5.0
  ```

  BƯỚC 7: Build APK
  -----------------
  ```bash
  buildozer android debug
  ```

  ⏱️ Thời gian: 20-45 phút (lần đầu)

  BƯỚC 8: Copy APK về Windows
  ----------------------------
  ```bash
  # APK nằm trong ~/App1/bin/
  cp ~/App1/bin/*.apk /mnt/g/AI_THUC_CHIEN_20K_2026_K1/test_app/
  ls -la ~/App1/bin/
  ```

================================================================================
 6. CÁCH 3: BUILD TRÊN TERMUX (ANDROID)
================================================================================
  Cho phép build trực tiếp trên điện thoại Android.

  BƯỚC 1: Cài đặt Termux
  ----------------------
  1. Gỡ cài đặt Termux cũ (nếu có)
  2. Cài Termux từ F-Droid (KHÔNG phải Google Play)
     https://f-droid.org/packages/com.termux/

  BƯỚC 2: Cài đặt Termux:API
  --------------------------
  Tải từ F-Droid:
  https://f-droid.org/packages/com.termux.api/

  Cấp quyền trong Termux:
  ```bash
  termux-setup-storage
  pkg install termux-api
  ```

  BƯỚC 3: Update packages
  -----------------------
  ```bash
  pkg update && pkg upgrade -y
  pkg install python buildozer git
  pkg install -y python-ndk-sysroot
  ```

  BƯỚC 4: Copy project vào Termux
  -------------------------------
  ```bash
  cd /sdcard
  ls
  # Tìm thư mục chứa App1

  # Copy vào Termux home
  cp -r /sdcard/Download/App1 ~/
  cd ~/App1
  ```

  BƯỚC 5: Cài dependencies
  ------------------------
  ```bash
  pip install -r requirements.txt
  pip install buildozer==1.5.0
  ```

  BƯỚC 6: Build
  -------------
  ```bash
  buildozer android debug
  ```

  ⏱️ Thời gian: 30-60 phút (phụ thuộc vào điện thoại)

  BƯỚC 7: Lấy APK
  ----------------
  ```bash
  ls ~/App1/bin/
  # Copy ra thẻ nhớ
  cp ~/App1/bin/*.apk /sdcard/
  ```

================================================================================
 7. CÁCH 4: BUILD TRÊN MÁY ẢO LINUX
================================================================================
  Dùng VirtualBox + Ubuntu Desktop.

  1. Tải Ubuntu Desktop ISO: https://ubuntu.com/download/desktop
  2. Cài VirtualBox: https://www.virtualbox.org/wiki/Downloads
  3. Tạo VM với:
     - RAM: 8GB
     - HDD: 50GB
     - CPU: 4 cores
  4. Cài Ubuntu Desktop
  5. Trong Ubuntu, cài dependencies như Bước 2, 3 trong WSL2
  6. Copy project vào VM (Shared Folders hoặc USB)
  7. Build với buildozer

================================================================================
 8. KHẮC PHỤC LỖI THƯỜNG GẶP
================================================================================

  ❌ LỖI: "sdk not found"
  ----------------------
  Nguyên nhân: Android SDK chưa được tải.
  Giải quyết:
  ```bash
  buildozer android debug --verbose
  # Buildozer sẽ tự tải SDK
  ```

  ❌ LỖI: "Java not found"
  -----------------------
  Nguyên nhân: JAVA_HOME chưa được set.
  Giải quyết:
  ```bash
  export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
  export PATH=$JAVA_HOME/bin:$PATH
  ```

  ❌ LỖI: "Operation not permitted" (WSL)
  --------------------------------------
  Nguyên nhân: WSL2 filesystem permission issue.
  Giải quyết: Copy project vào ~/ (Linux filesystem),
  KHÔNG build trong /mnt/g/

  ❌ LỖI: "Missing dependency: sdl2"
  ---------------------------------
  Nguyên nhân: Thiếu SDL2 dev packages.
  Giải quyết:
  ```bash
  sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
  ```

  ❌ LỖI: "python-fcntl not available on Android"
  ----------------------------------------------
  Nguyên nhân: Module không tương thích Android.
  Giải quyết: Bỏ qua, không ảnh hưởng build. App đã có try-except.

  ❌ LỖI: Build quá chậm / bị kill
  ---------------------------------
  Nguyên nhân: Thiếu RAM.
  Giải quyết:
  - Tăng RAM VM lên 8GB+
  - Trong WSL2, giới hạn WSL RAM:
    Tạo file %USERPROFILE%\\.wslconfig:
    ```
    [wsl2]
    memory=8GB
    processors=4
    ```

  ❌ LỖI: "pillow: no such file"
  -----------------------------
  Nguyên nhân: Pillow chưa được cài đúng cách.
  Giải quyết:
  ```bash
  pip install --force-reinstall Pillow
  ```

================================================================================
 9. CÀI ĐẶT APK LÊN ĐIỆN THOẠI
================================================================================

  CÁCH 1: Qua USB (Windows)
  -------------------------
  1. Bật "Developer Options" + "USB Debugging" trên điện thoại
  2. Kết nối USB
  3. Copy file .apk vào điện thoại
  4. Mở file APK trên điện thoại để cài

  CÁCH 2: Qua Google Drive
  ------------------------
  1. Upload APK lên Google Drive
  2. Mở Drive trên điện thoại
  3. Tap vào file .apk để cài

  CÁCH 3: Qua ADB (Command line)
  ------------------------------
  ```bash
  adb install medreminder-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
  ```

  CÁCH 4: Qua LocalSend
  ---------------------
  1. Cài LocalSend trên PC và điện thoại
  2. Gửi file APK qua mạng cục bộ

  LƯU Ý: Cần bật "Install from unknown sources" trong Settings > Security

================================================================================
 10. TỐI ƯU VÀ PHÁT HÀNH GOOGLE PLAY
================================================================================

  A. TẠO RELEASE APK (không debug)
  --------------------------------
  1. Ký APK bên trong buildozer.spec:
  ```
  android.release_artifact = apk
  ```

  2. Tạo keystore:
  ```bash
  keytool -genkey -v -keystore my-release-key.keystore \\
      -alias medreminder -keyalg RSA -keysize 2048 -validity 10000
  ```

  3. Cấu hình keystore trong buildozer.spec:
  ```
  android.keyalias = medreminder
  android.keystore = my-release-key.keystore
  android.keystore_password = PASSWORD
  android.keyalias_password = PASSWORD
  ```

  4. Build release:
  ```bash
  buildozer android release
  ```

  B. CẬP NHẬT BUILD SPEC
  ----------------------
  Trong buildozer.spec:
  ```
  version = 1.0.1        # Tăng version khi update
  android.version_code = 2  # Số nguyên tăng dần
  ```

  C. CHẠY THỬ TRÊN MÁY (không cần build)
  --------------------------------------
  Nếu chỉ muốn test trên điện thoại mà không build APK:

  1. Cài Kivy Launcher:
     - Tải từ Google Play hoặc F-Droid
     - Tạo thư mục: /sdcard/kivy/MedReminder/
     - Copy source code vào
     - Mở Kivy Launcher, chọn MedReminder

================================================================================
 KẾT LUẬN
================================================================================
  Sau khi build thành công, bạn sẽ có file:
    medreminder-1.0.0-armeabi-v7a-debug.apk   (32-bit)
    medreminder-1.0.0-arm64-v8a-debug.apk    (64-bit)

  Đây là file cài đặt có thể phân phối cho người dùng Android.

  Nếu cần hỗ trợ thêm, hãy kiểm tra:
  - Buildozer docs: https://buildozer.readthedocs.io
  - Kivy Android: https://github.com/kivy/python-for-android
  - KivyMD docs: https://kivymd.readthedocs.io
================================================================================
"""

if __name__ == "__main__":
    print(__doc__)
