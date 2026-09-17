# -*- coding: utf-8 -*-
"""پردازش هر Update دریافتی از بله. تقریباً همان منطق bot/handlers.py
تلگرام است (چون API بله بر پایهٔ API بات تلگرام است)، با دو تفاوت:
۱) بله inline mode ندارد، پس هیچ _handle_inline_query ای اینجا نیست.
۲) از ماژول‌های مستقل bale/api.py و bale/db.py و bale/config.py استفاده
   می‌کند تا هیچ ریسکی برای ربات تلگرام نداشته باشد.
"""
from bot import format as fmt, keyboards as kb, membership

from . import config
from . import api as bale_api
from . import db


def get_welcome_text():
    lines = [
        "👋 به <b>ربات نرخ امروز چند؟</b> خوش آمدید!",
        "",
        "از منوی زیر یکی از دسته‌ها را انتخاب کنید، یا برای جستجوی سریع کافی‌ست "
        "بخشی از نام یک نماد (مثلا «دلار» یا «سکه») را همین‌جا تایپ کنید.",
    ]
    return "\n".join(lines)


def handle_update(update: dict):
    if "message" in update:
        _handle_message(update["message"])
    elif "callback_query" in update:
        _handle_callback(update["callback_query"])
    # بله inline_query ندارد؛ اگر هم در آپدیت بیاید، نادیده گرفته می‌شود.


# ---------------------------------------------------------------------------
# عضویت اجباری در کانال
# ---------------------------------------------------------------------------

def _check_gate(user_id):
    if not config.REQUIRED_CHANNELS:
        return None
    missing = membership.get_missing_channels(bale_api, config.REQUIRED_CHANNELS, user_id)
    return missing or None


def _send_gate_message(chat_id, missing_channels):
    bale_api.send_message(
        chat_id,
        membership.build_join_message(missing_channels),
        membership.build_join_keyboard(missing_channels),
    )


# ---------------------------------------------------------------------------
# پیام‌های معمولی
# ---------------------------------------------------------------------------

def _handle_message(message: dict):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = (message.get("text") or "").strip()

    if text in ("/start", "/help"):
        bale_api.send_message(chat_id, get_welcome_text(), kb.main_menu())
        missing = _check_gate(user_id)
        if missing:
            _send_gate_message(chat_id, missing)
        return

    missing = _check_gate(user_id)
    if missing:
        _send_gate_message(chat_id, missing)
        return

    if text == "/watchlist":
        _send_watchlist(chat_id, user_id)
        return

    if not text or text.startswith("/"):
        bale_api.send_message(chat_id, "دستور ناشناخته. برای شروع /start را بزنید.", kb.main_menu())
        return

    results = db.search_items(text, limit=10)
    if not results:
        bale_api.send_message(
            chat_id,
            f"🔍 برای «{text}» نتیجه‌ای پیدا نشد.\nاملای دیگری را امتحان کنید یا از منوی اصلی استفاده کنید.",
            kb.main_menu(),
        )
        return

    bale_api.send_message(chat_id, f"🔍 نتایج جستجو برای «{text}»:", kb.search_results_keyboard(results))


def _send_watchlist(chat_id, user_id):
    keys = db.get_watchlist_keys(user_id)
    rows = db.get_items(keys)
    bale_api.send_message(chat_id, fmt.build_watchlist_message(rows), kb.watchlist_keyboard(rows))


# ---------------------------------------------------------------------------
# کلیک روی دکمه‌های شیشه‌ای
# ---------------------------------------------------------------------------

