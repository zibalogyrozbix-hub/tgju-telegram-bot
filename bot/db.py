# -*- coding: utf-8 -*-
"""
لایهٔ دیتابیس. همان Turso که پروژهٔ اسکرِیپر «نرخ‌خروچند» با آن کار می‌کند؛
این ربات فقط از جدول market_prices می‌خواند (هیچ‌وقت آن را دستکاری نمی‌کند)
و یک جدول کوچک مستقل به اسم watchlist برای دیده‌بان شخصی هر کاربر اضافه
می‌کند.
"""
from datetime import datetime, timezone
import libsql_experimental as libsql

from . import config

_conn = None


def get_conn():
    """اتصال به Turso را یک‌بار می‌سازد و در فراخوانی‌های بعدی (در همان
    اجرای serverless function) دوباره استفاده می‌کند."""
    global _conn
    if _conn is not None:
        return _conn

    url = config.TURSO_DATABASE_URL
    if url.startswith("libsql://"):
        url = url.replace("libsql://", "https://")
    elif not url.startswith("https://"):
        url = f"https://{url}"

    _conn = libsql.connect(database=url, auth_token=config.TURSO_AUTH_TOKEN)
    _ensure_watchlist_table(_conn)
    return _conn


def _ensure_watchlist_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            user_id     INTEGER NOT NULL,
            symbol_key  TEXT NOT NULL,
            added_at    TEXT,
            PRIMARY KEY (user_id, symbol_key)
        )
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# خواندن از market_prices
# ---------------------------------------------------------------------------

_COLUMNS = ["symbol_key", "title_fa", "price", "change_amount", "change_percent", "updated_at"]


def _row_to_dict(row):
    return dict(zip(_COLUMNS, row))


def get_item(symbol_key: str):
    conn = get_conn()
    cur = conn.execute(
        "SELECT symbol_key, title_fa, price, change_amount, change_percent, updated_at "
        "FROM market_prices WHERE symbol_key = ?",
        (symbol_key,),
    )
    row = cur.fetchone()
    return _row_to_dict(row) if row else None


def get_items(symbol_keys):
    """چند نماد را می‌خواند و دقیقا به همان ترتیب symbol_keys برمی‌گرداند
    (SQL با IN ترتیب را حفظ نمی‌کند، پس این‌جا دوباره مرتب می‌شود)."""
    if not symbol_keys:
        return []
    conn = get_conn()
    placeholders = ",".join("?" for _ in symbol_keys)
    cur = conn.execute(
        f"SELECT symbol_key, title_fa, price, change_amount, change_percent, updated_at "
        f"FROM market_prices WHERE symbol_key IN ({placeholders})",
        tuple(symbol_keys),
    )
    rows = {r[0]: _row_to_dict(r) for r in cur.fetchall()}
    return [rows[k] for k in symbol_keys if k in rows]


def search_items(query: str, limit: int = 15):
    conn = get_conn()
    like = f"%{query.strip()}%"
    cur = conn.execute(
        "SELECT symbol_key, title_fa, price, change_amount, change_percent, updated_at "
        "FROM market_prices WHERE title_fa LIKE ? ORDER BY title_fa LIMIT ?",
        (like, limit),
    )
    return [_row_to_dict(r) for r in cur.fetchall()]


# ---------------------------------------------------------------------------
# دیده‌بان شخصی (watchlist)
# ---------------------------------------------------------------------------

def add_to_watchlist(user_id: int, symbol_key: str):
    conn = get_conn()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO watchlist (user_id, symbol_key, added_at) VALUES (?, ?, ?) "
        "ON CONFLICT(user_id, symbol_key) DO NOTHING",
        (user_id, symbol_key, now),
    )
    conn.commit()


def remove_from_watchlist(user_id: int, symbol_key: str):
    conn = get_conn()
    conn.execute(
        "DELETE FROM watchlist WHERE user_id = ? AND symbol_key = ?",
        (user_id, symbol_key),
    )
    conn.commit()


def is_in_watchlist(user_id: int, symbol_key: str) -> bool:
    conn = get_conn()
    cur = conn.execute(
        "SELECT 1 FROM watchlist WHERE user_id = ? AND symbol_key = ?",
        (user_id, symbol_key),
    )
    return cur.fetchone() is not None


def get_watchlist_keys(user_id: int):
    conn = get_conn()
    cur = conn.execute(
        "SELECT symbol_key FROM watchlist WHERE user_id = ? ORDER BY added_at",
        (user_id,),
    )
    return [r[0] for r in cur.fetchall()]
