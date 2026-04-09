import os
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools import tools_list

load_dotenv()

with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools_list)

def agent_node(state: AgentState):
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools_list))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "patient_123"}}
    print("\n--- MediCare Trực Tuyến ---")
    print("MediCare: Chào anh/chị, hôm nay sức khỏe mình thế nào ạ? Có triệu chứng gì bất thường không?")

    while True:
        try:
            user_input = input("\nBạn: ").strip()
            if user_input.lower() in ["exit", "quit"]: break
            if not user_input: continue

            # Lấy trạng thái cuối cùng sau khi tất cả các Node (Agent & Tools) chạy xong
            result = graph.invoke({"messages": [HumanMessage(content=user_input)]}, config)
            
            # Chỉ lấy tin nhắn cuối cùng trong danh sách (là câu trả lời đã tổng hợp của AI)
            final_response = result["messages"][-1].content
            
            if final_response:
                print(f"\nMediCare: {final_response}")
            else:
                # Trường hợp hiếm khi AI chỉ gọi tool mà chưa phản hồi chữ, bắt nó phản hồi
                print("\nMediCare: Đang xử lý thông tin...")

        except KeyboardInterrupt:
            print("\nĐã dừng chương trình.")
            break