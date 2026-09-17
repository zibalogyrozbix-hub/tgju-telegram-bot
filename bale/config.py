# -*- coding: utf-8 -*-
"""
تنظیمات ربات بله. عمداً مستقل از bot/config.py است (توکن و کانال جدا)، ولی
دسته‌بندی‌های نمادها (ارز/طلا/بورس/کریپتو) را از همان bot/config.py
می‌خواند تا در دو جا تعریف نشوند و همیشه با هم هماهنگ بمانند.
"""
import os
from bot import config as tg_config

BALE_BOT_TOKEN = os.environ.get("BALE_BOT_TOKEN", "").strip()
BALE_WEBHOOK_SECRET = os.environ.get("BALE_WEBHOOK_SECRET", "").strip()
# یوزرنیم ربات در بله (فقط برای نمایش در متن راهنما استفاده می‌شود)
BALE_BOT_USERNAME = os.environ.get("BALE_BOT_USERNAME", "").strip()

BALE_API = f"https://tapi.bale.ir/bot{BALE_BOT_TOKEN}"

# دسته‌بندی‌ها را از پروژه تلگرام «قرض» می‌گیریم (منبع واحد حقیقت):
CATEGORIES = tg_config.CATEGORIES
BOURSE_SUBCATEGORIES = tg_config.BOURSE_SUBCATEGORIES
PAGE_SIZE = tg_config.PAGE_SIZE
category_emoji_for_key = tg_config.category_emoji_for_key

# کانال اجباری برای بله (می‌تواند همان کانال تلگرام باشد یا کانال جداگانهٔ
# بله؛ چون این دو پیام‌رسان کانال جدا از هم دارند، اینجا هم جداگانه تعریف
# شده تا مستقل تنظیم شود). برای افزودن کانال دوم، یک دیکشنری دیگر اضافه کنید.
REQUIRED_CHANNELS = [
    {
        "id": "@nerkhemroozchand",
        "title": "کانال نرخ امروز چند؟",
        "url": "https://ble.ir/nerkhemroozchand",
    },
]
