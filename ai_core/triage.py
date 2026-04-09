"""
=============================================================================
 AI Triage - Module phân loại triệu chứng bằng OpenAI API
=============================================================================
 File: ai_core/triage.py
 Mô tả: Gọi OpenAI API để phân loại triệu chứng thành RED/YELLOW/GREEN
        Thay thế keyword matching cũ bằng AI full.

 Response format: JSON với cấu trúc {level, confidence, reason, action, ...}
=============================================================================
"""

import os
import json
import sys
from typing import Optional, Dict

# Thêm project root vào path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


# ===== Đọc System Prompt cho Triage =====
TRIAGE_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "triage_prompt.txt")
try:
    with open(TRIAGE_PROMPT_PATH, "r", encoding="utf-8") as f:
        TRIAGE_SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    print(f"[Triage] Cảnh báo: Không tìm thấy {TRIAGE_PROMPT_PATH}")
    TRIAGE_SYSTEM_PROMPT = "Bạn là hệ thống phân loại triệu chứng y tế."


# ===== Kiểm tra OpenAI availability =====
OPENAI_AVAILABLE = False
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    OPENAI_AVAILABLE = True
except ImportError:
    print("[Triage] [!] LangChain OpenAI chưa cài đặt.")


def _parse_triage_response(response_text: str) -> Optional[Dict]:
    """
    Parse response text từ OpenAI thành dict chuẩn cho app.

    Tham số:
        response_text: Text trả về từ LLM (expected JSON)

    Trả về:
        dict với format: {level, confidence, reason, action, symptoms, recommendation}
        hoặc None nếu parse thất bại
    """
    try:
        # Thử parse JSON trực tiếp
        data = json.loads(response_text)

        # Validate fields
        required_fields = ["level", "confidence", "reason", "action"]
        if all(field in data for field in required_fields):
            # Normalize level
            data["level"] = data["level"].upper()
            if data["level"] not in ["RED", "YELLOW", "GREEN"]:
                data["level"] = "YELLOW"  # Default to YELLOW nếu invalid

            # Ensure confidence is float between 0-1
            data["confidence"] = float(data.get("confidence", 0.5))
            data["confidence"] = max(0, min(1, data["confidence"]))

            # Ensure symptoms is list
            if "symptoms" not in data or not isinstance(data["symptoms"], list):
                data["symptoms"] = []

            # Ensure recommendation is string
            if "recommendation" not in data:
                data["recommendation"] = ""

            return data
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    # Fallback: Thử tìm JSON trong response text
    try:
        start = response_text.index("{")
        end = response_text.rindex("}") + 1
        json_str = response_text[start:end]
        return _parse_triage_response(json_str)  # Recursive call
    except (ValueError, IndexError):
        pass

    # Parse thất bại - return None
    return None


def classify_symptoms(user_message: str, api_key: Optional[str] = None) -> Dict:
    """
    Gọi OpenAI API để phân loại triệu chứng.

    Tham số:
        user_message: Tin nhắn của bệnh nhân (ví dụ: "Tôi đau ngực")
        api_key: OpenAI API key (nếu None, sẽ lấy từ env)

    Trả về:
        dict: {
            "level": "RED|YELLOW|GREEN",
            "confidence": 0.0-1.0,
            "reason": "...",
            "action": "...",
            "symptoms": [...],
            "recommendation": "...",
            "error": None hoặc str nếu có lỗi
        }
    """

    if not OPENAI_AVAILABLE:
        return {
            "level": "YELLOW",
            "confidence": 0,
            "reason": "OpenAI API không khả dụng",
            "action": "Vui lòng liên hệ bác sĩ",
            "symptoms": [],
            "recommendation": "Không thể kết nối tới AI. Vui lòng chắc chắn LangChain OpenAI được cài đặt.",
            "error": "OpenAI not available",
        }

    # Lấy API key
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY", "")

    if not api_key or api_key.startswith("sk-proj-XXXX"):
        return {
            "level": "YELLOW",
            "confidence": 0,
            "reason": "API key không được cấu hình",
            "action": "Vui lòng thiết lập OPENAI_API_KEY",
            "symptoms": [],
            "recommendation": "API key chưa được cấu hình. Vui lòng thiết lập trong .env file.",
            "error": "No API key configured",
        }

    try:
        # Khởi tạo LLM
        llm = ChatOpenAI(
            openai_api_base="https://models.inference.ai.azure.com/",  # GitHub Copilot base URL
            model="gpt-4o-mini",
            temperature=0.2,  # Thấp để tăng consistency
            api_key=api_key,
            max_retries=2,
        )

        # Gửi request
        messages = [
            SystemMessage(content=TRIAGE_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = llm.invoke(messages)
        response_text = response.content

        print(f"[Triage] AI Response: {response_text[:150]}...")

        # Parse response
        parsed = _parse_triage_response(response_text)

        if parsed is None:
            print(f"[Triage] [!] Không thể parse response: {response_text}")
            return {
                "level": "YELLOW",
                "confidence": 0,
                "reason": "Không thể phân tích phản hồi từ AI",
                "action": "Hỏi thêm chi tiết",
                "symptoms": [],
                "recommendation": "Vui lòng mô tả triệu chứng chi tiết hơn",
                "error": "Parse error",
            }

        parsed["error"] = None
        return parsed

    except Exception as e:
        print(f"[Triage] [X] Lỗi khi gọi OpenAI: {str(e)}")
        return {
            "level": "YELLOW",
            "confidence": 0,
            "reason": f"Lỗi gọi API: {str(e)}",
            "action": "Vui lòng thử lại",
            "symptoms": [],
            "recommendation": "Hệ thống bị lỗi tạm thời. Vui lòng thử lại sau.",
            "error": str(e),
        }


# ===== Helper functions =====


def get_response_text(triage_result: Dict) -> str:
    """
    Tạo text phản hồi từ triage result để hiển thị cho user.

    Tham số:
        triage_result: Dict trả về từ classify_symptoms()

    Trả về:
        str: Text phản hồi (sử dụng reason + recommendation)
    """
    if triage_result.get("error"):
        return (
            f"Xin lỗi, có lỗi khi xử lý: {triage_result.get('reason')}\n\n"
            f"{triage_result.get('recommendation')}"
        )

    text = triage_result.get("reason", "")

    if triage_result.get("recommendation"):
        text += f"\n\n{triage_result.get('recommendation')}"

    return text


# ===== Test function =====


def test_classify_symptoms():
    """Function test cho CLI."""
    test_cases = [
        "Tôi khó thở và đau ngực",
        "Tôi mệt mỏi và đau đầu",
        "Tôi cảm thấy bình thường, không có vấn đề gì",
    ]

    for test_input in test_cases:
        print(f"\n{'=' * 60}")
        print(f"Input: {test_input}")
        print(f"{'=' * 60}")

        result = classify_symptoms(test_input)

        print(f"Level: {result['level']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Reason: {result['reason']}")
        print(f"Action: {result['action']}")
        print(f"Symptoms: {result['symptoms']}")
        print(f"Recommendation: {result['recommendation']}")

        if result.get("error"):
            print(f"Error: {result['error']}")


if __name__ == "__main__":
    print("[Triage] Starting test...")
    test_classify_symptoms()
