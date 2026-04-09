const state = {
  schedule: [],
  lastScanResult: null,
  chatHistory: [],
  imageUrl: "",
};

const storage = {
  load(key, fallback) {
    try {
      const raw = window.localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch (error) {
      return fallback;
    }
  },
  save(key, value) {
    window.localStorage.setItem(key, JSON.stringify(value));
  },
};

function navigate(route) {
  window.location.hash = route;
}

function routeName() {
  return window.location.hash.replace("#", "") || "home";
}

function api(path, options = {}) {
  return fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  }).then(async (response) => {
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Có lỗi xảy ra khi gọi API.");
    }
    return data;
  });
}

function apiForm(path, body) {
  return fetch(path, {
    method: "POST",
    body,
  }).then(async (response) => {
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Có lỗi xảy ra khi gọi API.");
    }
    return data;
  });
}

function escapeHtml(text) {
  return String(text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function render() {
  const route = routeName();
  document.body.setAttribute("data-route", route);
  document.querySelectorAll(".tab-bar a").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === route);
  });

  const template = document.getElementById(`${route}-template`) || document.getElementById("home-template");
  const app = document.getElementById("app");
  app.innerHTML = template.innerHTML;

  if (route === "home") renderHome();
  if (route === "scan") renderScan();
  if (route === "crosscheck") renderCrosscheck();
  if (route === "chat") renderChat();

  document.querySelectorAll("[data-go]").forEach((button) => {
    button.addEventListener("click", () => navigate(button.dataset.go));
  });
}

function syncClock() {
  const now = new Date();
  const time = now.toLocaleTimeString("vi-VN", { hour12: false });
  const date = now.toLocaleDateString("vi-VN");
  document.getElementById("clockTime").textContent = time;
  document.getElementById("clockDate").textContent = date;
}

function renderHome() {
  return;
}

function bannerClass(status) {
  if (status === "success") return "success";
  if (status === "partial") return "warning";
  return "danger";
}

function renderScan() {
  const scanStatus = document.getElementById("scanStatus");
  const scanBtn = document.getElementById("scanBtn");
  const scanFile = document.getElementById("scanFile");
  const selectedFileName = document.getElementById("selectedFileName");
  const scanImagePreview = document.getElementById("scanImagePreview");

  if (state.lastScanResult) {
    scanStatus.className = `status-banner ${bannerClass(state.lastScanResult.status)}`;
    scanStatus.textContent = `${state.lastScanResult.message} Đang chuyển sang màn hình đối chiếu...`;
  } else {
    scanStatus.className = "status-banner info";
    scanStatus.textContent = "Chưa quét đơn thuốc.";
  }

  scanFile.addEventListener("change", () => {
    const [file] = scanFile.files;
    if (!file) {
      selectedFileName.textContent = "Chưa chọn ảnh nào.";
      scanImagePreview.classList.add("hidden");
      scanImagePreview.removeAttribute("src");
      return;
    }
    selectedFileName.textContent = `Đã chọn: ${file.name}`;
    scanImagePreview.src = URL.createObjectURL(file);
    scanImagePreview.classList.remove("hidden");
  });

  scanBtn.addEventListener("click", async () => {
    const [file] = scanFile.files;
    if (!file) {
      scanStatus.className = "status-banner danger";
      scanStatus.textContent = "Bạn hãy chọn ảnh đơn thuốc trước khi quét.";
      return;
    }

    scanBtn.disabled = true;
    scanStatus.className = "status-banner info";
    scanStatus.textContent = "Hệ thống đang tải ảnh lên và gọi Gemini để OCR đơn thuốc...";
    try {
      const formData = new FormData();
      formData.append("file", file);
      const data = await apiForm("/api/scan", formData);
      state.lastScanResult = data;
      state.imageUrl = data.uploaded_image_url || state.imageUrl;
      storage.save("medreminder.lastScanResult", data);
      storage.save("medreminder.imageUrl", state.imageUrl);
      scanStatus.className = `status-banner ${bannerClass(data.status)}`;
      scanStatus.textContent = `${data.message} Đang chuyển sang màn hình đối chiếu...`;
      window.setTimeout(() => navigate("crosscheck"), 450);
    } catch (error) {
      scanStatus.className = "status-banner danger";
      scanStatus.textContent = error.message;
    } finally {
      scanBtn.disabled = false;
    }
  });
}

function medicationInput(label, value, key, index, full = false) {
  return `
    <label class="${full ? "full" : ""}">
      ${label}
      <input data-med-index="${index}" data-med-key="${key}" value="${escapeHtml(value ?? "")}">
    </label>
  `;
}

