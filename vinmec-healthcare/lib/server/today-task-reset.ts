const TASK_RESET_KEY = "today_tasks_last_reset_date";
const VIETNAM_TIME_ZONE = "Asia/Ho_Chi_Minh";

function getDateKeyInVietnamTime(date = new Date()) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: VIETNAM_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  })
    .formatToParts(date)
    .reduce<Record<string, string>>((acc, part) => {
      if (part.type !== "literal") {
        acc[part.type] = part.value;
      }
      return acc;
    }, {});

  return `${parts.year}-${parts.month}-${parts.day}`;
}

type ResetResult = {
  didReset: boolean;
  resetCount: number;
  dateKey: string;
};

async function ensureAppStateTable(prisma: any) {
  if (typeof prisma?.$executeRawUnsafe !== "function") {
    return;
  }

  await prisma.$executeRawUnsafe(`
    CREATE TABLE IF NOT EXISTS "app_state" (
      "key" TEXT NOT NULL PRIMARY KEY,
      "value" TEXT NOT NULL,
      "updated_at" DATETIME NOT NULL
    )
  `);
}

async function readLastResetDate(prisma: any): Promise<string | null> {
  if (typeof prisma?.$queryRawUnsafe !== "function") {
    return null;
  }

  const rows = (await prisma.$queryRawUnsafe(
    `SELECT "value" FROM "app_state" WHERE "key" = ? LIMIT 1`,
    TASK_RESET_KEY,
  )) as Array<{ value?: string }>;

  return rows?.[0]?.value ?? null;
}

async function writeLastResetDate(prisma: any, dateKey: string) {
  if (typeof prisma?.$executeRawUnsafe !== "function") {
    return;
  }

  await prisma.$executeRawUnsafe(
    `
      INSERT INTO "app_state" ("key", "value", "updated_at")
      VALUES (?, ?, CURRENT_TIMESTAMP)
      ON CONFLICT("key") DO UPDATE SET
        "value" = excluded."value",
        "updated_at" = CURRENT_TIMESTAMP
    `,
    TASK_RESET_KEY,
    dateKey,
  );
}

export async function ensureDailyTaskReset(prisma: any): Promise<ResetResult> {
  const dateKey = getDateKeyInVietnamTime();

  try {
    if (typeof prisma?.todayTask?.updateMany !== "function") {
      return { didReset: false, resetCount: 0, dateKey };
    }

    await ensureAppStateTable(prisma);
    const lastResetDate = await readLastResetDate(prisma);

    if (lastResetDate === dateKey) {
      return { didReset: false, resetCount: 0, dateKey };
    }

    const resetResult = await prisma.todayTask.updateMany({
      where: {
        NOT: {
          status: "TODO",
        },
      },
      data: {
        status: "TODO",
      },
    });

    await writeLastResetDate(prisma, dateKey);

    return {
      didReset: true,
      resetCount: Number(resetResult?.count ?? 0),
      dateKey,
    };
  } catch (error) {
    console.error("[today-task-reset] skipped due to error", error);
    return { didReset: false, resetCount: 0, dateKey };
  }
}
