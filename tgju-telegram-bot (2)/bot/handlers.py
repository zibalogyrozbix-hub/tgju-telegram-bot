# -*- coding: utf-8 -*-
"""پردازش هر Update دریافتی از تلگرام (پیام، کلیک روی دکمهٔ شیشه‌ای، یا
inline query برای autofill)."""
import uuid

from . import config, db, format as fmt, keyboards as kb, membership
from . import telegram_api as tg


def get_welcome_text():
    return (
        "👋 به <b>ربات نرخ امروز چند؟</b> خوش آمدید!\n\n"
        "از منوی زیر یکی از دسته‌ها را انتخاب کنید، یا برای جستجوی سریع کافی‌ست "
        "بخشی از نام یک نماد (مثلا «دلار» یا «سکه») را همین‌جا تایپ کنید.\n\n"
        "💡 در هر چت دیگری هم می‌توانید با نوشتن "
        f"<code>@{config.BOT_USERNAME} نام نماد</code> به‌صورت آنی پیشنهاد بگیرید."
    )


def handle_update(update: dict):
    if "message" in update:
        _handle_message(update["message"])
    elif "callback_query" in update:
        _handle_callback(update["callback_query"])
    elif "inline_query" in update:
        _handle_inline_query(update["inline_query"])


# ---------------------------------------------------------------------------
# عضویت اجباری در کانال (join gate)
# ---------------------------------------------------------------------------

def _check_gate(user_id):
    """اگر کاربر عضو همهٔ کانال‌های اجباری بود None برمی‌گرداند (یعنی اجازه
    عبور دارد)، وگرنه لیست کانال‌های ناقص را برمی‌گرداند."""
    if not config.REQUIRED_CHANNELS:
        return None
    missing = membership.get_missing_channels(tg, config.REQUIRED_CHANNELS, user_id)
    return missing or None


def _send_gate_message(chat_id, missing_channels):
    tg.send_message(
        chat_id,
        membership.build_join_message(missing_channels),
        membership.build_join_keyboard(missing_channels),
    )


# ---------------------------------------------------------------------------
# پیام‌های معمولی (دستورها + جستجوی متنی)
# ---------------------------------------------------------------------------

def _handle_message(message: dict):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = (message.get("text") or "").strip()

    if text in ("/start", "/help"):
        tg.send_message(chat_id, get_welcome_text(), kb.main_menu())
        missing = _check_gate(user_id)
        if missing:
            _send_gate_message(chat_id, missing)
        return

    # از اینجا به بعد، برای هر دستور/پیام دیگر ابتدا عضویت را چک می‌کنیم
    missing = _check_gate(user_id)
    if missing:
        _send_gate_message(chat_id, missing)
        return

    if text == "/watchlist":
        _send_watchlist(chat_id, user_id)
        return

    if not text or text.startswith("/"):
        tg.send_message(chat_id, "دستور ناشناخته. برای شروع /start را بزنید.", kb.main_menu())
        return

    # هر متن آزاد دیگر = جستجوی سریع
    results = db.search_items(text, limit=10)
    if not results:
        tg.send_message(
            chat_id,
            f"🔍 برای «{text}» نتیجه‌ای پیدا نشد.\nاملای دیگری را امتحان کنید یا از منوی اصلی استفاده کنید.",
            kb.main_menu(),
        )
        return

    tg.send_message(
        chat_id,
        f"🔍 نتایج جستجو برای «{text}»:",
        kb.search_results_keyboard(results),
    )


