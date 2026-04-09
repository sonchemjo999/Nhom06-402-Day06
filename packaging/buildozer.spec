[app]

title = MedReminder
package.name = medreminder
package.domain = org.medreminder

# Phiên bản ứng dụng
version = 1.0.0

# === NGUỒN MÃ ===
source.include_exts = py,png,jpg,kv,atlas,ttf,mp3,json,txt,svg

# Thư mục chính của source code (spec nằm trong packaging/ → project root là ..)
source.dir = ..

# Không đóng gói script/tool/dev
source.exclude_dirs = tool_test,packaging,admin,docs,.git,bin,.buildozer,venv,__pycache__

# === PHỤ THUỘC PYTHON ===
requirements = python3,kivy==2.3.0,kivymd==1.2.0,Pillow,android

# === CẤU HÌNH ANDROID ===
# Quyền Android
android.permissions = VIBRATE,WAKE_LOCK,INTERNET,RECEIVE_BOOT_COMPLETED

# Hướng màn hình: portrait (đứng) / landscape (ngang) / all
orientation = portrait

# Toàn màn hình
fullscreen = 0

# Icon ứng dụng (bạn cần tạo icon.png 512x512)
# android.icon = icon.png

# Màu nền khởi động
android.presplash_color = #FFFFFF

# Cho phép sao lưu dữ liệu
android.allow_backup = True

# Chỉ định NDK - sử dụng phiên bản mặc định của buildozer
p4a.bootstrap = sdl2

# Phiên bản Android tối thiểu
android.minapi = 21

# Mã nguồn Python yêu cầu
osx.python_version = 3
osx.kivy_version = 2.3.0

# === LOG ===
log_level = 2

# === TIÊU ĐỀ CỬA SỔ ===
window.title = MedReminder

# === PRESplash (màn hình chờ) ===
# Đặt một ảnh PNG có tên presplash.png trong thư mục gốc
# để hiển thị trong khi ứng dụng đang khởi động
