import { getPrisma } from "@/lib/server/prisma";
import { ensureDailyTaskReset } from "@/lib/server/today-task-reset";

type CronState = {
  started: boolean;
  running: boolean;
  timer: NodeJS.Timeout | null;
};

const globalForDailyTaskCron = globalThis as unknown as {
  dailyTaskCron?: CronState;
};

function getCronState(): CronState {
  if (!globalForDailyTaskCron.dailyTaskCron) {
    globalForDailyTaskCron.dailyTaskCron = {
      started: false,
      running: false,
      timer: null,
    };
  }

  return globalForDailyTaskCron.dailyTaskCron;
}

async function runDailyResetTick(state: CronState) {
  if (state.running) {
    return;
  }

  state.running = true;
  try {
    const prisma = await getPrisma();
    await ensureDailyTaskReset(prisma);
  } catch (error) {
    console.error("[daily-task-cron] reset failed", error);
  } finally {
    state.running = false;
  }
}

export function ensureDailyTaskCronStarted() {
  const state = getCronState();
  if (state.started) {
    return;
  }

  state.started = true;

  void runDailyResetTick(state);

  state.timer = setInterval(() => {
    void runDailyResetTick(state);
  }, 60 * 1000);

  if (typeof state.timer.unref === "function") {
    state.timer.unref();
  }
}
