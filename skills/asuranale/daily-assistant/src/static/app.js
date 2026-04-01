/* ============================================================
   日常小助手 Web UI — 前端逻辑
   ============================================================ */

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ── 状态 ──

let currentDate = new Date().toISOString().slice(0, 10);
let lang = "zh";

const i18n = {
  "app-title":     { zh: "日常小助手",           en: "Daily Assistant" },
  "lbl-tasks":     { zh: "📥 今日任务",          en: "📥 Today's Tasks" },
  "lbl-overdue":   { zh: "🔴 超期任务",          en: "🔴 Overdue" },
  "lbl-history":   { zh: "📈 7 天趋势",          en: "📈 7-Day Trend" },
  "lbl-split":     { zh: "✂️ 拆分提醒",          en: "✂️ Split Alerts" },
  "lbl-done":      { zh: "已完成",               en: "Done" },
  "lbl-todo":      { zh: "未完成",               en: "To do" },
  "lbl-rate":      { zh: "完成率",               en: "Rate" },
  "empty-no-file": { zh: "📭 当日文件不存在。\n点击「继承昨日任务」创建。",
                     en: "📭 No file for this date.\nClick 'Inherit' to create." },
  "empty-no-task": { zh: "📝 暂无任务，在下方添加。",
                     en: "📝 No tasks yet. Add one below." },
  "loading":       { zh: "加载中...",             en: "Loading..." },
  "confirm-del":   { zh: "确定删除这个任务？",    en: "Delete this task?" },
  "toast-toggled": { zh: "任务状态已更新",        en: "Task updated" },
  "toast-added":   { zh: "任务已添加",            en: "Task added" },
  "toast-deleted": { zh: "任务已删除",            en: "Task deleted" },
  "toast-inherit-ok": { zh: "继承完成",           en: "Inheritance done" },
  "toast-review-ok":  { zh: "回顾已生成",         en: "Review generated" },
  "toast-lang":    { zh: "语言已切换为中文",       en: "Language switched to English" },
};

function T(key) { return (i18n[key] || {})[lang] || key; }

// ── API ──

