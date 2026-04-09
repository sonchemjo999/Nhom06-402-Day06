import { apiError } from "@/lib/server/errors";
import { apiOk } from "@/lib/server/http";
import { getPrisma } from "@/lib/server/prisma";

function toIsoString(value: Date | string) {
  return new Date(value).toISOString();
}

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const userId = url.searchParams.get("userId")?.trim() || "";

    if (!userId) {
      return apiError(400, {
        code: "VALIDATION_ERROR",
        message: "userId là bắt buộc.",
      });
    }

    const prisma = await getPrisma();
    const sessions = await prisma.chatSession.findMany({
      where: { userId },
      orderBy: { lastMessageAt: "desc" },
      include: {
        messages: {
          orderBy: { createdAt: "desc" },
          take: 1,
        },
      },
    });

    return apiOk({
      sessions: sessions.map((session: any) => ({
        id: session.id,
        title: session.title,
        lastMessageAt: toIsoString(session.lastMessageAt),
        preview: session.messages[0]?.content ?? "",
      })),
    });
  } catch (error) {
    return apiError(500, {
      code: "INTERNAL_ERROR",
      message: "Không thể lấy danh sách lịch sử chat.",
      details: { error: String(error) },
    });
  }
}
