"""
==============================================================================
 Chatbot Agent - LangGraph Agent y tế cho MedReminder
==============================================================================
 File: ai_core/chatbot_agent.py

 Kiến trúc LangGraph:
   START → agent → [tools_condition] → tools → agent → ... → END
                         ↓ (no tool calls)
                        END

 MemorySaver: nhớ toàn bộ lịch sử hội thoại trong phiên.

 Import:
   from ai_core.chatbot_agent import chatbot_reply_sync
   result = chatbot_reply_sync(user_message, session_id)
==============================================================================
"""

import os
import sys
from typing import Annotated, Literal

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Thêm thư mục cha vào sys.path để import được các module cùng cấp
_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

# Đọc system prompt
_ai_core_dir = os.path.dirname(os.path.abspath(__file__))
_SYSTEM_PROMPT_PATH = os.path.join(_ai_core_dir, "chatbot_system_prompt.txt")

try:
    with open(_SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except Exception:
    SYSTEM_PROMPT = (
        "Bạn là trợ lý y tế của MedReminder. "
        "Trả lời tiếng Việt, giọng thân thiện, tư vấn về thuốc và triệu chứng. "
        "Ưu tiên an toàn: không chẩn đoán, không thay thế lời khuyên bác sĩ."
    )


# ============================================================================
# TRẠNG THÁI
# ============================================================================

class AgentState(dict):
    """State cho LangGraph chatbot agent."""
    messages: Annotated[list, add_messages]


# ============================================================================
# TOOLS — sử dụng chatbot_tools.py của App5 (5 tools phong phú)
# ============================================================================

def _get_tools():
    """Lazy load tools để tránh circular import."""
    from ai_core.chatbot_tools import get_tool_list
    return get_tool_list()

# ============================================================================
# LANGGRAPH GRAPH — kiểu D6/buoi6
# ============================================================================

_graph = None
_memory = None
_llm = None
_llm_with_tools = None


def _build_graph():
    """Xây dựng và compile LangGraph (lazy, chỉ 1 lần)."""
    global _graph, _memory, _llm, _llm_with_tools

    if _graph is not None:
        return _graph

    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(_app_dir, "config", ".env"))

        tools_list = _get_tools()
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        _llm_with_tools = _llm.bind_tools(tools_list)

        def agent_node(state: AgentState) -> dict:
            messages = state["messages"]
            # Đảm bảo system prompt ở đầu
            if not any(isinstance(m, SystemMessage) for m in messages):
                messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
            response = _llm_with_tools.invoke(messages)

            # Log tool calls
            if response.tool_calls:
                for tc in response.tool_calls:
                    print(f"  🔧 Tool: {tc['name']}({tc['args']})")
            else:
                print(f"  💬 Trả lời trực tiếp")

            return {"messages": [response]}

        # Xây dựng graph — kiểu D6/buoi6
        builder = StateGraph(AgentState)
        builder.add_node("agent", agent_node)
        builder.add_node("tools", ToolNode(tools_list))
        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", tools_condition)
        builder.add_edge("tools", "agent")

        _memory = MemorySaver()
        _graph = builder.compile(checkpointer=_memory)

        print(f"[ChatbotAgent] ✅ LangGraph loaded — gpt-4o-mini + {len(tools_list)} tools")
        return _graph

    except ImportError as e:
        print(f"[ChatbotAgent] ⚠️ Thiếu thư viện: {e}")
        _graph = None
        return None
    except Exception as e:
        print(f"[ChatbotAgent] ⚠️ Lỗi khởi tạo: {e}")
        _graph = None
        return None


def _get_graph():
    """Lấy graph, fallback về mock nếu không có thư viện."""
    g = _build_graph()
    if g is None:
        print("[ChatbotAgent] ⚠️ Fallback: dùng mock response")
    return g


# ============================================================================
# FALLBACK — Khi không có API key / thư viện
# ============================================================================

