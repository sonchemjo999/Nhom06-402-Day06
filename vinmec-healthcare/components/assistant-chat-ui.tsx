"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Role = "assistant" | "user";

type ChatMessage = {
  id: string;
  role: Role;
  content: string;
  time: string;
};

type SessionSummary = {
  id: string;
  title: string;
  preview: string;
  lastMessageAt: string;
};

type ToolEventPayload = {
  name: string;
  ok: boolean;
  message?: string;
  task?: {
    title?: string;
    dueTime?: string;
  };
};

const quickPrompts = [
  "Nhắc tôi uống thuốc lúc 20:00 tối nay",
  "Tôi bị chóng mặt nhẹ thì nên làm gì?",
  "Khi nào tôi cần đi cấp cứu ngay?",
  "Tóm tắt lịch uống thuốc trong ngày giúp tôi",
];

const LOCAL_USER_KEY = "id_user";
const WELCOME_CONTENT =
  "Chào bạn, mình là Vinmec AI Assistant. Mình hỗ trợ nhắc thuốc, theo dõi triệu chứng và gợi ý bước xử lý an toàn.";

function nowLabel() {
  return new Date().toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function toTimeLabel(isoDate: string) {
  const date = new Date(isoDate);
  if (Number.isNaN(date.getTime())) {
    return nowLabel();
  }

  return date.toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function toHistoryDateLabel(isoDate: string) {
  const date = new Date(isoDate);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toLocaleString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function createId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return String(Date.now()) + String(Math.random()).slice(2);
}

function createWelcomeMessage(): ChatMessage {
  return {
    id: "welcome",
    role: "assistant",
    content: WELCOME_CONTENT,
    time: nowLabel(),
  };
}

function renderAssistantContent(content: string) {
  const normalized = content.trim();

  return (
    <div className="markdown-body space-y-2.5 text-[15px] leading-7">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => <p className="mb-2 whitespace-pre-wrap last:mb-0">{children}</p>,
          ul: ({ children }) => <ul className="mb-2 list-disc space-y-1.5 pl-5 marker:text-emerald-700">{children}</ul>,
          ol: ({ children }) => <ol className="mb-2 list-decimal space-y-1.5 pl-5 marker:font-semibold">{children}</ol>,
          li: ({ children }) => <li className="leading-7">{children}</li>,
          h1: ({ children }) => <h1 className="mb-2 text-xl font-bold text-slate-900">{children}</h1>,
          h2: ({ children }) => <h2 className="mb-2 text-lg font-bold text-slate-900">{children}</h2>,
          h3: ({ children }) => <h3 className="mb-2 text-base font-semibold text-slate-900">{children}</h3>,
          h4: ({ children }) => <h4 className="mb-2 text-sm font-semibold text-slate-900">{children}</h4>,
          blockquote: ({ children }) => (
            <blockquote className="mb-2 border-l-4 border-emerald-300 bg-emerald-50/60 px-3 py-2 italic text-slate-700">
              {children}
            </blockquote>
          ),
          code: ({ children, className }) => {
            const lang = className?.replace("language-", "") || "";
            const text = String(children).replace(/\n$/, "");
            const isInline = !className;

            if (isInline) {
              return <code className="rounded bg-slate-100 px-1 py-0.5 text-[0.9em] text-slate-800">{text}</code>;
            }

            return (
              <pre className="mb-2 overflow-x-auto rounded-xl bg-slate-900 p-3 text-xs text-slate-100">
                {lang ? <div className="mb-2 text-[10px] uppercase tracking-[0.08em] text-slate-400">{lang}</div> : null}
                <code>{text}</code>
              </pre>
            );
          },
          table: ({ children }) => (
            <div className="mb-2 overflow-x-auto rounded-xl border border-slate-200">
              <table className="w-full border-collapse text-left text-sm">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-slate-100 text-slate-700">{children}</thead>,
          th: ({ children }) => <th className="border border-slate-200 px-2 py-1.5 font-semibold">{children}</th>,
          td: ({ children }) => <td className="border border-slate-200 px-2 py-1.5 align-top">{children}</td>,
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noreferrer noopener"
              className="font-medium text-emerald-700 underline decoration-emerald-300 underline-offset-2 hover:text-emerald-800"
            >
              {children}
            </a>
          ),
          hr: () => <hr className="my-3 border-slate-200" />,
        }}
      >
        {normalized}
      </ReactMarkdown>
    </div>
  );
}

