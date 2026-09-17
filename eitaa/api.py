# -*- coding: utf-8 -*-
"""پیاده‌سازی دقیق سه متد مستندشدهٔ eitaayar.ir. آدرس فراخوانی طبق مستندات:
https://eitaayar.ir/api/TOKEN/METHOD_NAME
"""
import re
import requests
from . import config


def clean_html(text: str) -> str:
    """حذف تمامی تگ‌های HTML برای نمایش متنی تمیز در ایتا"""
    if not text:
        return text
    return re.sub(r'<[^>]*>', '', str(text))


def _call(method: str, payload: dict):
    url = f"{config.EITAA_API}/{method}"
    try:
        resp = requests.post(url, json=payload, timeout=15)
        data = resp.json()
        if not data.get("ok"):
            print(f"[eitaa_api] {method} failed: {data}")
        return data
    except Exception as e:
        print(f"[eitaa_api] {method} exception: {e}")
        return None


def get_me():
    """ساده‌ترین متد؛ بدون ورودی، برای تست صحت توکن مفید است."""
    return _call("getMe", {})


def send_message(chat_id: str, text: str, title: str = None, disable_notification: bool = None, pin: bool = None):
    """ارسال پیام متنی. chat_id می‌تواند یوزرنیم کانال بدون @ باشد (مثلا
    'nerkhemroozchand') یا شناسهٔ عددی."""
    payload = {
        "chat_id": chat_id, 
        "text": clean_html(text)
    }
    if title:
        payload["title"] = clean_html(title)
    if disable_notification is not None:
        payload["disable_notification"] = 1 if disable_notification else 0
    if pin is not None:
        payload["pin"] = 1 if pin else 0
    return _call("sendMessage", payload)


def send_file(chat_id: str, file_url_or_path: str, caption: str = None):
    """ارسال فایل/مدیا. طبق مستندات، پارامتر file هم می‌تواند لینک باشد هم
    مسیر فایل روی دیسک (multipart/form-data) — اینجا نسخهٔ سادهٔ لینک/رشته
    پیاده شده است."""
    payload = {"chat_id": chat_id, "file": file_url_or_path}
    if caption:
        payload["caption"] = clean_html(caption)
    return _call("sendFile", payload)
