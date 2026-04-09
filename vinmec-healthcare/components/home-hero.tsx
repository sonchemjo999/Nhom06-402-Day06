"use client";

import Link from "next/link";
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

export function HomeHero() {
  const [userId, setUserId] = useState<string>("");
  const [tasks, setTasks] = useState<TodayTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  const [newTitle, setNewTitle] = useState("");
  const [newDueTime, setNewDueTime] = useState("08:00");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const [editingId, setEditingId] = useState<string>("");
  const [editTitle, setEditTitle] = useState("");
  const [editDueTime, setEditDueTime] = useState("");

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

  const sortedTasks = useMemo(
    () => [...tasks].sort((a, b) => a.dueTime.localeCompare(b.dueTime)),
    [tasks],
  );
  const taskCount = sortedTasks.length;

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
      setIsCreateModalOpen(false);
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

    setTasks((prev) => prev.map((item) => (item.id === task.id ? (payload.task as TodayTask) : item)));
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
    <section className="mx-auto grid w-full max-w-6xl gap-4 lg:grid-cols-[1.3fr_1fr]">
      <div className="glass-panel animate-in relative overflow-hidden p-6 sm:p-8">
        <div
          className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full"
          style={{
            background:
              "radial-gradient(circle, rgba(10,91,63,0.18) 0%, rgba(10,91,63,0) 70%)",
          }}
        />

        <p className="eyebrow">Trợ lý chăm sóc cá nhân</p>
        <h1 className="serif-title mt-3 max-w-xl text-3xl leading-tight text-[var(--color-primary-deep)] sm:text-5xl">
          Một nơi để theo dõi thuốc, triệu chứng và an toàn mỗi ngày.
        </h1>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-[var(--color-ink-soft)] sm:text-base">
          Giao diện được thiết kế cho bệnh nhân và người nhà: ít nhiễu, rõ việc
          cần làm ngay, và luôn có lối tắt đến hỗ trợ khẩn khi cần.
        </p>

        <div className="mt-7 flex flex-wrap gap-3">
          <Link
            className="rounded-2xl bg-[var(--color-primary)] px-5 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:opacity-95"
            href="/chat"
          >
            Trò chuyện với AI Assistant
          </Link>
          <Link
            className="rounded-2xl border border-emerald-900/15 bg-white px-5 py-3 text-sm font-semibold text-[var(--color-primary)] transition hover:bg-emerald-50"
            href="/demo"
          >
            Kiểm tra kết nối hệ thống
          </Link>
        </div>
      </div>

      <aside className="glass-panel animate-in p-5 [animation-delay:140ms] sm:p-6">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="eyebrow">Lịch hôm nay</p>
            <h2 className="mt-2 text-lg font-semibold text-[var(--color-primary-deep)]">
              {taskCount} mục cần theo dõi
            </h2>
          </div>
          <button
            type="button"
            className="inline-flex h-10 items-center rounded-xl bg-[var(--color-primary)] px-4 text-sm font-semibold text-white"
            onClick={() => setIsCreateModalOpen(true)}
          >
            + Thêm lịch
          </button>
        </div>

        {error ? (
          <p className="mt-3 rounded-xl border border-red-300/30 bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
          </p>
        ) : null}

        <ol className="mt-4 max-h-[21rem] space-y-3 overflow-y-auto pr-1">
          {loading ? <li className="text-sm text-slate-500">Đang tải lịch...</li> : null}

          {!loading && sortedTasks.length === 0 ? (
            <li className="rounded-2xl border border-emerald-900/10 bg-white p-3 text-sm text-slate-500">
              Chưa có lịch nào cho hôm nay.
            </li>
          ) : null}

          {sortedTasks.map((task) => {
            const isEditing = editingId === task.id;

            return (
              <li
                key={task.id}
                className="rounded-2xl border border-emerald-900/10 bg-[linear-gradient(165deg,#ffffff_0%,#f8fcfa_100%)] p-3 shadow-sm"
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
                      <span className="inline-flex rounded-full border border-emerald-900/15 bg-white px-2.5 py-1 text-[11px] font-semibold tracking-wide text-slate-500">
                        {task.dueTime}
                      </span>
                      <span
                        className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-medium ${statusTone[task.status]}`}
                      >
                        {statusLabel[task.status]}
                      </span>
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
      </aside>

      <div className="glass-panel animate-in p-5 [animation-delay:200ms] sm:p-6 lg:col-span-2">
        <div className="grid gap-3 sm:grid-cols-3">
          <article className="rounded-2xl border border-emerald-900/10 bg-[linear-gradient(160deg,#f7fffb_0%,#ffffff_100%)] p-4">
            <h3 className="text-sm font-semibold text-[var(--color-primary-deep)]">Nhắc thuốc đúng giờ</h3>
            <p className="mt-2 text-sm leading-6 text-[var(--color-ink-soft)]">
              Xác nhận uống, hoãn 15 phút, hoặc báo sai liều ngay trong một màn hình.
            </p>
          </article>
          <article className="rounded-2xl border border-amber-400/25 bg-[linear-gradient(160deg,#fffbef_0%,#ffffff_100%)] p-4">
            <h3 className="text-sm font-semibold text-[var(--color-primary-deep)]">Theo dõi triệu chứng</h3>
            <p className="mt-2 text-sm leading-6 text-[var(--color-ink-soft)]">
              Ghi nhận thay đổi sức khỏe nhanh, có ưu tiên cảnh báo khi dấu hiệu bất thường.
            </p>
          </article>
          <article className="rounded-2xl border border-rose-300/30 bg-[linear-gradient(160deg,#fff4f4_0%,#ffffff_100%)] p-4">
            <h3 className="text-sm font-semibold text-[var(--color-primary-deep)]">Hỗ trợ khẩn cấp</h3>
            <p className="mt-2 text-sm leading-6 text-[var(--color-ink-soft)]">
              Mở hướng dẫn xử lý ngay và tìm cơ sở Vinmec gần nhất khi cần hỗ trợ gấp.
            </p>
          </article>
        </div>
      </div>

      {isCreateModalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/35 px-4">
          <div className="w-full max-w-md rounded-2xl border border-emerald-900/10 bg-white p-5 shadow-xl">
            <h3 className="text-base font-semibold text-[var(--color-primary-deep)]">
              Thêm lịch mới
            </h3>
            <p className="mt-1 text-sm text-slate-600">
              Nhập việc cần làm và thời gian trong hôm nay.
            </p>

            <div className="mt-4 space-y-3">
              <input
                value={newTitle}
                onChange={(event) => setNewTitle(event.target.value)}
                placeholder="Ví dụ: Uống thuốc sau ăn"
                className="h-10 w-full rounded-xl border border-emerald-900/15 px-3 text-sm outline-none focus:border-emerald-600"
              />
              <input
                type="time"
                value={newDueTime}
                onChange={(event) => setNewDueTime(event.target.value)}
                className="h-10 w-full rounded-xl border border-emerald-900/15 px-3 text-sm outline-none focus:border-emerald-600"
              />
            </div>

            <div className="mt-5 flex justify-end gap-2">
              <button
                type="button"
                className="h-10 rounded-xl border border-emerald-900/20 px-4 text-sm font-semibold text-slate-600"
                onClick={() => setIsCreateModalOpen(false)}
              >
                Huỷ
              </button>
              <button
                type="button"
                className="h-10 rounded-xl bg-[var(--color-primary)] px-4 text-sm font-semibold text-white"
                onClick={() => void createTask()}
              >
                Lưu lịch
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