def _send_watchlist(chat_id, user_id):
    keys = db.get_watchlist_keys(user_id)
    rows = db.get_items(keys)
    tg.send_message(chat_id, fmt.build_watchlist_message(rows), kb.watchlist_keyboard(rows))


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
        # دکمهٔ «✅ عضو شدم» همیشه قابل کلیک است (خودش عضویت را می‌سنجد)
        if data == "check_membership":
            missing = _check_gate(user_id)
            if missing:
                names = "، ".join(ch["title"] for ch in missing)
                tg.answer_callback_query(
                    cq_id,
                    f"هنوز عضو این کانال(ها) نشده‌اید: {names}",
                    show_alert=True,
                )
                return
            tg.answer_callback_query(cq_id, "🎉 عضویت شما تایید شد!")
            tg.edit_message_text(
                chat_id, message_id,
                "🎉 عضویت شما تایید شد! حالا می‌توانید از ربات استفاده کنید.\n\n" + get_welcome_text(),
                kb.main_menu(),
            )
            return

        # برای بقیهٔ دکمه‌ها، اول عضویت را چک می‌کنیم
        missing = _check_gate(user_id)
        if missing:
            tg.answer_callback_query(cq_id, "🔒 لطفاً ابتدا عضو کانال(های) لازم شوید.", show_alert=True)
            _send_gate_message(chat_id, missing)
            return

        if data == "home":
            tg.edit_message_text(chat_id, message_id, get_welcome_text(), kb.main_menu())

        elif data == "burmenu":
            tg.edit_message_text(chat_id, message_id, "📈 <b>شاخص‌های بورس و جهانی</b>\nیکی از زیردسته‌ها را انتخاب کنید:", kb.bourse_submenu())

        elif data == "watchlist":
            keys = db.get_watchlist_keys(user_id)
            rows = db.get_items(keys)
            tg.edit_message_text(chat_id, message_id, fmt.build_watchlist_message(rows), kb.watchlist_keyboard(rows))

        elif data == "search_prompt":
            tg.edit_message_text(
                chat_id, message_id,
                "🔍 <b>جستجوی پیشرفته</b>\n\nبخشی از نام نماد مورد نظر را تایپ و ارسال کنید "
                "(مثلا «یورو» یا «بیت‌کوین»)؛ ربات نزدیک‌ترین نتایج را نشان می‌دهد.\n\n"
                f"💡 در هر چت دیگری هم با <code>@{config.BOT_USERNAME} نام</code> autofill می‌گیرید.",
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
            tg.answer_callback_query(cq_id, "⭐ به دیده‌بان اضافه شد.")
            _show_item(chat_id, message_id, user_id, key, origin, int(page_s))
            return

        elif data.startswith("fav_del:"):
            _, key, origin, page_s = data.split(":")
            db.remove_from_watchlist(user_id, key)
            tg.answer_callback_query(cq_id, "🗑 از دیده‌بان حذف شد.")
            _show_item(chat_id, message_id, user_id, key, origin, int(page_s))
            return

        elif data == "noop_search":
            tg.answer_callback_query(cq_id, "برای جستجوی دوباره، عبارت جدید را تایپ کنید.")
            return

        tg.answer_callback_query(cq_id)
    except Exception as e:
        print(f"[handlers] callback error: {e}")
        tg.answer_callback_query(cq_id, "⚠️ خطایی رخ داد، دوباره تلاش کنید.")


def _show_list(chat_id, message_id, origin, page):
    keys = kb._resolve_keys(origin)
    if keys is None:
        tg.edit_message_text(chat_id, message_id, get_welcome_text(), kb.main_menu())
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
    tg.edit_message_text(chat_id, message_id, text, kb.list_keyboard(origin, page, rows, len(keys)))


def _show_item(chat_id, message_id, user_id, symbol_key, origin, page):
    row = db.get_item(symbol_key)
    if row is None:
        tg.edit_message_text(chat_id, message_id, "❌ این نماد پیدا نشد (ممکن است حذف شده باشد).", kb.main_menu())
        return
    is_fav = db.is_in_watchlist(user_id, symbol_key)
    text = fmt.build_item_message(row)
    tg.edit_message_text(chat_id, message_id, text, kb.item_detail_keyboard(symbol_key, origin, page, is_fav))


# ---------------------------------------------------------------------------
# Inline mode (autofill در هر چتی با @ عبارت)
# ---------------------------------------------------------------------------
# توجه: عمداً اینجا هیچ gate عضویتی اعمال نشده. تلگرام هیچ راهی برای
# نمایش پیام «باید عضو شوید» داخل نتایج inline در اختیار نمی‌گذارد، و اگر
# نتیجه‌ای برنگردانیم، کاربر فقط یک لیست خالی می‌بیند (گیج‌کننده). محدودیت
# واقعی همان جایی اعمال می‌شود که کاربر وارد چت خود ربات می‌شود.

def _handle_inline_query(iq: dict):
    query = (iq.get("query") or "").strip()
    iq_id = iq["id"]

    if not query:
        results = []
    else:
        rows = db.search_items(query, limit=20)
        results = []
        for row in rows:
            text = fmt.build_item_message(row)
            results.append({
                "type": "article",
                "id": str(uuid.uuid4()),
                "title": f"{row['title_fa']} — {row['price']}",
                "description": f"تغییر: {row['change_amount']} ({row['change_percent']})",
                "input_message_content": {
                    "message_text": text,
                    "parse_mode": "HTML",
                },
            })

    tg.answer_inline_query(iq_id, results)
