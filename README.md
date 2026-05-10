# 💰 Hisoblagich — Telegram Mini App

Telegram boti orqali ishlaydigan kirim-chiqim hisoblagich ilovasi.

---

## 📁 Fayl tuzilmasi

```
├── index.html       ← Ilova sahifasi (Mini App)
├── style.css        ← Dizayn
├── app.js           ← Mantiq
├── bot.py           ← Telegram bot
├── requirements.txt ← Python kutubxonalari
└── README.md        ← Qo'llanma (shu fayl)
```

---

## 🚀 Bosqichma-bosqich o'rnatish

### 1-QADAM — Bot yarating (@BotFather)

1. Telegramda **@BotFather** ni oching
2. `/newbot` yuboring
3. Bot nomini kiriting (masalan: `HisoblagichBot`)
4. Bot username kiriting (masalan: `hisoblagich_bot`)
5. **TOKEN**ni olib qo'ying (ko'rinishi: `7123456789:AAF...`)

---

### 2-QADAM — HTML ilovani internetga joylashtiring (GitHub Pages)

> Telegram Mini App faqat **HTTPS** manzildan ishlaydi!

**GitHub Pages (bepul):**

1. [github.com](https://github.com) da yangi repo yarating (masalan: `hisoblagich`)
2. `index.html`, `style.css`, `app.js` fayllarini yuklang
3. Repo **Settings → Pages → Branch: main → Save**
4. Manzil tayyor bo'ladi: `https://SIZNING_USERNAME.github.io/hisoblagich`

---

### 3-QADAM — bot.py ni sozlang

`bot.py` faylini oching va 2 ta qatorni o'zgartiring:

```python
BOT_TOKEN   = "7123456789:AAF..."           # ← BotFather dan olgan token
WEB_APP_URL = "https://username.github.io/hisoblagich"  # ← GitHub Pages manzil
```

---

### 4-QADAM — Botni ishga tushiring

```bash
# Kutubxonalarni o'rnating
pip install -r requirements.txt

# Botni ishga tushiring
python bot.py
```

---

### 5-QADAM — Telegram da tekshiring

1. Botingizni oching
2. `/start` yuboring
3. **"💰 Ilovani ochish"** tugmasini bosing
4. Ilova Telegram ichida ochiladi ✅

---

## 🤖 Bot komandalar

| Komanda   | Nima qiladi               |
|-----------|---------------------------|
| `/start`  | Salomlashadi + tugma beradi |
| `/help`   | Yordam ko'rsatadi         |
| `/ochish` | To'g'ridan ilovani ochadi |

---

## ☁️ Botni doim ishlashiga (server)

Kompyuteringiz yoniq bo'lmasa bot to'xtaydi.  
Doim ishlashi uchun bepul serverlar:

- **Railway** — [railway.app](https://railway.app)
- **Render** — [render.com](https://render.com)
- **VPS** (agar bor bo'lsa)

---

## ❓ Muammo bo'lsa

- `WEB_APP_URL` HTTPS bo'lishi **shart** (http:// ishlamaydi)
- Token to'g'ri kiritilganini tekshiring
- GitHub Pages active bo'lishi uchun 1-2 daqiqa kuting
