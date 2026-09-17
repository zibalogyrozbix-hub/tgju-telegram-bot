# -*- coding: utf-8 -*-
"""
این اسکریپت را یک‌بار (و بعدها هر وقت آدرس دیپلوی عوض شد) روی سیستم خودتان
اجرا کنید تا به بله بگویید آپدیت‌ها را به کجا بفرستد.

اجرا:
    export BALE_BOT_TOKEN="..."          # از @botfather در بله
    export BALE_WEBHOOK_SECRET="یک-رشته-دلخواه-و-تصادفی"
    python set_webhook_bale.py https://<نام‌پروژه‌شما>.up.railway.app/webhook/bale

نکته: همین BALE_WEBHOOK_SECRET باید در تب Variables پروژه‌تان روی Railway
هم دقیقا همین مقدار را داشته باشد.
"""
import os
import sys
import requests

TOKEN = os.environ.get("BALE_BOT_TOKEN", "").strip()
SECRET = os.environ.get("BALE_WEBHOOK_SECRET", "").strip()

if not TOKEN:
    print("خطا: متغیر محیطی BALE_BOT_TOKEN تنظیم نشده.")
    sys.exit(1)

if len(sys.argv) < 2:
    print("استفاده: python set_webhook_bale.py https://<پروژه‌شما>.up.railway.app/webhook/bale")
    sys.exit(1)

webhook_url = sys.argv[1]

resp = requests.post(
    f"https://tapi.bale.ir/bot{TOKEN}/setWebhook",
    json={"url": webhook_url, "secret_token": SECRET},
)
print(resp.json())

commands_resp = requests.post(
    f"https://tapi.bale.ir/bot{TOKEN}/setMyCommands",
    json={"commands": [
        {"command": "start", "description": "شروع و نمایش منوی اصلی"},
        {"command": "watchlist", "description": "نمایش دیده‌بان من"},
        {"command": "help", "description": "راهنما"},
    ]},
)
print(commands_resp.json())
