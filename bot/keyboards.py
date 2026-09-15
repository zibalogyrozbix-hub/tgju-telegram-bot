# -*- coding: utf-8 -*-
"""ساخت ساختار inline_keyboard برای پیام‌های تلگرام.

قرارداد callback_data (حداکثر ۶۴ بایت طبق محدودیت تلگرام، همهٔ موارد زیر
خیلی کوتاه‌تر از این حد هستند):

    home                                 -> بازگشت به منوی اصلی
    burmenu                              -> نمایش زیردسته‌های بورس/جهانی
    cat:<code>:<page>                    -> لیست یک دستهٔ سطح اول
    sub:<code>:<page>                    -> لیست یک زیردستهٔ بورس
    item:<key>:<origin>:<page>           -> نمایش جزئیات یک نماد
    fav_add:<key>:<origin>:<page>        -> افزودن به دیده‌بان
    fav_del:<key>:<origin>:<page>        -> حذف از دیده‌بان
    refresh_item:<key>:<origin>:<page>   -> بروزرسانی صفحهٔ جزئیات
    refresh_list:<origin>:<page>         -> بروزرسانی لیست
    watchlist                            -> نمایش دیده‌بان من
    search_prompt                        -> راهنمای جستجو

<origin> یکی از کدهای دسته (cur/gld/cry/bir/bwd/cmd) یا 'srch' (نتیجهٔ
جستجو) یا 'wl' (دیده‌بان) است تا دکمهٔ «بازگشت» بداند کاربر از کجا آمده.
"""
from . import config, format as fmt


def main_menu():
    rows = [
        [{"text": "💵 ارزهای اصلی و سنتی", "callback_data": "cat:cur:0"}],
        [{"text": "🪙 طلا، سکه و حباب‌ها", "callback_data": "cat:gld:0"}],
        [{"text": "📈 شاخص‌های بورس و جهانی", "callback_data": "burmenu"}],
        [{"text": "💎 ارزهای دیجیتال", "callback_data": "cat:cry:0"}],
        [{"text": "🔍 جستجوی پیشرفته / استعلام سریع", "callback_data": "search_prompt"}],
        [{"text": "⭐ دیده‌بان من", "callback_data": "watchlist"}],
    ]
    return {"inline_keyboard": rows}


def bourse_submenu():
    rows = []
    for code, cat in config.BOURSE_SUBCATEGORIES.items():
        rows.append([{"text": f"{cat['emoji']} {cat['title']}", "callback_data": f"sub:{code}:0"}])
    rows.append([{"text": "🔙 بازگشت به منوی اصلی", "callback_data": "home"}])
    return {"inline_keyboard": rows}


def _resolve_keys(origin: str):
    if origin in config.CATEGORIES and config.CATEGORIES[origin]["keys"] is not None:
        return config.CATEGORIES[origin]["keys"]
    if origin in config.BOURSE_SUBCATEGORIES:
        return config.BOURSE_SUBCATEGORIES[origin]["keys"]
    return None


def list_keyboard(origin: str, page: int, rows_data: list, total_items: int):
    """کیبورد لیست یک دسته/زیردسته/جستجو/دیده‌بان با صفحه‌بندی.
    rows_data: خروجی db.get_items(...) برای همان صفحه (حداکثر PAGE_SIZE تا).
    """
    kb = []
    for item in rows_data:
        label = fmt.build_list_button_label(item)
        kb.append([{
            "text": label,
            "callback_data": f"item:{item['symbol_key']}:{origin}:{page}",
        }])

    nav_row = []
    if page > 0:
        nav_row.append({"text": "◀️ قبلی", "callback_data": f"{_list_prefix(origin)}:{origin}:{page-1}"})
    if (page + 1) * config.PAGE_SIZE < total_items:
        nav_row.append({"text": "بعدی ▶️", "callback_data": f"{_list_prefix(origin)}:{origin}:{page+1}"})
    if nav_row:
        kb.append(nav_row)

    action_row = [{"text": "🔄 بروزرسانی", "callback_data": f"refresh_list:{origin}:{page}"}]
    kb.append(action_row)

    back_row = []
    if origin in config.BOURSE_SUBCATEGORIES:
        back_row.append({"text": "🔙 بازگشت به شاخص‌ها", "callback_data": "burmenu"})
    back_row.append({"text": "🏠 منوی اصلی", "callback_data": "home"})
    kb.append(back_row)

    return {"inline_keyboard": kb}


def _list_prefix(origin: str) -> str:
    return "sub" if origin in config.BOURSE_SUBCATEGORIES else "cat"


def item_detail_keyboard(symbol_key: str, origin: str, page: int, is_favorite: bool):
    fav_btn = (
        {"text": "💔 حذف از علاقه‌مندی‌ها", "callback_data": f"fav_del:{symbol_key}:{origin}:{page}"}
        if is_favorite else
        {"text": "⭐ افزودن به علاقه‌مندی‌ها", "callback_data": f"fav_add:{symbol_key}:{origin}:{page}"}
    )
    kb = [
        [fav_btn],
        [{"text": "🔄 بروزرسانی لحظه‌ای", "callback_data": f"refresh_item:{symbol_key}:{origin}:{page}"}],
    ]
    back_row = []
    if origin in config.CATEGORIES or origin in config.BOURSE_SUBCATEGORIES:
        back_row.append({"text": "🔙 بازگشت به لیست", "callback_data": f"{_list_prefix(origin)}:{origin}:{page}"})
    elif origin == "wl":
        back_row.append({"text": "🔙 بازگشت به دیده‌بان", "callback_data": "watchlist"})
    elif origin == "srch":
        back_row.append({"text": "🔙 بازگشت به نتایج جستجو", "callback_data": "noop_search"})
    back_row.append({"text": "🏠 منوی اصلی", "callback_data": "home"})
    kb.append(back_row)
    return {"inline_keyboard": kb}


def search_results_keyboard(rows_data: list):
    kb = []
    for item in rows_data:
        label = fmt.build_list_button_label(item)
        kb.append([{"text": label, "callback_data": f"item:{item['symbol_key']}:srch:0"}])
    kb.append([{"text": "🏠 منوی اصلی", "callback_data": "home"}])
    return {"inline_keyboard": kb}


def watchlist_keyboard(rows_data: list):
    kb = []
    for item in rows_data:
        label = fmt.build_list_button_label(item)
        kb.append([{"text": label, "callback_data": f"item:{item['symbol_key']}:wl:0"}])
    kb.append([{"text": "🔄 بروزرسانی", "callback_data": "watchlist"}])
    kb.append([{"text": "🏠 منوی اصلی", "callback_data": "home"}])
    return {"inline_keyboard": kb}
