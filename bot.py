import logging
import threading
import os
import sys
import json
import sqlite3
from datetime import datetime, date, timedelta
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    MessageHandler, filters, CallbackQueryHandler
)

# ═══════════════════════════════════════════
#  SOZLAMALAR
# ═══════════════════════════════════════════
BOT_TOKEN   = os.environ.get("BOT_TOKEN", "")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://example.com")
ADMIN_ID    = int(os.environ.get("ADMIN_ID", "0"))  # Sizning Telegram ID ingiz

if not BOT_TOKEN:
    print("❌ XATO: BOT_TOKEN environment variable o'rnatilmagan!", flush=True)
    sys.exit(1)

if ADMIN_ID == 0:
    print("⚠️  OGOHLANTIRISH: ADMIN_ID o'rnatilmagan. Admin komandalar ishlamaydi.", flush=True)

# ═══════════════════════════════════════════
#  SQLITE MA'LUMOTLAR BAZASI
# ═══════════════════════════════════════════
DB_PATH = "hisoblagich.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER,
            username  TEXT,
            section   TEXT,
            type      TEXT,
            desc      TEXT,
            amount    REAL,
            entry_time TEXT,
            saved_at  TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_transactions(user_id, username, entries_json):
    """WebApp dan kelgan ma'lumotlarni DB ga saqlash"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Avval bu foydalanuvchining barcha yozuvlarini o'chir
    c.execute("DELETE FROM transactions WHERE user_id=?", (user_id,))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for section, entries in entries_json.items():
        for e in entries:
            c.execute("""
                INSERT INTO transactions (user_id,username,section,type,desc,amount,entry_time,saved_at)
                VALUES (?,?,?,?,?,?,?,?)
            """, (user_id, username, section, e.get('type'), e.get('desc'),
                  e.get('amount', 0), e.get('time',''), now))
    conn.commit()
    conn.close()

def get_stats(section_filter=None, user_filter=None, days=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    where = []
    params = []
    if section_filter:
        where.append("section=?")
        params.append(section_filter)
    if user_filter:
        where.append("user_id=?")
        params.append(user_filter)
    if days:
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        where.append("saved_at >= ?")
        params.append(from_date)
    sql = "SELECT section,type,SUM(amount),COUNT(*) FROM transactions"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " GROUP BY section,type"
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT user_id,username FROM transactions")
    rows = c.fetchall()
    conn.close()
    return rows

def get_recent(limit=10, user_filter=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_filter:
        c.execute("SELECT username,section,type,desc,amount,entry_time FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_filter, limit))
    else:
        c.execute("SELECT username,section,type,desc,amount,entry_time FROM transactions ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

# ═══════════════════════════════════════════
#  FLASK (UptimeRobot uchun)
# ═══════════════════════════════════════════
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ Hisoblagich bot ishlayapti!", 200

@flask_app.route("/health")
def health():
    return "OK", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ═══════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════
logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════
#  YORDAMCHI FUNKSIYALAR
# ═══════════════════════════════════════════
def fmt(amount):
    return f"{amount:,.0f} so'm".replace(",", " ")

def section_emoji(s):
    return {"restoran": "🍽", "mehmonxona": "🏨", "shaxsiy": "👤"}.get(s, "📁")

def build_stats_text(rows, title="📊 Statistika"):
    if not rows:
        return f"{title}\n\nMa'lumot yo'q."
    sections = {}
    for section, typ, total, count in rows:
        if section not in sections:
            sections[section] = {"income": 0, "expense": 0}
        sections[section][typ] = total
    text = f"{title}\n{'─'*28}\n"
    grand_income = grand_expense = 0
    for s, data in sections.items():
        inc = data.get("income", 0)
        exp = data.get("expense", 0)
        bal = inc - exp
        grand_income += inc
        grand_expense += exp
        text += (
            f"\n{section_emoji(s)} *{s.capitalize()}*\n"
            f"  📈 Kirim:  {fmt(inc)}\n"
            f"  📉 Chiqim: {fmt(exp)}\n"
            f"  💰 Balans: {fmt(bal)}\n"
        )
    text += (
        f"\n{'─'*28}\n"
        f"📈 Jami kirim:  {fmt(grand_income)}\n"
        f"📉 Jami chiqim: {fmt(grand_expense)}\n"
        f"💰 Jami balans: {fmt(grand_income - grand_expense)}"
    )
    return text

def is_admin(user_id):
    return ADMIN_ID != 0 and user_id == ADMIN_ID

# ═══════════════════════════════════════════
#  BOT KOMANDALAR
# ═══════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name or "Do'stim"
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("💰 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    text = (
        f"👋 Salom, <b>{first_name}</b>!\n\n"
        f"Men — <b>Hisoblagich</b> botiman 🧮\n\n"
        f"📌 Kuzatib borasiz:\n"
        f"  🍽 <b>Restoran</b> — kirim va chiqimlar\n"
        f"  🏨 <b>Mehmonxona</b> — kirim va chiqimlar\n"
        f"  👤 <b>Shaxsiy</b> — kirim va chiqimlar\n\n"
        f"Boshlash uchun quyidagi tugmani bosing 👇"
    )
    await update.message.reply_html(text, reply_markup=keyboard)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ <b>Komandalar:</b>\n\n"
        "/start  — Botni boshlash\n"
        "/ochish — Ilovani ochish\n"
        "/mystats — Mening statistikam\n"
    )
    if is_admin(update.effective_user.id):
        text += "\n<b>Admin komandalar:</b>\n/admin — Admin panel\n/stats — Umumiy statistika\n/users — Foydalanuvchilar"
    await update.message.reply_html(text)

async def ochish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("💰 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    await update.message.reply_text("👇 Ilovani ochish:", reply_markup=keyboard)

async def mystats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    rows = get_stats(user_filter=user.id)
    text = build_stats_text(rows, f"📊 Sizning statistikangiz")
    await update.message.reply_text(text, parse_mode="Markdown")

# ─── ADMIN KOMANDALAR ───
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Ruxsat yo'q.")
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Umumiy statistika", callback_data="admin_stats_all")],
        [InlineKeyboardButton("📅 Bugungi", callback_data="admin_stats_today"),
         InlineKeyboardButton("📆 Haftalik", callback_data="admin_stats_week")],
        [InlineKeyboardButton("🍽 Restoran", callback_data="admin_sec_restoran"),
         InlineKeyboardButton("🏨 Mehmonxona", callback_data="admin_sec_mehmonxona")],
        [InlineKeyboardButton("👤 Shaxsiy", callback_data="admin_sec_shaxsiy")],
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton("🕐 So'nggi 10 yozuv", callback_data="admin_recent")],
    ])
    await update.message.reply_text("🔐 *Admin Panel*", parse_mode="Markdown", reply_markup=keyboard)

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Ruxsat yo'q.")
        return
    rows = get_stats()
    await update.message.reply_text(build_stats_text(rows, "📊 Umumiy statistika"), parse_mode="Markdown")

async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("Hali foydalanuvchi yo'q.")
        return
    text = f"👥 *Foydalanuvchilar ({len(users)} ta)*\n{'─'*24}\n"
    for uid, uname in users:
        rows = get_stats(user_filter=uid)
        total_in = sum(r[2] for r in rows if r[1]=="income")
        total_ex = sum(r[2] for r in rows if r[1]=="expense")
        text += f"\n@{uname or '?'} (ID: {uid})\n  📈 {fmt(total_in)}  📉 {fmt(total_ex)}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

# ─── CALLBACK (Inline tugmalar) ───
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if not is_admin(q.from_user.id):
        await q.edit_message_text("❌ Ruxsat yo'q.")
        return

    data = q.data
    back_btn = [[InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")]]

    if data == "admin_stats_all":
        rows = get_stats()
        await q.edit_message_text(build_stats_text(rows, "📊 Umumiy statistika"),
                                   parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(back_btn))

    elif data == "admin_stats_today":
        rows = get_stats(days=1)
        await q.edit_message_text(build_stats_text(rows, "📅 Bugungi statistika"),
                                   parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(back_btn))

    elif data == "admin_stats_week":
        rows = get_stats(days=7)
        await q.edit_message_text(build_stats_text(rows, "📆 Haftalik statistika"),
                                   parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(back_btn))

    elif data.startswith("admin_sec_"):
        sec = data.replace("admin_sec_", "")
        rows = get_stats(section_filter=sec)
        await q.edit_message_text(
            build_stats_text(rows, f"{section_emoji(sec)} {sec.capitalize()} statistikasi"),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_btn))

    elif data == "admin_users":
        users = get_all_users()
        if not users:
            await q.edit_message_text("Hali foydalanuvchi yo'q.",
                                       reply_markup=InlineKeyboardMarkup(back_btn))
            return
        text = f"👥 *Foydalanuvchilar ({len(users)} ta)*\n{'─'*24}\n"
        for uid, uname in users:
            rows = get_stats(user_filter=uid)
            total_in = sum(r[2] for r in rows if r[1]=="income")
            total_ex = sum(r[2] for r in rows if r[1]=="expense")
            text += f"\n@{uname or '?'} (ID:{uid})\n  📈{fmt(total_in)}  📉{fmt(total_ex)}\n"
        await q.edit_message_text(text, parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(back_btn))

    elif data == "admin_recent":
        recent = get_recent(10)
        if not recent:
            await q.edit_message_text("Hali yozuv yo'q.",
                                       reply_markup=InlineKeyboardMarkup(back_btn))
            return
        text = "🕐 *So'nggi 10 yozuv*\n" + "─"*24 + "\n"
        for uname, sec, typ, desc, amount, time in recent:
            icon = "📈" if typ=="income" else "📉"
            text += f"\n{icon} @{uname or '?'} | {sec}\n{desc} — {fmt(amount)}\n"
        await q.edit_message_text(text, parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(back_btn))

    elif data == "admin_back":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Umumiy statistika", callback_data="admin_stats_all")],
            [InlineKeyboardButton("📅 Bugungi", callback_data="admin_stats_today"),
             InlineKeyboardButton("📆 Haftalik", callback_data="admin_stats_week")],
            [InlineKeyboardButton("🍽 Restoran", callback_data="admin_sec_restoran"),
             InlineKeyboardButton("🏨 Mehmonxona", callback_data="admin_sec_mehmonxona")],
            [InlineKeyboardButton("👤 Shaxsiy", callback_data="admin_sec_shaxsiy")],
            [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
            [InlineKeyboardButton("🕐 So'nggi 10 yozuv", callback_data="admin_recent")],
        ])
        await q.edit_message_text("🔐 *Admin Panel*", parse_mode="Markdown", reply_markup=keyboard)

# ─── WEBAPP DAN MA'LUMOT QABUL QILISH ───
async def webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        data = json.loads(update.message.web_app_data.data)
        save_transactions(user.id, user.username or str(user.id), data)
        # Statistika hisoblash
        rows = get_stats(user_filter=user.id)
        stats = build_stats_text(rows, "✅ Ma'lumotlar saqlandi!")
        await update.message.reply_text(stats, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"WebApp data xatosi: {e}")
        await update.message.reply_text("⚠️ Ma'lumotlarni saqlashda xato bo'ldi.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("💰 Ilovani ochish", web_app=WebAppInfo(url=WEB_APP_URL))
    ]])
    await update.message.reply_text("❓ /start yoki /ochish buyrug'ini yuboring.", reply_markup=keyboard)

# ═══════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════
def main():
    init_db()
    logger.info("✅ DB tayyor")

    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    logger.info("✅ Flask server ishga tushdi")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("help",    help_command))
    app.add_handler(CommandHandler("ochish",  ochish))
    app.add_handler(CommandHandler("mystats", mystats))
    app.add_handler(CommandHandler("admin",   admin))
    app.add_handler(CommandHandler("stats",   stats_cmd))
    app.add_handler(CommandHandler("users",   users_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    logger.info("✅ Bot ishga tushdi")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()