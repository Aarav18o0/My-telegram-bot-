
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8833501052:AAGsdb3RdB-b3NqYNr9JHH-zX5CoOeViOes"
BAD_WORDS = ["gali1", "gali2", "abuse", "saale", "kamine", "fraud", "badword"]

SHAYARI_TRACKER = {}  
USER_XP = {}          # Database: {user_id: {"xp": 100, "name": "Name"}}
MATH_GAMES = {}       

SHAYARI_BANK = [
    "Khuda ki mohabbat ko fanaa kaun karega, Sabhi nek banenge toh gunaah kaun karega! Ae khuda mere doston ko salamat rakhna, Warna meri shayari par waah-waah kaun karega! 😎",
    "Chand ke liye sitare bohot hain, Is jahan mein sahare bohot hain. Par aap jaise dosto ke hote hue, Hume dushman ke teer bhi pyare hain! ❤️",
    "Manzil mile na mile yeh toh muqaddar ki baat hai, Hum koshish bhi na karein yeh toh galat baat hai! 🔥",
    "Hawaon ke bharose mat ud, Chattane tufano ka bhi rukh mod deti hain. Apne pankhon par bharosa rakh, Hawaon ke bharose toh patange uda karti hain! 🚀",
    "Dil mein tamannaon ko dabana seekh gaye, Gham ko chhupa kar muskurana seekh gaye. Aap jaise dosto ki kya tareef karein, Jo bina bulaye hi group mein aana seekh gaye! 😂"
]

