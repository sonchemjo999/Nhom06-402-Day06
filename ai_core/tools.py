"""
Utilities tối thiểu cho AI core.

Repo hiện dùng Gemini OCR trực tiếp trong `ai_core.agent`.
File này giữ lại để sau này có thể thêm helper tiền xử lý ảnh nếu cần.
"""

from __future__ import annotations


def supported_image_extensions() -> tuple[str, ...]:
    return (".png", ".jpg", ".jpeg", ".webp")
