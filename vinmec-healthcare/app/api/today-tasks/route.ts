import { apiError } from "@/lib/server/errors";
import { apiOk } from "@/lib/server/http";
import { ensureDailyTaskCronStarted } from "@/lib/server/daily-task-cron";
import { getPrisma } from "@/lib/server/prisma";
import { ensureDailyTaskReset } from "@/lib/server/today-task-reset";

ensureDailyTaskCronStarted();

type TaskStatus = "TODO" | "UPCOMING" | "DONE";

function normalizeStatus(input: unknown): TaskStatus | null {
  if (input === "TODO" || input === "UPCOMING" || input === "DONE") {
    return input;
  }
  return null;
}

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const userId = url.searchParams.get("userId")?.trim();

    if (!userId) {
      return apiError(400, {
        code: "VALIDATION_ERROR",
        message: "Missing userId query parameter",
        details: { field: "userId" },
      });
    }

    const prisma = await getPrisma();
    await ensureDailyTaskReset(prisma);
    const tasks = await prisma.todayTask.findMany({
      where: { userId },
      orderBy: [{ dueTime: "asc" }, { createdAt: "asc" }],
    });

    return apiOk({ tasks });
  } catch (error) {
    return apiError(500, {
      code: "INTERNAL_ERROR",
      message: "Failed to load today tasks",
      details: { error: String(error) },
    });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => null);

    const userId = body?.userId?.trim();
    const title = body?.title?.trim();
    const dueTime = body?.dueTime?.trim();
    const status = normalizeStatus(body?.status) ?? "TODO";

    if (!userId || !title || !dueTime) {
      return apiError(400, {
        code: "VALIDATION_ERROR",
        message: "userId, title and dueTime are required",
        details: { userId: !!userId, title: !!title, dueTime: !!dueTime },
      });
    }

    const prisma = await getPrisma();
    await ensureDailyTaskReset(prisma);
    const task = await prisma.todayTask.create({
      data: {
        userId,
        title,
        dueTime,
        status,
      },
    });

    return apiOk({ task }, 201);
  } catch (error) {
    return apiError(500, {
      code: "INTERNAL_ERROR",
      message: "Failed to create today task",
      details: { error: String(error) },
    });
  }
}
