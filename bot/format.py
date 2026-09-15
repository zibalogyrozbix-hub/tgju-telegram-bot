# -*- coding: utf-8 -*-
"""ابزارهای فرمت‌بندی اعداد و ساخت متن پیام‌ها."""
import re
from . import config


def parse_number(s):
    """رشتهٔ فرمت‌شده مثل '2,313,000' یا '-27,000' یا '-0.18%' را به float
    تبدیل می‌کند. اگر عدد معتبری پیدا نشود None برمی‌گرداند."""
    if s is None:
        return None
    s = str(s).strip()
    if s in ("", "-", "None"):
        return None
    s = s.replace(",", "").replace("%", "").strip()
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    return float(m.group(0))


def format_number(n):
    if n is None:
        return "-"
    if float(n).is_integer():
        return f"{int(n):,}"
    return f"{n:,.4f}".rstrip("0").rstrip(".")


def change_emoji(change_amount_str):
    val = parse_number(change_amount_str)
    if val is None or val == 0:
        return "➖"
    return "🔺" if val > 0 else "🔻"


def yesterday_price(price_str, change_amount_str):
    """نرخ دیروز = نرخ امروز - میزان تغییر."""
    price_val = parse_number(price_str)
    change_val = parse_number(change_amount_str)
    if price_val is None or change_val is None:
        return None
    return price_val - change_val


def build_item_message(row: dict) -> str:
    """پیام کامل جزئیات یک نماد (برای نمایش در چت)."""
    emoji = config.category_emoji_for_key(row["symbol_key"])
    title = row["title_fa"]
    price = row["price"]
    change_amount = row["change_amount"]
    change_percent = row["change_percent"]
    updated_at = row["updated_at"]

    arrow = change_emoji(change_amount)
    y_price = yesterday_price(price, change_amount)
    y_price_text = format_number(y_price) if y_price is not None else "-"

    change_amt_val = parse_number(change_amount)
    change_amt_text = "-"
    if change_amt_val is not None:
        sign = "+" if change_amt_val > 0 else ""
        change_amt_text = f"{sign}{format_number(change_amt_val)}"

    pct_text = change_percent if change_percent not in (None, "", "-") else "0%"

    lines = [
        f"{emoji} <b>{title}</b>",
        "",
        f"💰 نرخ فعلی: <b>{price}</b>",
        f"📅 نرخ دیروز: {y_price_text}",
        f"{arrow} تغییر: {change_amt_text} ({pct_text})",
        "",
        f"🕒 آخرین بروزرسانی: {updated_at}",
    ]
    return "\n".join(lines)


def build_list_button_label(row: dict) -> str:
    """متن کوتاه روی دکمهٔ هر آیتم داخل لیست یک دسته."""
    arrow = change_emoji(row["change_amount"])
    title = row["title_fa"]
    price = row["price"]
    return f"{arrow} {title} — {price}"


def build_watchlist_message(rows: list) -> str:
    if not rows:
        return "⭐ <b>دیده‌بان من</b>\n\nفهرست علاقه‌مندی‌های شما خالی است.\nبرای افزودن، وارد هر نماد شوید و روی «⭐ افزودن به علاقه‌مندی‌ها» بزنید."

    lines = ["⭐ <b>دیده‌بان من</b>", ""]
    for row in rows:
        emoji = config.category_emoji_for_key(row["symbol_key"])
        arrow = change_emoji(row["change_amount"])
        pct = row["change_percent"] if row["change_percent"] not in (None, "", "-") else "0%"
        lines.append(f"{emoji} <b>{row['title_fa']}</b>: {row['price']} {arrow} ({pct})")
    lines.append("")
    lines.append("🕒 برای دیدن جزئیات کامل هر مورد، روی دکمهٔ آن در پایین بزنید.")
    return "\n".join(lines)
