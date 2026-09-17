# -*- coding: utf-8 -*-
"""
منطق «عضویت اجباری در کانال». طوری نوشته شده که هم برای تلگرام و هم برای
بله (که همان ساختار getChatMember را دارد) قابل استفاده مجدد است: کافی‌ست
ماژول api متناظر (که تابع get_chat_member_status(chat_id, user_id) را
دارد) و لیست کانال‌ها را بدهید.
"""

MEMBER_STATUSES = ("member", "administrator", "creator")


def get_missing_channels(api_module, channels: list, user_id) -> list:
    """برای هر کانال در channels، عضویت user_id را چک می‌کند و لیست
    کانال‌هایی که کاربر هنوز عضو نیست را برمی‌گرداند. اگر status قابل
    تشخیص نبود (مثلا ربات ادمین کانال نیست)، برای احتیاط همان کانال را هم
    «عضو نشده» در نظر می‌گیریم تا کاربر واقعاً از دسترسی محروم نشود در
    حالتی که مطمئن نیستیم.
    """
    missing = []
    for ch in channels:
        status = api_module.get_chat_member_status(ch["id"], user_id)
        if status not in MEMBER_STATUSES:
            missing.append(ch)
    return missing


def build_join_message(missing_channels: list) -> str:
    lines = [
        "🔒 <b>عضویت در کانال الزامی است</b>",
        "",
        "برای استفاده از این ربات، ابتدا باید عضو کانال(های) زیر شوید:",
        "",
    ]
    for ch in missing_channels:
        lines.append(f"📢 {ch['title']} — @{ch['id'].lstrip('@')}")
    lines.append("")
    lines.append("بعد از عضویت، روی دکمهٔ «✅ عضو شدم» بزنید.")
    return "\n".join(lines)


def build_join_keyboard(missing_channels: list) -> dict:
    kb = []
    for ch in missing_channels:
        kb.append([{"text": f"📢 عضویت در {ch['title']}", "url": ch["url"]}])
    kb.append([{"text": "✅ عضو شدم", "callback_data": "check_membership"}])
    return {"inline_keyboard": kb}
