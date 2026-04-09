"""
==============================================================================
 Chatbot Logger - Ghi logs phiên chat y tế
==============================================================================
 File: ai_core/chatbot_logger.py

 Mỗi phiên chat tạo 1 cặp file:
   - session_chatbot_YYYY-MM-DDTHH-MM-SS.jsonl   (events realtime)
   - session_chatbot_YYYY-MM-DDTHH-MM-SS.json    (tổng kết phiên)
==============================================================================
"""

import json
import os
import time
import uuid
from datetime import datetime


_LOGS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "logs"
)
os.makedirs(_LOGS_DIR, exist_ok=True)


class ChatSessionLogger:
    """
    Ghi logs phiên chat chatbot y tế.
    Mỗi phiên = 1 cặp file JSONL (realtime) + JSON (tổng kết).
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.session_id = f"chat_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
        self.model = model
        self.start_time = int(time.time() * 1000)
        self.events: list[dict] = []
        self.total_tokens = 0
        self.total_tool_calls = 0
        self.total_queries = 0

        ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        self.jsonl_path = os.path.join(_LOGS_DIR, f"session_chatbot_{ts}.jsonl")
        self.json_path = os.path.join(_LOGS_DIR, f"session_chatbot_{ts}.json")

        self._log_event("SESSION_START", {
            "session_id": self.session_id,
            "model": self.model,
        })

    def _now_iso(self) -> str:
        return (
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S.")
            + f"{datetime.now().microsecond // 1000:03d}Z"
        )

    def _log_event(self, event: str, data: dict) -> None:
        entry = {
            "timestamp": self._now_iso(),
            "event": event,
            "data": data,
        }
        self.events.append(entry)
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_user_message(self, message: str) -> float:
        """Ghi event khi user gửi tin nhắn. Trả về start_time để tính latency."""
        self.total_queries += 1
        self._log_event("USER_MESSAGE", {
            "session_id": self.session_id,
            "message": message[:300],  # cắt 300 ký tự
        })
        return time.time()

    def log_tool_call(self, tool_name: str, tool_args: dict, step: int) -> None:
        """Ghi event khi agent gọi tool."""
        self.total_tool_calls += 1
        self._log_event("TOOL_CALL", {
            "step": step,
            "tool_name": tool_name,
            "tool_args": tool_args,
        })

    def log_llm_metric(self, response, step: int) -> None:
        """Ghi LLM metrics (tokens) từ response."""
        usage = {}
        if hasattr(response, "response_metadata"):
            usage = response.response_metadata.get("usage", {})
        elif hasattr(response, "usage"):
            usage = response.usage

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
        self.total_tokens += total_tokens

        self._log_event("LLM_METRIC", {
            "step": step,
            "model": self.model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "tool_calls_count": len(response.tool_calls) if response.tool_calls else 0,
        })

    def log_ai_response(self, answer: str, start_time: float, step: int) -> None:
        """Ghi event khi agent trả lời xong."""
        latency_ms = int((time.time() - start_time) * 1000)
        self._log_event("AI_RESPONSE", {
            "step": step,
            "answer_preview": answer[:300] if answer else "",
            "latency_ms": latency_ms,
            "answer_length": len(answer),
        })

    def log_session_end(self) -> None:
        """Ghi tổng kết phiên ra file JSON."""
        total_duration_ms = int(time.time() * 1000) - self.start_time
        self._log_event("SESSION_END", {
            "total_duration_ms": total_duration_ms,
            "total_queries": self.total_queries,
            "total_tokens": self.total_tokens,
            "total_tool_calls": self.total_tool_calls,
        })

        summary = {
            "session_id": self.session_id,
            "label": "chatbot",
            "model": self.model,
            "start_time": self.start_time,
            "total_duration_ms": total_duration_ms,
            "total_queries": self.total_queries,
            "total_tokens": self.total_tokens,
            "total_tool_calls": self.total_tool_calls,
            "events": self.events,
        }
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"[ChatLogger] Logs lưu: {self.jsonl_path}")