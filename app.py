# -*- coding: utf-8 -*-
"""
نقطهٔ ورود اپ Flask. روی Railway این فایل توسط gunicorn اجرا می‌شود
(به Procfile نگاه کنید: `gunicorn app:app ...`)، یعنی همین شیء `app` مستقیم
به‌عنوان اپ WSGI استفاده می‌شود.

این فایل دو مسیر webhook دارد:
  /webhook        -> ربات تلگرام (بدون تغییر نسبت به قبل)
  /webhook/bale   -> ربات بله (جدید، کاملا افزوده‌شده و مستقل)
ایتا وبهوک ندارد (به eitaa/config.py توضیح داده شده چرا)، برای همین اینجا
مسیری برایش نیست؛ گزارش‌های ایتا با اجرای دستی/زمان‌بندی‌شدهٔ
eitaa/broadcaster.py ارسال می‌شوند.

آدرس نهایی وبهوک تلگرام بعد از دیپلوی روی Railway چیزی شبیه این می‌شود:
    https://<نام‌پروژه‌شما>.up.railway.app/webhook
و برای بله:
    https://<نام‌پروژه‌شما>.up.railway.app/webhook/bale
همین آدرس‌ها را باید هنگام اجرای set_webhook.py و set_webhook_bale.py بدهید.
"""
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# متغیرهای محیطی را اول از فایل .env می‌خواند (برای تست محلی روی کامپیوتر
# خودتان). روی خود Railway نیازی به فایل .env نیست چون متغیرها را مستقیم
# در تب Variables داشبورد Railway تنظیم می‌کنید؛ این خط در آن حالت صرفاً
# بی‌ضرر است (فایلی برای خواندن پیدا نمی‌کند).
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
    # Railway از مسیر "/" برای healthcheck استفاده می‌کند (به railway.json
    # نگاه کنید)؛ همین روت هم آن را جواب می‌دهد و هم برای تست دستی مفید است.
    return jsonify({"ok": True, "service": "تلگرام‌بات نرخ امروز چند؟"})


# ---------------------------------------------------------------------------
# مسیر جدید و مستقل ربات بله. اگر BALE_BOT_TOKEN تنظیم نشده باشد، این مسیر
# هم‌چنان بالا می‌آید ولی هر درخواستی که برسد را رد می‌کند (بی‌ضرر برای
# دیپلوی‌هایی که فقط تلگرام می‌خواهند).
# ---------------------------------------------------------------------------

try:
    from bale import config as bale_config
    from bale.handlers import handle_update as handle_bale_update
    _BALE_AVAILABLE = True
except Exception as e:
    print(f"[app] ماژول بله بارگذاری نشد (بی‌اشکال اگر استفاده نمی‌کنید): {e}")
    _BALE_AVAILABLE = False


@app.route("/webhook/bale", methods=["POST"])
def webhook_bale():
    if not _BALE_AVAILABLE or not bale_config.BALE_BOT_TOKEN:
        return jsonify({"ok": False, "error": "bale not configured"}), 404

    # نکته: چون بله «بر پایهٔ API بات تلگرام» ساخته شده ولی مستندات رسمی
    # دقیقی از نام هدر مخفی‌اش پیدا نکردم، هر دو حالت محتمل را چک می‌کنیم؛
    # اگر بعد از تنظیم دیدید درخواست‌های واقعی بله رد می‌شوند، خالی گذاشتن
    # BALE_WEBHOOK_SECRET (که این بررسی را کلاً غیرفعال می‌کند) امن‌ترین راه‌حل سریع است.
    secret_header = (
        request.headers.get("X-Bale-Bot-Api-Secret-Token", "")
        or request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    )
    if bale_config.BALE_WEBHOOK_SECRET and secret_header != bale_config.BALE_WEBHOOK_SECRET:
        return jsonify({"ok": False, "error": "invalid secret"}), 403

    update = request.get_json(silent=True) or {}
    try:
        handle_bale_update(update)
    except Exception as e:
        print(f"[webhook_bale] unhandled error: {e}")

    return jsonify({"ok": True})


@app.route("/webhook/bale", methods=["GET"])
def webhook_bale_health():
    return jsonify({"ok": True, "service": "ربات بله - نرخ امروز چند؟", "configured": _BALE_AVAILABLE})


if __name__ == "__main__":
    # فقط برای تست محلی روی کامپیوتر خودتان (نه روی Railway - آنجا gunicorn
    # طبق Procfile اجرا می‌کند)
    app.run(debug=True, port=5000)
