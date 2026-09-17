# -*- coding: utf-8 -*-
"""
داده‌های نرخ (get_item/get_items/search_items) کاملاً مستقل از پیام‌رسان
است، پس همان توابع bot/db.py مستقیم استفاده می‌شوند (فقط خواندن، هیچ خطری
برای ربات تلگرام ندارد).

اما دیده‌بان (watchlist) را در یک جدول جداگانه به اسم watchlist_bale
نگه می‌داریم، چون شناسهٔ کاربر (user_id) در بله فضای عددی کاملاً متفاوتی از
تلگرام دارد؛ اگر از همان جدول watchlist تلگرام استفاده می‌کردیم، ممکن بود
یک عدد به‌طور اتفاقی هم در تلگرام و هم در بله وجود داشته باشد و دیده‌بان دو
کاربر متفاوت با هم قاطی شود.
"""
from datetime import datetime, timezone
from bot import db as shared_db

# خواندن نرخ‌ها: مستقیم از پیاده‌سازی مشترک
get_item = shared_db.get_item
get_items = shared_db.get_items
search_items = shared_db.search_items

_table_ready = False


def _ensure_table():
    global _table_ready
    if _table_ready:
        return
    conn = shared_db.get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS watchlist_bale (
            user_id     INTEGER NOT NULL,
            symbol_key  TEXT NOT NULL,
            added_at    TEXT,
            PRIMARY KEY (user_id, symbol_key)
        )
    """)
    conn.commit()
    _table_ready = True


def add_to_watchlist(user_id: int, symbol_key: str):
    _ensure_table()
    conn = shared_db.get_conn()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO watchlist_bale (user_id, symbol_key, added_at) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, symbol_key) DO NOTHING",
        (user_id, symbol_key, now),
    )
    conn.commit()


def remove_from_watchlist(user_id: int, symbol_key: str):
    _ensure_table()
    conn = shared_db.get_conn()
    conn.execute(
        "DELETE FROM watchlist_bale WHERE user_id = ? AND symbol_key = ?",
        (user_id, symbol_key),
    )
    conn.commit()


def is_in_watchlist(user_id: int, symbol_key: str) -> bool:
    _ensure_table()
    conn = shared_db.get_conn()
    cur = conn.execute(
        "SELECT 1 FROM watchlist_bale WHERE user_id = ? AND symbol_key = ?",
        (user_id, symbol_key),
    )
    return cur.fetchone() is not None


def get_watchlist_keys(user_id: int):
    _ensure_table()
    conn = shared_db.get_conn()
    cur = conn.execute(
        "SELECT symbol_key FROM watchlist_bale WHERE user_id = ? ORDER BY added_at",
        (user_id,),
    )
    return [r[0] for r in cur.fetchall()]
