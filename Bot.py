import telebot
from telebot import types
import sqlite3
import random
import string
import requests
from datetime import datetime

# ================= الإعدادات الأساسية =================
TOKEN = "8734225282:AAEMhd8URoLIA6uTxYsVGxrch7-DT8ttA9c"
ADMIN_ID = 6759191586
API_TOKEN = "cb31934b7ce14c3fb458ae7ba0882d24" # توكن موقع توليد البطاقات

bot = telebot.TeleBot(TOKEN)

# ================= إعداد قاعدة البيانات =================
def init_db():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, balance INTEGER, invites INTEGER, last_daily TEXT, banned INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (order_id TEXT PRIMARY KEY, user_id INTEGER, card_data TEXT, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY, value INTEGER)''')
    
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('card_price', 100)")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('daily_bonus', 50)")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('invite_reward', 25)")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('daily_enabled', 1)")
    conn.commit()
    conn.close()

init_db()

def get_user(user_id):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(user_id, inviter_id=None):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, balance, invites, last_daily, banned) VALUES (?, ?, ?, ?, ?)",
              (user_id, 0, 0, "", 0))
    if c.rowcount > 0 and inviter_id and inviter_id != user_id:
        reward = get_setting('invite_reward')
        c.execute("UPDATE users SET balance = balance + ?, invites = invites + 1 WHERE user_id = ?", (reward, inviter_id))
        try:
            bot.send_message(inviter_id, f"🎉 قام شخص بالدخول عبر رابطك! حصلت على {reward} نقطة.")
        except:
            pass
    conn.commit()
    conn.close()

def update_balance(user_id, amount):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    val = c.fetchone()[0]
    conn.close()
    return val

# ================= لوحات المفاتيح =================
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💰 رصيدي"),
        types.KeyboardButton("🎁 المكافأة اليومية"),
        types.KeyboardButton("👥 دعوة الأصدقاء"),
        types.KeyboardButton("🛒 متجر البطاقات"),
        types.KeyboardButton("📦 طلباتي"),
        types.KeyboardButton("ℹ️ حسابي")
    )
    return markup

def admin_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats"),
        types.InlineKeyboardButton("⚙️ الإعدادات", callback_data="admin_settings"),
        types.InlineKeyboardButton("📢 إذاعة رسالة", callback_data="admin_broadcast")
    )
    return markup

# ================= الأوامر الأساسية =================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if user and user[4] == 1:
        bot.reply_to(message, "❌ حسابك محظور من استخدام البوت.")
        return

    if not user:
        args = message.text.split()
        inviter_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        add_user(user_id, inviter_id)
    
    bot.send_message(user_id, "أهلاً بك في البوت! 🤖\nاستخدم القائمة للتنقل:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if not user:
        add_user(user_id)
        user = get_user(user_id)
        
    if user[4] == 1:
        return 

    text = message.text

    if text == "💰 رصيدي":
        bot.reply_to(message, f"رصيدك الحالي هو: **{user[1]}** نقطة 💰", parse_mode="Markdown")

    elif text == "🎁 المكافأة اليومية":
        if get_setting('daily_enabled') == 0:
            bot.reply_to(message, "❌ المكافأة اليومية متوقفة حالياً.")
            return
            
        today = datetime.now().strftime("%Y-%m-%d")
        if user[3] == today:
            bot.reply_to(message, "❌ لقد حصلت على المكافأة اليومية مسبقاً، عد غداً!")
        else:
            bonus = get_setting('daily_bonus')
            conn = sqlite3.connect('bot_database.db')
            c = conn.cursor()
            c.execute("UPDATE users SET balance = balance + ?, last_daily = ? WHERE user_id = ?", (bonus, today, user_id))
            conn.commit()
            conn.close()
            bot.reply_to(message, f"🎉 مبروك! حصلت على {bonus} نقطة. رصيدك الآن: {user[1] + bonus}")

    elif text == "👥 دعوة الأصدقاء":
        bot_info = bot.get_me()
        link = f"https://t.me/{bot_info.username}?start={user_id}"
        reward = get_setting('invite_reward')
        msg = f"👥 شارك هذا الرابط مع أصدقائك!\nستحصل على **{reward} نقطة** لكل شخص يدخل البوت.\n\nرابطك: `{link}`"
        bot.reply_to(message, msg, parse_mode="Markdown")

    elif text == "🛒 متجر البطاقات":
        price = get_setting('card_price')
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(f"💳 شراء بطاقة Test (السعر: {price} نقطة)", callback_data="buy_test_card")
        markup.add(btn)
        bot.reply_to(message, "اختر الباقة التي تناسبك:", reply_markup=markup)

    elif text == "📦 طلباتي":
        conn = sqlite3.connect('bot_database.db')
        c = conn.cursor()
        c.execute("SELECT order_id, card_data, date FROM orders WHERE user_id=? ORDER BY date DESC LIMIT 5", (user_id,))
        orders = c.fetchall()
        conn.close()
        
        if not orders:
            bot.reply_to(message, "لا توجد لديك طلبات سابقة 📦.")
        else:
            msg = "📦 أحدث 5 طلبات لك:\n\n"
            for o in orders:
                msg += f"🔹 طلب: `{o[0]}`\n💳 البطاقة: `{o[1]}`\n📅 التاريخ: {o[2]}\n〰️〰️〰️〰️\n"
            bot.reply_to(message, msg, parse_mode="Markdown")

    elif text == "ℹ️ حسابي":
        msg = f"👤 **معلومات حسابك:**\n🆔 الأيدي: `{user_id}`\n💰 الرصيد: `{user[1]}` نقطة\n👥 عدد الدعوات: `{user[2]}` شخص"
        bot.reply_to(message, msg, parse_mode="Markdown")

# ================= الشراء والربط مع الـ API =================
@bot.callback_query_handler(func=lambda call: call.data == "buy_test_card")
def process_purchase(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    price = get_setting('card_price')

    if user[1] < price:
        bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ لشراء هذه البطاقة!", show_alert=True)
        return

    # إعلام المستخدم ببدء العملية
    bot.edit_message_text("🔄 جاري الاتصال بمزود الخدمة لاستخراج البطاقة...", chat_id=call.message.chat.id, message_id=call.message.message_id)

    # الاتصال بالـ API لتوليد البطاقة
    api_url = f"https://ccardgenerator.com/api-endpoints/cc-generator.php?token={API_TOKEN}&format=json&count=1"
    
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # التأكد من صحة استجابة الـ API
            if isinstance(data, list) and len(data) > 0 and "CreditCard" in data[0]:
                cc_info = data[0]["CreditCard"]
                network = cc_info.get("IssuingNetwork", "Unknown")
                number = cc_info.get("CardNumber", "N/A")
                cvv = cc_info.get("CVV", "N/A")
                exp = cc_info.get("Exp", "N/A")
                name = cc_info.get("Name", "Unknown")
                country = cc_info.get("Country", "Unknown")
                
                # تنسيق النتيجة النهائية
                card_data = f"{number}|{exp}|{cvv} - {network}"
                full_details = f"💳 **رقم البطاقة:** `{number}`\n📅 **الانتهاء:** `{exp}`\n🔐 **CVV:** `{cvv}`\n🏛 **الشبكة:** {network}\n👤 **الاسم:** {name}\n🌍 **الدولة:** {country}"
                
            else:
                bot.edit_message_text("❌ حدث خطأ غير متوقع في استجابة المزود.", chat_id=call.message.chat.id, message_id=call.message.message_id)
                return
        
        elif response.status_code == 429:
            bot.edit_message_text("❌ عذراً، تم الوصول للحد الأقصى اليومي لطلبات السيرفر (50 طلب). حاول غداً.", chat_id=call.message.chat.id, message_id=call.message.message_id)
            return
        else:
            try:
                error_msg = response.json().get("error", "خطأ غير معروف")
            except:
                error_msg = "خطأ في الاتصال"
            bot.edit_message_text(f"❌ فشل السحب من المزود: {error_msg}", chat_id=call.message.chat.id, message_id=call.message.message_id)
            return

    except requests.exceptions.RequestException:
        bot.edit_message_text("❌ المزود لا يستجيب حالياً (Timeout). حاول مرة أخرى لاحقاً.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        return

    # إذا نجح السحب: خصم النقاط وحفظ الطلب
    order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    update_balance(user_id, -price)
    
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (order_id, user_id, card_data, date) VALUES (?, ?, ?, ?)", (order_id, user_id, card_data, date_now))
    conn.commit()
    conn.close()

    success_msg = f"✅ **اكتمل طلبك بنجاح!**\n\n🆔 رقم الطلب: `{order_id}`\n\n{full_details}\n\n📉 تم خصم {price} نقطة من رصيدك."
    bot.edit_message_text(success_msg, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")

# ================= لوحة تحكم الأدمن =================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = "👑 **لوحة تحكم الإدارة**\n\nأوامر سريعة:\n`/add <ID> <النقاط>` - إضافة نقاط\n`/sub <ID> <النقاط>` - خصم نقاط\n`/ban <ID>` - حظر مستخدم\n`/unban <ID>` - فك حظر\n`/price <السعر>` - تغيير سعر البطاقة"
    bot.reply_to(message, msg, reply_markup=admin_menu(), parse_mode="Markdown")

@bot.message_handler(commands=['add', 'sub', 'ban', 'unban', 'price'])
def admin_commands(message):
    if message.from_user.id != ADMIN_ID:
        return
    cmd = message.text.split()
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()

    try:
        if cmd[0] == '/add' and len(cmd) == 3:
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (int(cmd[2]), int(cmd[1])))
            bot.reply_to(message, f"✅ تم إضافة {cmd[2]} نقطة للمستخدم {cmd[1]}")
        elif cmd[0] == '/sub' and len(cmd) == 3:
            c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (int(cmd[2]), int(cmd[1])))
            bot.reply_to(message, f"✅ تم خصم {cmd[2]} نقطة من المستخدم {cmd[1]}")
        elif cmd[0] == '/ban' and len(cmd) == 2:
            c.execute("UPDATE users SET banned = 1 WHERE user_id = ?", (int(cmd[1]),))
            bot.reply_to(message, f"✅ تم حظر المستخدم {cmd[1]}")
        elif cmd[0] == '/unban' and len(cmd) == 2:
            c.execute("UPDATE users SET banned = 0 WHERE user_id = ?", (int(cmd[1]),))
            bot.reply_to(message, f"✅ تم فك الحظر عن {cmd[1]}")
        elif cmd[0] == '/price' and len(cmd) == 2:
            c.execute("UPDATE settings SET value = ? WHERE key = 'card_price'", (int(cmd[1]),))
            bot.reply_to(message, f"✅ تم تغيير سعر البطاقة إلى {cmd[1]}")
        conn.commit()
    except:
        bot.reply_to(message, "❌ خطأ في كتابة الأمر. تأكد من إدخال الأرقام بشكل صحيح.")
    finally:
        conn.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callbacks(call):
    if call.from_user.id != ADMIN_ID:
        return
    if call.data == "admin_stats":
        conn = sqlite3.connect('bot_database.db')
        c = conn.cursor()
        users_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        orders_count = c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        conn.close()
        bot.send_message(ADMIN_ID, f"📊 **الإحصائيات:**\n👥 عدد المستخدمين: {users_count}\n📦 إجمالي الطلبات: {orders_count}", parse_mode="Markdown")
    
    elif call.data == "admin_settings":
        bot.send_message(ADMIN_ID, "استخدم الأمر `/price <الرقم>` لتغيير سعر البطاقة.")
        bot.answer_callback_query(call.id)
        
    elif call.data == "admin_broadcast":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(ADMIN_ID, "أرسل الرسالة التي تريد إذاعتها الآن:")
        bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    
    success = 0
    for u in users:
        try:
            bot.copy_message(chat_id=u[0], from_chat_id=ADMIN_ID, message_id=message.message_id)
            success += 1
        except:
            pass
    bot.send_message(ADMIN_ID, f"✅ تمت الإذاعة بنجاح إلى {success} مستخدم.")

# ================= تشغيل البوت =================
if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()
