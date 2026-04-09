import { apiError } from "@/lib/server/errors";
import { apiOk } from "@/lib/server/http";
import { getPrisma } from "@/lib/server/prisma";

type Params = {
  params:
    | {
        sessionId: string;
      }
    | Promise<{
        sessionId: string;
      }>;
};

function toIsoString(value: Date | string) {
  return new Date(value).toISOString();
}

export async function GET(request: Request, context: Params) {
  try {
    const userId = new URL(request.url).searchParams.get("userId")?.trim() || "";
    const resolvedParams = await Promise.resolve(context.params);
    const sessionId = resolvedParams.sessionId;

    if (!userId) {
      return apiError(400, {
        code: "VALIDATION_ERROR",
        message: "userId là bắt buộc.",
      });
    }

    if (!sessionId) {
      return apiError(400, {
        code: "VALIDATION_ERROR",
        message: "sessionId là bắt buộc.",
      });
    }

    const prisma = await getPrisma();
    const session = await prisma.chatSession.findUnique({
      where: { id: sessionId },
      include: {
        messages: {
          orderBy: { createdAt: "asc" },
        },
      },
    });

    if (!session || session.userId !== userId) {
      return apiError(404, {
        code: "NOT_FOUND",
        message: "Không tìm thấy phiên chat.",
      });
    }

    return apiOk({
      session: {
        id: session.id,
        title: session.title,
        lastMessageAt: toIsoString(session.lastMessageAt),
      },
      messages: session.messages.map((message: any) => ({
        id: message.id,
        role: message.role === "USER" ? "user" : "assistant",
        content: message.content,
        createdAt: toIsoString(message.createdAt),
      })),
    });
  } catch (error) {
    return apiError(500, {
      code: "INTERNAL_ERROR",
      message: "Không thể lấy nội dung phiên chat.",
      details: { error: String(error) },
    });
  }
}
