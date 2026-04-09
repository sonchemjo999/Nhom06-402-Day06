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

export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await context.params;
    const body = await request.json().catch(() => null);

    const userId = body?.userId?.trim();
    const title = body?.title?.trim();
    const dueTime = body?.dueTime?.trim();
    const status = normalizeStatus(body?.status);

    if (!userId || !title || !dueTime || !status) {
      return apiError(400, {
        code: "VALIDATION_ERROR",
        message: "userId, title, dueTime and valid status are required",
        details: { id },
      });
    }

    const prisma = await getPrisma();
    await ensureDailyTaskReset(prisma);
    const existing = await prisma.todayTask.findUnique({ where: { id } });
    if (!existing || existing.userId !== userId) {
      return apiError(404, {
        code: "NOT_FOUND",
        message: "Task not found",
        details: { id },
      });
    }

    const task = await prisma.todayTask.update({
      where: { id },
      data: { title, dueTime, status },
    });

    return apiOk({ task });
  } catch (error) {
    return apiError(500, {
      code: "INTERNAL_ERROR",
      message: "Failed to update today task",
      details: { error: String(error) },
    });
  }
}

export async function DELETE(
  request: Request,
  context: { params: Promise<{ id: string }> },
) {
  try {
    const { id } = await context.params;
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
    const existing = await prisma.todayTask.findUnique({ where: { id } });
    if (!existing || existing.userId !== userId) {
      return apiError(404, {
        code: "NOT_FOUND",
        message: "Task not found",
        details: { id },
      });
    }

    await prisma.todayTask.delete({ where: { id } });
    return apiOk({ ok: true });
  } catch (error) {
    return apiError(500, {
      code: "INTERNAL_ERROR",
      message: "Failed to delete today task",
      details: { error: String(error) },
    });
  }
}
