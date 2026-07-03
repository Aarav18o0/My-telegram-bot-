import logging
import random
import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# लॉगिंग सेटअप
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8833501052:AAGsdb3RdB-b3NqYNr9JHH-zX5CoOeViOes"
BAD_WORDS = ["gali1", "gali2", "abuse", "saale", "kamine", "fraud", "badword"]

SHAYARI_TRACKER = {}  
USER_XP = {}          
MATH_GAMES = {}       

SHAYARI_BANK = [
    "Khuda ki mohabbat ko fanaa kaun karega, Sabhi nek banenge toh gunaah kaun karega! 😎",
    "Chand ke liye sitare bohot hain, Is jahan mein sahare bohot hain. ❤️",
    "Manzil mile na mile yeh toh muqaddar ki baat hai, Hum koshish bhi na karein yeh toh galat baat hai! 🔥",
    "Hawaon ke bharose mat ud, Chattane tufano ka bhi rukh mod deti hain. 🚀",
    "Dil mein tamannaon ko dabana seekh gaye, Gham ko chhupa kar muskurana seekh gaye. 😂"
]

SCIENCE_QUIZZES = [
    {"question": "Pani ka rasayanik sutra (Chemical Formula) kya hai?", "options": ["CO2", "H2O", "O2", "NaCl"], "correct_id": 1, "explanation": "Pani ka sutra H2O hota hai."},
    {"question": "Manav sharir ki sabse badi haddi कौन सी है?", "options": ["Femur", "Stapes", "Tibia", "Humerus"], "correct_id": 0, "explanation": "Femur सबसे बड़ी होती है."}
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("🔥 Royal Quiz Bot Active!\n/quiz - Science Test\n/math - Calculation\n/rank - Check Rank\n/leaderboard - Top Members\n/balance - Coins\n/daily - Daily Bonus")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if not member.is_bot:
                await update.message.reply_text(text=f"👋 Swagat hai {member.first_name} group mein! 😊")

def get_title(xp):
    if xp < 50: return "Beginner 👶"
    elif xp < 150: return "Scholar 🧑‍🎓"
    else: return "Science King 👑"

async def check_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user_id = update.effective_user.id
        data = USER_XP.get(user_id, {"xp": 0, "name": update.effective_user.first_name})
        title = get_title(data["xp"])
        await update.message.reply_text(f"📊 **Your Status**\n👤 Name: {data['name']}\n⚡ XP Points: {data['xp']}\n🏆 Rank: **{title}**", parse_mode="Markdown")

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        if not USER_XP:
            await update.message.reply_text("📉 Abhi kisi ke paas koi points nahi hain.")
            return
        sorted_users = sorted(USER_XP.items(), key=lambda item: item[1]["xp"], reverse=True)
        leaderboard_text = "🏆 **GROUP LEADERBOARD** 🏆\n\n"
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for index, (user_id, data) in enumerate(sorted_users[:5]):
            leaderboard_text += f"{medals[index]} **{data['name']}** — {data['xp']} XP Points\n"
        await update.message.reply_text(leaderboard_text, parse_mode="Markdown")

async def math_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        chat_id = update.effective_chat.id
        num1, num2 = random.randint(10, 30), random.randint(5, 15)
        ans = num1 + num2
        MATH_GAMES[chat_id] = {"answer": ans, "active": True}
        await update.message.reply_text(f"🔢 **Math Challenge!**\n\nBatao: `{num1} + {num2} = ?`", parse_mode="Markdown")

# Database Backend Setup
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, xp INTEGER DEFAULT 0, coins INTEGER DEFAULT 100, last_daily TEXT DEFAULT '')")
conn.commit()

def get_user(user_id, name):
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, name, xp, coins, last_daily) VALUES (?, ?, 0, 100, '')", (user_id, name))
        conn.commit()

def add_xp(user_id, name, xp):
    get_user(user_id, name)
    cursor.execute("UPDATE users SET xp = xp + ? WHERE user_id=?", (xp, user_id))
    conn.commit()

def get_balance(user_id, name):
    get_user(user_id, name)
    cursor.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    return res[0] if res else 100

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat:
        quiz = random.choice(SCIENCE_QUIZZES)
        await context.bot.send_poll(chat_id=update.effective_chat.id, question=quiz["question"], options=quiz["options"], type="quiz", correct_option_id=quiz["correct_id"], is_anonymous=False, explanation=quiz["explanation"])

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user = update.effective_user
        coins = get_balance(user.id, user.first_name)
        await update.message.reply_text(f"💰 {user.first_name}, aapke paas **{coins} Coins** hain.", parse_mode="Markdown")

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user = update.effective_user
        today = datetime.now().strftime("%Y-%m-%d")
        get_user(user.id, user.first_name)
        cursor.execute("SELECT last_daily FROM users WHERE user_id=?", (user.id,))
        res = cursor.fetchone()
        if res and res[0] == today:
            await update.message.reply_text("🎁 Aaj ka daily reward aap pehle hi claim kar chuke hain.")
            return
        cursor.execute("UPDATE users SET coins = coins + 500, last_daily=? WHERE user_id=?", (today, user.id))
        conn.commit()
        new_coins = get_balance(user.id, user.first_name)
        await update.message.reply_text(f"🎉 Mubarak ho! 500 Coins mil gaye.\n💰 Total Coins: **{new_coins}**", parse_mode="Markdown")

async def message_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip().lower()
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    if any(bad_word in text for bad_word in BAD_WORDS):
        try: await update.message.delete()
        except: pass
        return

    if chat_id in MATH_GAMES and MATH_GAMES[chat_id]["active"]:
        try:
            if text.isdigit() and int(text) == MATH_GAMES[chat_id]["answer"]:
                MATH_GAMES[chat_id]["active"] = False
                USER_XP[user_id] = USER_XP.get(user_id, {"xp": 0, "name": user.first_name})
                USER_XP[user_id]["xp"] += 20
                add_xp(user_id, user.first_name, 20)
                await update.message.reply_text(f"🏆 **WINNER!** @{user.username or user.first_name} (+20 XP)")
                return
        except: pass

    USER_XP[user_id] = USER_XP.get(user_id, {"xp": 0, "name": user.first_name})
    USER_XP[user_id]["xp"] += 5
    add_xp(user_id, user.first_name, 5)

    if "@rudra0000000001" in text:
        await update.message.reply_text("🙂 Sir abhi busy hain.\n📅 Aap appointment mujhse le lijiye.")
        return

    if user_id not in SHAYARI_TRACKER or SHAYARI_TRACKER[user_id] != current_date:
        SHAYARI_TRACKER[user_id] = current_date
        await update.message.reply_text(f"✨ **Shayari For You {user.first_name}!** ✨\n\n{random.choice(SHAYARI_BANK)}")

    if text in ["hi", "hello", "hey"]:
        await update.message.reply_text(f"Hello {user.first_name}! Type /quiz to start.")

# मेन रनिंग ब्लॉक (बिना किसी गलत स्पेस के)
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CommandHandler("rank", check_rank))
    app.add_handler(CommandHandler("leaderboard", leaderboard_command))
    app.add_handler(CommandHandler("math", math_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("daily", daily_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_filter))
    
    print("🔥 Bot Status: ULTIMATE COMMUNITY BOT IS RUNNING LIVE...")
    app.run_polling()
    