async function api(path, opts = {}) {
  const url = path.startsWith("/") ? path : `/api/${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  return res.json();
}

// ── 初始化 ──

async function init() {
  const cfg = await api("config");
  lang = cfg.language || "zh";
  $("#lang-select").value = lang;
  applyLang();

  $("#date-picker").value = currentDate;

  // 事件绑定
  $("#lang-select").addEventListener("change", onLangChange);
  $("#date-picker").addEventListener("change", onDateChange);
  $("#btn-prev").addEventListener("click", () => shiftDate(-1));
  $("#btn-next").addEventListener("click", () => shiftDate(1));
  $("#btn-today").addEventListener("click", goToday);
  $("#btn-add").addEventListener("click", addTask);
  $("#new-task-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") addTask();
  });
  $("#btn-inherit").addEventListener("click", inheritTasks);
  $("#btn-review").addEventListener("click", generateReview);

  loadAll();
}

// ── 语言切换 ──

async function onLangChange() {
  lang = $("#lang-select").value;
  await api("config", { method: "PUT", body: { language: lang } });
  applyLang();
  loadAll();
  toast(T("toast-lang"), "success");
}

function applyLang() {
  // 按 id 翻译
  for (const [id, texts] of Object.entries(i18n)) {
    const el = document.getElementById(id);
    if (el) el.textContent = texts[lang] || texts.zh;
  }
  // data-zh / data-en 属性
  $$("[data-zh]").forEach((el) => {
    const text = lang === "en" ? el.dataset.en : el.dataset.zh;
    if (text) {
      if (el.tagName === "OPTION") el.textContent = text;
      else if (el.tagName === "INPUT") return; // placeholder 单独处理
      else el.textContent = text;
    }
  });
  // placeholder
  $$("[data-placeholder-zh]").forEach((el) => {
    el.placeholder = lang === "en" ? el.dataset.placeholderEn : el.dataset.placeholderZh;
  });
  document.documentElement.lang = lang === "en" ? "en" : "zh";
}

// ── 日期导航 ──

function onDateChange() {
  currentDate = $("#date-picker").value;
  loadAll();
}

function shiftDate(delta) {
  const d = new Date(currentDate);
  d.setDate(d.getDate() + delta);
  currentDate = d.toISOString().slice(0, 10);
  $("#date-picker").value = currentDate;
  loadAll();
}

function goToday() {
  currentDate = new Date().toISOString().slice(0, 10);
  $("#date-picker").value = currentDate;
  loadAll();
}

// ── 数据加载 ──

async function loadAll() {
  await Promise.all([loadTasks(), loadOverdue(), loadHistory(), loadSplit()]);
}

async function loadTasks() {
  const data = await api(`tasks?date=${currentDate}`);

  const list = $("#task-list");

  if (!data.exists) {
    list.innerHTML = `<div class="empty-state"><p>${T("empty-no-file")}</p></div>`;
    updateStats([], []);
    return;
  }

  if (data.tasks.length === 0) {
    list.innerHTML = `<div class="empty-state"><p>${T("empty-no-task")}</p></div>`;
    updateStats([], []);
    return;
  }

  list.innerHTML = data.tasks.map((t) => renderTask(t)).join("");
  bindTaskEvents();

  const done = data.tasks.filter((t) => t.completed);
  const todo = data.tasks.filter((t) => !t.completed);
  updateStats(done, todo);
}

function renderTask(t) {
  const checkedCls = t.completed ? "checked" : "";
  const doneCls = t.completed ? "completed" : "";
  const check = t.completed ? "✓" : "";

  let metaHtml = "";
  if (t.est_minutes) metaHtml += `<span class="meta-tag">⏱️ ${t.est_minutes}min</span>`;
  if (t.deadline) {
    let cls = "";
    if (t.days_until !== null && t.days_until < 0) cls = "overdue";
    else if (t.days_until === 0) cls = "today";
    metaHtml += `<span class="meta-tag ${cls}">📅 ${t.deadline}</span>`;
  }
  if (t.priority !== "medium") {
    const pMap = { highest: "priority-highest", high: "priority-high", low: "" };
    const pLabel = { highest: "⏫", high: "🔼", low: "🔽" };
    metaHtml += `<span class="meta-tag ${pMap[t.priority] || ""}">${pLabel[t.priority] || ""}</span>`;
  }

  return `
    <div class="task-item ${doneCls}" data-line="${t.line}">
      <div class="task-checkbox ${checkedCls}" data-action="toggle">${check}</div>
      <div class="task-body">
        <div class="task-desc">${escHtml(t.description)}</div>
        ${metaHtml ? `<div class="task-meta">${metaHtml}</div>` : ""}
      </div>
      <button class="task-delete" data-action="delete" title="Delete">×</button>
    </div>`;
}

function bindTaskEvents() {
  $$(".task-checkbox").forEach((el) => {
    el.addEventListener("click", () => {
      const line = parseInt(el.closest(".task-item").dataset.line);
      toggleTask(line);
    });
  });
  $$(".task-delete").forEach((el) => {
    el.addEventListener("click", () => {
      if (!confirm(T("confirm-del"))) return;
      const line = parseInt(el.closest(".task-item").dataset.line);
      deleteTask(line);
    });
  });
}

function updateStats(done, todo) {
  const total = done.length + todo.length;
  $("#stat-done").textContent = done.length;
  $("#stat-todo").textContent = todo.length;
  $("#stat-rate").textContent = total > 0 ? Math.round((done.length / total) * 100) + "%" : "—";
  // 完成率颜色
  const rate = total > 0 ? done.length / total : 0;
  $("#stat-rate").style.color = rate >= 0.8 ? "var(--green)" : rate >= 0.5 ? "var(--orange)" : "var(--accent)";
}

// ── 超期 ──

async function loadOverdue() {
  const data = await api(`overdue?date=${currentDate}`);
  const el = $("#overdue-list");

  if (data.overdue.length === 0) {
    el.innerHTML = `<span class="muted">${lang === "en" ? "No overdue" : "无超期"} ✅</span>`;
    return;
  }

  el.innerHTML = data.overdue
    .map(
      (o) =>
        `<div class="overdue-item"><span class="overdue-date">${o.date}</span> — ${o.tasks.length} ${lang === "en" ? "tasks" : "个任务"}</div>`
    )
    .join("");
}

// ── 7 天趋势 ──

async function loadHistory() {
  const data = await api("history");
  const chart = $("#history-chart");

  const maxTotal = Math.max(...data.history.map((d) => d.total), 1);

  chart.innerHTML = data.history
    .reverse()
    .map((d) => {
      const doneH = Math.round((d.completed / maxTotal) * 70);
      const todoH = Math.round((d.uncompleted / maxTotal) * 70);
      const label = d.date.slice(5); // MM-DD
      return `
        <div class="history-bar">
          <div class="bar-count">${d.total > 0 ? d.completed + "/" + d.total : ""}</div>
          <div class="bar-stack bar-todo" style="height:${todoH}px"></div>
          <div class="bar-stack bar-done" style="height:${doneH}px"></div>
          <div class="bar-label">${label}</div>
        </div>`;
    })
    .join("");
}

// ── 拆分提醒 ──

async function loadSplit() {
  const data = await api(`split?date=${currentDate}`);
  const el = $("#split-list");

  if (data.issues.length === 0) {
    el.innerHTML = `<span class="muted">${lang === "en" ? "All good" : "无需拆分"} ✅</span>`;
    return;
  }

  el.innerHTML = data.issues
    .map((i) => {
      const info =
        i.type === "too_long"
          ? `⚠️ ${i.minutes}min`
          : `❓ ${lang === "en" ? "no estimate" : "无时间"}`;
      return `<div class="split-item">${escHtml(i.description)} — ${info}</div>`;
    })
    .join("");
}

// ── 任务操作 ──

async function toggleTask(line) {
  const data = await api("tasks/toggle", {
    method: "POST",
    body: { date: currentDate, line },
  });
  if (data.success) {
    toast(T("toast-toggled"), "success");
    loadAll();
  }
}

async function deleteTask(line) {
  const data = await api("tasks/delete", {
    method: "POST",
    body: { date: currentDate, line },
  });
  if (data.success) {
    toast(T("toast-deleted"), "success");
    loadAll();
  }
}

async function addTask() {
  const desc = $("#new-task-input").value.trim();
  if (!desc) return;

  const timeVal = $("#new-task-time").value;
  const est = timeVal ? parseInt(timeVal) : null;
  const priority = $("#new-task-priority").value;

  const data = await api("tasks/create", {
    method: "POST",
    body: {
      date: currentDate,
      description: desc,
      est_minutes: est,
      priority,
    },
  });

  if (data.success) {
    $("#new-task-input").value = "";
    $("#new-task-time").value = "";
    $("#new-task-priority").value = "medium";
    toast(T("toast-added"), "success");
    loadAll();
  }
}

async function inheritTasks() {
  const data = await api("inherit", {
    method: "POST",
    body: { date: currentDate },
  });
  toast(data.message || T("toast-inherit-ok"), data.success ? "success" : "error");
  loadAll();
}

async function generateReview() {
  const data = await api("review", {
    method: "POST",
    body: { date: currentDate },
  });
  toast(data.message || data.review?.slice(0, 60) || T("toast-review-ok"),
    data.success ? "success" : "error");
}

// ── 工具 ──

function escHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function toast(msg, type = "success") {
  const el = $("#toast");
  el.textContent = msg;
  el.className = `toast ${type}`;
  setTimeout(() => el.classList.add("hidden"), 2500);
}

// ── 启动 ──

document.addEventListener("DOMContentLoaded", init);
