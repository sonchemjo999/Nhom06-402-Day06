import { apiError } from "@/lib/server/errors";
import { apiOk } from "@/lib/server/http";
import { ensureDailyTaskCronStarted } from "@/lib/server/daily-task-cron";
import { getPrisma } from "@/lib/server/prisma";
import { ensureDailyTaskReset } from "@/lib/server/today-task-reset";

ensureDailyTaskCronStarted();

type ChatTurn = {
  role: "user" | "assistant";
  content: string;
};

type ToolCall = {
  id: string;
  type: "function";
  function: {
    name: string;
    arguments: string;
  };
};

type OpenAIChatResponse = {
  choices?: Array<{
    message?: {
      role?: "assistant";
      content?: string | null;
      tool_calls?: ToolCall[];
    };
  }>;
  error?: { message?: string };
};

type ToolEvent = {
  name: string;
  ok: boolean;
  message?: string;
  task?: {
    id?: string;
    title?: string;
    dueTime?: string;
    status?: string;
  };
};

const SYSTEM_PROMPT = [
  "Bạn là Vinmec AI Assistant.",
  "Bạn chỉ được tư vấn các nội dung liên quan sức khỏe, y tế, lối sống lành mạnh, thuốc, triệu chứng, chăm sóc bệnh nhân và thông tin dịch vụ/cơ sở Vinmec.",
  "Nếu người dùng hỏi ngoài lĩnh vực trên (ví dụ: tài chính, lập trình, thể thao, giải trí, chính trị...), hãy từ chối lịch sự và nói rõ bạn chỉ hỗ trợ chủ đề sức khỏe và dịch vụ Vinmec.",
  "Trả lời ngắn gọn, rõ ràng, tiếng Việt tự nhiên, ưu tiên an toàn cho bệnh nhân.",
  "Không chẩn đoán chắc chắn hoặc khẳng định kết luận y khoa. Nếu có dấu hiệu nguy hiểm thì khuyên đi cơ sở y tế ngay hoặc gọi cấp cứu khi cần.",
  "Với câu hỏi về lịch hôm nay/lịch trình/việc cần làm/nhắc việc, bắt buộc gọi tool get_today_tasks trước khi trả lời và chỉ trả lời dựa trên dữ liệu tool, không tự tạo lịch mẫu.",
  "Khi user yêu cầu đánh dấu toàn bộ hoạt động trước thời điểm hiện tại là hoàn thành, hãy gọi tool complete_previous_today_tasks.",
  "Bạn có quyền dùng tools để đọc/sửa lịch hôm nay của user khi cần.",
  "Khi cần thông tin mới từ Internet, hãy gọi tool_search_duckduckgo và ưu tiên nêu nguồn/đường dẫn trong câu trả lời.",
  "Định dạng bắt buộc để dễ đọc:",
  "- Dòng đầu: 1 câu tóm tắt ngắn.",
  "- Nếu có nhiều ý: dùng danh sách đánh số, mỗi ý 1 dòng riêng (1., 2., 3.).",
  "- Tránh dồn nhiều ý trong một dòng.",
].join(" ");

