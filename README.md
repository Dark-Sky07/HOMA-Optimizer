<div align="center">
  <img src="panel/static/assets/homa-mark.svg" width="104" height="104" alt="HOMA logo" />

  # HOMA
  ### VPS Optimizer & Graphical Command Center

  **Rise Above Limits · سرورت را به اوج ببر**

  <p>
    <img src="https://img.shields.io/badge/Release-v5.1.0-e5b45b.svg?style=for-the-badge&logo=github" alt="Release v5.1.0" />
    <img src="https://img.shields.io/badge/Web%20Panel-FA%20%2B%20EN-72d3aa.svg?style=for-the-badge" alt="Bilingual Web Panel" />
    <img src="https://img.shields.io/badge/OS-Ubuntu%20%7C%20Debian-orange.svg?style=for-the-badge&logo=linux" alt="OS Support" />
    <img src="https://img.shields.io/badge/Runtime-Bash%20%2B%20Python%203-informational.svg?style=for-the-badge" alt="Runtime" />
  </p>
</div>

```text
========================================================================
               _   _  ___  __  __    _
              | | | |/ _ \|  \/  |  / \
              | |_| | | | | |\/| | / _ \
              |  _  | |_| | |  | |/ ___ \
              |_| |_|\___/|_|  |_/_/   \_\

               VPS OPTIMIZER & COMMAND CENTER
                    Version 5.1 · Rise Above Limits
========================================================================
```

**HOMA** یک سوئیت بهینه‌سازی سرورهای لینوکس و یک **پنل گرافیکی دوزبانهٔ فارسی/انگلیسی** است. هستهٔ پروژه ابزارهای مستقل Bash برای شبکه، کرنل، امنیت، پایداری اتصال، مانیتورینگ و نگهداری سرور را در اختیار می‌گذارد؛ داشبورد وب نیز همین ابزارها را با پایش زنده و اجرای کنترل‌شده در یک رابط حرفه‌ای یکپارچه می‌کند.

هویت بصری HOMA با الهام از پرندهٔ افسانه‌ای هما، پالت طلایی/سبز تیره و نماد اختصاصی طراحی شده است.

---

## ✨ امکانات نسخهٔ ۵٫۱

### پنل گرافیکی HOMA

- **داشبورد زنده:** مصرف CPU، حافظه، دیسک، Uptime، تعداد اتصال‌ها و نمودار لحظه‌ای دریافت/ارسال شبکه.
- **هویت بصری هما:** نشان اختصاصی در صفحهٔ اصلی، ورود و مرکز بهینه‌سازی؛ نمودار شبکه با نقشهٔ مسیر پرواز، گراف سلامت بال‌مانند و پالت طلایی/سبز الهام‌گرفته از هما.
- **به‌روزرسانی از داخل پنل:** نصب تازه‌ترین اسکریپت‌ها و رابط از مخزن رسمی، حفظ توکن و تنظیمات، راه‌اندازی مجدد کنترل‌شدهٔ سرویس و اتصال مجدد خودکار مرورگر.
- **سامانه‌های پرواز:** وضعیت 3x-ui/Xray، BBR، Watchdog، Scheduler، Fail2ban و Client Guard.
- **مرکز بهینه‌سازی:** اجرای سوئیت کامل یا ماژول‌های مستقل با پیام تأیید پیش از تغییر سرور.
- **عیب‌یابی:** ممیزی سیستم، پیش‌نمایش تغییرات شبکه، Port Scan، Cloudflare Scan، Speedtest و Iran Probe.
- **ترمینال زنده:** نمایش خروجی هر عملیات، ثبت وضعیت موفقیت/خطا و امکان کپی لاگ.
- **دو زبان و دو جهت:** رابط فارسی RTL و انگلیسی LTR با طراحی واکنش‌گرا برای موبایل و دسکتاپ.
- **بدون وابستگی وب:** رابط با HTML/CSS/JavaScript و بک‌اند با کتابخانهٔ استاندارد Python 3؛ بدون نیاز به Node، npm یا پایگاه داده.

