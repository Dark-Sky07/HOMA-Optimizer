"use strict";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const icon = (name, className = "") => `<svg${className ? ` class="${className}"` : ""} aria-hidden="true"><use href="#i-${name}"></use></svg>`;
const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
}[character]));

const translations = {
  fa: {
    workspace: "فضای کاری", navOverview: "داشبورد", navOptimization: "مرکز بهینه‌سازی", navDiagnostics: "عیب‌یابی و آزمون", navActivity: "رویدادها",
    coreTagline: "سبک‌تر، سریع‌تر، همیشه آمادهٔ پرواز.", connecting: "در حال اتصال به هسته", projectPage: "صفحهٔ پروژه در گیت‌هاب", connectingShort: "در حال اتصال",
    overviewTitle: "نمای کلی سرور", overviewSubtitle: "همهٔ نشانه‌های حیاتی سرور، در یک نگاه.", runAudit: "اجرای ممیزی سیستم",
    heroKicker: "متولد شده برای اوج‌گرفتن", heroTitle: "سرور تو،<br>در اوجِ پرواز.", heroText: "بهینه‌سازی هوشمند شبکه، پایش لحظه‌ای و محافظت مداوم؛ یکپارچه در مرکز فرمان HOMA.",
    optimizeNow: "بهینه‌سازی سرور", previewChanges: "پیش‌نمایش تغییرات", panelSafe: "ایمن برای پنل و کاربران", realtime: "بلادرنگ", systemHealth: "سلامت سیستم", collectingData: "در حال دریافت اطلاعات",
    uptime: "مدت روشن بودن", kernel: "کرنل", processor: "پردازنده", loadAverage: "میانگین بار", memory: "حافظه", used: "مصرف‌شده", disk: "فضای دیسک", available: "آزاد",
    connections: "اتصال‌های فعال", networkInterface: "کارت شبکه", liveTraffic: "ترافیک زنده", networkPulse: "نبض شبکه", download: "دریافت", upload: "ارسال",
    waitingForTraffic: "در انتظار نخستین نمونه‌های ترافیک", lastMinute: "۶۰ نمونهٔ اخیر", autoRefresh: "به‌روزرسانی خودکار", protectionLayer: "لایه‌های محافظ", flightSystems: "سامانه‌های پرواز",
    oneClick: "تنها با یک کلیک", quickActions: "دسترسی سریع", newBackup: "پشتیبان‌گیری تازه", newBackupHint: "ثبت یک نسخهٔ امن از پنل", speedTest: "سنجش سرعت", speedTestHint: "بررسی پهنای باند سرور",
    portScan: "بررسی پورت‌ها", portScanHint: "نقشهٔ پورت‌ها و فایروال", auditTrail: "ردپای عملیات", recentActivity: "رویدادهای اخیر", viewAll: "مشاهدهٔ همه", noActivity: "هنوز عملیاتی ثبت نشده است.",
    optimizationTitle: "مرکز بهینه‌سازی", optimizationSubtitle: "قدرت سرور را با ابزارهای دقیق و قابل‌کنترل آزاد کنید.", fullSuite: "سوئیت کامل HOMA", fullOptimization: "بهینه‌سازی یک‌مرحله‌ای سرور",
    fullOptimizationText: "شبکه، حافظه، امنیت، زمان‌بند و نگهبان را در یک فرایند هدایت‌شده ارتقا دهید.", startSuite: "آغاز سوئیت کامل", individualModules: "ماژول‌های مستقل", individualModulesHint: "پیش از اجرای تغییرات، تأیید شما دریافت می‌شود.",
    diagnosticsTitle: "عیب‌یابی و آزمون", diagnosticsSubtitle: "سرور را بسنجید، بدون آنکه پیکربندی آن را تغییر دهید.", readOnlyTools: "ابزارهای فقط‌خواندنی", diagnosticNote: "نتایج در پنجرهٔ عملیات به‌صورت زنده نمایش داده می‌شوند. آزمون‌های شبکه ممکن است چند لحظه طول بکشند.",
    activityTitle: "رویدادها و عملیات", activitySubtitle: "وضعیت و خروجی تمام فرایندهای این نشست پنل.", refreshList: "به‌روزرسانی فهرست", noActivityYet: "رویدادی وجود ندارد", noActivityDescription: "نخستین ممیزی یا بهینه‌سازی را اجرا کنید تا جزئیات آن اینجا ثبت شود.",
    footerSafety: "طراحی‌شده برای کنترل دقیق و عملکرد پایدار", confirmationWarning: "این عملیات تنظیمات سرور را تغییر می‌دهد. از دسترسی پایدار به سرور مطمئن باشید.", cancel: "انصراف", confirmRun: "تأیید و اجرا", backToPanel: "بازگشت به پنل",
    authText: "برای ورود به مرکز فرمان، نشانهٔ دسترسی پنل را وارد کنید.", accessToken: "نشانهٔ دسترسی", authError: "نشانهٔ دسترسی معتبر نیست.", unlockPanel: "ورود امن به پنل", authHint: "نشانه در فایل /etc/homa/panel.env روی سرور ذخیره شده است.",
    updateSuite: "ارتقای سوئیت HOMA", updateSuiteText: "دریافت تازه‌ترین اسکریپت‌ها و پنل از مخزن رسمی، با حفظ نشانهٔ دسترسی و تنظیمات شما.", officialSource: "منبع رسمی", checkAndUpdate: "به‌روزرسانی و راه‌اندازی مجدد",
    restartTitle: "هما برای پروازی تازه آماده می‌شود", restartText: "به‌روزرسانی نصب شد؛ پنل در حال راه‌اندازی مجدد و اتصال خودکار است.", retryConnection: "تلاش دوباره برای اتصال", updateWarning: "اسکریپت‌ها و پنل از مخزن رسمی HOMA جایگزین می‌شوند. نشانهٔ دسترسی حفظ می‌شود و پنل پس از نصب، یک بار راه‌اندازی مجدد خواهد شد.",
    live: "متصل و زنده", disconnected: "ارتباط قطع شد", coreConnected: "هستهٔ HOMA متصل است", coreDisconnected: "ارتباط با هسته برقرار نیست", excellentHealth: "وضعیت سرور عالی است", attentionHealth: "مصرف منابع نیازمند توجه است",
    controlMode: "CONTROL MODE", readOnlyMode: "READ ONLY", rootRequiredMode: "ROOT REQUIRED", coreCount: "هسته", day: "روز", hour: "ساعت", minute: "دقیقه",
    active: "فعال", inactive: "غیرفعال", failed: "خطا", unknown: "نامشخص", not_detected: "شناسایی نشد", activating: "در حال فعال‌سازی",
    servicePanel: "پنل 3x-ui / Xray", serviceNetwork: "شبکه و BBR", serviceWatchdog: "نگهبان خودکار", serviceScheduler: "زمان‌بند هوشمند", serviceSecurity: "محافظ امنیتی", serviceClient: "پایداری اتصال کاربر",
    run: "اجرای ماژول", viewOutput: "مشاهدهٔ خروجی", safeTag: "READ ONLY", optimizeTag: "OPTIMIZE", readOnlyBlocked: "در حالت فقط‌خواندنی، تغییرات سرور غیرفعال است.", rootRequired: "برای این عملیات، پنل باید با دسترسی root اجرا شود.", operationInProgress: "یک عملیات دیگر در حال اجراست.",
    queued: "در صف", running: "در حال اجرا", succeeded: "موفق", failedStatus: "ناموفق", noOutput: "هنوز خروجی ثبت نشده است…", operationStarted: "عملیات آغاز شد؛ خروجی زنده باز است.", operationSucceeded: "عملیات با موفقیت به پایان رسید.", operationFailed: "عملیات با خطا متوقف شد. خروجی را بررسی کنید.",
    copied: "خروجی عملیات کپی شد.", copyFailed: "کپی در این مرورگر ممکن نیست.", connectionError: "ارتباط با هستهٔ HOMA برقرار نشد.", refreshed: "اطلاعات پنل به‌روز شد.", now: "اکنون", secondsAgo: "۶۰ ثانیه قبل",
    diagnosticConfirm: "این ابزار فقط وضعیت را بررسی می‌کند و تغییری در پیکربندی ایجاد نمی‌کند.", detailsFor: "خروجی زندهٔ عملیات",
  },
  en: {
    workspace: "WORKSPACE", navOverview: "Overview", navOptimization: "Optimization", navDiagnostics: "Diagnostics", navActivity: "Activity",
    coreTagline: "Lighter, faster, always ready to fly.", connecting: "Connecting to HOMA core", projectPage: "Project on GitHub", connectingShort: "Connecting",
    overviewTitle: "Server overview", overviewSubtitle: "Every vital sign of your server, at a glance.", runAudit: "Run system audit",
    heroKicker: "BORN TO RISE ABOVE", heroTitle: "Your server,<br>in perfect flight.", heroText: "Intelligent network tuning, live telemetry and continuous protection, unified in the HOMA command center.",
    optimizeNow: "Optimize server", previewChanges: "Preview changes", panelSafe: "Panel & client safe", realtime: "REALTIME", systemHealth: "System health", collectingData: "Collecting system data",
    uptime: "System uptime", kernel: "Kernel", processor: "Processor", loadAverage: "Load average", memory: "Memory", used: "Used", disk: "Disk space", available: "Available",
    connections: "Active connections", networkInterface: "Interface", liveTraffic: "LIVE TRAFFIC", networkPulse: "Network pulse", download: "Download", upload: "Upload",
    waitingForTraffic: "Waiting for the first traffic samples", lastMinute: "Last 60 samples", autoRefresh: "Auto-refresh enabled", protectionLayer: "PROTECTION LAYERS", flightSystems: "Flight systems",
    oneClick: "ONE-CLICK CONTROL", quickActions: "Quick actions", newBackup: "Create backup", newBackupHint: "Take a safe panel snapshot", speedTest: "Speed test", speedTestHint: "Measure server bandwidth",
    portScan: "Port scan", portScanHint: "Map ports and firewall", auditTrail: "AUDIT TRAIL", recentActivity: "Recent activity", viewAll: "View all", noActivity: "No operations have been recorded yet.",
    optimizationTitle: "Optimization center", optimizationSubtitle: "Unlock your server's potential with precise, controlled tooling.", fullSuite: "THE COMPLETE HOMA SUITE", fullOptimization: "One-click server optimization",
    fullOptimizationText: "Elevate networking, memory, security, scheduling and self-healing in one guided workflow.", startSuite: "Start full suite", individualModules: "Individual modules", individualModulesHint: "Your confirmation is requested before every system change.",
    diagnosticsTitle: "Diagnostics & testing", diagnosticsSubtitle: "Inspect and measure your server without changing its configuration.", readOnlyTools: "Read-only tools", diagnosticNote: "Results stream into the operation drawer. Network tests may take a few moments to complete.",
    activityTitle: "Activity & operations", activitySubtitle: "Status and output for every process in this panel session.", refreshList: "Refresh list", noActivityYet: "No activity yet", noActivityDescription: "Run your first audit or optimization to see its details here.",
    footerSafety: "Engineered for precise control and sustainable performance", confirmationWarning: "This operation changes server settings. Make sure you have a stable out-of-band connection to the server.", cancel: "Cancel", confirmRun: "Confirm & run", backToPanel: "Back to panel",
    authText: "Enter the panel access token to unlock your command center.", accessToken: "Access token", authError: "The access token is not valid.", unlockPanel: "Unlock secure panel", authHint: "The token is stored in /etc/homa/panel.env on your server.",
    updateSuite: "Upgrade the HOMA suite", updateSuiteText: "Install the latest scripts and panel from the official repository while preserving your access token and settings.", officialSource: "Official source", checkAndUpdate: "Update & restart",
    restartTitle: "Homa is preparing for a new flight", restartText: "The update is installed. Your panel is restarting and will reconnect automatically.", retryConnection: "Retry connection", updateWarning: "Scripts and panel files will be replaced from the official HOMA repository. Your access token is preserved, and the panel will restart once after installation.",
    live: "Live & connected", disconnected: "Connection lost", coreConnected: "HOMA core connected", coreDisconnected: "HOMA core unavailable", excellentHealth: "Server health is excellent", attentionHealth: "Resource usage needs attention",
    controlMode: "CONTROL MODE", readOnlyMode: "READ ONLY", rootRequiredMode: "ROOT REQUIRED", coreCount: "cores", day: "days", hour: "hours", minute: "min",
    active: "Active", inactive: "Inactive", failed: "Failed", unknown: "Unknown", not_detected: "Not detected", activating: "Activating",
    servicePanel: "3x-ui / Xray panel", serviceNetwork: "Network & BBR", serviceWatchdog: "Self-healing watchdog", serviceScheduler: "Smart scheduler", serviceSecurity: "Security guard", serviceClient: "Client connection guard",
    run: "Run module", viewOutput: "View output", safeTag: "READ ONLY", optimizeTag: "OPTIMIZE", readOnlyBlocked: "Server changes are disabled in read-only mode.", rootRequired: "Run HOMA panel as root to use this operation.", operationInProgress: "Another operation is already running.",
    queued: "Queued", running: "Running", succeeded: "Succeeded", failedStatus: "Failed", noOutput: "No operation output yet…", operationStarted: "Operation started; live output is open.", operationSucceeded: "Operation completed successfully.", operationFailed: "Operation stopped with an error. Check the output.",
    copied: "Operation output copied.", copyFailed: "Clipboard access is unavailable in this browser.", connectionError: "Could not connect to the HOMA core.", refreshed: "Panel data refreshed.", now: "now", secondsAgo: "−60s",
    diagnosticConfirm: "This tool inspects system state without changing configuration.", detailsFor: "Live operation output",
  },
};

