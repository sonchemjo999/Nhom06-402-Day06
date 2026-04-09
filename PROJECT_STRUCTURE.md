# Project Structure - Production Standard

```
project_root/
├── src/                              # Source code chính
│   ├── __init__.py
│   ├── main.py                       # Entry point
│   │
│   ├── app_config/                   # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py               # App settings
│   │   ├── datetime_config.py        # DateTime config
│   │   └── theme.py                  # Theme manager
│   │
│   ├── ui/                           # User Interface
│   │   ├── __init__.py
│   │   ├── kv/                       # Kivy UI definitions
│   │   │   └── app_root.kv
│   │   └── styles/                   # UI utilities & styling
│   │       ├── icon_loader.py
│   │       ├── icon_painter.py
│   │       ├── icon_converter.py
│   │       └── create_med_icons.py
│   │
│   ├── core/                         # Business Logic & AI
│   │   ├── __init__.py
│   │   ├── ai/                       # AI Module
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── tools.py
│   │   │   └── system_prompt.txt
│   │   ├── admin/                    # Admin Commands
│   │   │   └── commands.py
│   │   └── utils/                    # Utilities
│   │
│   ├── services/                     # External Services
│   │   ├── __init__.py
│   │   └── sound_manager.py
│   │
│   └── assets/                       # Static Resources
│       ├── icons/
│       │   ├── medications/
│       │   └── medications_png/
│       ├── sounds/
│       └── data/
│
├── tests/                            # Unit Tests
│   └── __init__.py
│
├── build/                            # Build Configuration
│   ├── buildozer.spec
│   ├── build_apk.py
│   ├── build_guide.py
│   └── README.md
│
├── config/                           # Environment Configuration
│   ├── .env.example
│   └── .env (not in git)
│
├── docs/                             # Documentation
│   ├── spec-draft.md
│   ├── walkthrough.md
│   └── HƯỚNG_DẪN_BUILD_APK.md
│
├── scripts/                          # Utility Scripts
│
├── requirements.txt                  # Dependencies
├── README.md                         # Project README
├── .gitignore
└── PROJECT_STRUCTURE.md              # This file
```

## Import Pattern

```python
# Correct imports
from src.core.ai.agent import Agent
from src.services.sound_manager import SoundManager
from src.app_config.settings import SETTINGS
```

## Key Improvements

1. **Clear Separation**: Code được tổ chức theo chức năng
2. **Scalability**: Dễ dàng mở rộng và thêm features mới
3. **Testing**: Cấu trúc thuận tiện cho unit tests
4. **Configuration**: Tách riêng config từ code
5. **Documentation**: Mỗi module có README rõ ràng
6. **Dependencies**: Quản lý requirements tập trung

## Next Steps

1. Update `requirements.txt` theo dependencies thực tế
2. Tạo `src/core/utils/__init__.py` với common utilities
3. Thêm tests cho mỗi module
4. Setup CI/CD pipeline