### هستهٔ بهینه‌سازی و مدیریت سرور

- تنظیم BBR، FQ، بافرهای TCP/UDP، Keepalive و سازگاری مسیر اپراتورهای موبایل.
- زمان‌بند ساعات اوج، بهینه‌سازی حافظه و محدودیت منابع، Smart Swap و نگهداری زمان‌بندی‌شده.
- ابزارهای Domain/SNI، اسکن IP لبهٔ Cloudflare، DNS، Iran Unlocker و Bridge Doctor.
- Fail2ban، Port Doctor، مانیتورینگ زنده، هشدار تلگرام و نگهبان بازیابی پنل/Xray.
- پشتیبان‌گیری و Rollback ماژول‌های پشتیبانی‌شده از طریق منوی ترمینال.

---

## ⚡ نصب سریع

روی سرور لینوکسی و با دسترسی root اجرا کنید:

```bash
sudo bash -c "cd /tmp && rm -rf homa-pkg && mkdir -p homa-pkg && curl -fsSL 'https://github.com/Dark-Sky07/HOMA-Optimizer/archive/refs/heads/main.tar.gz' | tar -xz -C homa-pkg --strip-components=1 && bash homa-pkg/install.sh && rm -rf homa-pkg"
```

یا با اجرای مستقیم نصب‌کننده:

```bash
sudo bash <(curl -fsSL https://raw.githubusercontent.com/Dark-Sky07/HOMA-Optimizer/main/install.sh)
```

نصب‌کننده این موارد را آماده می‌کند:

| مؤلفه | مسیر / دستور |
|---|---|
| فایل‌های HOMA | `/opt/homa` |
| ماژول‌های Bash | `/opt/homa/scripts` |
| پنل گرافیکی | `/opt/homa/panel` |
| منوی ترمینال | `homa` |
| اجرای دستی پنل | `homa-panel` |
| سرویس پنل | `homa-panel.service` |
| تنظیمات و توکن پنل | `/etc/homa/panel.env` |

گزینه‌های نصب:

```bash
sudo bash install.sh --no-launch   # بدون باز کردن خودکار منوی ترمینال
sudo bash install.sh --no-panel    # بدون راه‌اندازی خودکار سرویس پنل
```

---

## 🖥️ ورود به پنل گرافیکی

پنل به‌صورت پیش‌فرض فقط روی آدرس امن محلی `127.0.0.1:8787` اجرا می‌شود و توکن دسترسی تصادفی می‌گیرد.

### مشاهدهٔ توکن و وضعیت سرویس

```bash
sudo systemctl status homa-panel
sudo cat /etc/homa/panel.env
```

### اتصال امن از سیستم خودتان با SSH Tunnel

```bash
ssh -L 8787:127.0.0.1:8787 USER@SERVER
```

سپس در مرورگر باز کنید:

```text
http://127.0.0.1:8787
```

توکن نمایش‌داده‌شده در پایان نصب یا مقدار `HOMA_PANEL_TOKEN` را وارد کنید. توکن فقط در Session Storage همان تب مرورگر نگهداری می‌شود.

### اجرای دستی و مدیریت سرویس

```bash
sudo homa-panel                       # اجرای مستقیم با تنظیمات /etc/homa/panel.env
sudo systemctl restart homa-panel    # راه‌اندازی دوباره
sudo systemctl stop homa-panel       # توقف پنل
sudo journalctl -u homa-panel -f     # مشاهدهٔ لاگ سرویس
```

> **هشدار امنیتی:** برای دسترسی مستقیم از اینترنت، مقدار `HOMA_PANEL_HOST=0.0.0.0` را فقط همراه با فایروال، توکن قوی و ترجیحاً HTTPS از طریق Reverse Proxy تنظیم کنید. باز کردن پنل مدیریتی بدون TLS روی اینترنت توصیه نمی‌شود.

