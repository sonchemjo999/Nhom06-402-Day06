#!/usr/bin/env python3
"""
=============================================================================
 CLI Test Script - Kiểm tra AI Triage
=============================================================================
 File: test_triage_cli.py
 Mô tả: Script để test phân loại triệu chứng bằng OpenAI API trực tiếp
        từ CLI trước khi tích hợp vào UI.

 Usage:
   python test_triage_cli.py

   Hoặc nhập triệu chứng cụ thể:
   python test_triage_cli.py "tôi khó thở"
=============================================================================
"""

import os
import sys
import json

# Thêm project root vào path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ai_core.triage import classify_symptoms, OPENAI_AVAILABLE
from dotenv import load_dotenv

load_dotenv()


def print_separator(title: str = ""):
    """In dòng phân cách đẹp."""
    if title:
        print(f"\n{'=' * 70}")
        print(f"  {title}")
        print(f"{'=' * 70}\n")
    else:
        print(f"{'=' * 70}\n")


def format_result(result: dict) -> None:
    """Format và in kết quả từ AI."""
    print(f"📊 PHÂN LOẠI KẾT QUẢ:\n")
    print(f"  Level (Mức độ):      {result['level']}")
    print(f"  Confidence (Độ tin):  {result['confidence'] * 100:.1f}%")
    print(f"  Reason (Lý do):       {result['reason']}")
    print(f"  Action (Hành động):   {result['action']}")
    print(
        f"  Symptoms (Triệu chứng): {', '.join(result['symptoms']) if result['symptoms'] else 'Không xác định'}"
    )
    print(f"\n💬 Khuyến nghị:\n  {result['recommendation']}")

    if result.get("error"):
        print(f"\n⚠️  Lỗi: {result['error']}")

    print(
        f"\n📋 Raw JSON Response:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
    )


def test_predefined_cases() -> None:
    """Test các case được định trước."""
    test_cases = [
        {
            "input": "Tôi khó thở và đau ngực",
            "expected": "RED",
            "description": "Triệu chứng cấp cứu",
        },
        {
            "input": "Tôi mệt mỏi và đau đầu",
            "expected": "YELLOW",
            "description": "Triệu chứng cần theo dõi",
        },
        {
            "input": "Tôi cảm thấy bình thường, không có vấn đề gì",
            "expected": "GREEN",
            "description": "Trạng thái bình thường",
        },
        {"input": "Tôi sốt 40 độ", "expected": "RED", "description": "Sốt cao"},
        {
            "input": "Tôi chóng mặt và buồn nôn",
            "expected": "YELLOW",
            "description": "Triệu chứng trung bình",
        },
        {"input": "Tôi co giật", "expected": "RED", "description": "Co giật - cấp cứu"},
    ]

    print_separator("TEST CÁC CASE ĐỀ XUẤT")

    passed = 0
    failed = 0

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test_case['description']}")
        print(f'Input: "{test_case["input"]}"')
        print(f"Expected: {test_case['expected']}")
        print("-" * 70)

        result = classify_symptoms(test_case["input"])

        print(f"Result: {result['level']}")
        print(f"Confidence: {result['confidence'] * 100:.1f}%")
        print(f"Reason: {result['reason']}")

        if result["level"] == test_case["expected"]:
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
            failed += 1

    print_separator()
    print(f"📈 TỔNG KẾT: {passed} passed, {failed} failed")
    print(f"Success rate: {passed / (passed + failed) * 100:.1f}%\n")


def interactive_test() -> None:
    """Test tương tác - nhập triệu chứng và xem kết quả."""
    print_separator("CHẾ ĐỘ INTERACTIVE - NHẬP TRIỆU CHỨNG CỦA BẠN")
    print("Ghi chú: Nhập 'exit' để thoát, 'test' để chạy các case test\n")

    while True:
        user_input = input("Nhập triệu chứng (hoặc lệnh): ").strip()

        if user_input.lower() == "exit":
            print("👋 Thoát...")
            break
        elif user_input.lower() == "test":
            test_predefined_cases()
            continue
        elif not user_input:
            print("⚠️  Vui lòng nhập triệu chứng!")
            continue

        print_separator(f"Xử lý: {user_input}")

        result = classify_symptoms(user_input)
        format_result(result)


def main():
    """Hàm main."""
    print("\n")
    print("🏥 " + "=" * 66)
    print("   AI MEDICAL TRIAGE SYSTEM - CLI TEST")
    print("=" * 66 + " 🏥\n")

    # Kiểm tra OpenAI availability
    if not OPENAI_AVAILABLE:
        print("❌ OPENAI_AVAILABLE is False")
        print("   LangChain OpenAI module chưa được cài đặt.")
        print("   Vui lòng cài đặt: pip install langchain-openai")
        print("")
        return

    # Kiểm tra API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-proj-XXXX"):
        print("⚠️  OPENAI_API_KEY không được cấu hình hoặc có giá trị placeholder")
        print("   Vui lòng thêm API key vào .env file:")
        print("   OPENAI_API_KEY=your_api_key_here")
        print("")
        return

    print("✅ OpenAI API: Sẵn sàng")
    print(f"✅ API Key: Được cấu hình ({api_key[:10]}...)")
    print("")

    # Menú chính
    while True:
        print_separator("MENU CHÍNH")
        print("1. Test các case được định trước")
        print("2. Test tương tác (nhập triệu chứng)")
        print("3. Thoát")
        print("")

        choice = input("Chọn (1-3): ").strip()

        if choice == "1":
            test_predefined_cases()
        elif choice == "2":
            interactive_test()
        elif choice == "3":
            print("👋 Tạm biệt!\n")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Nếu có argument, test với input đó
        test_input = " ".join(sys.argv[1:])
        print_separator(f"TEST SINGLE INPUT: {test_input}")

        if not OPENAI_AVAILABLE:
            print("❌ OpenAI API not available")
            sys.exit(1)

        result = classify_symptoms(test_input)
        format_result(result)
    else:
        # Chạy menu tương tác
        main()
