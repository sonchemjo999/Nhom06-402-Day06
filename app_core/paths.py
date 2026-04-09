"""Đường dẫn gốc project — dùng chung cho app_core."""
import os

_APP_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(_APP_CORE_DIR)
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
