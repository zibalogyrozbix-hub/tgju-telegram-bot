# -*- coding: utf-8 -*-
"""
نقطهٔ ورود اپ Flask. فایل WSGI که PythonAnywhere می‌سازد فقط باید این خط را
داشته باشد:

    from app import app as application

آدرس نهایی وبهوک می‌شود:  https://<یوزرنیم‌شما>.pythonanywhere.com/webhook
همین آدرس را باید هنگام اجرای set_webhook.py بدهید.
"""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# متغیرهای محیطی را از فایل .env (که فقط روی خود PythonAnywhere می‌سازید و
# هرگز به گیت‌هاب پوش نمی‌شود) می‌خواند. اگر متغیرها را از راه دیگری
# (مثلا export در bash_profile) تنظیم کرده باشید، این خط بی‌ضرر است.
from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

from flask import Flask, request, jsonify

from bot import config
from bot.handlers import handle_update

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    # اعتبارسنجی با هدر مخفی: فقط درخواست‌هایی که تلگرام (بعد از
    # setWebhook با secret_token) می‌فرستد قبول می‌شوند.
    secret_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if config.WEBHOOK_SECRET and secret_header != config.WEBHOOK_SECRET:
        return jsonify({"ok": False, "error": "invalid secret"}), 403

    update = request.get_json(silent=True) or {}
    try:
        handle_update(update)
    except Exception as e:
        # هرگز نباید خطای داخلی باعث شود تلگرام کد غیر ۲۰۰ ببیند (وگرنه
        # همان آپدیت را دوباره و دوباره retry می‌کند)
        print(f"[webhook] unhandled error: {e}")

    return jsonify({"ok": True})


@app.route("/webhook", methods=["GET"])
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"ok": True, "service": "تلگرام‌بات نرخ امروز چند؟"})


if __name__ == "__main__":
    # فقط برای تست محلی روی کامپیوتر خودتان (نه روی PythonAnywhere)
    app.run(debug=True, port=5000)