const CHAT_TOOLS = [
  {
    type: "function",
    function: {
      name: "get_today_tasks",
      description: "Lấy danh sách lịch hôm nay của user, có thể lọc theo tên và khoảng thời gian",
      parameters: {
        type: "object",
        properties: {
          title: {
            type: "string",
            description: "Lọc task theo tên (chứa chuỗi này)",
          },
          status: {
            type: "string",
            enum: ["TODO", "UPCOMING", "DONE"],
            description: "Lọc theo 1 trạng thái cụ thể",
          },
          includeDone: {
            type: "boolean",
            description: "Có lấy task DONE hay không. Mặc định true",
          },
          fromTime: {
            type: "string",
            description: "Giờ bắt đầu lọc theo định dạng HH:mm",
          },
          toTime: {
            type: "string",
            description: "Giờ kết thúc lọc theo định dạng HH:mm",
          },
          limit: {
            type: "number",
            description: "Số lượng tối đa task trả về (1-50), mặc định không giới hạn",
          },
          sort: {
            type: "string",
            enum: ["asc", "desc"],
            description: "Sắp xếp theo thời gian tăng dần/giảm dần. Mặc định asc",
          },
        },
        additionalProperties: false,
      },
    },
  },
  {
    type: "function",
    function: {
      name: "create_today_task",
      description: "Tạo lịch mới cho user",
      parameters: {
        type: "object",
        properties: {
          title: { type: "string" },
          dueTime: { type: "string", description: "Định dạng HH:mm" },
          status: { type: "string", enum: ["TODO", "UPCOMING", "DONE"] },
        },
        required: ["title", "dueTime"],
        additionalProperties: false,
      },
    },
  },
  {
    type: "function",
    function: {
      name: "update_today_task_status",
      description: "Cập nhật trạng thái task theo taskId hoặc theo tên task",
      parameters: {
        type: "object",
        properties: {
          taskId: { type: "string" },
          title: { type: "string", description: "Tên task để tìm gần đúng nếu không có taskId" },
          status: { type: "string", enum: ["TODO", "UPCOMING", "DONE"] },
        },
        required: ["status"],
        additionalProperties: false,
      },
    },
  },
  {
    type: "function",
    function: {
      name: "complete_previous_today_tasks",
      description:
        "Đánh dấu hoàn thành hàng loạt các task có giờ nhỏ hơn hoặc bằng beforeTime (mặc định là giờ hiện tại tại Việt Nam)",
      parameters: {
        type: "object",
        properties: {
          beforeTime: {
            type: "string",
            description: "Giờ chặn trên theo định dạng HH:mm. Nếu bỏ trống sẽ dùng giờ hiện tại.",
          },
        },
        additionalProperties: false,
      },
    },
  },
  {
    type: "function",
    function: {
      name: "delete_today_task",
      description: "Xóa task theo taskId",
      parameters: {
        type: "object",
        properties: {
          taskId: { type: "string" },
        },
        required: ["taskId"],
        additionalProperties: false,
      },
    },
  },
  {
    type: "function",
    function: {
      name: "tool_search_duckduckgo",
      description:
        "Tìm kiếm web bằng DuckDuckGo để lấy thông tin mới nhất. Dùng khi cần thông tin ngoài dữ liệu nội bộ.",
      parameters: {
        type: "object",
        properties: {
          query: { type: "string", description: "Từ khóa cần tìm kiếm" },
          maxResults: {
            type: "number",
            description: "Số link tối đa trả về (1-8), mặc định 5",
          },
        },
        required: ["query"],
        additionalProperties: false,
      },
    },
  },
] as const;