const actionTranslations = {
  fa: {
    "suite-update": ["به‌روزرسانی سوئیت HOMA", "دریافت و نصب تازه‌ترین نسخه از مخزن رسمی؛ پنل پس از نصب به‌صورت خودکار راه‌اندازی مجدد می‌شود.", "۱–۳ دقیقه"],
    "full-optimize": ["بهینه‌سازی کامل سرور", "اجرای همهٔ ماژول‌های اصلی، از شبکه و سخت‌افزار تا امنیت و نگهبان.", "۱۰–۳۰ دقیقه"],
    "network-optimize": ["بهینه‌سازی شبکه و کرنل", "فعال‌سازی BBR و FQ و تنظیم بافرهای TCP برای مسیرهای پرنوسان.", "۱–۲ دقیقه"],
    "hardware-optimize": ["بهینه‌سازی سخت‌افزار", "تنظیم حافظهٔ مجازی، محدودیت فایل‌ها، journald و منابع سیستم.", "۱–۳ دقیقه"],
    "client-guard": ["نگهبان اتصال کاربران", "تنظیم Keepalive برای پایداری اتصال کلاینت‌ها در شبکه‌های موبایل.", "کمتر از ۱ دقیقه"],
    "security-hardening": ["تقویت امنیت سرور", "فعال‌سازی Fail2ban و محدودسازی flood برای مقاومت بیشتر.", "۲–۵ دقیقه"],
    "watchdog-enable": ["فعال‌سازی نگهبان", "پایش پنل و هستهٔ Xray با بازیابی خودکار در صورت توقف.", "کمتر از ۱ دقیقه"],
    "scheduler-enable": ["زمان‌بند ساعات اوج", "تنظیم خودکار کارایی شبکه در ساعات پرترافیک ایران.", "کمتر از ۱ دقیقه"],
    "backup-create": ["پشتیبان‌گیری از پنل", "ساخت آرشیو از دیتابیس، گواهی‌ها و تنظیمات پشتیبانی‌شده.", "۱–۲ دقیقه"],
    "network-rollback": ["بازگردانی تنظیمات شبکه", "بازگرداندن مقادیر شبکه به آخرین نسخهٔ پشتیبان ثبت‌شده.", "کمتر از ۱ دقیقه"],
    "system-audit": ["ممیزی جامع سیستم", "بررسی فقط‌خواندنی سخت‌افزار، پنل، پورت‌ها و آمادگی کرنل.", "۱۰–۳۰ ثانیه"],
    "network-audit": ["پیش‌نمایش تغییرات شبکه", "مقایسهٔ مقادیر فعلی با تنظیمات پیشنهادی، بدون اعمال تغییر.", "۵–۱۵ ثانیه"],
    "port-scan": ["نقشهٔ پورت و فایروال", "شناسایی پورت‌های باز، تداخل‌ها و وضعیت محافظت شبکه.", "۱۰–۲۰ ثانیه"],
    "cloudflare-scan": ["جست‌وجوی IP تمیز Cloudflare", "سنجش تأخیر TCP روی گروهی از آدرس‌های لبهٔ Cloudflare.", "۲۰–۴۰ ثانیه"],
    speedtest: ["سنجش پهنای باند", "اندازه‌گیری سرعت دانلود از چند مسیر و مقصد مختلف.", "۳۰–۹۰ ثانیه"],
    "iran-probe": ["پایش مسیرهای اپراتور ایران", "سنجش تأخیر و از دست رفتن بسته به مقصدهای منتخب اپراتورها.", "۳۰–۹۰ ثانیه"],
  },
  en: {
    "suite-update": ["Update HOMA suite", "Download and install the latest release from the official repository. The panel restarts automatically after installation.", "1–3 min"],
    "full-optimize": ["Full server optimization", "Run all core modules, from networking and hardware to security and watchdog.", "10–30 min"],
    "network-optimize": ["Network & kernel tuning", "Enable BBR and FQ, then tune TCP buffers for unstable network paths.", "1–2 min"],
    "hardware-optimize": ["Hardware optimization", "Tune virtual memory, file limits, journald and system resources.", "1–3 min"],
    "client-guard": ["Client connection guard", "Tune keepalive behavior for persistent clients on mobile networks.", "Under 1 min"],
    "security-hardening": ["Security hardening", "Enable Fail2ban and flood limits for a more resilient server.", "2–5 min"],
    "watchdog-enable": ["Enable watchdog", "Monitor the panel and Xray core with automatic recovery after a crash.", "Under 1 min"],
    "scheduler-enable": ["Peak-hours scheduler", "Automatically adjust network performance during Iran's busiest hours.", "Under 1 min"],
    "backup-create": ["Panel backup", "Archive the database, certificates and supported configuration files.", "1–2 min"],
    "network-rollback": ["Rollback network tuning", "Restore network values from the most recent recorded backup.", "Under 1 min"],
    "system-audit": ["Full system audit", "Read-only inspection of hardware, panel, ports and kernel readiness.", "10–30 sec"],
    "network-audit": ["Preview network changes", "Compare current values with recommended tuning without applying changes.", "5–15 sec"],
    "port-scan": ["Port & firewall map", "Discover listening ports, conflicts and network protection status.", "10–20 sec"],
    "cloudflare-scan": ["Cloudflare clean IP scan", "Measure TCP latency across a selection of Cloudflare edge addresses.", "20–40 sec"],
    speedtest: ["Bandwidth speed test", "Measure download throughput across several routes and destinations.", "30–90 sec"],
    "iran-probe": ["Iran operator path probe", "Measure latency and packet loss to selected operator destinations.", "30–90 sec"],
  },
};

