import { apiError } from "@/lib/server/errors";
import { apiOk } from "@/lib/server/http";
import { getPrisma } from "@/lib/server/prisma";
import { ensureDailyTaskReset } from "@/lib/server/today-task-reset";

function getTokenFromRequest(request: Request) {
  const auth = request.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ")) {
    return auth.slice("Bearer ".length).trim();
  }

  const url = new URL(request.url);
  return url.searchParams.get("token")?.trim() || "";
}

async function handleCronReset(request: Request) {
  try {
    const expectedToken = process.env.CRON_SECRET?.trim() || process.env.REVIEWER_TOKEN?.trim() || "";
    if (!expectedToken) {
      return apiError(500, {
        code: "INTERNAL_ERROR",
        message: "CRON_SECRET (hoặc REVIEWER_TOKEN) chưa được cấu hình.",
      });
    }

    const incomingToken = getTokenFromRequest(request);
    if (!incomingToken || incomingToken !== expectedToken) {
      return apiError(401, {
        code: "UNAUTHORIZED",
        message: "Unauthorized cron request.",
      });
    }

    const prisma = await getPrisma();
    const result = await ensureDailyTaskReset(prisma);

    return apiOk({
      ok: true,
      didReset: result.didReset,
      resetCount: result.resetCount,
      dateKey: result.dateKey,
    });
  } catch (error) {
    return apiError(500, {
      code: "INTERNAL_ERROR",
      message: "Failed to run daily task reset.",
      details: { error: String(error) },
    });
  }
}

export async function POST(request: Request) {
  return handleCronReset(request);
}

export async function GET(request: Request) {
  return handleCronReset(request);
}
