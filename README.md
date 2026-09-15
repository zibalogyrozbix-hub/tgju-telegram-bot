# 🤖 ربات نرخ امروز چند؟ (نسخهٔ PythonAnywhere)

ربات تلگرامی که نرخ‌های دلار، طلا، سکه، ارز دیجیتال و شاخص‌های بورس را
مستقیم از همان دیتابیس Turso که پروژهٔ اسکرِیپرِ شما (`nrkhmroozchand-db`)
پر می‌کند، می‌خواند و با منوی شیشه‌ای (Inline Keyboard) شیک نمایش می‌دهد.

این نسخه به‌جای Vercel روی **[PythonAnywhere](https://www.pythonanywhere.com)**
دیپلوی می‌شود — یک هاست رایگان که از ایران هم در دسترس است، نیازی به کارت
اعتباری ندارد، و برای وب‌اپ‌های همیشه‌روشن (نه صرفا serverless) رایگان است.

✅ هر دو دامنه‌ای که ربات لازم دارد (`api.telegram.org` و `*.turso.io`) در
لیست سفید (allowlist) اکانت رایگان PythonAnywhere هستند و بدون هیچ تنظیم
اضافه‌ای کار می‌کنند — این را قبل از نوشتن این نسخه بررسی کردم.

---

## 🧠 معماری در یک نگاه

```
کاربر در تلگرام --> Telegram Bot API --> POST /webhook (وب‌اپ PythonAnywhere)
                                                |
                                                v
                                    bot/handlers.py تصمیم می‌گیرد
                                                |
                                                v
                                bot/db.py از Turso می‌خواند (فقط خواندن)
                                                |
                                                v
                          bot/telegram_api.py جواب را به کاربر می‌فرستد
```

بر خلاف Vercel که serverless و کوتاه‌عمر است، اینجا یک وب‌اپ Flask واقعی و
همیشه‌روشن روی PythonAnywhere اجرا می‌شود (زیرساخت uWSGI خودشان). این ربات
هرگز داده‌ای در `market_prices` نمی‌نویسد؛ فقط می‌خواند. آپدیت قیمت‌ها
همچنان کار همان پروژهٔ اسکرِیپر (کرون GitHub Actions) شماست. یک جدول کوچک
مستقل به اسم `watchlist` هم برای دیده‌بان شخصی هر کاربر، خودکار در همان
Turso ساخته می‌شود.

### ساختار فایل‌ها

```
tgju-telegram-bot/
├── app.py                          # اپ Flask؛ همین فایل را WSGI ایمپورت می‌کند
├── bot/
│   ├── config.py                    # env varها + لیست دسته‌بندی‌ها
│   ├── db.py                         # خواندن از Turso + جدول watchlist
│   ├── format.py                     # محاسبهٔ «نرخ دیروز»، ایموجی صعود/نزول
│   ├── keyboards.py                  # دکمه‌های شیشه‌ای و صفحه‌بندی
│   ├── telegram_api.py               # تماس با HTTP API تلگرام
│   └── handlers.py                   # مغز ربات
├── requirements.txt
├── set_webhook.py                    # ثبت آدرس وبهوک نزد تلگرام (اجرای محلی)
├── pythonanywhere_wsgi_example.py    # نمونهٔ محتوای فایل WSGI پای‌تون‌انی‌ور
├── .env.example
└── .gitignore
```

---

## 🎛 امکانات پیاده‌شده

- منوی اصلی شیشه‌ای: 💵 ارزهای اصلی، 🪙 طلا/سکه/حباب‌ها، 📈 بورس و جهانی
  (با زیرمنوی 🏛 ایران / 🌍 جهانی / 🛢 کالا و انرژی چون بیش از ۳۰ آیتم دارد)،
  💎 ارزهای دیجیتال، 🔍 جستجو، ⭐ دیده‌بان من.
- صفحه‌بندی ۸تایی روی هر لیست با ◀️ قبلی / بعدی ▶️.
- جزئیات هر نماد: نرخ فعلی، **نرخ دیروز** (= نرخ فعلی − میزان تغییر)، تغییر
  با 🔺/🔻، درصد تغییر در پرانتز، زمان بروزرسانی.
- ⭐ افزودن/💔 حذف از دیده‌بان شخصی + `/watchlist`.
- 🔄 «بروزرسانی لحظه‌ای» (دوباره از دیتابیس می‌خواند؛ توضیح مهم پایین صفحه).
- جستجوی autofill به دو شکل: تایپ آزاد داخل چت ربات، و **inline mode واقعی
  تلگرام** (`@یوزرنیم‌ربات‌شما دلار` در هر چتی).

### ⚠️ نکتهٔ مهم دربارهٔ «لحظه‌ای»
ربات خودش اسکرِیپینگ نمی‌کند؛ فقط آخرین ردیف ذخیره‌شده توسط پروژهٔ اسکرِیپر
را نشان می‌دهد. «لحظه‌ای بودن» دقیقاً به فاصلهٔ کرون GitHub Actions شما
بستگی دارد، نه لحظهٔ کلیک کاربر.

---

## 🚀 راه‌اندازی سریع، قدم‌به‌قدم

### ۱) ساخت ربات در تلگرام
1. به [@BotFather](https://t.me/BotFather) پیام بدهید و `/newbot` را بزنید؛
   توکن را جایی امن کپی کنید.
2. برای autofill سراسری: `/setinline` را به BotFather بدهید، ربات‌تان را
   انتخاب کنید و یک متن placeholder وارد کنید (مثلا «نام نماد را بنویسید...»).

### ۲) پوش کردن پروژه در گیت‌هاب
```bash
cd tgju-telegram-bot
git init && git add . && git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/<یوزرنیم‌شما>/tgju-telegram-bot.git
git push -u origin main
```

### ۳) ساخت اکانت رایگان PythonAnywhere
1. در [pythonanywhere.com](https://www.pythonanywhere.com/registration/register/beginner/)
   یک اکانت **Beginner (Free)** بسازید (نیاز به کارت اعتباری ندارد).

### ۴) کلون کردن پروژه داخل PythonAnywhere
از تب **Consoles** یک کنسول **Bash** جدید باز کنید و بزنید:
```bash
git clone https://github.com/<یوزرنیم‌شما>/tgju-telegram-bot.git
cd tgju-telegram-bot
```

### ۵) ساخت virtualenv و نصب پکیج‌ها
همان‌جا در کنسول Bash:
```bash
mkvirtualenv --python=/usr/bin/python3.10 tgjubot-venv
pip install -r requirements.txt
```
(دفعات بعد که کنسول جدید باز کردید، کافی‌ست `workon tgjubot-venv` بزنید تا
همین محیط دوباره فعال شود.)

### ۶) ساخت فایل .env (رمزها را اینجا نگه می‌داریم، نه در گیت‌هاب)
```bash
nano ~/tgju-telegram-bot/.env
```
این محتوا را (با مقدارهای واقعی خودتان) بنویسید و ذخیره کنید (`Ctrl+O` سپس
`Ctrl+X`):
```
TELEGRAM_BOT_TOKEN=همان توکن از BotFather
TURSO_DATABASE_URL=libsql://your-db-name.turso.io
TURSO_AUTH_TOKEN=توکن دیتابیس Turso
WEBHOOK_SECRET=یک-رشتهٔ-تصادفی-دلخواه
```

### ۷) ساخت وب‌اپ در تب Web
1. تب **Web** → **Add a new web app** → دامنهٔ پیش‌فرض
   `<یوزرنیم‌شما>.pythonanywhere.com` را تایید کنید.
2. وقتی framework را می‌پرسد، **«Manual configuration»** را انتخاب کنید
   (نه Flask خودکار) و نسخهٔ **Python 3.10** را بزنید.
3. در بخش **Virtualenv** همان صفحه، مسیر virtualenv‌ای که ساختید را وارد
   کنید: `/home/<یوزرنیم‌شما>/.virtualenvs/tgjubot-venv`
4. در همان صفحه روی لینک فایل **WSGI configuration file** بزنید (چیزی مثل
   `/var/www/<یوزرنیم‌شما>_pythonanywhere_com_wsgi.py` باز می‌شود). تمام
   محتوای پیش‌فرض آن را پاک کنید و محتوای فایل
   `pythonanywhere_wsgi_example.py` را (با جایگزین کردن یوزرنیم و مسیر
   واقعی خودتان) کپی کنید. ذخیره کنید.
5. برگردید به تب Web و دکمهٔ سبز **Reload** را بزنید.

حالا اگر آدرس `https://<یوزرنیم‌شما>.pythonanywhere.com/webhook` را در
مرورگر باز کنید، باید یک JSON شبیه `{"ok": true, "service": "..."}` ببینید
— یعنی وب‌اپ زنده است.

### ۸) ثبت وبهوک نزد تلگرام
این بخش را روی **کامپیوتر خودتان** (نه PythonAnywhere) اجرا کنید:
```bash
pip install requests
export TELEGRAM_BOT_TOKEN="همان توکن"
export WEBHOOK_SECRET="همان رشتهٔ قدم ۶"
python set_webhook.py https://<یوزرنیم‌شما>.pythonanywhere.com/webhook
```
اگر `{"ok": true, "result": true, ...}` دیدید، تمام شد. به تلگرام بروید و
`/start` بزنید.

### ۹) تست inline mode
در هر چتی بنویسید: `@یوزرنیم‌ربات‌شما دلار` — باید لیست پیشنهادها ظاهر شود.

---

## 🔄 هر بار که کد را تغییر دادید
```bash
cd ~/tgju-telegram-bot
git pull
```
سپس از تب **Web**، دکمهٔ **Reload** را بزنید (PythonAnywhere کد جدید را
خودکار برنمی‌دارد؛ حتما باید Reload بزنید).

## ➕ اضافه کردن نماد جدید به منوها
کافی‌ست `symbol_key` مربوطه را به یکی از لیست‌های داخل `bot/config.py`
اضافه کنید. عنوان/قیمت/تغییرات همیشه مستقیم از دیتابیس خوانده می‌شود، پس
جای دیگری نیاز به تغییر نیست.

## 🔧 عیب‌یابی سریع
- **ربات جواب نمی‌دهد:**
  `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo` بزنید و چک
  کنید `url` درست ثبت شده و `last_error_message` خالی است.
- **صفحهٔ `/webhook` خطای 500 می‌دهد:** تب **Web** → پایین صفحه لینک
  **Error log** را باز کنید؛ معمولا یا `.env` درست ساخته نشده یا پکیجی نصب
  نشده (`pip install -r requirements.txt` را دوباره با virtualenv فعال
  اجرا کنید).
- **دکمه‌ها کار نمی‌کنند ولی پیام اول می‌آید:** یعنی وبهوک درست ثبت شده ولی
  `WEBHOOK_SECRET` بین `.env` و `set_webhook.py` یکی نیست؛ دوباره با مقدار
  درست `set_webhook.py` را اجرا کنید.
- **خطای اتصال به Turso:** مطمئن شوید `TURSO_DATABASE_URL` با `libsql://`
  یا `https://` شروع می‌شود و توکن هنوز منقضی نشده.
- محدودیت اکانت رایگان: PythonAnywhere هر روز سهمیهٔ محدودی «CPU seconds»
  می‌دهد؛ برای یک ربات شخصی/کوچک این سهمیه به‌سادگی کافی است.
