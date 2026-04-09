"use client";

import { useEffect, useMemo, useState } from "react";

type TaskStatus = "TODO" | "UPCOMING" | "DONE";

type TodayTask = {
  id: string;
  userId: string;
  title: string;
  dueTime: string;
  status: TaskStatus;
  createdAt: string;
  updatedAt: string;
};

const statusLabel: Record<TaskStatus, string> = {
  TODO: "Chưa bắt đầu",
  UPCOMING: "Sắp đến hạn",
  DONE: "Đã hoàn thành",
};

const statusTone: Record<TaskStatus, string> = {
  DONE: "text-emerald-700 bg-emerald-100 border-emerald-200",
  UPCOMING: "text-amber-700 bg-amber-100 border-amber-200",
  TODO: "text-slate-600 bg-slate-100 border-slate-200",
};

const statusChoices: TaskStatus[] = ["TODO", "DONE"];
const LOCAL_USER_KEY = "id_user";

function createBrowserUuid() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `user_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

function getCurrentMinutesOfDay() {
  const now = new Date();
  return now.getHours() * 60 + now.getMinutes();
}

function parseDueTimeToMinutes(dueTime: string) {
  const [hoursRaw, minutesRaw] = dueTime.split(":");
  const hours = Number(hoursRaw);
  const minutes = Number(minutesRaw);

  if (!Number.isInteger(hours) || !Number.isInteger(minutes)) {
    return null;
  }
  if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) {
    return null;
  }

  return hours * 60 + minutes;
}

export function TodayTasksPanel() {
  const [userId, setUserId] = useState<string>("");
  const [tasks, setTasks] = useState<TodayTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  const [newTitle, setNewTitle] = useState("");
  const [newDueTime, setNewDueTime] = useState("08:00");

  const [editingId, setEditingId] = useState<string>("");
  const [editTitle, setEditTitle] = useState("");
  const [editDueTime, setEditDueTime] = useState("");
  const [currentMinutes, setCurrentMinutes] = useState<number>(getCurrentMinutesOfDay());

  useEffect(() => {
    const existing = window.localStorage.getItem(LOCAL_USER_KEY);
    const nextUserId = existing || createBrowserUuid();

    if (!existing) {
      window.localStorage.setItem(LOCAL_USER_KEY, nextUserId);
    }

    setUserId(nextUserId);
  }, []);

  useEffect(() => {
    if (!userId) return;
    void fetchTasks(userId);
  }, [userId]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setCurrentMinutes(getCurrentMinutesOfDay());
    }, 60 * 1000);

    return () => {
      window.clearInterval(timer);
    };
  }, []);

  const sortedTasks = useMemo(
    () => [...tasks].sort((a, b) => a.dueTime.localeCompare(b.dueTime)),
    [tasks],
  );

  async function readApiPayload(response: Response) {
    const raw = await response.text();
    if (!raw) return {};

    try {
      return JSON.parse(raw) as Record<string, unknown>;
    } catch {
      return {
        message:
          "Phản hồi từ server không đúng JSON. Có thể API đang lỗi hoặc chưa migrate database.",
      };
    }
  }

  async function fetchTasks(ownerId: string) {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`/api/today-tasks?userId=${encodeURIComponent(ownerId)}`, {
        cache: "no-store",
      });
      const payload = await readApiPayload(response);

      if (!response.ok) {
        throw new Error(String(payload?.message || "Không tải được lịch hôm nay"));
      }

      setTasks((payload.tasks as TodayTask[]) || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Đã có lỗi không xác định";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function createTask() {
    if (!userId || !newTitle.trim() || !newDueTime) return;

    try {
      const response = await fetch("/api/today-tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId,
          title: newTitle.trim(),
          dueTime: newDueTime,
          status: "TODO",
        }),
      });
      const payload = await readApiPayload(response);

      if (!response.ok) {
        throw new Error(String(payload?.message || "Không tạo được lịch"));
      }

      setTasks((prev) => [...prev, payload.task as TodayTask]);
      setNewTitle("");
      setNewDueTime("08:00");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không tạo được lịch");
    }
  }

  async function saveTask(task: TodayTask, patch?: Partial<TodayTask>) {
    if (!userId) return;

    const title = patch?.title ?? task.title;
    const dueTime = patch?.dueTime ?? task.dueTime;
    const status = (patch?.status ?? task.status) as TaskStatus;

    const response = await fetch(`/api/today-tasks/${task.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId, title, dueTime, status }),
    });

    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(String(payload?.message || "Không cập nhật được lịch"));
    }

    setTasks((prev) =>
      prev.map((item) => (item.id === task.id ? (payload.task as TodayTask) : item)),
    );
  }

  async function removeTask(taskId: string) {
    if (!userId) return;

    try {
      const response = await fetch(
        `/api/today-tasks/${taskId}?userId=${encodeURIComponent(userId)}`,
        { method: "DELETE" },
      );
      const payload = await readApiPayload(response);

      if (!response.ok) {
        throw new Error(String(payload?.message || "Không xoá được lịch"));
      }

      setTasks((prev) => prev.filter((item) => item.id !== taskId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không xoá được lịch");
    }
  }

  return (
    <>
      <div className="glass-panel animate-in mb-3 p-3 sm:p-4">
        <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
          Thêm lịch nhanh
        </p>
        <div className="mt-2 grid gap-2 sm:grid-cols-[1fr_auto_auto]">
          <input
            value={newTitle}
            onChange={(event) => setNewTitle(event.target.value)}
            placeholder="Ví dụ: Uống thuốc sau ăn"
            className="h-9 rounded-lg border border-emerald-900/15 px-2 text-sm outline-none focus:border-emerald-600"
          />
          <input
            type="time"
            value={newDueTime}
            onChange={(event) => setNewDueTime(event.target.value)}
            className="h-9 rounded-lg border border-emerald-900/15 px-2 text-sm outline-none focus:border-emerald-600"
          />
          <button
            type="button"
            className="inline-flex h-9 items-center justify-center rounded-lg bg-[var(--color-primary)] px-3 text-xs font-semibold text-white"
            onClick={() => void createTask()}
          >
            Thêm lịch
          </button>
        </div>
      </div>

      <section className="glass-panel animate-in p-5 sm:p-6">
        <div>
          <p className="eyebrow">Lịch hôm nay</p>
          <h2 className="mt-2 text-lg font-semibold text-[var(--color-primary-deep)]">
            {sortedTasks.length} mục cần theo dõi
          </h2>
        </div>

        {error ? (
          <p className="mt-3 rounded-xl border border-red-300/30 bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
          </p>
        ) : null}

      <ol className="mt-4 grid max-h-[70vh] grid-cols-1 gap-3 overflow-y-auto pr-1 sm:grid-cols-2 xl:grid-cols-3">
        {loading ? <li className="col-span-full text-sm text-slate-500">Đang tải lịch...</li> : null}

        {!loading && sortedTasks.length === 0 ? (
          <li className="col-span-full rounded-2xl border border-emerald-900/10 bg-white p-3 text-sm text-slate-500">
            Chưa có lịch nào cho hôm nay.
          </li>
        ) : null}

        {sortedTasks.map((task) => {
          const isEditing = editingId === task.id;
          const dueMinutes = parseDueTimeToMinutes(task.dueTime);
          const isOverdue =
            task.status !== "DONE" && dueMinutes !== null && dueMinutes < currentMinutes;

          return (
            <li
              key={task.id}
              className={[
                "rounded-2xl border p-3 shadow-sm",
                isOverdue
                  ? "border-amber-300 bg-[linear-gradient(165deg,#fffdf5_0%,#fff8df_100%)]"
                  : "border-emerald-900/10 bg-[linear-gradient(165deg,#ffffff_0%,#f8fcfa_100%)]",
              ].join(" ")}
            >
              {isEditing ? (
                <div className="space-y-2 rounded-xl border border-emerald-900/10 bg-white p-2.5">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-slate-500">
                    Chỉnh sửa lịch
                  </p>
                  <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
                    <input
                      value={editTitle}
                      onChange={(event) => setEditTitle(event.target.value)}
                      className="h-9 w-full rounded-lg border border-emerald-900/15 px-2 text-sm outline-none focus:border-emerald-600"
                    />
                    <input
                      type="time"
                      value={editDueTime}
                      onChange={(event) => setEditDueTime(event.target.value)}
                      className="h-9 w-full rounded-lg border border-emerald-900/15 px-2 text-sm outline-none focus:border-emerald-600"
                    />
                  </div>
                  <div className="flex gap-2 pt-1">
                    <button
                      type="button"
                      className="rounded-lg bg-[var(--color-primary)] px-3 py-1.5 text-xs font-semibold text-white"
                      onClick={async () => {
                        try {
                          await saveTask(task, {
                            title: editTitle.trim() || task.title,
                            dueTime: editDueTime || task.dueTime,
                          });
                          setEditingId("");
                        } catch (err) {
                          setError(err instanceof Error ? err.message : "Không cập nhật được lịch");
                        }
                      }}
                    >
                      Lưu
                    </button>
                    <button
                      type="button"
                      className="rounded-lg border border-emerald-900/20 px-3 py-1.5 text-xs font-semibold text-slate-600"
                      onClick={() => setEditingId("")}
                    >
                      Huỷ
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex items-start justify-between gap-2">
                    <span
                      className={[
                        "inline-flex rounded-full border bg-white px-2.5 py-1 text-[11px] font-semibold tracking-wide",
                        isOverdue ? "border-amber-300 text-amber-700" : "border-emerald-900/15 text-slate-500",
                      ].join(" ")}
                    >
                      {task.dueTime}
                    </span>
                    <div className="flex flex-wrap items-center justify-end gap-1.5">
                      {isOverdue ? (
                        <span className="inline-flex rounded-full border border-amber-300 bg-amber-100 px-2.5 py-1 text-[11px] font-semibold text-amber-800">
                          Quá giờ
                        </span>
                      ) : null}
                      <span
                        className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-medium ${statusTone[task.status]}`}
                      >
                        {statusLabel[task.status]}
                      </span>
                    </div>
                  </div>
                  <p className="mt-2 text-sm font-semibold leading-6 text-slate-900">{task.title}</p>

                  <div className="mt-3 flex flex-wrap gap-1.5 rounded-xl border border-emerald-900/10 bg-white p-1">
                    {statusChoices.map((choice) => {
                      const active = task.status === choice;
                      return (
                        <button
                          key={choice}
                          type="button"
                          className={[
                            "rounded-lg px-2.5 py-1 text-[11px] font-semibold transition",
                            active
                              ? "bg-[var(--color-primary)] text-white"
                              : "text-slate-600 hover:bg-emerald-50",
                          ].join(" ")}
                          onClick={async () => {
                            try {
                              await saveTask(task, { status: choice });
                            } catch (err) {
                              setError(
                                err instanceof Error
                                  ? err.message
                                  : "Không cập nhật được trạng thái",
                              );
                            }
                          }}
                        >
                          {choice === "TODO" ? "Chưa hoàn thành" : "Đã hoàn thành"}
                        </button>
                      );
                    })}
                  </div>

                  <div className="mt-2 flex flex-wrap gap-2">
                    <button
                      type="button"
                      className="rounded-lg border border-emerald-900/20 px-2 py-1 text-xs font-semibold text-slate-600"
                      onClick={() => {
                        setEditingId(task.id);
                        setEditTitle(task.title);
                        setEditDueTime(task.dueTime);
                      }}
                    >
                      Sửa
                    </button>
                    <button
                      type="button"
                      className="rounded-lg border border-red-300/40 bg-red-50 px-2 py-1 text-xs font-semibold text-red-700"
                      onClick={() => void removeTask(task.id)}
                    >
                      Xoá
                    </button>
                  </div>
                </>
              )}
            </li>
          );
        })}
        </ol>
      </section>
    </>
  );
}