function renderCrosscheck() {
  const badge = document.getElementById("crosscheckBadge");
  const alert = document.getElementById("crosscheckAlert");
  const form = document.getElementById("medicationForm");
  const saveBtn = document.getElementById("saveCrosscheckBtn");
  const checkbox = document.getElementById("confirmCheckbox");
  const image = document.getElementById("prescriptionImage");

  image.src = state.imageUrl || "";

  const result = state.lastScanResult;
  if (!result) {
    badge.textContent = "Chưa có dữ liệu";
    form.innerHTML = '<div class="empty-state">Bạn hãy quét đơn thuốc trước khi vào màn hình này.</div>';
  } else {
    badge.textContent = result.status.toUpperCase();
    alert.className = `status-banner ${bannerClass(result.status)}`;
    const reviewFlags = (result.review_flags || []).length
      ? ` Cờ kiểm tra: ${(result.review_flags || []).join(", ")}.`
      : "";
    alert.textContent = `${result.message}${reviewFlags}`;

    if (!result.medications.length) {
      form.innerHTML = '<div class="empty-state">Không có thuốc nào đủ chắc chắn để hiển thị.</div>';
    } else {
      form.innerHTML = result.medications.map((med, index) => `
        <article class="med-card">
          <div class="med-main">
            <strong>${escapeHtml(med.name || "UNCLEAR")}</strong>
            <div class="med-extra">Confidence: ${med.confidence ?? "n/a"} ${med.uncertain_fields?.length ? `• Chưa chắc: ${escapeHtml(med.uncertain_fields.join(", "))}` : ""}</div>
            <div class="pill-row">
              ${med.is_prn ? '<span class="pill warning">Thuốc dùng khi cần</span>' : ""}
              ${med.route ? `<span class="pill">${escapeHtml(med.route)}</span>` : ""}
              ${med.frequency_text ? `<span class="pill">${escapeHtml(med.frequency_text)}</span>` : ""}
            </div>
          </div>
          <div class="med-grid">
            ${medicationInput("Tên thuốc", med.name, "name", index)}
            ${medicationInput("Hàm lượng", med.strength, "strength", index)}
            ${medicationInput("Liều mỗi lần", med.dosage_per_use, "dosage_per_use", index)}
            ${medicationInput("Số ngày", med.days, "days", index)}
            ${medicationInput("Đường dùng", med.route, "route", index)}
            ${medicationInput("Tần suất", med.frequency_text, "frequency_text", index)}
            ${medicationInput("Ghi chú thời điểm", med.timing_notes, "timing_notes", index, true)}
          </div>
        </article>
      `).join("");

      form.querySelectorAll("input[data-med-index]").forEach((input) => {
        input.addEventListener("input", (event) => {
          const medIndex = Number(event.target.dataset.medIndex);
          const key = event.target.dataset.medKey;
          state.lastScanResult.medications[medIndex][key] = event.target.value;
          storage.save("medreminder.lastScanResult", state.lastScanResult);
        });
      });
    }
  }

  saveBtn.addEventListener("click", async () => {
    if (!state.lastScanResult) {
      alert.className = "status-banner danger";
      alert.textContent = "Chưa có dữ liệu quét để lưu.";
      return;
    }
    try {
      const payload = await api("/api/crosscheck/save", {
        method: "POST",
        body: JSON.stringify({
          confirmed: checkbox.checked,
          medications: state.lastScanResult.medications,
        }),
      });
      alert.className = "status-banner success";
      alert.textContent = payload.message;
    } catch (error) {
      alert.className = "status-banner danger";
      alert.textContent = error.message;
    }
  });
}

function appendChatBubble(message, role, level = "normal") {
  state.chatHistory.push({ message, role, level });
  storage.save("medreminder.chatHistory", state.chatHistory);
  renderChatMessages();
}

function renderChatMessages() {
  const messages = document.getElementById("chatMessages");
  messages.innerHTML = state.chatHistory.map((item) => `
    <div class="chat-bubble ${item.role === "user" ? "user" : item.level}">
      ${escapeHtml(item.message)}
    </div>
  `).join("");
  messages.scrollTop = messages.scrollHeight;
}

function renderChat() {
  if (!state.chatHistory.length) {
    state.chatHistory = [
      {
        role: "assistant",
        level: "normal",
        message: "Xin chào. Hôm nay sức khỏe của bạn sau khi dùng thuốc thế nào?",
      },
    ];
    storage.save("medreminder.chatHistory", state.chatHistory);
  }

  renderChatMessages();

  const form = document.getElementById("chatForm");
  const input = document.getElementById("chatInput");
  const emergencyCard = document.getElementById("emergencyCard");
  const emergencyBtn = document.getElementById("emergencyBtn");

  const latestAssistant = [...state.chatHistory].reverse().find((item) => item.role === "assistant");
  const showEmergency = latestAssistant?.level === "danger";
  emergencyCard.classList.toggle("hidden", !showEmergency);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    appendChatBubble(message, "user");
    input.value = "";

    try {
      const data = await api("/api/chat", {
        method: "POST",
        body: JSON.stringify({ message }),
      });
      appendChatBubble(data.reply, "assistant", data.level);
      emergencyCard.classList.toggle("hidden", !data.show_emergency_button);
    } catch (error) {
      appendChatBubble(error.message, "assistant", "danger");
    }
  });

  emergencyBtn.addEventListener("click", () => {
    appendChatBubble(
      "Vinmec Times City: 458 Minh Khai, Hai Bà Trưng, Hà Nội. Hotline: 024 3974 3556.\nBản demo không tự động gọi, vui lòng liên hệ 115 nếu có tình huống khẩn cấp.",
      "assistant",
      "danger"
    );
    emergencyCard.classList.add("hidden");
  });
}

async function loadSchedule(force = false) {
  if (!force) {
    const cached = storage.load("medreminder.schedule", null);
    if (cached?.length) {
      state.schedule = cached;
      return;
    }
  }
  const data = await api("/api/schedule");
  state.schedule = data.items;
  storage.save("medreminder.schedule", state.schedule);
}

async function loadPrescriptionImage() {
  const data = await api("/api/prescription-image");
  state.imageUrl = data.url;
}

async function boot() {
  state.lastScanResult = null;
  state.chatHistory = storage.load("medreminder.chatHistory", []);
  state.imageUrl = "";
  window.localStorage.removeItem("medreminder.lastScanResult");
  window.localStorage.removeItem("medreminder.imageUrl");
  await loadSchedule();
  syncClock();
  setInterval(syncClock, 1000);
  window.addEventListener("hashchange", render);
  render();
}

boot().catch((error) => {
  document.getElementById("app").innerHTML = `
    <section class="panel">
      <div class="status-banner danger">${escapeHtml(error.message)}</div>
    </section>
  `;
});
