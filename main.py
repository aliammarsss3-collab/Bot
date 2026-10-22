import os
import random
import re
import logging
from urllib.parse import quote
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

LETTERS = "qwertyuiopasdfghjklzxcvbnm"
DIGITS = "0123456789"
MIXED = LETTERS + DIGITS

def make_usernames(count=10):
    found = set()
    while len(found) < count:
        a = random.choice(LETTERS)
        b = random.choice(DIGITS)
        c = random.choice(LETTERS.upper())
        d = random.choice(MIXED)
        e = random.choice(MIXED)
        options = [
            a + b + c + d + e,
            b + "_" + d + "_" + a,
            a + "." + b + "." + e,
            a + b + "." + c + d + e,
            a + b + "_" + c + d + e,
            a + c + b + e + "_",
            a + c + b + e + "." + a,
            a + a + "_" + d + b,
            a + a + "." + d + b,
        ]
        user = random.choice(options).lower()
        if 1 <= len(user) <= 30 and re.fullmatch(r"[a-z0-9._]+", user):
            found.add(user)
    return list(found)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎲 توليد يوزرات", callback_data="generate")]]
    await update.message.reply_text(
        "هلا بيك ببوت تخمين اليوزرات 🎲\n\n"
        "أكدر أولّد اقتراحات وأرسل روابط فحصها يدوياً على إنستغرام.\n"
        "ما أسوي طلبات آلية إلى واجهة إنشاء الحسابات، وما أگدر أضمن توفر أي يوزر.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = make_usernames(10)
    lines = ["🎲 اقتراحات اليوزرات:\n"]
    for i, user in enumerate(users, 1):
        lines.append(f"{i}. @{user} — https://www.instagram.com/{quote(user)}/")
    lines.append("\nملاحظة: الرابط يفتح صفحة الحساب؛ عدم ظهور الحساب مو دليل أكيد أن اليوزر متاح.")
    keyboard = [[InlineKeyboardButton("🔄 توليد غيرها", callback_data="generate")]]
    message = update.effective_message
    await message.reply_text("\n".join(lines), disable_web_page_preview=True,
                             reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "generate":
        users = make_usernames(10)
        lines = ["🎲 اقتراحات اليوزرات:\n"]
        for i, user in enumerate(users, 1):
            lines.append(f"{i}. @{user} — https://www.instagram.com/{quote(user)}/")
        lines.append("\nملاحظة: التوفر غير مضمون ويحتاج تحقق يدوي.")
        keyboard = [[InlineKeyboardButton("🔄 توليد غيرها", callback_data="generate")]]
        await query.message.reply_text("\n".join(lines), disable_web_page_preview=True,
                                       reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    if not TOKEN:
        raise RuntimeError("Set BOT_TOKEN as an environment variable in your hosting dashboard.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
