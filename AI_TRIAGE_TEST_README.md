# 🏥 AI Medical Triage CLI Test Guide

## Giới thiệu

Script này cho phép bạn test phân loại triệu chứng y tế bằng OpenAI API trực tiếp từ CLI, **trước khi tích hợp vào UI**.

Điều này giúp:
- ✅ Kiểm tra kết nối API
- ✅ Xác minh JSON response format
- ✅ Test các triệu chứng khác nhau
- ✅ Debug vấn đề trước khi chạy app

## Chuẩn bị

### 1. Cài đặt dependencies

```bash
pip install langchain-openai langchain-core
```

### 2. Cấu hình API key

Thêm vào `.env` file:

```env
OPENAI_API_KEY=your_github_copilot_api_key
```

## Chạy Test

### Mode 1: Interactive (Menu)

```bash
python test_triage_cli.py
```

Menu options:
```
1. Test các case được định trước
2. Test tương tác (nhập triệu chứng)
3. Thoát
```

### Mode 2: Single Input Test

Test với input cụ thể:

```bash
python test_triage_cli.py "Tôi khó thở"
```

Output:
```
======================================================================
  TEST SINGLE INPUT: Tôi khó thở
======================================================================

📊 PHÂN LOẠI KẾT QUẢ:

  Level (Mức độ):      RED
  Confidence (Độ tin):  95.0%
  Reason (Lý do):       Bệnh nhân mô tả khó thở - triệu chứng cấp cứu nghiêm trọng.
  Action (Hành động):   Gọi 115 hoặc đến bệnh viện ngay lập tức
  Symptoms (Triệu chứng): khó thở

💬 Khuyến nghị:
  Bạn cần được hỗ trợ y tế NGAY LẬP TỨC. Vui lòng gọi 115 hoặc tới bệnh viện gần nhất

📋 Raw JSON Response:
{
  "level": "RED",
  "confidence": 0.95,
  "reason": "Bệnh nhân mô tả khó thở - triệu chứng cấp cứu nghiêm trọng.",
  "action": "Gọi 115 hoặc đến bệnh viện ngay lập tức",
  "symptoms": ["khó thở"],
  "recommendation": "Bạn cần được hỗ trợ y tế NGAY LẬP TỨC...",
  "error": null
}
```

## Test Cases (Được định trước)

| Input | Expected Level | Status |
|-------|---|---|
| "Tôi khó thở và đau ngực" | RED | ✅ |
| "Tôi mệt mỏi và đau đầu" | YELLOW | ✅ |
| "Tôi cảm thấy bình thường, không có vấn đề gì" | GREEN | ✅ |
| "Tôi sốt 40 độ" | RED | ✅ |
| "Tôi chóng mặt và buồn nôn" | YELLOW | ✅ |
| "Tôi co giật" | RED | ✅ |

## Response Format

Mỗi response trả về JSON với cấu trúc:

```json
{
  "level": "RED|YELLOW|GREEN",
  "confidence": 0.0-1.0,
  "reason": "Giải thích ngắn gọn",
  "action": "Hành động gợi ý",
  "symptoms": ["triệu chứng 1", "triệu chứng 2"],
  "recommendation": "Khuyến nghị cho bệnh nhân",
  "error": null
}
```

### Field Descriptions

- **level**: Mức độ cấp cứu
  - `RED`: Cấp cứu ngay (gọi 115)
  - `YELLOW`: Cần theo dõi (hỏi thêm)
  - `GREEN`: Bình thường (tiếp tục theo dõi)

- **confidence**: Độ tin cậy (0-1)
  - 0.7+: Đủ tin cậy
  - <0.7: Cần xác nhận thêm

- **symptoms**: Array các triệu chứng được nhận diện

- **recommendation**: Khuyến nghị cho bệnh nhân

- **error**: Thông báo lỗi (null nếu thành công)

## Troubleshooting

### "OpenAI API not available"

```bash
pip install langchain-openai
```

### "OPENAI_API_KEY không được cấu hình"

1. Tạo file `.env` nếu chưa có
2. Thêm: `OPENAI_API_KEY=your_key_here`
3. Thử lại

### API Timeout

- Response từ API có thể mất 5-10 giây
- Đợi lần đầu (khởi tạo connection)
- Retry nếu vẫn timeout

### JSON Parse Error

- Kiểm tra system prompt trong `ai_core/triage_prompt.txt`
- Đảm bảo API trả về JSON hợp lệ
- Check console output cho `[Triage]` logs

## Integration vào UI

Khi CLI test thành công, bạn có thể:

1. **Chạy app Kivy:**
   ```bash
   python main.py
   ```

2. **Navigate tới Chatbot screen**

3. **Test phân loại triệu chứng:**
   - Nhập triệu chứng
   - Chờ AI phân loại
   - Xem response

## Logs

Console output sẽ hiển thị:

```
[Triage] AI Response: {...}  # Raw response từ API
[Triage] [!] Không thể parse response  # Nếu có lỗi
[Triage] [X] Lỗi khi gọi OpenAI: ...  # API error
```

## Files Related

- **ai_core/triage.py** - Module chính gọi API
- **ai_core/triage_prompt.txt** - System prompt cho AI
- **test_triage_cli.py** - Script test này
- **screens/chatbot_screen.py** - UI sử dụng triage module

## Tham khảo

- [Triage Levels](../ai_core/triage_prompt.txt)
- [Triage Module](../ai_core/triage.py)
- [Chatbot Screen](../screens/chatbot_screen.py)
