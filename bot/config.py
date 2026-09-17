# -*- coding: utf-8 -*-
"""
تنظیمات ربات: متغیرهای محیطی و ساختار دسته‌بندی‌ها.

نکته مهم: این فایل فقط می‌گوید هر دسته شامل چه symbol_key هایی است. عنوان
فارسی، قیمت، تغییرات و زمان بروزرسانی هر کدام همیشه مستقیم از جدول
market_prices در Turso خوانده می‌شود؛ یعنی هر وقت پروژه اسکرِیپر (نرخ‌خروچند)
یک ستون/شاخص جدید اضافه کرد، کافی‌ست کلیدش را به یکی از لیست‌های زیر اضافه
کنید تا در ربات هم ظاهر شود.
"""
import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL", "").strip()
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "").strip()
# یک رشتهٔ دلخواه و مخفی که در URL وبهوک استفاده می‌شود تا کسی جز تلگرام
# نتواند به آدرس وبهوک درخواست جعلی بزند.
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "changeme").strip()

# اضافه کردن یوزرنیم ربات (می‌توانید از متغیر محیطی بخوانید یا مستقیماً یوزرنیم خود را قرار دهید)
BOT_USERNAME = os.environ.get("BOT_USERNAME", "nerkhemrooz_bot").strip()

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ---------------------------------------------------------------------------
# عضویت اجباری در کانال (join gate)
# ---------------------------------------------------------------------------
# هر ورودی یک کانال است که کاربر باید قبل از استفاده از ربات عضوش باشد.
#   id  : همان‌طور که در فراخوانی getChatMember به تلگرام داده می‌شود
#         (یوزرنیم با @ یا chat_id عددی کانال‌های خصوصی)
#   title: نام نمایشی در پیام و روی دکمه
#   url  : لینکی که با کلیک روی دکمه باز می‌شود
#
# برای افزودن کانال دوم/سوم بعداً، کافی‌ست یک دیکشنری دیگر به همین لیست
# اضافه کنید؛ بقیه کد (پیام، دکمه‌ها، بررسی عضویت) خودکار همه را پوشش می‌دهد.
#
# ⚠️ نکتهٔ فنی مهم: تلگرام فقط زمانی به ربات اجازهٔ getChatMember می‌دهد که
# خود ربات عضو (ترجیحاً ادمین) همان کانال باشد. حتماً ربات را در کانال زیر
# ادمین کنید.
REQUIRED_CHANNELS = [
    {
        "id": "@nerkhemroozchand",
        "title": "کانال نرخ امروز چند؟",
        "url": "https://t.me/nerkhemroozchand",
    },
]

# ---------------------------------------------------------------------------
# دسته‌بندی‌های سطح اول منوی شیشه‌ای
# ---------------------------------------------------------------------------

CURRENCY_KEYS = [
    "usd", "eur", "gbp", "aed", "try", "chf", "cny", "jpy", "krw", "cad",
    "aud", "nzd", "sgd", "hkd", "thb", "inr", "pkr", "afn", "iqd", "syp",
    "amd", "azn", "bhd", "dkk", "gel", "kgs", "kwd", "myr", "nok", "omr",
    "qar", "rub", "sar", "sek", "tjs", "tmt",
]

GOLD_COIN_KEYS = [
    "coin_emami", "coin_azadi", "coin_half", "coin_quarter", "coin_gram",
    "gold_18k", "gold_24k", "gold_used", "gold_mesghal", "gold_ounce",
    "silver_gram", "silver_ounce", "platinum_ounce", "palladium_ounce",
    "abshedeh_cash", "abshedeh_trade", "mesghal_no_bubble",
    "bubble_emami", "bubble_azadi", "bubble_half", "bubble_quarter", "bubble_gram",
    "fund_ayar", "fund_lotus", "fund_gohar", "fund_mesghal", "fund_kahreba",
    "fund_nab", "fund_riton", "fund_tabesh", "fund_zarvan",
]

CRYPTO_KEYS = [
    "btc", "eth", "usdt", "xrp", "bnb", "sol", "doge", "trx", "ada",
    "ton", "avax", "shib", "dot", "ltc", "bch", "xlm", "dash",
]

BOURSE_IR_KEYS = [
    "bourse_total", "bourse_market1", "bourse_market2",
    "bourse_pequal", "bourse_pweighted", "ifb_market1", "ifb_market2",
]

BOURSE_WORLD_KEYS = [
    "dow_jones", "nasdaq", "smi_swiss", "nifty_50", "ftse_100",
    "dax", "cac_40", "nikkei_225", "shanghai_composite", "ibex_35",
]

COMMODITY_KEYS = [
    "oil_crude", "oil_brent", "oil_opec", "gasoline", "natural_gas", "coal",
    "aluminum", "nickel", "lead", "zinc", "copper", "tin",
    "cotton", "sugar", "soybeans", "wheat", "corn", "rice",
]

# دسته سطح اول: کد کوتاه -> عنوان/ایموجی/کلیدها (یا زیردسته)
CATEGORIES = {
    "cur": {"emoji": "💵", "title": "ارزهای اصلی و سنتی", "keys": CURRENCY_KEYS},
    "gld": {"emoji": "🪙", "title": "طلا، سکه و حباب‌ها", "keys": GOLD_COIN_KEYS},
    "bur": {"emoji": "📈", "title": "شاخص‌های بورس و جهانی", "keys": None},  # زیرمنو دارد
    "cry": {"emoji": "💎", "title": "ارزهای دیجیتال", "keys": CRYPTO_KEYS},
}

# زیردسته‌های «شاخص‌های بورس و جهانی»
BOURSE_SUBCATEGORIES = {
    "bir": {"emoji": "🏛", "title": "بورس و فرابورس ایران", "keys": BOURSE_IR_KEYS},
    "bwd": {"emoji": "🌍", "title": "شاخص‌های جهانی", "keys": BOURSE_WORLD_KEYS},
    "cmd": {"emoji": "🛢", "title": "کالا، نفت و فلزات", "keys": COMMODITY_KEYS},
}

PAGE_SIZE = 8  # تعداد آیتم در هر صفحه از لیست‌ها

# برای انتخاب ایموجی مناسب سر پیام جزئیات یک نماد
def category_emoji_for_key(symbol_key: str) -> str:
    if symbol_key in CURRENCY_KEYS:
        return "💵"
    if symbol_key in GOLD_COIN_KEYS:
        return "🪙"
    if symbol_key in CRYPTO_KEYS:
        return "💎"
    if symbol_key in BOURSE_IR_KEYS or symbol_key in BOURSE_WORLD_KEYS:
        return "📈"
    if symbol_key in COMMODITY_KEYS:
        return "🛢"
    return "🔹"