def _mock_reply(user_message: str) -> str:
    """
    Fallback khi không gọi được LangGraph:
    - Phân loại triệu chứng bằng keyword (giống code cũ)
    - Gọi tool mock tương ứng
    """
    from ai_core.chatbot_tools import get_symptom_advice, search_hospital

    import unicodedata
    def nodia(s):
        nd = unicodedata.normalize("NFD", s.lower())
        return "".join(c for c in nd if not unicodedata.combining(c))

    text_nd = nodia(user_message)

    # Check RED first
    red_kw = [
        "kho tho", "sot cao", "dau nguc", "bat tinh", "ngat",
        "xuat huyet", "co giat",
    ]
    for kw in red_kw:
        if kw in text_nd:
            return (
                "🚨 **CẢNH BÁO NGUY HIỂM!**\n\n"
                "Triệu chứng bạn mô tả có thể nghiêm trọng!\n"
                "Hành động NGAY:\n"
                "1. Gọi 115 — cấp cứu ngay!\n"
                "2. Không tự ý uống thêm thuốc.\n"
                "3. Nếu có người nhà → nhờ hỗ trợ.\n\n"
                "⚠️ Hãy gặp bác sĩ ngay!\n\n"
                f"{search_hospital.invoke({'location': ''})}"
            )

    # Check YELLOW
    yellow_kw = [
        "met", "dau dau", "buon non", "chong mat", "xay xam",
        "mat ngu", "phat ban", "dau bung", "tieu chay",
    ]
    for kw in yellow_kw:
        if kw in text_nd:
            return (
                "⚠️ **CẦN THEO DÕI** — Triệu chứng của bạn cần chú ý.\n\n"
                "Bạn có thể đánh giá mức độ từ 1 đến 10 không?\n"
                "  • 1-3: Nhẹ, theo dõi tại nhà\n"
                "  • 4-6: Trung bình, nên liên hệ bác sĩ\n"
                "  • 7-10: Nặng, cần khám ngay\n\n"
                "💡 Nếu tình trạng nặng hơn → đến bệnh viện ngay nha!"
            )

    # Check GREEN
    green_kw = [
        "tot", "khoe", "on", "binh thuong",
        "duoc", "giam",
    ]
    for kw in green_kw:
        if kw in text_nd:
            return (
                "✅ **TÌNH TRẠNG ỔN ĐỊNH**\n\n"
                "Tuyệt vời! Rất vui khi bạn cảm thấy tốt hơn.\n\n"
                "Nhớ duy trì:\n"
                "  • Uống thuốc đúng giờ như bác sĩ chỉ định\n"
                "  • Ăn uống đầy đủ, nghỉ ngơi hợp lý\n"
                "  • Tái khám đúng lịch\n\n"
                "Nếu có thay đổi gì → báo ngay cho em nha!"
            )

    # Drug question
    drug_kw_nd = ["lieu", "uong", "thuoc"]
    has_drug = any(kw in text_nd for kw in drug_kw_nd)
    if has_drug:
        drug_names = [d for d in ["paracetamol", "ibuprofen", "amoxicillin",
                                   "metformin", "aspirin", "omeprazole", "loratadine", "vitamin_c"]
                      if d in text_nd]
        if drug_names:
            from ai_core.chatbot_tools import get_dosage_info
            return get_dosage_info.invoke({"drug_name": drug_names[0]})

    # Không nhận diện được
    return (
        "📋 Em chưa rõ lắm. Bạn có thể mô tả chi tiết hơn không?\n\n"
        "Ví dụ: đau ở đâu? mức độ ntn? kéo dài bao lâu?\n"
        "Em sẽ hỗ trợ tốt nhất có thể nha!"
    )


# ============================================================================
# ENTRY POINT — GỌI TỪ chatbot_screen.py
# ============================================================================

def chatbot_reply_sync(user_message: str, session_id: str = "default") -> str:
    """
    Gọi chatbot agent (sync version).
    Trả về: str — nội dung phản hồi của AI.

    Từ chatbot_screen.py:
        from ai_core.chatbot_agent import chatbot_reply_sync
        reply = chatbot_reply_sync(text, session_id="user_123")
    """
    graph = _get_graph()

    if graph is None:
        print(f"[ChatbotAgent] Fallback: keyword matching")
        return _mock_reply(user_message)

    # Check API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(f"[ChatbotAgent] ⚠️ Không có OPENAI_API_KEY → fallback")
        return _mock_reply(user_message)

    config = {"configurable": {"thread_id": session_id}}

    try:
        result = graph.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config,
        )
        final = result["messages"][-1]

        # Lấy nội dung phản hồi
        if hasattr(final, "content"):
            reply = final.content
        elif isinstance(final, dict):
            reply = final.get("content", str(final))
        else:
            reply = str(final)

        # Check xem có cảnh báo nguy hiểm không → trả kèm level
        text_lower = reply.lower()
        if any(kw in text_lower for kw in ["cảnh báo", "nguy hiểm", "🚨", "115", "cấp cứu"]):
            return reply  # chatbot_screen.py sẽ tự detect cờ

        return reply

    except Exception as e:
        print(f"[ChatbotAgent] ❌ Lỗi: {e}")
        return (
            "Xin lỗi bạn, đã có lỗi xảy ra. "
            "Em sẽ trả lời lại ngay khi hệ thống ổn định nha!\n\n"
            "Trong lúc chờ, bạn có thể gọi 115 nếu cần cấp cứu."
        )


# ============================================================================
# DÀNH CHO KIVY — chạy trong thread riêng để không block UI
# ============================================================================

def run_chatbot(user_message: str, session_id: str = "default",
                callback=None, error_callback=None):
    """
    Chạy chatbot trong thread riêng, gọi callback khi có kết quả.
    Dùng với Kivy Clock / threading.

    Usage:
        def on_result(result):
            print("AI trả lời:", result)

        run_chatbot("Tôi bị đau đầu", session_id="u1",
                    callback=on_result)
    """
    from kivy.clock import Clock

    def _execute():
        try:
            result = chatbot_reply_sync(user_message, session_id)
            if callback:
                Clock.schedule_once(lambda dt: callback(result), 0)
        except Exception as e:
            print(f"[ChatbotAgent] ❌ Thread error: {e}")
            if error_callback:
                Clock.schedule_once(lambda dt: error_callback(str(e)), 0)

    import threading
    t = threading.Thread(target=_execute, daemon=True)
    t.start()


# ============================================================================
# AUTO-GREETING — Lời chào khi mở chatbot
# ============================================================================

GREETING = (
    "Xin chào!  Em là trợ lý y tế của MedReminder nè!\n\n"
    "Hôm nay sức khỏe của anh/chị sau khi dùng thuốc thế nào rồi, có triệu chứng gì không?"
)