class HttpError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function parseArgs(raw: string): Record<string, unknown> {
  try {
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function normalizeHHmm(value: unknown) {
  const raw = String(value ?? "").trim();
  if (!raw) return "";
  if (!/^\d{2}:\d{2}$/.test(raw)) return "";

  const [hourRaw, minuteRaw] = raw.split(":");
  const hour = Number(hourRaw);
  const minute = Number(minuteRaw);

  if (!Number.isInteger(hour) || !Number.isInteger(minute)) return "";
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return "";

  return raw;
}

function normalizeTaskStatus(value: unknown) {
  const raw = String(value ?? "").trim();
  if (raw === "TODO" || raw === "UPCOMING" || raw === "DONE") {
    return raw;
  }
  return "";
}

function inferTaskStatusFromMessage(message: string) {
  const text = message.toLowerCase();
  if (
    text.includes("hoàn thành") ||
    text.includes("hoan thanh") ||
    text.includes("xong") ||
    text.includes("done")
  ) {
    return "DONE";
  }
  if (text.includes("upcoming") || text.includes("sắp tới") || text.includes("sap toi")) {
    return "UPCOMING";
  }
  if (text.includes("todo") || text.includes("to do") || text.includes("chưa làm") || text.includes("chua lam")) {
    return "TODO";
  }
  return "";
}

function getCurrentHHmmInVn() {
  const formatter = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Ho_Chi_Minh",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  return formatter.format(new Date());
}

function isNextScheduleIntent(message: string) {
  const text = message.toLowerCase();
  return (
    text.includes("tiếp theo") ||
    text.includes("tiep theo") ||
    text.includes("sắp tới") ||
    text.includes("sap toi") ||
    text.includes("sắp đến") ||
    text.includes("sap den") ||
    text.includes("upcoming") ||
    text.includes("next")
  );
}

function isScheduleIntent(message: string) {
  const text = message.toLowerCase();
  return (
    text.includes("lịch") ||
    text.includes("lich") ||
    text.includes("lịch trình") ||
    text.includes("nhắc việc") ||
    text.includes("task") ||
    text.includes("việc hôm nay")
  );
}

function isCompletePreviousTasksIntent(message: string) {
  const text = message.toLowerCase();
  const hasCompleteAll =
    text.includes("hoàn thành hết") ||
    text.includes("hoan thanh het") ||
    text.includes("hoàn thành tất cả") ||
    text.includes("hoan thanh tat ca") ||
    text.includes("đánh dấu hết") ||
    text.includes("danh dau het") ||
    text.includes("mark all");
  const hasPastScope =
    text.includes("trước") ||
    text.includes("truoc") ||
    text.includes("đã qua") ||
    text.includes("da qua") ||
    text.includes("hoạt động trước") ||
    text.includes("hoat dong truoc");

  return hasCompleteAll && hasPastScope;
}

function isUpdateTaskStatusIntent(message: string) {
  const text = message.toLowerCase();
  const hasUpdateVerb =
    text.includes("đánh dấu") ||
    text.includes("danh dau") ||
    text.includes("cập nhật") ||
    text.includes("cap nhat") ||
    text.includes("mark");
  const hasStatusHint =
    text.includes("hoàn thành") ||
    text.includes("hoan thanh") ||
    text.includes("xong") ||
    text.includes("done") ||
    text.includes("upcoming") ||
    text.includes("todo");
  return hasUpdateVerb && hasStatusHint;
}

function extractTaskTitleFromUpdateIntent(message: string) {
  const raw = message.trim();
  if (!raw) return "";

  const match = raw.match(/(?:đánh dấu|danh dau|mark)\s+(.+?)\s+(?:hoàn thành|hoan thanh|xong|done)\b/i);
  if (match?.[1]) {
    return match[1].trim();
  }
  return "";
}

function normalizeTurns(raw: unknown): ChatTurn[] {
  if (!Array.isArray(raw)) {
    return [];
  }

  return raw
    .filter(
      (message) =>
        (message as ChatTurn)?.role &&
        ((message as ChatTurn).role === "user" || (message as ChatTurn).role === "assistant") &&
        typeof (message as ChatTurn).content === "string",
    )
    .map((message) => ({
      role: (message as ChatTurn).role,
      content: (message as ChatTurn).content.trim(),
    }))
    .filter((message) => message.content.length > 0)
    .slice(-20);
}

function buildSessionTitle(content: string) {
  const cleaned = content.replace(/\s+/g, " ").trim();
  if (cleaned.length <= 60) {
    return cleaned;
  }
  return `${cleaned.slice(0, 57)}...`;
}

async function callOpenAI(apiKey: string, body: Record<string, unknown>) {
  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const payload = (await response.json().catch(() => ({}))) as OpenAIChatResponse;

  return { response, payload };
}

function extractLinksFromMarkdown(markdown: string, maxResults: number) {
  const linkRegex = /\[([^\]]+)\]\((https?:\/\/[^)\s]+)(?:\s+"[^"]*")?\)/g;
  const blockedHosts = [
    "duckduckgo.com",
    "external-content.duckduckgo.com",
    "start.duckduckgo.com",
  ];

  const links: Array<{ title: string; url: string }> = [];
  const seen = new Set<string>();
  let match: RegExpExecArray | null;

  while ((match = linkRegex.exec(markdown)) !== null && links.length < maxResults) {
    const title = (match[1] || "").replace(/^#+\s*/, "").trim();
    const url = (match[2] || "").trim();
    if (!title || !url) continue;

    const host = (() => {
      try {
        return new URL(url).hostname.toLowerCase();
      } catch {
        return "";
      }
    })();

    if (!host || blockedHosts.some((blockedHost) => host.endsWith(blockedHost))) {
      continue;
    }

    if (seen.has(url)) continue;
    seen.add(url);

    links.push({ title, url });
  }

  return links;
}

async function toolSearchDuckDuckGo(query: string, maxResultsRaw: unknown) {
  const normalizedQuery = query.trim();
  if (!normalizedQuery) {
    return { ok: false, error: "Thiếu query để tìm kiếm." };
  }

  const maxResults = Math.min(8, Math.max(1, Number(maxResultsRaw) || 5));
  const searchUrl = `https://r.jina.ai/http://duckduckgo.com/?q=${encodeURIComponent(normalizedQuery)}`;

  const response = await fetch(searchUrl, {
    method: "GET",
    headers: {
      Accept: "text/plain",
      "User-Agent": "VinmecAssistant/1.0 (+duckduckgo-search-tool)",
    },
  });

  if (!response.ok) {
    return { ok: false, error: `DuckDuckGo search failed (${response.status}).` };
  }

  const markdown = (await response.text()).trim();
  if (!markdown) {
    return { ok: false, error: "DuckDuckGo không trả về dữ liệu." };
  }

  const links = extractLinksFromMarkdown(markdown, maxResults);

  return {
    ok: true,
    query: normalizedQuery,
    provider: "duckduckgo",
    links,
    raw: markdown.slice(0, 12000),
  };
}

async function executeToolCall(toolCall: ToolCall, userId: string, latestUserMessage: string) {
  const args = parseArgs(toolCall.function.arguments);

  switch (toolCall.function.name) {
    case "get_today_tasks": {
      if (!userId) {
        return { ok: false, error: "Thiếu userId để lấy lịch hôm nay." };
      }
      const title = String(args.title ?? "").trim();
      const status = normalizeTaskStatus(args.status);
      const includeDone = typeof args.includeDone === "boolean" ? args.includeDone : true;
      const fromTime = normalizeHHmm(args.fromTime);
      const toTime = normalizeHHmm(args.toTime);
      const sort = String(args.sort ?? "").toLowerCase() === "desc" ? "desc" : "asc";
      const limitRaw = Number(args.limit);
      const limit =
        Number.isFinite(limitRaw) && limitRaw > 0 ? Math.min(50, Math.max(1, Math.floor(limitRaw))) : undefined;
      const inferredFromTime =
        !fromTime && isNextScheduleIntent(latestUserMessage) ? getCurrentHHmmInVn() : "";
      const effectiveFromTime = fromTime || inferredFromTime;

      if (args.status != null && !status) {
        return { ok: false, error: "status không hợp lệ. Chỉ nhận TODO, UPCOMING hoặc DONE." };
      }
      if (args.fromTime != null && !fromTime) {
        return { ok: false, error: "fromTime không hợp lệ, yêu cầu định dạng HH:mm." };
      }
      if (args.toTime != null && !toTime) {
        return { ok: false, error: "toTime không hợp lệ, yêu cầu định dạng HH:mm." };
      }
      if (status === "DONE" && includeDone === false) {
        return { ok: false, error: "Filter mâu thuẫn: status=DONE nhưng includeDone=false." };
      }
      if (args.limit != null && limit === undefined) {
        return { ok: false, error: "limit không hợp lệ. Yêu cầu số nguyên từ 1 đến 50." };
      }
      if (effectiveFromTime && toTime && effectiveFromTime > toTime) {
        return { ok: false, error: "Khoảng thời gian không hợp lệ: fromTime phải nhỏ hơn hoặc bằng toTime." };
      }

      const prisma = await getPrisma();
      await ensureDailyTaskReset(prisma);
      const where = {
        userId,
        AND: [
          ...(title ? [{ title: { contains: title } }] : []),
          ...(status ? [{ status }] : []),
          ...(!includeDone ? [{ status: { not: "DONE" } }] : []),
          ...(effectiveFromTime || toTime
            ? [
                {
                  dueTime: {
                    ...(effectiveFromTime ? { gte: effectiveFromTime } : {}),
                    ...(toTime ? { lte: toTime } : {}),
                  },
                },
              ]
            : []),
        ],
      };
      const tasks = await prisma.todayTask.findMany({
        where,
        orderBy: [{ dueTime: sort }, { createdAt: sort }],
        ...(limit ? { take: limit } : {}),
      });
      return {
        ok: true,
        appliedFilters: {
          title: title || undefined,
          status: status || undefined,
          includeDone,
          fromTime: effectiveFromTime || undefined,
          toTime: toTime || undefined,
          sort,
          limit,
        },
        tasks,
      };
    }
    case "create_today_task": {
      if (!userId) {
        return { ok: false, error: "Thiếu userId để tạo lịch." };
      }
      const prisma = await getPrisma();
      await ensureDailyTaskReset(prisma);
      const title = String(args.title ?? "").trim();
      const dueTime = String(args.dueTime ?? "").trim();
      const status = ["TODO", "UPCOMING", "DONE"].includes(String(args.status))
        ? String(args.status)
        : "TODO";

      if (!title || !dueTime) {
        return { ok: false, error: "Thiếu title hoặc dueTime" };
      }

      const task = await prisma.todayTask.create({
        data: {
          userId,
          title,
          dueTime,
          status,
        },
      });
      return { ok: true, task };
    }
    case "update_today_task_status": {
      if (!userId) {
        return { ok: false, error: "Thiếu userId để cập nhật lịch." };
      }
      const prisma = await getPrisma();
      await ensureDailyTaskReset(prisma);
      const taskId = String(args.taskId ?? "").trim();
      const titleFromArgs = String(args.title ?? "").trim();
      const titleFromMessage = extractTaskTitleFromUpdateIntent(latestUserMessage);
      const title = titleFromArgs || titleFromMessage;
      const status =
        normalizeTaskStatus(args.status) || normalizeTaskStatus(inferTaskStatusFromMessage(latestUserMessage));

      if (!status) {
        return { ok: false, error: "Thiếu status hoặc status không hợp lệ" };
      }
      if (!taskId && !title) {
        return { ok: false, error: "Thiếu taskId hoặc title để xác định task cần cập nhật." };
      }

      let existing: { id: string; userId: string } | null = null;

      if (taskId) {
        const byId = await prisma.todayTask.findUnique({ where: { id: taskId } });
        if (byId?.userId === userId) {
          existing = byId;
        }
      } else if (title) {
        existing = await prisma.todayTask.findFirst({
          where: {
            userId,
            title: { contains: title },
            ...(status === "DONE" ? { status: { not: "DONE" } } : {}),
          },
          orderBy: [{ dueTime: "asc" }, { createdAt: "asc" }],
        });
      }

      if (!existing) {
        return { ok: false, error: "Không tìm thấy task" };
      }

      const task = await prisma.todayTask.update({
        where: { id: existing.id },
        data: { status },
      });
      return { ok: true, task, matchedBy: taskId ? "taskId" : "title" };
    }
    case "complete_previous_today_tasks": {
      if (!userId) {
        return { ok: false, error: "Thiếu userId để cập nhật lịch." };
      }

      const beforeTime = normalizeHHmm(args.beforeTime);
      if (args.beforeTime != null && !beforeTime) {
        return { ok: false, error: "beforeTime không hợp lệ, yêu cầu định dạng HH:mm." };
      }
      const effectiveBeforeTime = beforeTime || getCurrentHHmmInVn();

      const prisma = await getPrisma();
      await ensureDailyTaskReset(prisma);

      const tasksToComplete = await prisma.todayTask.findMany({
        where: {
          userId,
          status: { not: "DONE" },
          dueTime: { lte: effectiveBeforeTime },
        },
        orderBy: [{ dueTime: "asc" }, { createdAt: "asc" }],
      });

      if (tasksToComplete.length === 0) {
        return {
          ok: true,
          beforeTime: effectiveBeforeTime,
          updatedCount: 0,
          updatedTaskIds: [] as string[],
        };
      }

      await prisma.todayTask.updateMany({
        where: { id: { in: tasksToComplete.map((task: { id: string }) => task.id) } },
        data: { status: "DONE" },
      });

      return {
        ok: true,
        beforeTime: effectiveBeforeTime,
        updatedCount: tasksToComplete.length,
        updatedTaskIds: tasksToComplete.map((task: { id: string }) => task.id),
      };
    }
    case "delete_today_task": {
      if (!userId) {
        return { ok: false, error: "Thiếu userId để xóa lịch." };
      }
      const prisma = await getPrisma();
      await ensureDailyTaskReset(prisma);
      const taskId = String(args.taskId ?? "").trim();
      if (!taskId) {
        return { ok: false, error: "Thiếu taskId" };
      }

      const existing = await prisma.todayTask.findUnique({ where: { id: taskId } });
      if (!existing || existing.userId !== userId) {
        return { ok: false, error: "Không tìm thấy task" };
      }

      await prisma.todayTask.delete({ where: { id: taskId } });
      return { ok: true, deletedTaskId: taskId };
    }
    case "tool_search_duckduckgo": {
      const query = String(args.query ?? "");
      return toolSearchDuckDuckGo(query, args.maxResults);
    }
    default:
      return { ok: false, error: `Tool không hỗ trợ: ${toolCall.function.name}` };
  }
}

async function generateAssistantReply(params: {
  apiKey: string;
  model: string;
  turns: ChatTurn[];
  userId: string;
}) {
  const { apiKey, model, turns, userId } = params;
  const latestUserMessage =
    [...turns].reverse().find((turn) => turn.role === "user")?.content.trim() || "";
  let toolChoice:
    | "auto"
    | {
        type: "function";
        function: { name: "get_today_tasks" | "complete_previous_today_tasks" | "update_today_task_status" };
      } = "auto";

  if (latestUserMessage && isCompletePreviousTasksIntent(latestUserMessage)) {
    toolChoice = { type: "function", function: { name: "complete_previous_today_tasks" } };
  } else if (latestUserMessage && isUpdateTaskStatusIntent(latestUserMessage)) {
    toolChoice = { type: "function", function: { name: "update_today_task_status" } };
  } else if (latestUserMessage && isScheduleIntent(latestUserMessage)) {
    toolChoice = { type: "function", function: { name: "get_today_tasks" } };
  }

  const firstCall = await callOpenAI(apiKey, {
    model,
    temperature: 0.4,
    tool_choice: toolChoice,
    tools: CHAT_TOOLS,
    messages: [{ role: "system", content: SYSTEM_PROMPT }, ...turns],
  });

  if (!firstCall.response.ok) {
    throw new HttpError(
      firstCall.response.status,
      firstCall.payload?.error?.message || "OpenAI request failed.",
    );
  }

  const firstMessage = firstCall.payload?.choices?.[0]?.message;
  if (!firstMessage) {
    throw new HttpError(502, "OpenAI không trả về message hợp lệ.");
  }

  const toolCalls = firstMessage.tool_calls ?? [];
  if (toolCalls.length > 0) {
    const toolEvents: ToolEvent[] = [];
    const toolResults = [] as Array<{ role: "tool"; tool_call_id: string; content: string }>;
    for (const toolCall of toolCalls) {
      const result = await executeToolCall(toolCall, userId, latestUserMessage);

      const event: ToolEvent = {
        name: toolCall.function.name,
        ok: Boolean((result as { ok?: boolean })?.ok),
      };
      if (typeof (result as { error?: unknown })?.error === "string") {
        event.message = String((result as { error?: string }).error);
      }
      if (toolCall.function.name === "create_today_task" && (result as { task?: unknown })?.task) {
        const task = (result as { task?: Record<string, unknown> }).task;
        event.task = {
          id: String(task?.id ?? ""),
          title: String(task?.title ?? ""),
          dueTime: String(task?.dueTime ?? ""),
          status: String(task?.status ?? ""),
        };
      }
      toolEvents.push(event);

      toolResults.push({
        role: "tool",
        tool_call_id: toolCall.id,
        content: JSON.stringify(result),
      });
    }

    const secondCall = await callOpenAI(apiKey, {
      model,
      temperature: 0.4,
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        ...turns,
        {
          role: "assistant",
          content: firstMessage.content ?? null,
          tool_calls: toolCalls,
        },
        ...toolResults,
      ],
    });

    if (!secondCall.response.ok) {
      throw new HttpError(
        secondCall.response.status,
        secondCall.payload?.error?.message || "OpenAI request failed (tool round).",
      );
    }

    const reply = secondCall.payload?.choices?.[0]?.message?.content?.trim();
    if (!reply) {
      throw new HttpError(502, "OpenAI không trả về nội dung hợp lệ sau khi gọi tool.");
    }

    return { reply, usedTools: toolCalls.map((t) => t.function.name), toolEvents };
  }

  const reply = firstMessage.content?.trim();
  if (!reply) {
    throw new HttpError(502, "OpenAI không trả về nội dung hợp lệ.");
  }

  return { reply, usedTools: [] as string[], toolEvents: [] as ToolEvent[] };
}

async function createOrGetSession(prisma: any, userId: string, sessionId: string | undefined, firstMessage: string) {
  if (sessionId) {
    const existing = await prisma.chatSession.findUnique({ where: { id: sessionId } });
    if (!existing || existing.userId !== userId) {
      throw new HttpError(404, "Không tìm thấy phiên chat.");
    }
    return existing;
  }

  return prisma.chatSession.create({
    data: {
      userId,
      title: buildSessionTitle(firstMessage),
    },
  });
}

async function appendChatMessage(prisma: any, sessionId: string, role: "USER" | "ASSISTANT", content: string) {
  const now = new Date();
  await prisma.chatMessage.create({
    data: {
      sessionId,
      role,
      content,
    },
  });

  await prisma.chatSession.update({
    where: { id: sessionId },
    data: {
      lastMessageAt: now,
    },
  });
}

async function getSessionTurns(prisma: any, sessionId: string): Promise<ChatTurn[]> {
  const rows = await prisma.chatMessage.findMany({
    where: { sessionId },
    orderBy: { createdAt: "desc" },
    take: 20,
  });

  return rows.reverse().map((row: { role: "USER" | "ASSISTANT"; content: string }) => ({
    role: row.role === "USER" ? "user" : "assistant",
    content: row.content,
  }));
}

export async function POST(request: Request) {
  try {
    const apiKey = process.env.OPENAI_API_KEY?.trim();
    if (!apiKey) {
      return apiError(500, {
        code: "INTERNAL_ERROR",
        message: "OPENAI_API_KEY chưa được cấu hình ở server.",
      });
    }

    const model = process.env.OPENAI_MODEL?.trim() || "gpt-4o-mini";
    const body = await request.json().catch(() => null);

    const userId = String(body?.userId ?? "").trim();
    const content = String(body?.content ?? "").trim();
    const sessionId = String(body?.sessionId ?? "").trim() || undefined;

    if (content) {
      if (!userId) {
        return apiError(400, {
          code: "VALIDATION_ERROR",
          message: "userId là bắt buộc khi chat theo session.",
        });
      }

      const prisma = await getPrisma();
      const session = await createOrGetSession(prisma, userId, sessionId, content);

      await appendChatMessage(prisma, session.id, "USER", content);

      const turns = await getSessionTurns(prisma, session.id);
      const aiResult = await generateAssistantReply({ apiKey, model, turns, userId });

      await appendChatMessage(prisma, session.id, "ASSISTANT", aiResult.reply);

      return apiOk({
        reply: aiResult.reply,
        usedTools: aiResult.usedTools,
        toolEvents: aiResult.toolEvents,
        sessionId: session.id,
      });
    }

    const messages = normalizeTurns(body?.messages);
    if (messages.length === 0) {
      return apiError(400, {
        code: "VALIDATION_ERROR",
        message: "messages hoặc content là bắt buộc.",
      });
    }

    const aiResult = await generateAssistantReply({ apiKey, model, turns: messages, userId });
    return apiOk({ reply: aiResult.reply, usedTools: aiResult.usedTools, toolEvents: aiResult.toolEvents });
  } catch (error) {
    if (error instanceof HttpError) {
      return apiError(error.status, {
        code: "INTERNAL_ERROR",
        message: error.message,
      });
    }

    return apiError(500, {
      code: "INTERNAL_ERROR",
      message: "Không thể gọi AI agent ở server.",
      details: { error: String(error) },
    });
  }
}