### حالت فقط‌خواندنی

برای مانیتورینگ بدون اجازهٔ تغییر تنظیمات:

```bash
sudo homa-panel --read-only
```

در این حالت ابزارهای تشخیصی فقط‌خواندنی در دسترس‌اند و همهٔ عملیات تغییردهندهٔ سرور در بک‌اند مسدود می‌شوند؛ صرفاً مخفی شدن دکمه در رابط کافی نیست.

---

## 🧭 منوی ترمینال

```bash
homa
```

گزینه‌های تکمیلی:

```bash
homa --version
homa --help
homa --one-click --yes       # اجرای غیرتعاملی سوئیت کامل؛ با احتیاط
homa --update                # به‌روزرسانی کامل اسکریپت‌ها و پنل
homa-panel                  # پنل گرافیکی
```

نقشهٔ ابزارهای اصلی منو:

```text
CORE
 [1]  Read-only preflight audit
 [2]  One-click full optimization

NETWORK & CONNECTIONS
 [3]  BBR + FQ + kernel/network tuning
 [4]  Mobile operator compatibility
 [5]  Instagram & video streaming optimizer
 [6]  Client persistent-connection guard
 [7]  Iran peak-hours scheduler
 [8]  Domain & subdomain health checker
 [9]  Reality SNI analyzer
 [10] Cloudflare clean IP scanner
 [11] Smart anti-pollution DNS

SYSTEM & PROTECTION
 [12] Hardware/RAM/limits tuning       [13] Smart swap manager
 [14] IP reputation healer             [15] Iran download booster
 [16] Fail2ban & security hardening    [17] Backup & recovery
 [18] Nightly maintenance              [19] System package update
 [20] Panel/Xray watchdog              [21] Telegram alerts

DIAGNOSTICS & MANAGEMENT
 [22] Iran operator probe              [23] Bridge health doctor
 [24] Bandwidth speed test             [25] Live traffic monitor
 [26] Port & firewall doctor           [27] VLESS-Reality guide
 [w]  Start graphical panel            [r]  Rollback settings
 [u]  Update complete HOMA suite       [0]  Exit
```

---

## 🛡️ قرارداد ایمنی و کنترل دسترسی

| مؤلفه | سیاست HOMA |
|---|---|
| **دیتابیس 3x-ui** | ماژول‌های بهینه‌سازی شبکه و کرنل `x-ui.db` را تغییر نمی‌دهند. بازیابی نسخهٔ پشتیبان فقط با انتخاب صریح Restore انجام می‌شود. |
| **هستهٔ Xray** | HOMA باینری رسمی Xray یا کانفیگ Inbound کاربران را جایگزین نمی‌کند. |
| **ری‌استارت پنل** | بهینه‌سازی‌های شبکه به ری‌استارت پنل نیاز ندارند. Watchdog فقط پس از تشخیص توقف سرویس و برای بازیابی آن اقدام می‌کند. |
| **فایروال و شبکه** | تغییرات از ماژولهای مشخص انجام می‌شوند و مسیرهای Rollback مربوط به آن‌ها در منو وجود دارد. پیش از کار عملی، نسخهٔ پشتیبان بگیرید. |
| **اجرای دستور از وب** | API فقط یک Allowlist ثابت از اسکریپت‌ها و آرگومان‌ها را قبول می‌کند؛ دستور Shell دلخواه از مرورگر پذیرفته نمی‌شود. |
| **احراز هویت** | توکن در `/etc/homa/panel.env` با مجوز `600` نگهداری می‌شود و مقایسهٔ آن Constant-Time است. |
| **CSRF / XSS** | درخواست‌های تغییر به Header مخصوص Same-Origin و تأیید صریح نیاز دارند؛ CSP و Security Headerها نیز فعال‌اند. |
| **دسترسی root** | عملیات تغییردهنده فقط زمانی اجرا می‌شوند که سرویس پنل با root در حال اجرا باشد. مانیتورینگ بدون root نیز ممکن است. |

