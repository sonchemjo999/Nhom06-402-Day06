"""
=============================================================================
 AI Core - Agent đọc đơn thuốc (LangGraph)
=============================================================================
 File: ai_core/agent.py
 Mô tả: Agent AI sử dụng kiến trúc LangGraph để đọc và phân tích đơn thuốc.
         Kiến trúc tham khảo từ lab buổi 4 (TravelBuddy), đã chuyển đổi
         sang Medical domain.

 Kiến trúc:
   [User Input] → [Agent Node] → [Tool: extract_prescription] → [Agent Node] → [JSON Result]

 Fallback: Nếu không có API key hoặc gặp lỗi, tự động fallback về mock data.
=============================================================================
"""

import os
import sys
import json
from typing import Annotated
from typing_extensions import TypedDict

# Thêm project root vào path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data.mock_data import MOCK_RESULT_SUCCESS, MOCK_RESULT_FAILURE
from ai_core.tools import extract_prescription, get_mock_prescription

# Flag kiểm tra có đủ dependencies không
LANGGRAPH_AVAILABLE = False
try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.graph.message import add_messages
    from langgraph.prebuilt import ToolNode, tools_condition
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
    from dotenv import load_dotenv

    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    LANGGRAPH_AVAILABLE = True
except ImportError:
    print("[AI Core] [!] LangGraph/LangChain chua cai dat. Se dung mock data.")


# ===== Đọc System Prompt =====
SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


# ===== State cho LangGraph =====
class AgentState(TypedDict):
    messages: Annotated[list, add_messages] if LANGGRAPH_AVAILABLE else list


def _build_graph():
    """
    Xây dựng LangGraph agent cho đọc đơn thuốc.
    Trả về compiled graph hoặc None nếu thiếu dependencies.
    """
    if not LANGGRAPH_AVAILABLE:
        return None

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("sk-proj-XXXX"):
        print("[AI Core] ⚠️ OPENAI_API_KEY chưa được cấu hình. Sẽ dùng mock data.")
        return None

    try:
        # Khởi tạo LLM và Tools
        tools_list = [extract_prescription]
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        llm_with_tools = llm.bind_tools(tools_list)

        def agent_node(state: AgentState) -> dict:
            """Node agent: gọi LLM để phân tích đơn thuốc."""
            messages = state["messages"]
            if not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}

        # Xây dựng graph
        builder = StateGraph(AgentState)
        builder.add_node("agent", agent_node)
        builder.add_node("tools", ToolNode(tools_list))
        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", tools_condition)
        builder.add_edge("tools", "agent")

        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)
        print("[AI Core] [OK] LangGraph agent da san sang!")
        return graph

    except Exception as e:
        print(f"[AI Core] [X] Loi khoi tao LangGraph: {e}")
        return None


# Khởi tạo graph (lazy - chỉ build khi cần)
_graph = None
_graph_initialized = False


def _get_graph():
    """Lazy initialization cho graph."""
    global _graph, _graph_initialized
    if not _graph_initialized:
        _graph = _build_graph()
        _graph_initialized = True
    return _graph


def _parse_ai_response(response_text: str) -> dict:
    """
    Parse response text từ AI thành dict chuẩn cho app.

    Tham số:
        response_text: Text trả về từ LLM (expected JSON)

    Trả về:
        dict với format: {status, confidence, message, medications}
    """
    try:
        # Thử parse JSON trực tiếp
        data = json.loads(response_text)
        return data
    except json.JSONDecodeError:
        # Thử tìm JSON trong response text
        try:
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            json_str = response_text[start:end]
            data = json.loads(json_str)
            return data
        except (ValueError, json.JSONDecodeError):
            # Không parse được → coi như failure
            return {
                "status": "failure",
                "confidence": 0.0,
                "message": "Không thể phân tích kết quả từ AI.",
                "medications": []
            }


def scan_prescription(case: str = "random") -> dict:
    """
    Hàm chính: Quét đơn thuốc bằng AI agent.
    
    Tham số:
        case: "clear" = đơn rõ, "blurry" = đơn mờ, "random" = ngẫu nhiên
    
    Trả về:
        dict: {status, confidence, message, medications}
    
    Fallback: Nếu AI agent không khả dụng, sử dụng mock data.
    """
    graph = _get_graph()

    if graph is None:
        # === FALLBACK: Dùng mock data ===
        print("[AI Core] [Mock] Su dung mock data (AI agent khong kha dung)")
        import random as rnd
        if case == "clear":
            return MOCK_RESULT_SUCCESS.copy()
        elif case == "blurry":
            return MOCK_RESULT_FAILURE.copy()
        else:
            return rnd.choice([MOCK_RESULT_SUCCESS, MOCK_RESULT_FAILURE]).copy()

    # === REAL AI: Dùng LangGraph agent ===
    try:
        # Lấy đơn thuốc mock để gửi cho AI
        prescription_text = get_mock_prescription(case)
        user_message = (
            f"Hãy đọc và phân tích đơn thuốc sau. "
            f"Trả kết quả dưới dạng JSON thuần (không markdown).\n\n"
            f"NỘI DUNG ĐƠN THUỐC:\n{prescription_text}"
        )

        import time
        config = {"configurable": {"thread_id": f"scan_{int(time.time())}"}}
        result = graph.invoke(
            {"messages": [("human", user_message)]},
            config=config
        )

        # Lấy response cuối cùng từ agent
        final_message = result["messages"][-1]
        response_text = final_message.content
        print(f"[AI Core] [Bot] AI response: {response_text[:200]}...")

        # Parse response thành dict
        parsed = _parse_ai_response(response_text)
        return parsed

    except Exception as e:
        print(f"[AI Core] [X] Loi khi goi AI: {e}")
        # Fallback về mock khi gặp lỗi
        import random as rnd
        return rnd.choice([MOCK_RESULT_SUCCESS, MOCK_RESULT_FAILURE]).copy()