export function AssistantChatUi() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);
  const [userId, setUserId] = useState("");
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const bottomAnchorRef = useRef<HTMLDivElement | null>(null);
  const toastTimeoutRef = useRef<number | null>(null);

  const canSend = useMemo(function () {
    return input.trim().length > 0 && !isTyping && !isLoadingConversation;
  }, [input, isTyping, isLoadingConversation]);

  const hasUserMessage = useMemo(
    () => messages.some((message) => message.role === "user"),
    [messages],
  );

  const forceScrollToBottom = () => {
    const container = scrollRef.current;
    if (!container) return;
    container.scrollTop = container.scrollHeight;
    bottomAnchorRef.current?.scrollIntoView({ block: "end" });
  };

  const showToast = (message: string) => {
    if (!message) return;
    setToastMessage(message);
    if (toastTimeoutRef.current) {
      window.clearTimeout(toastTimeoutRef.current);
    }
    toastTimeoutRef.current = window.setTimeout(() => {
      setToastMessage("");
      toastTimeoutRef.current = null;
    }, 3000);
  };

  const fetchSessions = async () => {
    if (!userId) return [] as SessionSummary[];

    const response = await fetch(`/api/chat/sessions?userId=${encodeURIComponent(userId)}`);
    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(payload?.message || "Không tải được lịch sử chat.");
    }

    return (payload?.sessions ?? []) as SessionSummary[];
  };

  const loadConversation = async (sessionId: string) => {
    if (!userId || !sessionId) return;

    setIsLoadingConversation(true);

    try {
      const response = await fetch(
        `/api/chat/sessions/${sessionId}?userId=${encodeURIComponent(userId)}`,
      );
      const payload = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(payload?.message || "Không tải được nội dung hội thoại.");
      }

      const nextMessages = ((payload?.messages ?? []) as Array<{
        id: string;
        role: Role;
        content: string;
        createdAt: string;
      }>).map((message) => ({
        id: message.id,
        role: message.role,
        content: message.content,
        time: toTimeLabel(message.createdAt),
      }));

      setActiveSessionId(sessionId);
      setMessages(nextMessages.length > 0 ? nextMessages : [createWelcomeMessage()]);
    } catch (error) {
      const fallback = error instanceof Error ? error.message : "Không tải được hội thoại.";
      setMessages([
        {
          id: createId(),
          role: "assistant",
          content: `Xin lỗi, hiện chưa thể tải hội thoại: ${fallback}`,
          time: nowLabel(),
        },
      ]);
    } finally {
      setIsLoadingConversation(false);
    }
  };

  const refreshSessionList = async () => {
    if (!userId) return;

    setIsLoadingSessions(true);

    try {
      const nextSessions = await fetchSessions();
      setSessions(nextSessions);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  useEffect(() => {
    setMessages([createWelcomeMessage()]);

    const existing = window.localStorage.getItem(LOCAL_USER_KEY);
    const nextUserId = existing || createId();
    if (!existing) {
      window.localStorage.setItem(LOCAL_USER_KEY, nextUserId);
    }
    setUserId(nextUserId);
  }, []);

  useEffect(() => {
    if (!userId) return;

    let cancelled = false;

    const boot = async () => {
      setIsLoadingSessions(true);

      try {
        const nextSessions = await fetchSessions();
        if (cancelled) return;

        setSessions(nextSessions);

        if (nextSessions.length > 0) {
          const recent = nextSessions[0];
          setActiveSessionId(recent.id);
          await loadConversation(recent.id);
        } else {
          setActiveSessionId(null);
          setMessages([createWelcomeMessage()]);
        }
      } catch {
        if (cancelled) return;
        setSessions([]);
        setActiveSessionId(null);
        setMessages([createWelcomeMessage()]);
      } finally {
        if (!cancelled) {
          setIsLoadingSessions(false);
        }
      }
    };

    void boot();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  useEffect(() => {
    const frameId = window.requestAnimationFrame(forceScrollToBottom);
    const timeoutId = window.setTimeout(forceScrollToBottom, 120);
    return () => {
      window.cancelAnimationFrame(frameId);
      window.clearTimeout(timeoutId);
    };
  }, [messages, isTyping, isLoadingConversation]);

  useEffect(() => {
    return () => {
      if (toastTimeoutRef.current) {
        window.clearTimeout(toastTimeoutRef.current);
      }
    };
  }, []);

  const sendMessage = async (content: string) => {
    const safeContent = content.trim();
    if (!safeContent || isTyping || !userId) return;

    const userMessage: ChatMessage = {
      id: createId(),
      role: "user",
      content: safeContent,
      time: nowLabel(),
    };

    setMessages((prev) => prev.concat(userMessage));
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId,
          sessionId: activeSessionId,
          content: safeContent,
        }),
      });

      const payload = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(payload?.message || "Không thể gọi AI lúc này.");
      }

      const reply = String(payload?.reply || "").trim();
      const serverSessionId = String(payload?.sessionId || "").trim();
      const toolEvents = (payload?.toolEvents ?? []) as ToolEventPayload[];

      if (!reply) {
        throw new Error("AI không trả về nội dung hợp lệ.");
      }

      if (serverSessionId) {
        setActiveSessionId(serverSessionId);
      }

      const createdTaskEvents = toolEvents.filter(
        (event) => event.name === "create_today_task" && event.ok,
      );
      if (createdTaskEvents.length > 0) {
        const first = createdTaskEvents[0];
        const title = String(first.task?.title ?? "").trim();
        const dueTime = String(first.task?.dueTime ?? "").trim();
        const toastText = title
          ? `AI đã tạo lịch: ${title}${dueTime ? ` lúc ${dueTime}` : ""}`
          : "AI đã tạo lịch mới thành công.";
        showToast(toastText);
      }

      setMessages((prev) =>
        prev.concat({
          id: createId(),
          role: "assistant",
          content: reply,
          time: nowLabel(),
        }),
      );

      await refreshSessionList();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Không thể gọi AI lúc này.";
      setMessages((prev) =>
        prev.concat({
          id: createId(),
          role: "assistant",
          content: `Xin lỗi, hiện chưa thể phản hồi: ${message}`,
          time: nowLabel(),
        }),
      );
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void sendMessage(input);
  };

  const handleStartNewConversation = () => {
    setActiveSessionId(null);
    setMessages([createWelcomeMessage()]);
    setInput("");
  };

  const handleSelectSession = (sessionId: string) => {
    if (!sessionId || sessionId === activeSessionId || isLoadingConversation) {
      return;
    }

    void loadConversation(sessionId);
  };

  return (
    <section className="mx-auto grid w-full max-w-6xl gap-4 lg:grid-cols-[1fr_1.6fr]">
      {toastMessage ? (
        <div className="fixed top-5 right-5 z-50 rounded-xl border border-emerald-200 bg-white px-4 py-3 text-sm font-medium text-emerald-800 shadow-lg shadow-emerald-900/10">
          {toastMessage}
        </div>
      ) : null}

      <aside className="glass-panel animate-in p-5 sm:p-6 lg:sticky lg:top-24 lg:max-h-[calc(100vh-7rem)] lg:overflow-y-auto">
        <div className="rounded-2xl border border-emerald-900/10 bg-white p-4">
          <button
            type="button"
            onClick={handleStartNewConversation}
            className="w-full rounded-xl border border-emerald-900/15 bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-800 transition hover:bg-emerald-100"
          >
            + Cuộc trò chuyện mới
          </button>

          <div className="mt-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-emerald-700">
              Lịch sử chat
            </p>

            <div className="mt-3 max-h-64 space-y-2 overflow-y-auto pr-1">
              {isLoadingSessions ? (
                <p className="rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-500">
                  Đang tải lịch sử...
                </p>
              ) : null}

              {!isLoadingSessions && sessions.length === 0 ? (
                <p className="rounded-xl bg-slate-50 px-3 py-2 text-xs text-slate-500">
                  Chưa có hội thoại nào.
                </p>
              ) : null}

              {sessions.map((session) => {
                const active = session.id === activeSessionId;
                return (
                  <button
                    key={session.id}
                    type="button"
                    onClick={() => handleSelectSession(session.id)}
                    className={[
                      "w-full rounded-xl border px-3 py-2 text-left transition",
                      active
                        ? "border-emerald-600/40 bg-emerald-50"
                        : "border-emerald-900/10 bg-white hover:bg-emerald-50/60",
                    ].join(" ")}
                  >
                    <p className="line-clamp-1 text-sm font-semibold text-slate-800">{session.title}</p>
                    <p className="mt-1 line-clamp-1 text-xs text-slate-500">
                      {session.preview || "(Chưa có tin nhắn)"}
                    </p>
                    <p className="mt-1 text-[11px] text-slate-400">
                      {toHistoryDateLabel(session.lastMessageAt)}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </aside>

      <div className="glass-panel animate-in relative flex h-[calc(100vh-7.5rem)] min-h-[70vh] min-w-0 flex-col overflow-hidden [animation-delay:120ms]">
        <div className="border-b border-emerald-900/10 bg-white px-4 py-3 sm:px-5">
          <p className="text-sm font-semibold text-[var(--color-primary-deep)]">
            {activeSessionId ? "Đang xem hội thoại đã lưu" : "Hội thoại hiện tại"}
          </p>
        </div>

        <div
          ref={scrollRef}
          className="min-h-0 flex-1 space-y-3 overflow-y-auto bg-[linear-gradient(180deg,#f8fcf9_0%,#f0f7f3_46%,#f8fcf9_100%)] p-4 sm:p-5"
        >
          {isLoadingConversation ? (
            <div className="rounded-2xl border border-emerald-900/10 bg-white px-4 py-2.5 text-sm text-slate-500 shadow-sm">
              Đang tải hội thoại...
            </div>
          ) : null}

          {messages.map((message) => {
            const isUser = message.role === "user";
            const wrapper = ["flex", isUser ? "justify-end" : "justify-start"].join(" ");
            const bubble = [
              "max-w-[88%] rounded-3xl px-4 py-3.5 text-sm leading-6 shadow-sm sm:max-w-[72%]",
              isUser
                ? "bg-[var(--color-primary)] text-white"
                : "border border-emerald-900/15 bg-gradient-to-b from-white to-emerald-50/35 text-slate-800",
            ].join(" ");
            const timeClass = ["mt-1 text-[11px]", isUser ? "text-emerald-100" : "text-slate-400"].join(" ");

            return (
              <div key={message.id} className={wrapper}>
                <div className={bubble}>
                  {isUser ? (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  ) : (
                    renderAssistantContent(message.content)
                  )}
                  <p className={timeClass}>{message.time}</p>
                </div>
              </div>
            );
          })}

          {isTyping ? (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-emerald-900/10 bg-white px-4 py-2.5 text-sm text-slate-500 shadow-sm">
                Trợ lý đang soạn câu trả lời...
              </div>
            </div>
          ) : null}
          <div ref={bottomAnchorRef} />
        </div>

        <div className="border-t border-emerald-900/10 bg-white/95 p-3 backdrop-blur-sm sm:p-4">
          {!hasUserMessage ? (
            <div className="mb-3 flex flex-wrap gap-2">
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => void sendMessage(prompt)}
                  disabled={isTyping || isLoadingConversation}
                  className="rounded-full border border-emerald-900/15 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-800 transition hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {prompt}
                </button>
              ))}
            </div>
          ) : null}

          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Nhập câu hỏi của bạn..."
              aria-label="Nội dung câu hỏi"
              className="h-11 flex-1 rounded-2xl border border-emerald-900/20 bg-white px-4 text-sm outline-none transition placeholder:text-slate-400 focus:border-emerald-700 focus:ring-2 focus:ring-emerald-200"
            />
            <button
              type="submit"
              disabled={!canSend}
              className="h-11 rounded-2xl bg-[var(--color-primary)] px-5 text-sm font-semibold text-white transition hover:opacity-90 focus:ring-2 focus:ring-emerald-200 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50"
            >
              Gửi
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
