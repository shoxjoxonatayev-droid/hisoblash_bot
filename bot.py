import logging
import threading
import os
import sys
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ─── Environment Variables dan olish ───
BOT_TOKEN   = os.environ.get("BOT_TOKEN", "8516628447:AAFKh4VCAa9fuIGU81DVp19Brg4rc58z7lg")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://shoxjoxonatayev-droid.github.io/hisoblash_bot")

if not BOT_TOKEN:
    print("XATO: BOT_TOKEN environment variable o'rnatilmagan!", flush=True)
    sys.exit(1)

# ─── Flask (UptimeRobot uchun) ───
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot ishlayapti!", 200

@flask_app.route("/health")
def health():
    return "OK", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ─── Logging ───
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Handlerlar ───
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name or "Do'stim"
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(text="💰 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    await update.message.reply_html(
        f"👋 Salom, <b>{first_name}</b>!\n\n"
        f"Men — <b>Hisoblagich</b> botiman 🧮\n\n"
        f"📌 Kuzatib borasiz:\n"
        f"  🍽️ <b>Restoran</b> — kirim va chiqimlar\n"
        f"  🏨 <b>Mehmonxona</b> — kirim va chiqimlar\n"
        f"  👤 <b>Shaxsiy</b> — kirim va chiqimlar\n\n"
        f"Boshlash uchun pastdagi tugmani bosing 👇",
        reply_markup=keyboard,
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(text="💰 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    await update.message.reply_html(
        "ℹ️ <b>Yordam</b>\n\n/start — Botni boshlash\n/help — Yordam\n/ochish — Ilovani ochish",
        reply_markup=keyboard,
    )

async def ochish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(text="💰 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    await update.message.reply_text("👇 Ilovani ochish uchun bosing:", reply_markup=keyboard)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(text="💰 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    await update.message.reply_text("❓ /start yoki /ochish buyrug'ini yuboring.", reply_markup=keyboard)

# ─── Main ───
def main():
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    logger.info("Flask server ishga tushdi")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ochish", ochish))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    logger.info("Bot ishga tushdi")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()