def _handle_callback(cq: dict):
    data = cq.get("data", "")
    chat_id = cq["message"]["chat"]["id"]
    message_id = cq["message"]["message_id"]
    user_id = cq["from"]["id"]
    cq_id = cq["id"]

    try:
        if data == "check_membership":
            missing = _check_gate(user_id)
            if missing:
                names = "، ".join(ch["title"] for ch in missing)
                bale_api.answer_callback_query(cq_id, f"هنوز عضو این کانال(ها) نشده‌اید: {names}", show_alert=True)
                return
            bale_api.answer_callback_query(cq_id, "🎉 عضویت شما تایید شد!")
            bale_api.edit_message_text(
                chat_id, message_id,
                "🎉 عضویت شما تایید شد! حالا می‌توانید از ربات استفاده کنید.\n\n" + get_welcome_text(),
                kb.main_menu(),
            )
            return

        missing = _check_gate(user_id)
        if missing:
            bale_api.answer_callback_query(cq_id, "🔒 لطفاً ابتدا عضو کانال(های) لازم شوید.", show_alert=True)
            _send_gate_message(chat_id, missing)
            return

        if data == "home":
            bale_api.edit_message_text(chat_id, message_id, get_welcome_text(), kb.main_menu())

        elif data == "burmenu":
            bale_api.edit_message_text(chat_id, message_id, "📈 <b>شاخص‌های بورس و جهانی</b>\nیکی از زیردسته‌ها را انتخاب کنید:", kb.bourse_submenu())

        elif data == "watchlist":
            keys = db.get_watchlist_keys(user_id)
            rows = db.get_items(keys)
            bale_api.edit_message_text(chat_id, message_id, fmt.build_watchlist_message(rows), kb.watchlist_keyboard(rows))

        elif data == "search_prompt":
            bale_api.edit_message_text(
                chat_id, message_id,
                "🔍 <b>جستجوی پیشرفته</b>\n\nبخشی از نام نماد مورد نظر را تایپ و ارسال کنید "
                "(مثلا «یورو» یا «بیت‌کوین»)؛ ربات نزدیک‌ترین نتایج را نشان می‌دهد.",
                {"inline_keyboard": [[{"text": "🏠 منوی اصلی", "callback_data": "home"}]]},
            )

        elif data.startswith("cat:") or data.startswith("sub:") or data.startswith("refresh_list:"):
            _, origin, page_s = data.split(":")
            _show_list(chat_id, message_id, origin, int(page_s))

        elif data.startswith("item:") or data.startswith("refresh_item:"):
            _, key, origin, page_s = data.split(":")
            _show_item(chat_id, message_id, user_id, key, origin, int(page_s))

        elif data.startswith("fav_add:"):
            _, key, origin, page_s = data.split(":")
            db.add_to_watchlist(user_id, key)
            bale_api.answer_callback_query(cq_id, "⭐ به دیده‌بان اضافه شد.")
            _show_item(chat_id, message_id, user_id, key, origin, int(page_s))
            return

        elif data.startswith("fav_del:"):
            _, key, origin, page_s = data.split(":")
            db.remove_from_watchlist(user_id, key)
            bale_api.answer_callback_query(cq_id, "🗑 از دیده‌بان حذف شد.")
            _show_item(chat_id, message_id, user_id, key, origin, int(page_s))
            return

        elif data == "noop_search":
            bale_api.answer_callback_query(cq_id, "برای جستجوی دوباره، عبارت جدید را تایپ کنید.")
            return

        bale_api.answer_callback_query(cq_id)
    except Exception as e:
        print(f"[bale_handlers] callback error: {e}")
        bale_api.answer_callback_query(cq_id, "⚠️ خطایی رخ داد، دوباره تلاش کنید.")


def _show_list(chat_id, message_id, origin, page):
    keys = kb._resolve_keys(origin)
    if keys is None:
        bale_api.edit_message_text(chat_id, message_id, get_welcome_text(), kb.main_menu())
        return

    start = page * config.PAGE_SIZE
    page_keys = keys[start:start + config.PAGE_SIZE]
    rows = db.get_items(page_keys)

    title = None
    if origin in config.CATEGORIES:
        cat = config.CATEGORIES[origin]
        title = f"{cat['emoji']} <b>{cat['title']}</b>"
    elif origin in config.BOURSE_SUBCATEGORIES:
        cat = config.BOURSE_SUBCATEGORIES[origin]
        title = f"{cat['emoji']} <b>{cat['title']}</b>"

    text = f"{title}\n\nبرای مشاهده جزئیات هر مورد، روی آن بزنید:"
    bale_api.edit_message_text(chat_id, message_id, text, kb.list_keyboard(origin, page, rows, len(keys)))


def _show_item(chat_id, message_id, user_id, symbol_key, origin, page):
    row = db.get_item(symbol_key)
    if row is None:
        bale_api.edit_message_text(chat_id, message_id, "❌ این نماد پیدا نشد (ممکن است حذف شده باشد).", kb.main_menu())
        return
    is_fav = db.is_in_watchlist(user_id, symbol_key)
    text = fmt.build_item_message(row)
    bale_api.edit_message_text(chat_id, message_id, text, kb.item_detail_keyboard(symbol_key, origin, page, is_fav))