const state = {
  language: localStorage.getItem("homa-language") || "fa",
  view: "overview",
  token: sessionStorage.getItem("homa-panel-token") || "",
  overview: null,
  actions: [],
  jobs: [],
  activeJob: null,
  pendingAction: null,
  drawerJobId: null,
  drawerTimer: null,
  refreshTimer: null,
  restartPollTimer: null,
  restartRetryTimer: null,
  restartStartedAt: 0,
  restarting: false,
  refreshing: false,
  eventsBound: false,
  chartSamples: [],
  connected: false,
  readOnly: false,
  root: true,
};
const validViews = new Set(["overview", "optimization", "diagnostics", "activity"]);
const validIcons = new Set(["refresh", "sparkles", "network", "cpu", "shield", "lock", "pulse", "clock", "archive", "rollback", "scan", "sliders", "radar", "cloud", "gauge", "signal", "activity"]);
const t = (key) => translations[state.language][key] ?? translations.fa[key] ?? key;
const actionText = (id) => actionTranslations[state.language][id] || actionTranslations.en[id] || [id, "", ""];

function formatNumber(value, maximumFractionDigits = 1) {
  return new Intl.NumberFormat(state.language === "fa" ? "fa-IR" : "en-US", { maximumFractionDigits }).format(Number(value) || 0);
}

