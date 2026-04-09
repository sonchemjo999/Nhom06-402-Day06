"use client";

import { useEffect, useMemo, useRef, useState } from "react";

type Role = "assistant" | "user";

type DemoMessage = {
  id: string;
  role: Role;
  content: string;
};

type ScriptStep = {
  user: string;
  assistant: string;
};

type Scenario = {
  id: string;
  title: string;
  steps: ScriptStep[];
};

const SCENARIOS: Scenario[] = [
  {
    id: "health-question",
    title: "Hỏi sức khỏe",
    steps: [
      {
        user: "Mình đang hơi mệt, đau đầu nhẹ từ sáng. Mình nên làm gì trước?",
        assistant:
          "Bạn có thể nghỉ ngơi, uống đủ nước, ăn nhẹ và theo dõi thêm 24 giờ. Nếu đau đầu tăng dần, sốt cao hoặc nôn, bạn nên đi khám sớm để được bác sĩ kiểm tra.",
      },
      {
        user: "Nếu chiều nay vẫn chưa đỡ thì sao?",
        assistant:
          "Nếu chưa cải thiện, bạn nên hạn chế làm việc gắng sức và cân nhắc đặt lịch khám tổng quát để được đánh giá chính xác hơn.",
      },
    ],
  },
  {
    id: "recovery-booking",
    title: "Đặt lịch dưỡng sức",
    steps: [
      {
        user: "Mình muốn đặt lịch dưỡng sức vào cuối tuần này.",
        assistant:
          "Mình đã ghi nhận nhu cầu đặt lịch dưỡng sức cuối tuần. Bạn có thể chọn khung giờ sáng 09:00 hoặc chiều 15:00, mình sẽ ưu tiên sắp lịch phù hợp.",
      },
      {
        user: "Mình chọn chiều 15:00 thứ bảy.",
        assistant:
          "Đã ghi nhận lịch dự kiến 15:00 thứ bảy. Bước tiếp theo là xác nhận thông tin liên hệ để hoàn tất đặt lịch.",
      },
    ],
  },
  {
    id: "hanoi-hospital",
    title: "Tìm Vinmec Hà Nội",
    steps: [
      {
        user: "Cho mình địa chỉ bệnh viện Vinmec ở Hà Nội.",
        assistant:
          "Tại Hà Nội, bạn có thể tham khảo Vinmec Times City ở 458 Minh Khai, quận Hai Bà Trưng.",
      },
      {
        user: "Bệnh viện này có khám cuối tuần không?",
        assistant:
          "Bạn nên kiểm tra lịch khám chuyên khoa theo ngày vì từng khoa có khung giờ khác nhau. Mình có thể hỗ trợ bạn danh sách hotline để gọi xác nhận nhanh.",
      },
    ],
  },
];

const FULL_SCENARIO_ID = "full-all-scenarios";
const FULL_SCENARIO: Scenario = {
  id: FULL_SCENARIO_ID,
  title: "Full demo 3 kịch bản",
  steps: [
    {
      user: "[Kịch bản 1] Hỏi sức khỏe",
      assistant: "Bắt đầu kịch bản Hỏi sức khỏe.",
    },
    ...SCENARIOS[0].steps,
    {
      user: "[Kịch bản 2] Đặt lịch dưỡng sức",
      assistant: "Chuyển sang kịch bản Đặt lịch dưỡng sức.",
    },
    ...SCENARIOS[1].steps,
    {
      user: "[Kịch bản 3] Tìm Vinmec Hà Nội",
      assistant: "Chuyển sang kịch bản Tìm bệnh viện Vinmec tại Hà Nội.",
    },
    ...SCENARIOS[2].steps,
  ],
};

const WELCOME_MESSAGE: DemoMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Chào bạn, đây là bản demo chat AI Assistant (mockup nội bộ). Mình có thể tư vấn sức khỏe cơ bản, hỗ trợ đặt lịch dưỡng sức và tìm cơ sở Vinmec tại Hà Nội.",
};