---

## 🗂️ ساختار پروژه

```text
HOMA-Optimizer/
├── install.sh                  # نصب‌کنندهٔ کامل
├── scripts/
│   ├── homa-menu.sh            # منوی ترمینال و سوئیت یک‌کلیکی
│   ├── homa-boost.sh           # شبکه و کرنل
│   ├── homa-watchdog.sh        # نگهبان پنل و Xray
│   └── ...                     # ماژول‌های مستقل HOMA
└── panel/
    ├── server.py               # وب‌سرور، Telemetry و API امن
    ├── homa-panel.service      # سرویس systemd
    └── static/
        ├── index.html          # ساختار داشبورد
        ├── styles.css          # هویت بصری و Responsive UI
        ├── app.js              # زبان، نمودار، عملیات و Live Jobs
        └── assets/             # لوگو، الگو و تصویر اختصاصی هما
```

---

## 🔄 به‌روزرسانی و Rollback

### به‌روزرسانی از پنل گرافیکی

در **مرکز بهینه‌سازی** کارت «ارتقای سوئیت HOMA» را انتخاب کنید؛ دکمهٔ طلایی Refresh در نوار بالایی نیز همین مسیر را باز می‌کند. پس از تأیید، پنل مراحل زیر را انجام می‌دهد:

1. اجرای عملیات ثابت و Allowlistشدهٔ `homa-menu.sh --update --from-panel`؛ هیچ URL یا فرمان دلخواهی از مرورگر پذیرفته نمی‌شود.
2. دریافت آخرین Release رسمی `Dark-Sky07/HOMA-Optimizer` و در صورت در دسترس نبودن آن، شاخهٔ `main` همان مخزن.
3. نصب هم‌زمان اسکریپت‌ها و فایل‌های پنل با حفظ `/etc/homa/panel.env`، توکن دسترسی و سایر تنظیمات.
4. ثبت نتیجهٔ عملیات و سپس Restart سرویس `homa-panel.service` پس از تأخیر کوتاه؛ رابط به‌صورت خودکار منتظر بازگشت سرویس می‌ماند و صفحه را تازه می‌کند.

این عملیات به root نیاز دارد و در حالت فقط‌خواندنی مسدود است. اگر پنل خارج از systemd اجرا شود، Restart خودکار انجام نمی‌شود؛ در این حالت پس از نصب موفق، `homa-panel` را دستی راه‌اندازی مجدد کنید. توکن در خروجی عملیات به‌روزرسانی چاپ نمی‌شود.

### به‌روزرسانی از ترمینال

```bash
homa --update
# یا از داخل منو:
homa → [u] Update complete HOMA suite
```

### بازگردانی تنظیمات

```text
homa → [r] Restore / Rollback settings
```

برای بازگردانی فقط تنظیمات شبکه، ماژول **Rollback network tuning** در مرکز بهینه‌سازی گرافیکی نیز موجود است. به‌روزرسانی برنامه جایگزین Rollback پیکربندی نیست و پیش از تغییرات عملیاتی همچنان پشتیبان‌گیری توصیه می‌شود.

---

## ✅ بررسی سلامت سورس

```bash
# Syntax همهٔ اسکریپت‌ها
for script in install.sh scripts/*.sh; do bash -n "$script" || exit 1; done

# بک‌اند و تست‌های آن
python3 -m unittest discover -s panel -p 'test_*.py' -v

# JavaScript، در صورت وجود Node روی سیستم توسعه
node --check panel/static/app.js
```

---

## 🤝 لایسنس

این پروژه تحت لایسنس MIT و برای کمک به جامعهٔ مدیران سرور و دسترسی به اینترنت آزاد توسعه داده می‌شود.

**HOMA · Rise Above Limits.**
