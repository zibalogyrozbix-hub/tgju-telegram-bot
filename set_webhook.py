# -*- coding: utf-8 -*-
"""
این اسکریپت را فقط یک‌بار (و بعدها هر وقت آدرس دیپلوی عوض شد) روی سیستم
خودتان اجرا کنید تا به تلگرام بگویید آپدیت‌ها را به کجا بفرستد.

اجرا:
    export TELEGRAM_BOT_TOKEN="..."      # از BotFather
    export WEBHOOK_SECRET="یک-رشته-دلخواه-و-تصادفی"
    python set_webhook.py https://<یوزرنیم‌شما>.pythonanywhere.com/webhook

نکته: همین WEBHOOK_SECRET باید داخل فایل .env که روی خود PythonAnywhere
ساختید هم دقیقا همین مقدار را داشته باشد.
"""
import os
import sys
import requests

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
SECRET = os.environ.get("WEBHOOK_SECRET", "").strip()

if not TOKEN:
    print("خطا: متغیر محیطی TELEGRAM_BOT_TOKEN تنظیم نشده.")
    sys.exit(1)

if len(sys.argv) < 2:
    print("استفاده: python set_webhook.py https://<یوزرنیم‌شما>.pythonanywhere.com/webhook")
    sys.exit(1)

webhook_url = sys.argv[1]

resp = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/setWebhook",
    json={
        "url": webhook_url,
        "secret_token": SECRET,
        "allowed_updates": ["message", "callback_query", "inline_query"],
    },
)
print(resp.json())

# دستورهای منوی / (اختیاری ولی خوب است)
commands_resp = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/setMyCommands",
    json={"commands": [
        {"command": "start", "description": "شروع و نمایش منوی اصلی"},
        {"command": "watchlist", "description": "نمایش دیده‌بان من"},
        {"command": "help", "description": "راهنما"},
    ]},
)
print(commands_resp.json())

info_resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
print("وضعیت فعلی وبهوک:", info_resp.json())