function createReply(input: string) {
  const text = input.toLowerCase();

  if (
    text.includes("đau") ||
    text.includes("mệt") ||
    text.includes("sức khoẻ") ||
    text.includes("sức khỏe")
  ) {
    return "Bạn nên nghỉ ngơi, uống đủ nước, theo dõi triệu chứng 24 giờ và đi khám nếu có dấu hiệu nặng hơn như sốt cao hoặc đau tăng dần.";
  }

  if (text.includes("đặt lịch") || text.includes("dưỡng sức")) {
    return "Mình đã tiếp nhận yêu cầu đặt lịch dưỡng sức. Bạn vui lòng chọn thời gian mong muốn để mình xác nhận lịch hẹn.";
  }

  if (
    text.includes("hà nội") ||
    text.includes("ha noi") ||
    text.includes("vinmec")
  ) {
    return "Bạn có thể đến Vinmec Times City: 458 Minh Khai, quận Hai Bà Trưng, Hà Nội.";
  }

  return "Mình đang ở chế độ mockup nên phản hồi theo kịch bản demo. Bạn thử hỏi về sức khỏe, đặt lịch dưỡng sức hoặc Vinmec Hà Nội nhé.";
}

export function HealthDemo() {
  const [messages, setMessages] = useState<DemoMessage[]>([WELCOME_MESSAGE]);
  const [draft, setDraft] = useState("");
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);
  const [scriptIndex, setScriptIndex] = useState(0);
  const [isAutoRunning, setIsAutoRunning] = useState(false);
  const nextMessageId = useRef(1);
  const autoRunTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const hasAutoStartedFullRun = useRef(false);

  const selectedScenario = useMemo(
    () => {
      if (selectedScenarioId === FULL_SCENARIO_ID) return FULL_SCENARIO;
      return SCENARIOS.find((scenario) => scenario.id === selectedScenarioId) ?? null;
    },
    [selectedScenarioId],
  );
  const isScriptDone = Boolean(selectedScenario && scriptIndex >= selectedScenario.steps.length);

  const scenarioLabel = useMemo(() => {
    if (!selectedScenario) return "Chưa chọn kịch bản";
    if (isScriptDone) return `Đã chạy xong: ${selectedScenario.title}`;
    if (isAutoRunning) return `Đang tự động chạy: ${selectedScenario.title} (${scriptIndex + 1}/${selectedScenario.steps.length})`;
    return `Sẵn sàng chạy: ${selectedScenario.title}`;
  }, [isAutoRunning, isScriptDone, scriptIndex, selectedScenario]);

  const appendTurn = (userContent: string, assistantContent: string) => {
    const userId = `m-${nextMessageId.current++}`;
    const assistantId = `m-${nextMessageId.current++}`;
    setMessages((prev) => [
      ...prev,
      { id: userId, role: "user", content: userContent },
      { id: assistantId, role: "assistant", content: assistantContent },
    ]);
  };

  const clearAutoRunTimer = () => {
    if (!autoRunTimer.current) return;
    clearTimeout(autoRunTimer.current);
    autoRunTimer.current = null;
  };

  const selectScenario = (scenarioId: string) => {
    const scenario =
      scenarioId === FULL_SCENARIO_ID
        ? FULL_SCENARIO
        : SCENARIOS.find((item) => item.id === scenarioId);
    if (!scenario) return;

    clearAutoRunTimer();
    setSelectedScenarioId(scenarioId);
    setScriptIndex(0);
    setIsAutoRunning(true);
    setMessages([
      WELCOME_MESSAGE,
      {
        id: `m-${nextMessageId.current++}`,
        role: "assistant",
        content: `Đã chọn kịch bản: ${scenario.title}. Hệ thống đang tự động chạy hội thoại...`,
      },
    ]);
  };

  const stopAndResetDemo = () => {
    clearAutoRunTimer();
    setMessages([WELCOME_MESSAGE]);
    setDraft("");
    setSelectedScenarioId(null);
    setScriptIndex(0);
    setIsAutoRunning(false);
    nextMessageId.current = 1;
  };

  const rerunScenario = () => {
    if (!selectedScenarioId) return;
    selectScenario(selectedScenarioId);
  };

  useEffect(() => {
    if (!isAutoRunning || !selectedScenario) return;
    if (scriptIndex >= selectedScenario.steps.length) {
      setIsAutoRunning(false);
      return;
    }

    autoRunTimer.current = setTimeout(() => {
      const step = selectedScenario.steps[scriptIndex];
      appendTurn(step.user, step.assistant);
      setScriptIndex((prev) => prev + 1);
    }, 900);

    return () => clearAutoRunTimer();
  }, [isAutoRunning, scriptIndex, selectedScenario]);

  useEffect(() => () => clearAutoRunTimer(), []);

  useEffect(() => {
    if (hasAutoStartedFullRun.current) return;
    hasAutoStartedFullRun.current = true;
    selectScenario(FULL_SCENARIO_ID);
  }, []);

  const submitCustomMessage = () => {
    if (isAutoRunning) return;
    const trimmed = draft.trim();
    if (!trimmed) return;
    appendTurn(trimmed, createReply(trimmed));
    setDraft("");
  };

  return (
    <section className="glass-panel animate-in space-y-5 p-5 sm:p-7">
      <div>
        <p className="eyebrow">Demo chat mockup</p>
        <h1 className="serif-title mt-2 text-2xl text-[var(--color-primary-deep)] sm:text-3xl">
          Vinmec AI Assistant (không dùng OpenAI)
        </h1>
        <p className="mt-2 text-sm leading-7 text-[var(--color-ink-soft)] sm:text-base">
          Tự động chạy full cả 3 kịch bản khi mở trang, hoặc bạn có thể chọn chạy từng kịch bản.
        </p>
      </div>

      <div className="rounded-2xl border border-emerald-900/10 bg-white p-4 sm:p-5">
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
            {scenarioLabel}
          </span>
          <button
            type="button"
            onClick={rerunScenario}
            disabled={!selectedScenario}
            className="rounded-xl bg-[var(--color-primary)] px-3 py-2 text-sm font-semibold text-white transition hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-55"
          >
            Chạy lại kịch bản
          </button>
          <button
            type="button"
            onClick={stopAndResetDemo}
            className="rounded-xl border border-emerald-900/15 bg-white px-3 py-2 text-sm font-semibold text-[var(--color-primary-deep)] transition hover:bg-emerald-50"
          >
            Dừng và reset
          </button>
        </div>

        <div className="mb-4 flex flex-wrap gap-2">
          <button
            key={FULL_SCENARIO.id}
            type="button"
            onClick={() => selectScenario(FULL_SCENARIO.id)}
            className={`rounded-xl px-3 py-2 text-sm font-semibold transition ${
              selectedScenarioId === FULL_SCENARIO.id
                ? "bg-emerald-700 text-white"
                : "border border-emerald-900/15 bg-white text-[var(--color-primary-deep)] hover:bg-emerald-50"
            }`}
          >
            {FULL_SCENARIO.title}
          </button>
          {SCENARIOS.map((scenario) => (
            <button
              key={scenario.id}
              type="button"
              onClick={() => selectScenario(scenario.id)}
              className={`rounded-xl px-3 py-2 text-sm font-semibold transition ${
                selectedScenarioId === scenario.id
                  ? "bg-emerald-700 text-white"
                  : "border border-emerald-900/15 bg-white text-[var(--color-primary-deep)] hover:bg-emerald-50"
              }`}
            >
              {scenario.title}
            </button>
          ))}
        </div>

        <div className="max-h-[420px] space-y-3 overflow-y-auto rounded-xl border border-emerald-900/10 bg-[linear-gradient(180deg,#f9fcfa_0%,#f3f8f4_100%)] p-3 sm:p-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`max-w-[90%] rounded-2xl px-3 py-2 text-sm leading-6 shadow-sm sm:max-w-[80%] ${
                message.role === "user"
                  ? "ml-auto rounded-br-md bg-[var(--color-primary)] text-white"
                  : "rounded-bl-md border border-emerald-900/10 bg-white text-slate-700"
              }`}
            >
              {message.content}
            </div>
          ))}
        </div>

        <div className="mt-4 space-y-2">
          <label htmlFor="demo-chat-input" className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
            Nhập thử câu hỏi
          </label>
          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              id="demo-chat-input"
              value={draft}
              disabled={isAutoRunning}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  submitCustomMessage();
                }
              }}
              placeholder="Ví dụ: Tôi muốn đặt lịch dưỡng sức thứ 7"
              className="w-full rounded-xl border border-emerald-900/15 bg-white px-3 py-2 text-sm text-slate-700 outline-none ring-0 transition focus:border-emerald-700"
            />
            <button
              type="button"
              onClick={submitCustomMessage}
              disabled={isAutoRunning}
              className="rounded-xl bg-slate-800 px-4 py-2 text-sm font-semibold text-white transition hover:brightness-95"
            >
              Gửi mockup
            </button>
          </div>
          <p className="text-xs text-slate-500">Phản hồi được xử lý local theo rule-based, không gọi OpenAI.</p>
        </div>
      </div>
    </section>
  );
}