SCIENCE_QUIZZES = [
    {"question": "Pani ka rasayanik sutra (Chemical Formula) kya hai?", "options": ["CO2", "H2O", "O2", "NaCl"], "correct_id": 1, "explanation": "Pani ka sutra H2O hota hai."},
    {"question": "Manav sharir ki sabse badi haddi (Largest Bone) kaun si hai?", "options": ["Femur", "Stapes", "Tibia", "Humerus"], "correct_id": 0, "explanation": "Femur (jaangh ki haddi) sabse badi hoti hai."},
    {"question": "Suraj ki roshni se hume kaun sa Vitamin milta hai?", "options": ["Vitamin A", "Vitamin B", "Vitamin C", "Vitamin D"], "correct_id": 3, "explanation": "Suraj ki dhoop se Vitamin D milta hai."},
    {"question": "Hamare brahmand (Universe) ka sabse bada grah kaun sa hai?", "options": ["Mars", "Earth", "Jupiter", "Saturn"], "correct_id": 2, "explanation": "Jupiter sabse bada grah hai."}
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Royal Quiz Bot Active!\nCommands:\n/quiz - Science Test\n/math - Speed Calculation\n/rank - Check Level\n/leaderboard - Top Active Members List")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if not member.is_bot:
            await update.message.reply_text(text=f"👋 Swagat hai {member.first_name} group mein! 😊")

def get_title(xp):
    if xp < 50: return "Beginner 👶"
    elif xp < 150: return "Scholar 🧑‍🎓"
    else: return "Science King 👑"

# 📊 1. Rank Command Handler
async def check_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = USER_XP.get(user_id, {"xp": 0, "name": update.effective_user.first_name})
    title = get_title(data["xp"])
    await update.message.reply_text(f"📊 **Your Status**\n👤 Name: {data['name']}\n⚡ XP Points: {data['xp']}\n🏆 Rank: **{title}**", parse_mode="Markdown")

# 🏆 2. Leaderboard Command Handler (Sabse Active Logon Ki List)
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not USER_XP:
        await update.message.reply_text("📉 Abhi kisi ke paas koi points nahi hain. Group mein message bhejkar rank badhaiye!")
        return
    
    # Users ko unke XP points ke mutabik highest se lowest order mein sort karna
    sorted_users = sorted(USER_XP.items(), key=lambda item: item[1]["xp"], reverse=True)
    
    leaderboard_text = "🏆 **GROUP LEADERBOARD (TOP ACTIVE MEMBERS)** 🏆\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    
    # Top 5 active users ko list mein dikhana
    for index, (user_id, data) in enumerate(sorted_users[:5]):
        leaderboard_text += f"{medals[index]} **{data['name']}** — {data['xp']} XP Points\n"
        
    await update.message.reply_text(leaderboard_text, parse_mode="Markdown")

async def math_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    num1, num2 = random.randint(10, 30), random.randint(5, 15)
    ans = num1 + num2
    MATH_GAMES[chat_id] = {"answer": ans, "active": True}
    await update.message.reply_text(f"🔢 **Math Challenge!**\n\nBatao: `{num1} + {num2} = ?` \n\nSabse pehle reply karo!")
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    xp INTEGER DEFAULT 0,
    coins INTEGER DEFAULT 100
)
""")

conn.commit()
try:
    cursor.execute("ALTER TABLE users ADD COLUMN last_daily TEXT DEFAULT ''")
    conn.commit()
except:
    pass  
def get_user(user_id, name):
    cursor.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (user_id,)
    )
    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, name, xp, coins) VALUES (?, ?, ?, ?)",
            (user_id, name, 0, 100)
        )
        conn.commit()

def add_xp(user_id, name, xp):
    get_user(user_id, name)
    cursor.execute(
        "UPDATE users SET xp = xp + ? WHERE user_id=?",
        (xp, user_id)
    )
    conn.commit()

def add_coins(user_id, name, coins):
    get_user(user_id, name)
    cursor.execute(
        "UPDATE users SET coins = coins + ? WHERE user_id=?",
        (coins, user_id)
    )
    conn.commit()

def get_balance(user_id, name):
    get_user(user_id, name)
    cursor.execute(
        "SELECT coins FROM users WHERE user_id=?",
        (user_id,)
    )
    return cursor.fetchone()[0]
async def send_random_quiz(chat_id, context: ContextTypes.DEFAULT_TYPE):
    quiz = random.choice(SCIENCE_QUIZZES)
    await context.bot.send_poll(chat_id=chat_id, question=quiz["question"], options=quiz["options"], type="quiz", correct_option_id=quiz["correct_id"], is_anonymous=False, explanation=quiz["explanation"])

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_random_quiz(update.effective_chat.id, context)
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    coins = get_balance(user.id, user.first_name)

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    today = datetime.now().strftime("%Y-%m-%d")

    get_user(user.id, user.first_name)

    cursor.execute(
        "SELECT last_daily FROM users WHERE user_id=?",
        (user.id,)
    )
    last = cursor.fetchone()[0]

    if last == today:
        await update.message.reply_text("🎁 Aaj ka daily reward aap pehle hi claim kar chuke hain.")
        return

    cursor.execute(
        "UPDATE users SET coins = coins + 500, last_daily=? WHERE user_id=?",
        (today, user.id)
    )
    conn.commit()

async def message_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    if any(bad_word in text for bad_word in BAD_WORDS):
        try: await update.message.delete()
        except: pass
        return

    # Math Challenge Winner Check
    if chat_id in MATH_GAMES and MATH_GAMES[chat_id]["active"]:
        try:
            if int(text) == MATH_GAMES[chat_id]["answer"]:
                MATH_GAMES[chat_id]["active"] = False
                USER_XP[user_id] = USER_XP.get(user_id, {"xp": 0, "name": user.first_name})
                USER_XP[user_id]["xp"] += 20  # Winner ko bonus +20 XP milega
                await update.message.reply_text(f"🏆 **WINNER!** @{user.username or user.first_name} ne sabse pehle sahi jawab diya! (+20 XP)")
                return
        except: pass

    # Normal message bhejti hi points jodna (+5 XP)
    USER_XP[user_id] = USER_XP.get(user_id, {"xp": 0, "name": user.first_name})
    USER_XP[user_id]["xp"] += 5
    # Auto reply when @Rudra0000000001 is mentioned
    if "@rudra0000000001" in text:
        await update.message.reply_text(
            "🙂 Sir abhi busy hain.\n\n"
            "📅 Aap appointment mujhse le lijiye.\n"
            "Sir aayenge to hum aapka number lagwa denge."
        )
        return
    # Daily One-Time Shayari System
    if user_id not in SHAYARI_TRACKER or SHAYARI_TRACKER[user_id] != current_date:
        SHAYARI_TRACKER[user_id] = current_date
        await update.message.reply_text(f"✨ **Shayari For You {user.first_name}!** ✨\n\n{random.choice(SHAYARI_BANK)}")

    if text in ["hi", "hello", "hey"]:
        await update.message.reply_text(f"Hello {user.first_name}! Type /quiz to start test.")

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
