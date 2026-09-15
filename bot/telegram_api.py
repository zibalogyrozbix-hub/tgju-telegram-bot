# -*- coding: utf-8 -*-
"""تماس مستقیم با HTTP API تلگرام. عمدا به‌جای کتابخانه‌های سنگین async از
درخواست‌های ساده requests استفاده شده چون در محیط serverless (هر
فراخوانی = یک پردازش کوتاه‌عمر) سریع‌تر initialize می‌شود و دیباگش هم
ساده‌تر است."""
import requests
from . import config


def _call(method: str, payload: dict):
    url = f"{config.TELEGRAM_API}/{method}"
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if not data.get("ok"):
            print(f"[telegram_api] {method} failed: {data}")
        return data
    except Exception as e:
        print(f"[telegram_api] {method} exception: {e}")
        return None


def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    return _call("sendMessage", payload)


def edit_message_text(chat_id, message_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    result = _call("editMessageText", payload)
    # اگر متن/کیبورد جدید دقیقا مثل قبل باشد، تلگرام خطای
    # "message is not modified" می‌دهد؛ این خطا بی‌ضرر است (مثلا وقتی
    # کاربر روی «بروزرسانی» می‌زند ولی قیمت هنوز عوض نشده).
    return result


def answer_callback_query(callback_query_id, text=None, show_alert=False):
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = show_alert
    return _call("answerCallbackQuery", payload)


def answer_inline_query(inline_query_id, results, cache_time=15):
    payload = {
        "inline_query_id": inline_query_id,
        "results": results,
        "cache_time": cache_time,
        "is_personal": False,
    }
    return _call("answerInlineQuery", payload)


def set_my_commands(commands):
    return _call("setMyCommands", {"commands": commands})
