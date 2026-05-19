"""
==============================================
  HISOBLAGICH TELEGRAM BOT — bot.py
==============================================
  Ishlatish:
  1. pip install -r requirements.txt
  2. BOT_TOKEN va WEB_APP_URL ni o'zgartiring
  3. python bot.py
==============================================
"""

import logging
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ─────────────────────────────────────────
#  SOZLAMALAR — bularni o'zgartiring!
# ─────────────────────────────────────────

BOT_TOKEN   = "8516628447:AAFKh4VCAa9fuIGU81DVp19Brg4rc58z7lg"      # @BotFather dan olingan token
WEB_APP_URL = "https://shoxjoxonatayev-droid.github.io/hisoblash_bot"  # GitHub Pages havolasi

# ─────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────
#  /start KOMANDASI
# ─────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchi /start yuborganda ishlaydi."""

    user = update.effective_user
    first_name = user.first_name if user.first_name else "Do'stim"

    # Ilovani ochish tugmasi (Web App)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="💰 Ilovani ochish",
                web_app=WebAppInfo(url=WEB_APP_URL),
            )
        ]
    ])

    welcome_text = (
        f"👋 Salom, <b>{first_name}</b>!\n\n"
        f"Men — <b>Hisoblagich</b> botiman 🧮\n\n"
        f"📌 Ushbu ilova orqali quyidagilarni kuzatib borasiz:\n"
        f"  🍽️ <b>Restoran</b> — kirim va chiqimlar\n"
        f"  🏨 <b>Mehmonxona</b> — kirim va chiqimlar\n"
        f"  👤 <b>Shaxsiy</b> — kirim va chiqimlar\n\n"
        f"Boshlash uchun pastdagi tugmani bosing 👇"
    )

    await update.message.reply_html(
        text=welcome_text,
        reply_markup=keyboard,
    )
    logger.info(f"Start: {user.id} — @{user.username}")


# ─────────────────────────────────────────
#  /help KOMANDASI
# ─────────────────────────────────────────
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="💰 Ilovani ochish",
                web_app=WebAppInfo(url=WEB_APP_URL),
            )
        ]
    ])

    await update.message.reply_html(
        "ℹ️ <b>Yordam</b>\n\n"
        "Bu bot sizga kirim-chiqimlaringizni 3 ta bo'lim bo'yicha kuzatib borishga yordam beradi.\n\n"
        "<b>Komandalar:</b>\n"
        "/start — Botni boshlash\n"
        "/help  — Yordam\n"
        "/ochish — Ilovani ochish\n\n"
        "👇 Yoki quyidagi tugmani bosing:",
        reply_markup=keyboard,
    )


# ─────────────────────────────────────────
#  /ochish KOMANDASI (qisqa yo'l)
# ─────────────────────────────────────────
async def ochish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="💰 Ilovani ochish",
                web_app=WebAppInfo(url=WEB_APP_URL),
            )
        ]
    ])
    await update.message.reply_text(
        "👇 Ilovani ochish uchun bosing:",
        reply_markup=keyboard,
    )


# ─────────────────────────────────────────
#  NOTO'G'RI XABAR — ixtiyoriy
# ─────────────────────────────────────────
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="💰 Ilovani ochish",
                web_app=WebAppInfo(url=WEB_APP_URL),
            )
        ]
    ])
    await update.message.reply_text(
        "❓ Tushunmadim. /start yoki /ochish buyrug'ini yuboring.",
        reply_markup=keyboard,
    )


# ─────────────────────────────────────────
#  BOTNI ISHGA TUSHIRISH
# ─────────────────────────────────────────
def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # Komandalar
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_command))
    app.add_handler(CommandHandler("ochish", ochish))

    # Noto'g'ri xabarlar
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    logger.info("✅ Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