function formatBytes(bytes, precision = 1) {
  let value = Math.max(0, Number(bytes) || 0);
  const units = ["B", "KB", "MB", "GB", "TB", "PB"];
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) { value /= 1024; unit += 1; }
  return `${formatNumber(value, unit === 0 ? 0 : precision)} ${units[unit]}`;
}

function formatSpeed(bytes) { return `${formatBytes(bytes)}/s`; }

function formatUptime(seconds) {
  const totalMinutes = Math.floor((Number(seconds) || 0) / 60);
  const days = Math.floor(totalMinutes / 1440);
  const hours = Math.floor((totalMinutes % 1440) / 60);
  const minutes = totalMinutes % 60;
  if (days > 0) return `${formatNumber(days, 0)} ${t("day")}، ${formatNumber(hours, 0)} ${t("hour")}`;
  if (hours > 0) return `${formatNumber(hours, 0)} ${t("hour")}، ${formatNumber(minutes, 0)} ${t("minute")}`;
  return `${formatNumber(minutes, 0)} ${t("minute")}`;
}

function formatDate(date, includeDate = false) {
  const locale = state.language === "fa" ? "fa-IR" : "en-US";
  const options = includeDate
    ? { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }
    : { hour: "2-digit", minute: "2-digit", second: "2-digit" };
  return new Intl.DateTimeFormat(locale, options).format(new Date(date));
}

function applyLanguage() {
  document.documentElement.lang = state.language;
  document.documentElement.dir = state.language === "fa" ? "rtl" : "ltr";
  localStorage.setItem("homa-language", state.language);
  $$('[data-i18n]').forEach((element) => {
    const key = element.dataset.i18n;
    if (key === "heroTitle") element.innerHTML = t(key);
    else if (translations[state.language][key]) element.textContent = t(key);
  });
  $("#language-toggle span").textContent = state.language === "fa" ? "EN" : "FA";
  $(".update-button").setAttribute("aria-label", actionText("suite-update")[0]);
  document.title = state.language === "fa" ? "HOMA · مرکز فرمان سرور" : "HOMA · Server Command Center";
  const date = new Intl.DateTimeFormat(state.language === "fa" ? "fa-IR" : "en-US", { weekday: "long", day: "numeric", month: "long" }).format(new Date());
  $("#current-date").textContent = `${date} · HOMA`;
  $("#breadcrumb-current").textContent = t({ overview: "navOverview", optimization: "navOptimization", diagnostics: "navDiagnostics", activity: "navActivity" }[state.view]);
  renderActions();
  if (state.overview) renderOverview(state.overview, false);
  renderJobs();
  if (state.drawerJobId) refreshDrawerJob();
  drawNetworkChart();
}

async function api(path, options = {}) {
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  if (state.token) headers["X-HOMA-Token"] = state.token;
  if (options.method === "POST") {
    headers["Content-Type"] = "application/json";
    headers["X-HOMA-Request"] = "dashboard";
  }
  let response;
  try {
    response = await fetch(path, { ...options, headers, cache: "no-store" });
  } catch (error) {
    setConnection(false);
    const connectionError = new Error(t("connectionError"));
    connectionError.code = "network";
    throw connectionError;
  }
  let payload = {};
  try { payload = await response.json(); } catch { payload = {}; }
  if (response.status === 401) {
    showAuth();
    const error = new Error(payload.error?.message || t("authError"));
    error.code = "unauthorized";
    throw error;
  }
  if (!response.ok) {
    const error = new Error(payload.error?.message || `Request failed (${response.status})`);
    error.code = payload.error?.code || "request_failed";
    throw error;
  }
  return payload;
}

function setConnection(connected) {
  state.connected = connected;
  const dot = $("#connection-pill .status-dot");
  dot.className = `status-dot ${connected ? "online" : "offline"}`;
  $("#connection-text").textContent = connected ? t("live") : t("disconnected");
  $("#core-status-text").textContent = connected ? t("coreConnected") : t("coreDisconnected");
  const coreDot = $(".core-status .status-dot");
  coreDot.className = `status-dot ${connected ? "online" : "offline"}`;
}

function showAuth() {
  window.clearInterval(state.refreshTimer);
  window.clearInterval(state.drawerTimer);
  state.refreshTimer = null;
  state.drawerTimer = null;
  setConnection(false);
  $("#auth-screen").hidden = false;
  $("#auth-error").hidden = true;
  window.setTimeout(() => $("#auth-token").focus(), 50);
}

function hideAuth() {
  $("#auth-screen").hidden = true;
  $("#auth-error").hidden = true;
}

