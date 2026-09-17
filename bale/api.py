# -*- coding: utf-8 -*-
"""تماس مستقیم با HTTP API بله (tapi.bale.ai). API بله «بر پایهٔ API بات
تلگرام و با تغییراتی جزئی» طراحی شده (طبق مستندات رسمی docs.bale.ai)، برای
همین ساختار این فایل تقریبا عین bot/telegram_api.py است. مهم‌ترین تفاوت:
بله از inline mode (answerInlineQuery) و parse_mode (مثل HTML) پشتیبانی نمی‌کند، 
پس تگ‌ها پیش از ارسال پاک‌سازی می‌شوند.
"""
import re
import requests
from . import config


def clean_html(text: str) -> str:
    """حذف تمامی تگ‌های HTML برای نمایش تمیز در پیام‌رسان بله"""
    if not text:
        return text
    return re.sub(r'<[^>]*>', '', str(text))


def _call(method: str, payload: dict):
    url = f"{config.BALE_API}/{method}"
    try:
        resp = requests.post(url, json=payload, timeout=10)
        data = resp.json()
        if not data.get("ok"):
            print(f"[bale_api] {method} failed: {data}")
        return data
    except Exception as e:
        print(f"[bale_api] {method} exception: {e}")
        return None


def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": clean_html(text),
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    return _call("sendMessage", payload)


def edit_message_text(chat_id, message_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": clean_html(text),
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    return _call("editMessageText", payload)


def answer_callback_query(callback_query_id, text=None, show_alert=False):
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = clean_html(text)
        payload["show_alert"] = show_alert
    return _call("answerCallbackQuery", payload)


def get_chat_member(chat_id, user_id):
    return _call("getChatMember", {"chat_id": chat_id, "user_id": user_id})


def get_chat_member_status(chat_id, user_id):
    result = get_chat_member(chat_id, user_id)
    if result and result.get("ok"):
        return result.get("result", {}).get("status")
    return None


def set_my_commands(commands):
    return _call("setMyCommands", {"commands": commands})
