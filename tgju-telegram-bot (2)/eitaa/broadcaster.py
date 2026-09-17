# -*- coding: utf-8 -*-
"""
چون ایتا امکان تعامل دو طرفه ندارد، به‌جای منوی شیشه‌ای، این ماژول یک
«گزارش نرخ» متنی برای یک دسته را می‌سازد و به کانال ایتای شما پست می‌کند.
می‌توانید این را دستی اجرا کنید یا (مثل پروژهٔ اسکرِیپر) با یک کرون
(GitHub Actions یا Railway Cron) هر چند ساعت یک‌بار زمان‌بندی کنید.
"""
from bot import db, format as fmt, config as shared_config
from . import api, config


def build_digest_text(title: str, emoji: str, symbol_keys: list) -> str:
    rows = db.get_items(symbol_keys)
    lines = [f"{emoji} <b>{title}</b>", ""]
    if not rows:
        lines.append("داده‌ای برای نمایش پیدا نشد.")
    for row in rows:
        arrow = fmt.change_emoji(row["change_amount"])
        pct = row["change_percent"] if row["change_percent"] not in (None, "", "-") else "0%"
        lines.append(f"{arrow} {row['title_fa']}: <b>{row['price']}</b> ({pct})")
    if rows:
        lines.append("")
        lines.append(f"🕒 بروزرسانی: {rows[0]['updated_at']}")
    lines.append("")
    lines.append("📊 نرخ‌های بیشتر: ربات تلگرام @" + shared_config.BOT_USERNAME)
    return "\n".join(lines)


def send_category_digest(category_code: str, chat_id: str = None):
    """category_code یکی از کلیدهای bot.config.CATEGORIES (مثلا 'cur')
    یا bot.config.BOURSE_SUBCATEGORIES (مثلا 'bir') است."""
    chat_id = chat_id or config.EITAA_CHAT_ID
    cat = shared_config.CATEGORIES.get(category_code) or shared_config.BOURSE_SUBCATEGORIES.get(category_code)
    if not cat or cat.get("keys") is None:
        print(f"[eitaa_broadcaster] دستهٔ نامعتبر یا بدون کلید: {category_code}")
        return None
    text = build_digest_text(cat["title"], cat["emoji"], cat["keys"])
    return api.send_message(chat_id, text)


if __name__ == "__main__":
    # اجرای دستی نمونه: گزارش ارزهای اصلی را به کانال پیش‌فرض بفرست
    # (chat_id از EITAA_CHAT_ID در .env خوانده می‌شود)
    import sys
    category = sys.argv[1] if len(sys.argv) > 1 else "cur"
    result = send_category_digest(category)
    print(result)