function toast(message, type = "success") {
  const element = document.createElement("div");
  element.className = `toast ${type === "error" ? "error" : ""}`;
  element.innerHTML = icon(type === "error" ? "alert" : "check");
  const text = document.createElement("span");
  text.textContent = message;
  element.append(text);
  $("#toast-region").append(element);
  window.setTimeout(() => element.remove(), 4200);
}

function switchView(view, updateHash = true) {
  if (!validViews.has(view)) return;
  state.view = view;
  $$('[data-view-panel]').forEach((panel) => {
    const active = panel.dataset.viewPanel === view;
    panel.hidden = !active;
    panel.classList.toggle("active", active);
  });
  $$('.nav-item[data-view]').forEach((button) => button.classList.toggle("active", button.dataset.view === view));
  $("#breadcrumb-current").textContent = t({ overview: "navOverview", optimization: "navOptimization", diagnostics: "navDiagnostics", activity: "navActivity" }[view]);
  if (updateHash) history.replaceState(null, "", `#${view}`);
  closeSidebar();
  if (view === "activity") fetchJobs();
  if (view === "overview") window.setTimeout(drawNetworkChart, 50);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function openSidebar() {
  $("#sidebar").classList.add("open");
  $("#sidebar-backdrop").hidden = false;
}
function closeSidebar() {
  $("#sidebar").classList.remove("open");
  $("#sidebar-backdrop").hidden = true;
}

function renderOverview(payload, addSample = true) {
  state.overview = payload;
  state.readOnly = Boolean(payload.read_only);
  state.root = Boolean(payload.root);
  state.activeJob = payload.active_job || state.jobs.find((job) => ["queued", "running"].includes(job.status)) || null;
  const metrics = payload.metrics;
  if (!metrics) return;
  setConnection(true);

  $("#top-hostname").textContent = metrics.host.name || "localhost";
  $("#hero-os").textContent = metrics.host.os || "Linux";
  $("#cpu-value").textContent = formatNumber(metrics.cpu.percent);
  $("#cpu-progress").value = metrics.cpu.percent;
  $("#cpu-cores").textContent = `${formatNumber(metrics.cpu.cores, 0)} ${t("coreCount")}`;
  $("#cpu-load").textContent = metrics.cpu.load.map((value) => formatNumber(value, 2)).join("  ·  ");
  $("#memory-value").textContent = formatNumber(metrics.memory.percent);
  $("#memory-progress").value = metrics.memory.percent;
  $("#memory-total").textContent = formatBytes(metrics.memory.total, 0);
  $("#memory-used").textContent = `${formatBytes(metrics.memory.used)} / ${formatBytes(metrics.memory.total)}`;
  $("#disk-value").textContent = formatNumber(metrics.disk.percent);
  $("#disk-progress").value = metrics.disk.percent;
  $("#disk-total").textContent = formatBytes(metrics.disk.total, 0);
  $("#disk-free").textContent = formatBytes(metrics.disk.free);
  $("#connections-value").textContent = formatNumber(metrics.connections, 0);
  $("#network-interface").textContent = metrics.network.interface;
  $("#rx-rate").textContent = formatSpeed(metrics.network.rx_rate);
  $("#tx-rate").textContent = formatSpeed(metrics.network.tx_rate);
  $("#health-score").textContent = formatNumber(metrics.health.score, 0);
  $("#health-arc").setAttribute("stroke-dasharray", `${Math.max(0, Math.min(100, metrics.health.score))} 100`);
  $("#health-label").innerHTML = `<span class="status-dot ${metrics.health.score >= 85 ? "online" : "offline"}"></span><span>${escapeHtml(t(metrics.health.score >= 85 ? "excellentHealth" : "attentionHealth"))}</span>`;
  $("#health-uptime").textContent = formatUptime(metrics.uptime);
  $("#health-kernel").textContent = metrics.host.kernel;
  $("#optimization-mode").textContent = state.readOnly ? t("readOnlyMode") : (state.root ? t("controlMode") : t("rootRequiredMode"));

  if (addSample) {
    const last = state.chartSamples.at(-1);
    if (!last || last.timestamp !== metrics.timestamp) {
      state.chartSamples.push({ timestamp: metrics.timestamp, rx: metrics.network.rx_rate, tx: metrics.network.tx_rate });
      if (state.chartSamples.length > 60) state.chartSamples.shift();
    }
  }
  $("#chart-empty").hidden = state.chartSamples.length > 1;
  drawNetworkChart();
  renderServices(metrics.services, metrics.optimization);
  updateActionAvailability();
}

function renderServices(services = [], optimization = {}) {
  const definitions = {
    panel: ["servicePanel", "server", "3x-ui · Xray"],
    network: ["serviceNetwork", "network", `${optimization.congestion_control || "—"} · ${optimization.qdisc || "—"}`],
    watchdog: ["serviceWatchdog", "pulse", "homa-watchdog.service"],
    scheduler: ["serviceScheduler", "clock", "homa-scheduler.timer"],
    security: ["serviceSecurity", "lock", "Fail2ban"],
    client: ["serviceClient", "shield", "TCP Keepalive"],
  };
  $("#service-list").innerHTML = services.map((service) => {
    const definition = definitions[service.id] || [service.id, "server", service.id];
    const status = ["active", "inactive", "failed", "unknown", "not_detected", "activating"].includes(service.status) ? service.status : "unknown";
    return `<div class="service-row"><span class="service-icon">${icon(definition[1])}</span><div class="service-info"><strong>${escapeHtml(t(definition[0]))}</strong><small dir="ltr">${escapeHtml(definition[2])}</small></div><span class="service-status ${status}">${escapeHtml(t(status))}</span></div>`;
  }).join("");
}

function renderActions() {
  if (!state.actions.length) return;
  const card = (action) => {
    const [name, description, duration] = actionText(action.id);
    const actionIcon = validIcons.has(action.icon) ? action.icon : "sparkles";
    return `<article class="action-card"><div class="action-card-top"><span class="action-icon">${icon(actionIcon)}</span><span class="action-tag ${action.mutating ? "" : "safe"}">${escapeHtml(t(action.mutating ? "optimizeTag" : "safeTag"))}</span></div><h3>${escapeHtml(name)}</h3><p>${escapeHtml(description)}</p><div class="action-footer"><span class="action-time">${icon("clock")}<span>${escapeHtml(duration)}</span></span><button class="run-action" type="button" data-action="${escapeHtml(action.id)}"><span>${escapeHtml(t("run"))}</span>${icon("arrow", "flip-rtl")}</button></div></article>`;
  };
  $("#optimization-grid").innerHTML = state.actions.filter((action) => action.category === "optimize" && action.id !== "full-optimize").map(card).join("");
  $("#diagnostics-grid").innerHTML = state.actions.filter((action) => action.category === "diagnostics").map(card).join("");
  updateActionAvailability();
}

function updateActionAvailability() {
  const active = state.activeJob || state.jobs.find((job) => ["queued", "running"].includes(job.status));
  $$('[data-action]').forEach((button) => {
    const action = state.actions.find((entry) => entry.id === button.dataset.action);
    if (!action) return;
    let reason = "";
    if (active) reason = t("operationInProgress");
    else if (action.mutating && state.readOnly) reason = t("readOnlyBlocked");
    else if (action.mutating && !state.root) reason = t("rootRequired");
    button.disabled = Boolean(reason);
    button.title = reason || (button.dataset.action === "suite-update" ? actionText("suite-update")[0] : "");
  });
  const count = active ? 1 : 0;
  $("#job-count").hidden = !count;
  $("#job-count").textContent = String(count);
}

async function fetchOverview() {
  const payload = await api("/api/overview");
  renderOverview(payload);
  return payload;
}

async function fetchActions() {
  const payload = await api("/api/actions");
  state.actions = payload.actions || [];
  state.activeJob = payload.active_job || state.activeJob;
  renderActions();
}

async function fetchJobs() {
  try {
    const payload = await api("/api/jobs");
    state.jobs = payload.jobs || [];
    state.activeJob = state.jobs.find((job) => ["queued", "running"].includes(job.status)) || null;
    renderJobs();
    updateActionAvailability();
    const restartedUpdate = state.jobs.find((job) => job.action === "suite-update" && job.status === "succeeded" && job.restart_scheduled);
    if (restartedUpdate) beginPanelRestart();
  } catch (error) {
    if (error.code !== "unauthorized") throw error;
  }
}

function jobStatusText(status) { return status === "failed" ? t("failedStatus") : t(status); }

function activityItem(job) {
  const status = ["queued", "running", "succeeded", "failed"].includes(job.status) ? job.status : "failed";
  const statusIcon = status === "succeeded" ? "check" : status === "failed" ? "alert" : "activity";
  return `<div class="activity-item"><span class="activity-icon ${status}">${icon(statusIcon)}</span><div class="activity-info"><strong>${escapeHtml(actionText(job.action)[0])}</strong><small>${escapeHtml(formatDate(job.created_at, true))} · ${escapeHtml(job.id)}</small></div><span class="job-status-badge ${status}">${escapeHtml(jobStatusText(status))}</span><button class="icon-button activity-open" type="button" data-open-job="${escapeHtml(job.id)}" aria-label="${escapeHtml(t("viewOutput"))}">${icon("eye")}</button></div>`;
}

function renderJobs() {
  const recent = $("#recent-activity");
  const full = $("#activity-list");
  if (!state.jobs.length) {
    recent.innerHTML = `<div class="empty-state small">${icon("activity")}<p>${escapeHtml(t("noActivity"))}</p></div>`;
    full.innerHTML = `<div class="empty-state">${icon("activity")}<h3>${escapeHtml(t("noActivityYet"))}</h3><p>${escapeHtml(t("noActivityDescription"))}</p></div>`;
    return;
  }
  recent.innerHTML = state.jobs.slice(0, 3).map(activityItem).join("");
  full.innerHTML = state.jobs.map(activityItem).join("");
}

function actionBlockReason(action) {
  if (state.activeJob) return t("operationInProgress");
  if (action.mutating && state.readOnly) return t("readOnlyBlocked");
  if (action.mutating && !state.root) return t("rootRequired");
  return "";
}

function requestAction(actionId) {
  const action = state.actions.find((entry) => entry.id === actionId);
  if (!action) return;
  const reason = actionBlockReason(action);
  if (reason) { toast(reason, "error"); return; }
  if (!action.mutating) { startAction(actionId); return; }
  state.pendingAction = actionId;
  const [name, description] = actionText(actionId);
  $("#modal-title").textContent = name;
  $("#modal-description").textContent = description;
  $("#modal-symbol").classList.toggle("danger", Boolean(action.danger));
  $("#modal-symbol use").setAttribute("href", actionId === "suite-update" ? "#i-refresh" : "#i-sparkles");
  $("#modal-warning span").textContent = actionId === "suite-update" ? t("updateWarning") : t("confirmationWarning");
  $("#modal-warning").classList.remove("safe");
  $("#action-modal").hidden = false;
  window.setTimeout(() => $("#confirm-action").focus(), 40);
}

function closeActionModal() {
  $("#action-modal").hidden = true;
  state.pendingAction = null;
}

async function startAction(actionId) {
  const action = state.actions.find((entry) => entry.id === actionId);
  if (!action) return;
  closeActionModal();
  try {
    const payload = await api(`/api/actions/${encodeURIComponent(actionId)}`, {
      method: "POST",
      body: JSON.stringify({ confirm: Boolean(action.mutating) }),
    });
    state.activeJob = payload.job;
    state.jobs = [payload.job, ...state.jobs.filter((job) => job.id !== payload.job.id)];
    renderJobs();
    updateActionAvailability();
    toast(t("operationStarted"));
    openJobDrawer(payload.job.id);
  } catch (error) {
    const localized = error.code === "read_only" ? t("readOnlyBlocked") : error.code === "root_required" ? t("rootRequired") : error.code === "busy" ? t("operationInProgress") : error.message;
    toast(localized, "error");
  }
}

function openJobDrawer(jobId) {
  state.drawerJobId = jobId;
  $("#job-drawer").hidden = false;
  $("#drawer-backdrop").hidden = false;
  $("#job-output").textContent = t("noOutput");
  refreshDrawerJob();
  window.clearInterval(state.drawerTimer);
  state.drawerTimer = window.setInterval(refreshDrawerJob, 1000);
}

function closeJobDrawer() {
  state.drawerJobId = null;
  window.clearInterval(state.drawerTimer);
  state.drawerTimer = null;
  $("#job-drawer").hidden = true;
  $("#drawer-backdrop").hidden = true;
}

function beginPanelRestart() {
  if (state.restarting) return;
  state.restarting = true;
  state.restartStartedAt = Date.now();
  state.activeJob = null;
  window.clearInterval(state.refreshTimer);
  window.clearInterval(state.drawerTimer);
  window.clearTimeout(state.restartPollTimer);
  window.clearTimeout(state.restartRetryTimer);
  state.refreshTimer = null;
  state.drawerTimer = null;
  setConnection(false);
  $("#restart-retry").hidden = true;
  $("#restart-screen").hidden = false;
  state.restartPollTimer = window.setTimeout(pollPanelRestart, 8000);
  state.restartRetryTimer = window.setTimeout(() => { $("#restart-retry").hidden = false; }, 45000);
}

async function pollPanelRestart() {
  if (!state.restarting) return;
  window.clearTimeout(state.restartPollTimer);
  state.restartPollTimer = null;
  const remaining = 8000 - (Date.now() - state.restartStartedAt);
  if (remaining > 0) {
    state.restartPollTimer = window.setTimeout(pollPanelRestart, remaining);
    return;
  }
  const headers = { Accept: "application/json" };
  if (state.token) headers["X-HOMA-Token"] = state.token;
  try {
    const response = await fetch("/api/session", { headers, cache: "no-store" });
    if (response.ok) {
      // A clean reload picks up the newly installed backend and static assets;
      // sessionStorage preserves the panel token across this navigation.
      window.location.reload();
      return;
    }
  } catch {
    // The service is expected to be unavailable briefly during restart.
  }
  if (state.restarting) state.restartPollTimer = window.setTimeout(pollPanelRestart, 2500);
}

async function refreshDrawerJob() {
  if (!state.drawerJobId) return;
  const requestedId = state.drawerJobId;
  try {
    const payload = await api(`/api/jobs/${encodeURIComponent(requestedId)}`);
    if (state.drawerJobId !== requestedId) return;
    const job = payload.job;
    const previous = state.jobs.find((entry) => entry.id === job.id);
    state.jobs = [job, ...state.jobs.filter((entry) => entry.id !== job.id)].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    $("#job-title").textContent = actionText(job.action)[0];
    $("#job-status").className = `job-status-badge ${job.status}`;
    $("#job-status").textContent = jobStatusText(job.status);
    $("#job-time").textContent = `${formatDate(job.created_at, true)} · ${job.id}`;
    const output = $("#job-output");
    const nearBottom = output.scrollHeight - output.scrollTop - output.clientHeight < 60;
    output.textContent = job.output || t("noOutput");
    if (nearBottom || ["queued", "running"].includes(job.status)) output.scrollTop = output.scrollHeight;
    renderJobs();
    if (!["queued", "running"].includes(job.status)) {
      if (job.action === "suite-update" && job.status === "succeeded" && job.restart_scheduled) {
        beginPanelRestart();
        return;
      }
      window.clearInterval(state.drawerTimer);
      state.drawerTimer = null;
      if (state.activeJob?.id === job.id) state.activeJob = null;
      updateActionAvailability();
      fetchOverview().catch(() => {});
      if (previous && ["queued", "running"].includes(previous.status)) {
        toast(t(job.status === "succeeded" ? "operationSucceeded" : "operationFailed"), job.status === "succeeded" ? "success" : "error");
      }
    }
  } catch (error) {
    const trackedJob = state.jobs.find((entry) => entry.id === requestedId);
    if (trackedJob?.action === "suite-update" && error.code === "job_not_found") {
      // The job registry is in memory, so its disappearance after a completed
      // update means the new panel process is already answering requests.
      beginPanelRestart();
      return;
    }
    if (error.code !== "unauthorized") {
      $("#job-output").textContent = `${t("connectionError")}\n${error.message}`;
      window.clearInterval(state.drawerTimer);
      state.drawerTimer = null;
      if (trackedJob?.action === "suite-update" && error.code === "network") {
        $("#job-output").textContent = `${t("connectionError")}\n${t("retryConnection")}…`;
        state.drawerTimer = window.setTimeout(refreshDrawerJob, 2000);
      }
    }
  }
}

async function refreshAll(manual = false) {
  if (state.restarting || state.refreshing || document.hidden) return;
  state.refreshing = true;
  if (manual) $("#refresh-button").classList.add("is-spinning");
  try {
    await fetchOverview();
    if (state.view === "activity" || state.activeJob) await fetchJobs();
    if (manual) toast(t("refreshed"));
  } catch (error) {
    if (state.activeJob?.action === "suite-update" && error.code === "network") beginPanelRestart();
    if (error.code !== "unauthorized" && manual && !state.restarting) toast(error.message, "error");
  } finally {
    state.refreshing = false;
    $("#refresh-button").classList.remove("is-spinning");
  }
}

function niceMaximum(value) {
  if (value <= 0) return 1024;
  const exponent = 10 ** Math.floor(Math.log10(value));
  const fraction = value / exponent;
  const nice = fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 5 ? 5 : 10;
  return nice * exponent;
}

function drawNetworkChart() {
  const canvas = $("#network-chart");
  if (!canvas || state.view !== "overview") return;
  const bounds = canvas.getBoundingClientRect();
  if (bounds.width < 10 || bounds.height < 10) return;
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  const width = Math.round(bounds.width * ratio);
  const height = Math.round(bounds.height * ratio);
  if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
  const context = canvas.getContext("2d");
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  const w = bounds.width;
  const h = bounds.height;
  context.clearRect(0, 0, w, h);
  const pad = { top: 21, right: 9, bottom: 23, left: 9 };
  const chartW = w - pad.left - pad.right;
  const chartH = h - pad.top - pad.bottom;
  const styles = getComputedStyle(document.documentElement);
  const lineColor = styles.getPropertyValue("--line").trim() || "rgba(220,234,227,.08)";
  const muted = styles.getPropertyValue("--muted-dark").trim() || "#5e6b68";
  context.font = `8px ${state.language === "fa" ? "Vazirmatn" : "Arial"}`;
  context.lineWidth = 1;
  for (let index = 0; index < 4; index += 1) {
    const y = pad.top + (chartH / 3) * index;
    context.beginPath();
    context.setLineDash([3, 5]);
    context.strokeStyle = lineColor;
    context.moveTo(pad.left, y);
    context.lineTo(w - pad.right, y);
    context.stroke();
  }
  context.setLineDash([]);
  context.fillStyle = muted;
  context.textAlign = "left";
  context.fillText(t("secondsAgo"), pad.left, h - 5);
  context.textAlign = "right";
  context.fillText(t("now"), w - pad.right, h - 5);
  const samples = state.chartSamples;
  if (samples.length < 2) return;
  const maximum = niceMaximum(Math.max(...samples.flatMap((sample) => [sample.rx, sample.tx])) * 1.18);
  context.textAlign = "left";
  context.fillStyle = muted;
  context.fillText(formatBytes(maximum, 0), pad.left + 2, 10);

  const points = (key) => samples.map((sample, index) => ({
    x: pad.left + ((index + (60 - samples.length)) / 59) * chartW,
    y: pad.top + chartH - (Math.min(sample[key], maximum) / maximum) * chartH,
  }));
  const trace = (coords) => {
    context.beginPath();
    context.moveTo(coords[0].x, coords[0].y);
    for (let index = 1; index < coords.length - 1; index += 1) {
      const midpointX = (coords[index].x + coords[index + 1].x) / 2;
      const midpointY = (coords[index].y + coords[index + 1].y) / 2;
      context.quadraticCurveTo(coords[index].x, coords[index].y, midpointX, midpointY);
    }
    const last = coords.at(-1);
    context.lineTo(last.x, last.y);
  };
  const drawSeries = (key, color, fill) => {
    const coords = points(key);
    if (fill) {
      trace(coords);
      context.lineTo(coords.at(-1).x, pad.top + chartH);
      context.lineTo(coords[0].x, pad.top + chartH);
      context.closePath();
      const gradient = context.createLinearGradient(0, pad.top, 0, pad.top + chartH);
      gradient.addColorStop(0, fill);
      gradient.addColorStop(1, "rgba(0,0,0,0)");
      context.fillStyle = gradient;
      context.fill();
    }
    trace(coords);
    context.strokeStyle = color;
    context.lineWidth = 1.8;
    context.shadowColor = color;
    context.shadowBlur = 7;
    context.stroke();
    context.shadowBlur = 0;
    const last = coords.at(-1);
    context.beginPath();
    context.arc(last.x, last.y, 3, 0, Math.PI * 2);
    context.fillStyle = "#0f191a";
    context.fill();
    context.strokeStyle = color;
    context.lineWidth = 1.5;
    context.stroke();
  };
  drawSeries("rx", "#72d3aa", "rgba(114,211,170,.16)");
  drawSeries("tx", "#e5b45b", null);
}

function bindEvents() {
  document.addEventListener("click", (event) => {
    const nav = event.target.closest("[data-view]");
    if (nav) { switchView(nav.dataset.view); return; }
    const target = event.target.closest("[data-view-target]");
    if (target) { switchView(target.dataset.viewTarget); return; }
    const link = event.target.closest("[data-view-link]");
    if (link) { event.preventDefault(); switchView(link.dataset.viewLink); return; }
    const action = event.target.closest("[data-action]");
    if (action && !action.disabled) { requestAction(action.dataset.action); return; }
    const job = event.target.closest("[data-open-job]");
    if (job) { openJobDrawer(job.dataset.openJob); return; }
    if (event.target.closest("[data-close-modal]")) closeActionModal();
  });
  $("#language-toggle").addEventListener("click", () => {
    state.language = state.language === "fa" ? "en" : "fa";
    applyLanguage();
  });
  $("#refresh-button").addEventListener("click", () => refreshAll(true));
  $("#restart-retry").addEventListener("click", pollPanelRestart);
  $("#activity-refresh").addEventListener("click", () => fetchJobs().then(() => toast(t("refreshed"))).catch((error) => toast(error.message, "error")));
  $("#mobile-menu").addEventListener("click", openSidebar);
  $("#sidebar-close").addEventListener("click", closeSidebar);
  $("#sidebar-backdrop").addEventListener("click", closeSidebar);
  $("#confirm-action").addEventListener("click", () => { if (state.pendingAction) startAction(state.pendingAction); });
  $("#action-modal").addEventListener("click", (event) => { if (event.target === $("#action-modal")) closeActionModal(); });
  $("#close-drawer").addEventListener("click", closeJobDrawer);
  $("#drawer-done").addEventListener("click", closeJobDrawer);
  $("#drawer-backdrop").addEventListener("click", closeJobDrawer);
  $("#copy-log").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText($("#job-output").textContent); toast(t("copied")); }
    catch { toast(t("copyFailed"), "error"); }
  });
  $("#auth-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    state.token = $("#auth-token").value.trim();
    $("#auth-error").hidden = true;
    try {
      await fetchOverview();
      sessionStorage.setItem("homa-panel-token", state.token);
      hideAuth();
      await Promise.all([fetchActions(), fetchJobs()]);
      startRefreshTimer();
    } catch (error) {
      state.token = "";
      sessionStorage.removeItem("homa-panel-token");
      $("#auth-error").hidden = false;
      $("#auth-token").select();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (!$("#action-modal").hidden) closeActionModal();
    else if (state.drawerJobId) closeJobDrawer();
    else closeSidebar();
  });
  window.addEventListener("hashchange", () => switchView(location.hash.slice(1), false));
  window.addEventListener("resize", drawNetworkChart);
  if ("ResizeObserver" in window) new ResizeObserver(drawNetworkChart).observe($("#network-chart"));
}

function startRefreshTimer() {
  window.clearInterval(state.refreshTimer);
  state.refreshTimer = window.setInterval(() => refreshAll(false), 3000);
}

async function init() {
  applyLanguage();
  if (!state.eventsBound) {
    bindEvents();
    state.eventsBound = true;
  }
  switchView(validViews.has(location.hash.slice(1)) ? location.hash.slice(1) : "overview", false);
  try {
    const session = await api("/api/session");
    state.readOnly = Boolean(session.read_only);
    if (session.auth_required && !state.token) { showAuth(); return; }
    await Promise.all([fetchOverview(), fetchActions(), fetchJobs()]);
    hideAuth();
    startRefreshTimer();
  } catch (error) {
    if (error.code !== "unauthorized") {
      setConnection(false);
      toast(error.message, "error");
      window.setTimeout(init, 5000);
    }
  }
}

init();
