# -*- coding: utf-8 -*-
"""
محتوای این فایل را (با جایگزین کردن مسیر واقعی خودتان) کامل کپی کنید داخل
فایل WSGI که PythonAnywhere در تب Web می‌سازد
(معمولا مسیرش چیزی شبیه این است:
/var/www/<یوزرنیم>_pythonanywhere_com_wsgi.py)

فقط دو خط زیر لازم است؛ هر چیز دیگری که PythonAnywhere از قبل در آن فایل
نوشته را پاک کنید.
"""
import sys

# ⚠️ این مسیر را با مسیر واقعی پوشه‌ای که ریپازیتوری را در آن clone کردید
# جایگزین کنید (یوزرنیم پای‌تون‌anywhere‌تان را هم جایگزین کنید):
path = "/home/YOUR_PYTHONANYWHERE_USERNAME/tgju-telegram-bot"
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
