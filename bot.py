import telebot
from telebot import types, apihelper
import os
import sqlite3
import threading
import time
import hashlib
import random
import string
import logging
import datetime
import requests
import json
import re
import base64
import urllib.parse
from bs4 import BeautifulSoup

TOKEN = "8734225282:AAEMhd8URoLIA6uTxYsVGxrch7-DT8ttA9c"
ADMIN_ID = 6759191586
VERSION = "0.1"
BOT_NAME = "مصنع البوتات"

REQUIRED_CHANNELS = ["@bshshshkk", "@BQBOOB", "@O5O6J", "@EQJ_1"]
DEV_NAME = "الذئب الأبيض"
DEV_LINK = "https://t.me/j49_c"

PLAN_PRICES = {"month": 100, "3m": 250, "year": 800, "life": 2000}
PLAN_NAMES = {"month": "شهري 🥉", "3m": "3 أشهر 🥈", "year": "سنوي 🥇", "life": "مدى الحياة 💎"}
PLAN_DAYS = {"month": 30, "3m": 90, "year": 365, "life": -1}
BOT_LIMITS = {"free": 0, "month": 3, "3m": 5, "year": 10, "life": 999}

BANNED_WORDS = ["سبام", "اعلان", "مبروك ربحت", "واتساب", "تيليغرام", "ارسل"]
SPAM_THRESHOLD = 5
SPAM_WINDOW = 60

bot = telebot.TeleBot(TOKEN, parse_mode=None)
DB_FILE = "factory.db"
active_bots = {}
user_message_times = {}
lock = threading.Lock()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("factory.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class _DB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.execute("PRAGMA cache_size=10000")
        self.cur = self.conn.cursor()
        self._init()

    def _init(self):
        self.cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT,
            join_date TEXT, last_seen TEXT, sub_type TEXT DEFAULT 'free', sub_expiry TEXT,
            stars INTEGER DEFAULT 0, invited INTEGER DEFAULT 0, invited_by INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0, ban_reason TEXT, lang TEXT DEFAULT 'ar',
            total_messages INTEGER DEFAULT 0, daily_bonus_date TEXT,
            referral_earnings INTEGER DEFAULT 0, profile_views INTEGER DEFAULT 0,
            vip INTEGER DEFAULT 0, vip_expiry TEXT
        );
        CREATE TABLE IF NOT EXISTS hosted_bots (
            id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, bot_token TEXT UNIQUE,
            bot_type TEXT, bot_name TEXT, bot_username TEXT, created_at TEXT,
            status TEXT DEFAULT 'active', admin_id INTEGER, settings TEXT DEFAULT '{}',
            force_channels TEXT, bot_stars INTEGER DEFAULT 0, bot_plan_price INTEGER DEFAULT 0,
            bot_plan_type TEXT DEFAULT 'free', welcome_msg TEXT, total_users INTEGER DEFAULT 0,
            total_revenue INTEGER DEFAULT 0, last_activity TEXT, description TEXT,
            thumbnail TEXT, max_users INTEGER DEFAULT 0, custom_commands TEXT DEFAULT '{}',
            blocked_users TEXT DEFAULT '[]',
            allowed_types TEXT DEFAULT '["text","photo","video","document","audio","voice","sticker","animation"]'
        );
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, bot_id INTEGER DEFAULT 0,
            amount INTEGER, currency TEXT DEFAULT 'XTR', plan TEXT,
            status TEXT DEFAULT 'pending', payload TEXT UNIQUE, created_at TEXT,
            expiry TEXT, refunded INTEGER DEFAULT 0, notes TEXT
        );
        CREATE TABLE IF NOT EXISTS shop_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER, name TEXT, description TEXT,
            price INTEGER, original_price INTEGER DEFAULT 0, stock INTEGER DEFAULT -1,
            delivery TEXT DEFAULT 'manual', content TEXT, category TEXT DEFAULT 'عام',
            image TEXT, sold_count INTEGER DEFAULT 0, created_at TEXT,
            active INTEGER DEFAULT 1, discount INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS shop_users (
            user_id INTEGER, bot_id INTEGER, balance INTEGER DEFAULT 0,
            total_spent INTEGER DEFAULT 0, total_earned INTEGER DEFAULT 0,
            last_daily INTEGER DEFAULT 0, daily_streak INTEGER DEFAULT 0,
            referred_by INTEGER DEFAULT 0, referral_count INTEGER DEFAULT 0,
            sub_type TEXT DEFAULT 'free', sub_expiry TEXT, rank TEXT DEFAULT 'عادي',
            total_purchases INTEGER DEFAULT 0, wishlist TEXT DEFAULT '[]',
            cart TEXT DEFAULT '[]', join_date TEXT, PRIMARY KEY (user_id, bot_id)
        );
        CREATE TABLE IF NOT EXISTS shop_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER, user_id INTEGER,
            product_id INTEGER, quantity INTEGER DEFAULT 1, total_price INTEGER,
            status TEXT DEFAULT 'pending', created_at TEXT, delivered_at TEXT, notes TEXT
        );
        CREATE TABLE IF NOT EXISTS contact_replies (
            user_id INTEGER, bot_id INTEGER, msg_id INTEGER, admin_msg_id INTEGER,
            time TEXT, replied INTEGER DEFAULT 0, PRIMARY KEY (user_id, bot_id, msg_id)
        );
        CREATE TABLE IF NOT EXISTS mail_sessions (
            user_id INTEGER, bot_id INTEGER, email TEXT, svc TEXT, token TEXT,
            created_at TEXT, expires_at TEXT, message_count INTEGER DEFAULT 0,
            last_checked TEXT, PRIMARY KEY (user_id, bot_id)
        );
        CREATE TABLE IF NOT EXISTS bot_subscribers (
            user_id INTEGER, bot_id INTEGER, sub_type TEXT DEFAULT 'free',
            sub_expiry TEXT, join_date TEXT, last_seen TEXT,
            total_messages INTEGER DEFAULT 0, banned INTEGER DEFAULT 0,
            notes TEXT, PRIMARY KEY (user_id, bot_id)
        );
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER, user_id INTEGER,
            title TEXT, category TEXT DEFAULT 'عام', priority TEXT DEFAULT 'normal',
            status TEXT DEFAULT 'open', created_at TEXT, closed_at TEXT, rating INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS ticket_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id INTEGER, user_id INTEGER,
            is_admin INTEGER DEFAULT 0, message TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS bot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER, event TEXT,
            details TEXT, user_id INTEGER DEFAULT 0, created_at TEXT, ip TEXT
        );
        CREATE TABLE IF NOT EXISTS auto_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER, trigger TEXT,
            response TEXT, match_type TEXT DEFAULT 'exact', active INTEGER DEFAULT 1,
            uses INTEGER DEFAULT 0, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER DEFAULT 0,
            user_id INTEGER, reason TEXT, banned_at TEXT, banned_by INTEGER, expires_at TEXT
        );
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER DEFAULT 0,
            title TEXT, content TEXT, created_at TEXT, expires_at TEXT,
            views INTEGER DEFAULT 0, active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, referred_id INTEGER,
            bot_id INTEGER DEFAULT 0, reward INTEGER DEFAULT 0, created_at TEXT,
            status TEXT DEFAULT 'pending'
        );
        CREATE TABLE IF NOT EXISTS user_sessions (
            user_id INTEGER, bot_id INTEGER DEFAULT 0, state TEXT,
            data TEXT DEFAULT '{}', updated_at TEXT, PRIMARY KEY (user_id, bot_id)
        );
        CREATE TABLE IF NOT EXISTS coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER, code TEXT UNIQUE,
            discount_type TEXT DEFAULT 'percent', discount_value INTEGER,
            max_uses INTEGER DEFAULT 1, used_count INTEGER DEFAULT 0,
            expires_at TEXT, created_at TEXT, active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            bot_id INTEGER DEFAULT 0, title TEXT, message TEXT,
            read INTEGER DEFAULT 0, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS stars_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount INTEGER,
            type TEXT, description TEXT, created_at TEXT, balance_after INTEGER
        );
        CREATE TABLE IF NOT EXISTS factory_settings (
            key TEXT PRIMARY KEY, value TEXT, updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS support_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER, user_id INTEGER,
            admin_id INTEGER, status TEXT DEFAULT 'active', created_at TEXT, closed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS scheduled_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER,
            target_type TEXT DEFAULT 'all', target_id INTEGER DEFAULT 0,
            message TEXT, scheduled_at TEXT, sent INTEGER DEFAULT 0, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS bot_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER,
            name TEXT, emoji TEXT DEFAULT '📁', order_num INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER, msg_id INTEGER,
            original TEXT, translated TEXT, lang TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS bot_webhooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, bot_id INTEGER, event TEXT,
            url TEXT, secret TEXT, active INTEGER DEFAULT 1, created_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_users_sub ON users(sub_type);
        CREATE INDEX IF NOT EXISTS idx_hosted_bots_owner ON hosted_bots(owner_id);
        CREATE INDEX IF NOT EXISTS idx_hosted_bots_status ON hosted_bots(status);
        CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id);
        CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
        CREATE INDEX IF NOT EXISTS idx_bot_subscribers_bot ON bot_subscribers(bot_id);
        CREATE INDEX IF NOT EXISTS idx_shop_users_bot ON shop_users(bot_id);
        CREATE INDEX IF NOT EXISTS idx_shop_products_bot ON shop_products(bot_id);
        CREATE INDEX IF NOT EXISTS idx_tickets_bot ON tickets(bot_id);
        CREATE INDEX IF NOT EXISTS idx_bot_logs_bot ON bot_logs(bot_id);
        CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
        CREATE INDEX IF NOT EXISTS idx_stars_user ON stars_transactions(user_id);
        """)
        self.conn.commit()
        self._seed_settings()

    def _seed_settings(self):
        defaults = {
            "maintenance": "0", "max_free_bots": "0", "referral_reward": "10",
            "daily_bonus": "10", "daily_streak_bonus": "2", "welcome_bonus": "5",
            "min_withdraw": "100", "factory_version": VERSION,
            "registration_open": "1", "debug_mode": "0",
        }
        for k, v in defaults.items():
            self.cur.execute(
                "INSERT OR IGNORE INTO factory_settings (key, value, updated_at) VALUES (?,?,?)",
                (k, v, datetime.datetime.now().isoformat()))
        self.conn.commit()

    def q(self, sql, params=()):
        with lock:
            try:
                self.cur.execute(sql, params)
                self.conn.commit()
                return self.cur
            except sqlite3.Error as e:
                logger.error(f"DB Error: {e} | SQL: {sql}")
                return None

    def f(self, sql, params=()):
        with lock:
            try:
                self.cur.execute(sql, params)
                return self.cur.fetchone()
            except sqlite3.Error as e:
                logger.error(f"DB Error: {e}")
                return None

    def fa(self, sql, params=()):
        with lock:
            try:
                self.cur.execute(sql, params)
                return self.cur.fetchall()
            except sqlite3.Error as e:
                logger.error(f"DB Error: {e}")
                return []

    def setting(self, key, default="0"):
        r = self.f("SELECT value FROM factory_settings WHERE key=?", (key,))
        return r[0] if r else default

    def set_setting(self, key, value):
        self.q("INSERT OR REPLACE INTO factory_settings (key, value, updated_at) VALUES (?,?,?)",
               (key, str(value), datetime.datetime.now().isoformat()))

    def log(self, bot_id, event, details, user_id=0):
        self.q("INSERT INTO bot_logs (bot_id, event, details, user_id, created_at) VALUES (?,?,?,?,?)",
               (bot_id, event, details, user_id, datetime.datetime.now().isoformat()))

    def notify(self, user_id, title, message, bot_id=0):
        self.q("INSERT INTO notifications (user_id, bot_id, title, message, created_at) VALUES (?,?,?,?,?)",
               (user_id, bot_id, title, message, datetime.datetime.now().isoformat()))

    def add_stars(self, user_id, amount, desc=""):
        self.q("UPDATE users SET stars = stars + ? WHERE user_id=?", (amount, user_id))
        bal = self.f("SELECT stars FROM users WHERE user_id=?", (user_id,))
        bal = bal[0] if bal else 0
        self.q("INSERT INTO stars_transactions (user_id, amount, type, description, created_at, balance_after) VALUES (?,?,?,?,?,?)",
               (user_id, amount, "credit" if amount > 0 else "debit", desc,
                datetime.datetime.now().isoformat(), bal))

    def get_state(self, user_id, bot_id=0):
        r = self.f("SELECT state, data FROM user_sessions WHERE user_id=? AND bot_id=?", (user_id, bot_id))
        if r:
            return r[0], json.loads(r[1]) if r[1] else {}
        return None, {}

    def set_state(self, user_id, state, data=None, bot_id=0):
        self.q("INSERT OR REPLACE INTO user_sessions (user_id, bot_id, state, data, updated_at) VALUES (?,?,?,?,?)",
               (user_id, bot_id, state, json.dumps(data or {}), datetime.datetime.now().isoformat()))

    def clear_state(self, user_id, bot_id=0):
        self.q("DELETE FROM user_sessions WHERE user_id=? AND bot_id=?", (user_id, bot_id))


db = _DB()


class _MailEngine:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        self.timeout = 20

    def create(self, svc):
        methods = {
            "1secmail": self._1s, "tempmail": self._tm, "yopmail": self._yp,
            "mobtemp": self._mb, "guerrilla": self._gg, "mailnull": self._mn
        }
        fn = methods.get(svc)
        return fn() if fn else None

    def fetch(self, email, svc, token=None):
        methods = {
            "1secmail": lambda: self._1si(email),
            "tempmail": lambda: self._tmi(email),
            "yopmail": lambda: self._ypi(email),
            "mobtemp": lambda: self._mbi(token),
            "guerrilla": lambda: self._ggi(email),
            "mailnull": lambda: self._mni(email)
        }
        fn = methods.get(svc)
        return fn() if fn else None

    def _1s(self):
        try:
            r = self.s.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1", timeout=self.timeout).json()
            return {"email": r[0], "token": None, "svc": "1secmail"} if r else None
        except:
            return None

    def _1si(self, email):
        try:
            l, d = email.split("@")
            r = self.s.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={l}&domain={d}", timeout=self.timeout).json()
            result = []
            for m in (r if isinstance(r, list) else []):
                detail = self.s.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={l}&domain={d}&id={m.get('id')}", timeout=self.timeout).json()
                result.append({"from": m.get("from", ""), "sub": m.get("subject", ""),
                                "body": detail.get("body", detail.get("textBody", ""))[:500],
                                "time": m.get("date", ""), "id": m.get("id", "")})
            return result
        except:
            return None

    def _tm(self):
        try:
            data = {"name": "".join(random.choices(string.ascii_lowercase + string.digits, k=12)),
                    "domain": random.choice(["greencafe24.com", "tmpmail.org", "niwghx.com"])}
            r = self.s.post("https://api.internal.temp-mail.io/api/v3/email/new", data=data, timeout=self.timeout).json()
            return {"email": r.get("email"), "token": None, "svc": "tempmail"} if r.get("email") else None
        except:
            return None

    def _tmi(self, email):
        try:
            r = self.s.get(f"https://api.internal.temp-mail.io/api/v3/email/{email}/messages", timeout=self.timeout).json()
            return [{"from": m.get("from", ""), "sub": m.get("subject", ""),
                     "body": m.get("body_text", "")[:500], "time": m.get("created_at", "")}
                    for m in (r if isinstance(r, list) else [])]
        except:
            return None

    def _yp(self):
        c = string.ascii_lowercase + string.digits
        return {"email": "".join(random.choices(c, k=14)) + "@yopmail.com", "token": None, "svc": "yopmail"}

    def _ypi(self, email):
        try:
            l = email.split("@")[0]
            p = {"login": l, "p": "1", "yp": "CZGt2ZwL3AGp3ZGNmZGxmBQR",
                 "yj": "RZGxmZGZ4ZGL4ZmV2AQHkBGx", "v": "9.2"}
            r = self.s.get("https://yopmail.com/en/inbox", params=p,
                           headers={"User-Agent": "Mozilla/5.0"}, timeout=self.timeout)
            s = BeautifulSoup(r.text, "html.parser")
            items = s.find_all("div", class_="m")
            return [{"from": i.find("span", class_="lmf").text if i.find("span", class_="lmf") else "",
                     "sub": "", "body": i.find("div", class_="lms").text if i.find("div", class_="lms") else "",
                     "time": i.find("span", class_="lmh").text if i.find("span", class_="lmh") else ""}
                    for i in items]
        except:
            return None

    def _mb(self):
        try:
            h = {"Host": "mob2.temp-mail.org", "accept": "application/json",
                 "accept-encoding": "gzip", "user-agent": "3.33", "content-length": "0"}
            r = self.s.post("https://mob2.temp-mail.org/mailbox", headers=h, timeout=self.timeout).json()
            return {"email": r["mailbox"], "token": r["token"], "svc": "mobtemp"} if r.get("mailbox") else None
        except:
            return None

    def _mbi(self, token):
        try:
            h = {"Host": "mob2.temp-mail.org", "accept": "application/json",
                 "accept-encoding": "gzip", "user-agent": "3.33", "authorization": token}
            r = self.s.get("https://mob2.temp-mail.org/messages", headers=h, timeout=self.timeout).json()
            return [{"from": m.get("from", ""), "sub": m.get("subject", ""),
                     "body": json.dumps(m)[:500], "time": m.get("created_at", "")}
                    for m in (r if isinstance(r, list) else [])]
        except:
            return None

    def _gg(self):
        try:
            r = self.s.get("https://www.guerrillamail.com/ajax.php?f=get_email_address&lang=en&sid_token=",
                           timeout=self.timeout).json()
            return {"email": r.get("email_addr"), "token": r.get("sid_token"), "svc": "guerrilla"} if r.get("email_addr") else None
        except:
            return None

    def _ggi(self, email):
        try:
            r = self.s.get("https://www.guerrillamail.com/ajax.php?f=check_email&seq=0", timeout=self.timeout).json()
            msgs = r.get("list", [])
            return [{"from": m.get("mail_from", ""), "sub": m.get("mail_subject", ""),
                     "body": m.get("mail_excerpt", "")[:500], "time": m.get("mail_date", "")}
                    for m in msgs]
        except:
            return None

    def _mn(self):
        try:
            name = "".join(random.choices(string.ascii_lowercase, k=10))
            return {"email": f"{name}@mailnull.com", "token": None, "svc": "mailnull"}
        except:
            return None

    def _mni(self, email):
        try:
            l = email.split("@")[0]
            r = self.s.get(f"https://mailnull.com/{l}", timeout=self.timeout)
            s = BeautifulSoup(r.text, "html.parser")
            items = s.find_all("div", class_="mail-item")
            return [{"from": i.find("span", class_="from").text if i.find("span", class_="from") else "",
                     "sub": i.find("span", class_="subject").text if i.find("span", class_="subject") else "",
                     "body": i.find("div", class_="preview").text if i.find("div", class_="preview") else "",
                     "time": ""} for i in items]
        except:
            return None


mail_engine = _MailEngine()

SVC_NAMES = {
    "1secmail": "الصاعقة ⚡", "tempmail": "التيمب 🚀", "yopmail": "اليوب 📮",
    "mobtemp": "الأصلي 🔥", "guerrilla": "المحارب ⚔️", "mailnull": "الصفر 🌀"
}
SVC_LIST = list(SVC_NAMES.keys())


def _chk_sub(uid, channels=None):
    chs = channels if channels else REQUIRED_CHANNELS
    if not chs:
        return True
    try:
        for ch in chs:
            m = bot.get_chat_member(ch, uid)
            if m.status in ["left", "kicked"]:
                return False
        return True
    except:
        return False

def _sub_kb(channels=None):
    chs = channels if channels else REQUIRED_CHANNELS
    k = types.InlineKeyboardMarkup(row_width=1)
    for ch in chs:
        name = ch.replace("@", "")
        k.add(types.InlineKeyboardButton(f"📢 اشترك في {name}", url=f"https://t.me/{name}"))
    k.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="verify_bot_sub"))
    return k

def _main_kb(uid):
    k = types.InlineKeyboardMarkup(row_width=2)
    sub = db.f("SELECT sub_type FROM users WHERE user_id=?", (uid,))
    st = sub[0] if sub else "free"
    stars_r = db.f("SELECT stars FROM users WHERE user_id=?", (uid,))
    star_count = stars_r[0] if stars_r else 0
    bc = db.f("SELECT COUNT(*) FROM hosted_bots WHERE owner_id=? AND status='active'", (uid,))
    bots_count = bc[0] if bc else 0
    if st == "free":
        k.add(types.InlineKeyboardButton("⭐ ترقية للبرو", callback_data="upgrade"))
    else:
        k.add(types.InlineKeyboardButton(f"🌟 مشترك - {PLAN_NAMES.get(st, st)}", callback_data="my_acc"))
    k.add(types.InlineKeyboardButton("🤖 إنشاء بوت", callback_data="create_bot"),
          types.InlineKeyboardButton(f"📊 بوتاتي ({bots_count})", callback_data="my_bots"))
    k.add(types.InlineKeyboardButton(f"⭐ نجومي ({star_count})", callback_data="my_stars"),
          types.InlineKeyboardButton("👤 حسابي", callback_data="my_acc"))
    k.add(types.InlineKeyboardButton("📋 قائمة البوتات", callback_data="bot_store"),
          types.InlineKeyboardButton("🎁 الإحالات", callback_data="referrals"))
    k.add(types.InlineKeyboardButton("📢 الإعلانات", callback_data="announcements"),
          types.InlineKeyboardButton("🔔 إشعاراتي", callback_data="my_notifications"))
    k.add(types.InlineKeyboardButton("🆘 الدعم الفني", url=DEV_LINK))
    return k

def _admin_kb():
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("📊 إحصائيات", callback_data="adm_stats"),
          types.InlineKeyboardButton("📢 إذاعة", callback_data="adm_broadcast"))
    k.add(types.InlineKeyboardButton("⭐ إضافة نجوم", callback_data="adm_add_stars"),
          types.InlineKeyboardButton("🤖 إدارة بوتات", callback_data="adm_bots"))
    k.add(types.InlineKeyboardButton("👥 المستخدمين", callback_data="adm_users"),
          types.InlineKeyboardButton("💰 المدفوعات", callback_data="adm_payments"))
    k.add(types.InlineKeyboardButton("🎫 التذاكر", callback_data="adm_tickets"),
          types.InlineKeyboardButton("📈 التحليلات", callback_data="adm_analytics"))
    k.add(types.InlineKeyboardButton("🔧 إعدادات المصنع", callback_data="adm_factory_settings"),
          types.InlineKeyboardButton("🚫 المحظورين", callback_data="adm_banned"))
    k.add(types.InlineKeyboardButton("📣 إضافة إعلان", callback_data="adm_add_announcement"),
          types.InlineKeyboardButton("🎟️ كوبونات", callback_data="adm_coupons"))
    k.add(types.InlineKeyboardButton("📅 رسائل مجدولة", callback_data="adm_scheduled"),
          types.InlineKeyboardButton("💎 ترقية VIP", callback_data="adm_vip"))
    k.add(types.InlineKeyboardButton("🗂️ سجل النشاط", callback_data="adm_logs"),
          types.InlineKeyboardButton("🏪 متجر المصنع", callback_data="adm_factory_store"))
    k.add(types.InlineKeyboardButton("⚙️ الإعدادات", callback_data="adm_settings"),
          types.InlineKeyboardButton("💳 إدارة الخطط", callback_data="adm_plans"))
    k.add(types.InlineKeyboardButton("🔄 إعادة تشغيل البوتات", callback_data="adm_restart_bots"),
          types.InlineKeyboardButton("📤 تصدير البيانات", callback_data="adm_export"))
    return k

def _plans_kb():
    k = types.InlineKeyboardMarkup(row_width=1)
    plans = [
        ("🥉 شهري - 100⭐ | 30 يوم | 3 بوتات", "month", 100),
        ("🥈 3 أشهر - 250⭐ | وفر 50⭐ | 5 بوتات", "3m", 250),
        ("🥇 سنوي - 800⭐ | وفر 400⭐ | 10 بوتات", "year", 800),
        ("💎 مدى الحياة - 2000⭐ | لامحدود", "life", 2000)
    ]
    for t, d, p in plans:
        k.add(types.InlineKeyboardButton(t, callback_data=f"plan_{d}_{p}"))
    k.add(types.InlineKeyboardButton("🎟️ لدي كوبون خصم", callback_data="use_coupon"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return k

def _gen_payload():
    return hashlib.sha256(f"{time.time()}{random.randint(100000, 999999)}".encode()).hexdigest()[:20]

def _ensure_user(uid, uname, fname, lname=""):
    existing = db.f("SELECT 1 FROM users WHERE user_id=?", (uid,))
    if not existing:
        db.q("INSERT INTO users (user_id, username, first_name, last_name, join_date, last_seen) VALUES (?,?,?,?,?,?)",
             (uid, uname, fname, lname, datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat()))
        db.add_stars(uid, int(db.setting("welcome_bonus", "5")), "مكافأة التسجيل")
    else:
        db.q("UPDATE users SET username=?, first_name=?, last_name=?, last_seen=? WHERE user_id=?",
             (uname, fname, lname, datetime.datetime.now().isoformat(), uid))

def _is_banned(uid):
    r = db.f("SELECT banned FROM users WHERE user_id=?", (uid,))
    return r and r[0] == 1

def _anti_spam(uid):
    now = time.time()
    if uid not in user_message_times:
        user_message_times[uid] = []
    user_message_times[uid] = [t for t in user_message_times[uid] if now - t < SPAM_WINDOW]
    user_message_times[uid].append(now)
    return len(user_message_times[uid]) > SPAM_THRESHOLD

def _contains_banned_words(text):
    if not text:
        return False
    text_lower = text.lower()
    return any(w in text_lower for w in BANNED_WORDS)

def _check_bot_subscription(uid, channels, tb_instance=None):
    try:
        b = tb_instance or bot
        for ch in channels:
            m = b.get_chat_member(ch, uid)
            if m.status in ["left", "kicked"]:
                return False
        return True
    except:
        return False

def _bot_sub_kb(channels, bot_name="البوت"):
    k = types.InlineKeyboardMarkup(row_width=1)
    for ch in channels:
        name = ch.replace("@", "")
        k.add(types.InlineKeyboardButton(f"📢 {name}", url=f"https://t.me/{name}"))
    k.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_bot_sub"))
    return k

def _bot_upgrade_kb(bid, price=100):
    k = types.InlineKeyboardMarkup(row_width=1)
    k.add(types.InlineKeyboardButton(f"⭐ ترقية للبرو - {price} نجمة", callback_data=f"bot_upgrade_{bid}"))
    return k

def _ct_reply_kb(uid, mid):
    k = types.InlineKeyboardMarkup(row_width=3)
    k.add(types.InlineKeyboardButton("📨 رد", callback_data=f"reply_{uid}_{mid}"),
          types.InlineKeyboardButton("🚫 حظر", callback_data=f"ban_user_{uid}"),
          types.InlineKeyboardButton("👤 معلومات", callback_data=f"user_info_{uid}"))
    return k

def _owner_contact_kb():
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("📊 إحصائيات", callback_data="owner_stats"),
          types.InlineKeyboardButton("📢 إذاعة", callback_data="owner_broadcast"))
    k.add(types.InlineKeyboardButton("💰 سعر الاشتراك", callback_data="owner_set_plan"),
          types.InlineKeyboardButton("📢 قنوات إجبارية", callback_data="owner_set_channels"))
    k.add(types.InlineKeyboardButton("🎫 التذاكر", callback_data="owner_tickets"),
          types.InlineKeyboardButton("👥 المستخدمين", callback_data="owner_users"))
    k.add(types.InlineKeyboardButton("💳 المدفوعات", callback_data="owner_payments"),
          types.InlineKeyboardButton("🤖 AI Moderation", callback_data="owner_ai_moderation"))
    k.add(types.InlineKeyboardButton("⚡ ردود تلقائية", callback_data="owner_auto_reply"),
          types.InlineKeyboardButton("📋 الأوامر المخصصة", callback_data="owner_custom_cmds"))
    k.add(types.InlineKeyboardButton("🎟️ كوبونات", callback_data="owner_coupons"),
          types.InlineKeyboardButton("📣 إعلان", callback_data="owner_announce"))
    k.add(types.InlineKeyboardButton("🚫 المحظورين", callback_data="owner_banned"),
          types.InlineKeyboardButton("📈 التحليلات", callback_data="owner_analytics"))
    k.add(types.InlineKeyboardButton("🔑 إدارة المشرفين", callback_data="owner_admins"),
          types.InlineKeyboardButton("⚙️ الإعدادات", callback_data="owner_settings"))
    k.add(types.InlineKeyboardButton("📅 رسائل مجدولة", callback_data="owner_schedule"),
          types.InlineKeyboardButton("🏅 لوحة صدارة", callback_data="owner_leaderboard"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
    return k

def _owner_shop_kb():
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("📊 إحصائيات", callback_data="owner_stats"),
          types.InlineKeyboardButton("📢 إذاعة", callback_data="owner_broadcast"))
    k.add(types.InlineKeyboardButton("➕ إضافة سلعة", callback_data="sh_add_prod"),
          types.InlineKeyboardButton("📦 إدارة السلع", callback_data="sh_manage"))
    k.add(types.InlineKeyboardButton("💰 سعر الاشتراك", callback_data="owner_set_plan"),
          types.InlineKeyboardButton("📢 قنوات إجبارية", callback_data="owner_set_channels"))
    k.add(types.InlineKeyboardButton("💳 المدفوعات", callback_data="owner_payments"),
          types.InlineKeyboardButton("🎟️ كوبونات", callback_data="owner_coupons"))
    k.add(types.InlineKeyboardButton("🏆 لوحة الصدارة", callback_data="owner_leaderboard"),
          types.InlineKeyboardButton("📈 التحليلات", callback_data="owner_analytics"))
    k.add(types.InlineKeyboardButton("👥 المستخدمين", callback_data="owner_users"),
          types.InlineKeyboardButton("🚫 المحظورين", callback_data="owner_banned"))
    k.add(types.InlineKeyboardButton("📅 رسائل مجدولة", callback_data="owner_schedule"),
          types.InlineKeyboardButton("🔑 المشرفين", callback_data="owner_admins"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
    return k

def _owner_tempmail_kb():
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("📢 إذاعة", callback_data="tm_broadcast"),
          types.InlineKeyboardButton("📊 إحصائيات", callback_data="tm_stats"))
    k.add(types.InlineKeyboardButton("💰 سعر الاشتراك", callback_data="owner_set_plan"),
          types.InlineKeyboardButton("📢 قنوات إجبارية", callback_data="owner_set_channels"))
    k.add(types.InlineKeyboardButton("👥 المستخدمين", callback_data="tm_users"),
          types.InlineKeyboardButton("📈 التحليلات", callback_data="tm_analytics"))
    k.add(types.InlineKeyboardButton("🚫 المحظورين", callback_data="owner_banned"),
          types.InlineKeyboardButton("🎟️ كوبونات", callback_data="owner_coupons"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
    return k

def _sh_main_kb(uid=None, bot_id=None):
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("🛒 المتجر", callback_data="sh_products"))
    k.add(types.InlineKeyboardButton("🎁 المكافأة اليومية", callback_data="sh_daily"),
          types.InlineKeyboardButton("👥 إحالاتي", callback_data="sh_refs"))
    k.add(types.InlineKeyboardButton("💰 رصيدي", callback_data="sh_balance"),
          types.InlineKeyboardButton("🏆 الصدارة", callback_data="sh_leaderboard"))
    k.add(types.InlineKeyboardButton("🛍️ طلباتي", callback_data="sh_orders"),
          types.InlineKeyboardButton("❤️ المفضلة", callback_data="sh_wishlist"))
    k.add(types.InlineKeyboardButton("🎟️ كوبون خصم", callback_data="sh_coupon"),
          types.InlineKeyboardButton("📊 إحصائياتي", callback_data="sh_mystats"))
    return k

def _sh_back_kb():
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="sh_back"))
    return k

def _tm_svc_kb():
    k = types.InlineKeyboardMarkup(row_width=2)
    svcs = list(SVC_NAMES.items())
    for i in range(0, len(svcs), 2):
        row = [types.InlineKeyboardButton(svcs[i][1], callback_data=f"pick_{svcs[i][0]}")]
        if i + 1 < len(svcs):
            row.append(types.InlineKeyboardButton(svcs[i+1][1], callback_data=f"pick_{svcs[i+1][0]}"))
        k.add(*row)
    k.add(types.InlineKeyboardButton("🎲 عشوائي", callback_data="pick_random"))
    return k

def _tm_main_kb(email, svc):
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("📥 فحص البريد", callback_data=f"get_{svc}"),
          types.InlineKeyboardButton("🔄 تجديد", callback_data=f"ref_{svc}"))
    k.add(types.InlineKeyboardButton("📋 نسخ العنوان", callback_data=f"cp_{email}"),
          types.InlineKeyboardButton("🗑️ حذف البريد", callback_data="del"))
    k.add(types.InlineKeyboardButton("✉️ بريد جديد", callback_data="new"),
          types.InlineKeyboardButton("📊 معلوماتي", callback_data="me"))
    k.add(types.InlineKeyboardButton("⚙️ الخدمات", callback_data="svcs"),
          types.InlineKeyboardButton("🔔 تنبيه تلقائي", callback_data="auto_check"))
    return k


@bot.message_handler(commands=["start"])
def _start(m):
    uid = m.from_user.id
    _ensure_user(uid, m.from_user.username, m.from_user.first_name, m.from_user.last_name or "")
    if _is_banned(uid):
        bot.send_message(uid, "🚫 تم حظرك من استخدام البوت.")
        return
    if db.setting("maintenance") == "1" and uid != ADMIN_ID:
        bot.send_message(uid, "🔧 البوت في وضع الصيانة. جرب لاحقاً.")
        return
    parts = m.text.split()
    if len(parts) > 1:
        ref = parts[1]
        if ref.isdigit() and int(ref) != uid:
            ref_id = int(ref)
            existing_ref = db.f("SELECT 1 FROM referrals WHERE referred_id=? AND bot_id=0", (uid,))
            if not existing_ref:
                reward = int(db.setting("referral_reward", "10"))
                db.q("INSERT INTO referrals (referrer_id, referred_id, bot_id, reward, created_at, status) VALUES (?,?,0,?,?,?)",
                     (ref_id, uid, reward, datetime.datetime.now().isoformat(), "completed"))
                db.add_stars(ref_id, reward, f"إحالة جديدة - مستخدم {uid}")
                db.q("UPDATE users SET invited = invited + 1 WHERE user_id=?", (ref_id,))
                db.q("UPDATE users SET invited_by=? WHERE user_id=?", (ref_id, uid))
                db.notify(ref_id, "إحالة جديدة! 🎉", f"انضم مستخدم جديد برابطك! +{reward}⭐")
                try:
                    bot.send_message(ref_id, f"🎉 انضم مستخدم جديد برابطك!\n⭐ حصلت على {reward} نجمة!")
                except:
                    pass
    if uid == ADMIN_ID:
        u = db.f("SELECT COUNT(*) FROM users")[0]
        b = db.f("SELECT COUNT(*) FROM hosted_bots WHERE status='active'")[0]
        p = db.f("SELECT SUM(amount) FROM payments WHERE status='completed'")[0] or 0
        bot.send_message(uid,
            f"👑 مرحباً {DEV_NAME}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🤖 {BOT_NAME} v{VERSION}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👥 المستخدمين: {u}\n"
            f"🤖 البوتات النشطة: {b}\n"
            f"💰 الإيرادات: {p}⭐\n"
            f"━━━━━━━━━━━━━━━",
            reply_markup=_admin_kb()
        )
        return
    if not _chk_sub(uid):
        bot.send_message(uid,
            f"👋 أهلاً بك في {BOT_NAME}!\n\n"
            f"⚠️ يجب الاشتراك في القنوات التالية للمتابعة:",
            reply_markup=_sub_kb()
        )
        return
    u = db.f("SELECT first_name, sub_type, stars FROM users WHERE user_id=?", (uid,))
    name = u[0] if u else m.from_user.first_name
    bot.send_message(uid,
        f"🤖 {BOT_NAME} v{VERSION}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👋 أهلاً {name}!\n"
        f"🌟 الخطة: {PLAN_NAMES.get(u[1], 'مجاني') if u else 'مجاني'}\n"
        f"⭐ نجومك: {u[2] if u else 0}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔧 صنع بواسطة: {DEV_NAME}\n"
        f"📞 التواصل: {DEV_LINK}",
        reply_markup=_main_kb(uid)
    )


@bot.message_handler(commands=["admin"])
def _admin_cmd(m):
    if m.from_user.id != ADMIN_ID:
        return
    bot.send_message(ADMIN_ID, "👑 لوحة التحكم العليا", reply_markup=_admin_kb())


@bot.message_handler(commands=["id"])
def _id_cmd(m):
    bot.reply_to(m, f"🆔 معرفك: `{m.from_user.id}`", parse_mode="Markdown")


@bot.message_handler(commands=["ref"])
def _ref_cmd(m):
    uid = m.from_user.id
    me = bot.get_me()
    link = f"https://t.me/{me.username}?start={uid}"
    count = db.f("SELECT invited FROM users WHERE user_id=?", (uid,))[0] or 0
    bot.reply_to(m, f"👥 رابط إحالتك:\n`{link}`\n\n📊 إجمالي الإحالات: {count}", parse_mode="Markdown")


@bot.message_handler(commands=["stars"])
def _stars_cmd(m):
    uid = m.from_user.id
    r = db.f("SELECT stars FROM users WHERE user_id=?", (uid,))
    stars = r[0] if r else 0
    history = db.fa("SELECT amount, description, created_at FROM stars_transactions WHERE user_id=? ORDER BY id DESC LIMIT 5", (uid,))
    txt = f"⭐ نجومك: {stars}\n\n📜 آخر المعاملات:\n"
    for amt, desc, dt in history:
        sign = "+" if amt > 0 else ""
        txt += f"{sign}{amt}⭐ - {desc} | {dt[:10]}\n"
    bot.reply_to(m, txt)


@bot.message_handler(commands=["mybots"])
def _mybots_cmd(m):
    uid = m.from_user.id
    bots_list = db.fa("SELECT bot_name, bot_username, bot_type, status FROM hosted_bots WHERE owner_id=? ORDER BY id DESC", (uid,))
    if not bots_list:
        bot.reply_to(m, "❌ لا يوجد بوتات. اضغط إنشاء بوت من القائمة الرئيسية.")
        return
    txt = f"🤖 بوتاتك ({len(bots_list)}):\n━━━━━━━━━━━━━━━\n"
    for name, username, btype, status in bots_list:
        t = "📨" if btype == "contact" else "🛒" if btype == "shop" else "📧"
        s = "🟢" if status == "active" else "🔴"
        txt += f"{t} {s} @{username or name}\n"
    bot.reply_to(m, txt)


@bot.callback_query_handler(func=lambda c: c.data == "verify_bot_sub")
def _verify(c):
    uid = c.from_user.id
    if _chk_sub(uid):
        bot.answer_callback_query(c.id, "✅ تم التحقق!")
        u = db.f("SELECT first_name, sub_type, stars FROM users WHERE user_id=?", (uid,))
        bot.edit_message_text(
            f"🎉 تم التحقق بنجاح!\n\n🤖 {BOT_NAME} v{VERSION}\n👋 أهلاً {u[0] if u else ''}!",
            uid, c.message.message_id, reply_markup=_main_kb(uid)
        )
    else:
        bot.answer_callback_query(c.id, "❌ يجب الاشتراك في جميع القنوات أولاً!", show_alert=True)


@bot.callback_query_handler(func=lambda c: c.data == "back_main")
def _back(c):
    uid = c.from_user.id
    bot.edit_message_text(f"🏠 القائمة الرئيسية:", uid, c.message.message_id, reply_markup=_main_kb(uid))


@bot.callback_query_handler(func=lambda c: c.data == "upgrade")
def _upg(c):
    uid = c.from_user.id
    r = db.f("SELECT stars FROM users WHERE user_id=?", (uid,))
    stars = r[0] if r else 0
    bot.edit_message_text(
        f"⭐ اختر خطتك:\n\n"
        f"💰 نجومك الحالية: {stars}⭐\n\n"
        f"🥉 شهري: 100⭐ | 3 بوتات\n"
        f"🥈 3 أشهر: 250⭐ | 5 بوتات\n"
        f"🥇 سنوي: 800⭐ | 10 بوتات\n"
        f"💎 مدى الحياة: 2000⭐ | لامحدود",
        uid, c.message.message_id, reply_markup=_plans_kb()
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("plan_"))
def _plan(c):
    d = c.data.split("_")
    plan = d[1]
    price = int(d[2])
    uid = c.from_user.id
    payload = _gen_payload()
    db.q("INSERT INTO payments (user_id, amount, currency, plan, status, payload, created_at) VALUES (?,?,?,?,?,?,?)",
         (uid, price, "XTR", plan, "pending", payload, datetime.datetime.now().isoformat()))
    bot.send_invoice(uid,
        f"اشتراك {PLAN_NAMES.get(plan, plan)}",
        f"ترقية حسابك في {BOT_NAME} إلى {PLAN_NAMES.get(plan, plan)}\n\n✅ الصلاحيات الكاملة\n🤖 إنشاء بوتات متعددة\n⚡ دعم أولوية",
        payload, "", "XTR",
        [types.LabeledPrice(f"اشتراك {PLAN_NAMES.get(plan, plan)}", price)],
        start_parameter="sub"
    )


@bot.callback_query_handler(func=lambda c: c.data == "use_coupon")
def _use_coupon(c):
    uid = c.from_user.id
    msg = bot.send_message(uid, "🎟️ أرسل كود الكوبون:")
    bot.register_next_step_handler(msg, lambda m: _apply_factory_coupon(m, uid))


def _apply_factory_coupon(m, uid):
    code = m.text.strip().upper()
    coupon = db.f("SELECT id, discount_type, discount_value, max_uses, used_count, expires_at FROM coupons WHERE code=? AND bot_id=0 AND active=1", (code,))
    if not coupon:
        bot.send_message(uid, "❌ الكوبون غير صالح أو منتهي الصلاحية.", reply_markup=_plans_kb())
        return
    cid, dtype, dval, maxu, used, exp = coupon
    if exp and datetime.datetime.fromisoformat(exp) < datetime.datetime.now():
        bot.send_message(uid, "❌ انتهت صلاحية الكوبون.", reply_markup=_plans_kb())
        return
    if maxu > 0 and used >= maxu:
        bot.send_message(uid, "❌ تم استنفاد الكوبون.", reply_markup=_plans_kb())
        return
    db.q("UPDATE coupons SET used_count = used_count + 1 WHERE id=?", (cid,))
    if dtype == "percent":
        bot.send_message(uid, f"✅ كوبون صالح! خصم {dval}%\nاختر خطتك:", reply_markup=_plans_kb())
    else:
        bot.send_message(uid, f"✅ كوبون صالح! خصم {dval}⭐\nاختر خطتك:", reply_markup=_plans_kb())


@bot.pre_checkout_query_handler(func=lambda q: True)
def _checkout(q):
    bot.answer_pre_checkout_query(q.id, ok=True)


@bot.message_handler(content_types=["successful_payment"])
def _pay(m):
    uid = m.from_user.id
    p = m.successful_payment
    db.q("UPDATE payments SET status='completed' WHERE payload=?", (p.invoice_payload,))
    pay = db.f("SELECT plan, bot_id FROM payments WHERE payload=?", (p.invoice_payload,))
    if not pay:
        return
    plan, bot_id = pay
    if bot_id == 0:
        if plan.startswith("stars_"):
            amount = int(plan.split("_")[1])
            db.add_stars(uid, amount, "شراء نجوم")
            bot.send_message(uid, f"✅ تم إضافة {amount}⭐ لحسابك!", reply_markup=_main_kb(uid))
            return
        if plan == "life":
            exp = "lifetime"
        else:
            days = PLAN_DAYS.get(plan, 30)
            exp = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()
        db.q("UPDATE users SET sub_type=?, sub_expiry=? WHERE user_id=?", (plan, exp, uid))
        pname = PLAN_NAMES.get(plan, plan)
        bot.send_message(uid,
            f"✅ تم الدفع بنجاح!\n\n"
            f"🌟 الخطة: {pname}\n"
            f"📅 الانتهاء: {'مدى الحياة' if exp == 'lifetime' else exp[:10]}\n\n"
            f"شكراً لاشتراكك! 🎉",
            reply_markup=_main_kb(uid)
        )
        db.notify(uid, "تم الاشتراك! 🎉", f"اشتراكك في {pname} تم تفعيله.")
        db.log(0, "payment", f"user={uid} plan={plan} amount={p.total_amount}", uid)
        try:
            bot.send_message(ADMIN_ID,
                f"💰 دفع جديد!\n👤 المستخدم: {uid}\n📦 الخطة: {pname}\n⭐ المبلغ: {p.total_amount}\n📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
        except:
            pass
    else:
        if plan == "bot_premium":
            db.q("UPDATE bot_subscribers SET sub_type='premium', sub_expiry=? WHERE user_id=? AND bot_id=?",
                 ((datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(), uid, bot_id))
            bot.send_message(uid, "✅ تم تفعيل اشتراك البرو في البوت! 🎉")


@bot.callback_query_handler(func=lambda c: c.data == "my_acc")
def _acc(c):
    uid = c.from_user.id
    r = db.f("SELECT sub_type, sub_expiry, stars, invited, first_name, join_date, total_messages, vip FROM users WHERE user_id=?", (uid,))
    if r:
        st, exp, stars, inv, fname, jdate, msgs, vip = r
        bc = db.f("SELECT COUNT(*) FROM hosted_bots WHERE owner_id=?", (uid,))
        bots_count = bc[0] if bc else 0
        me = bot.get_me()
        ref_link = f"https://t.me/{me.username}?start={uid}"
        k = types.InlineKeyboardMarkup(row_width=2)
        k.add(types.InlineKeyboardButton("🔄 تجديد الاشتراك", callback_data="upgrade"),
              types.InlineKeyboardButton("🎁 المكافأة اليومية", callback_data="daily_stars"))
        k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        bot.edit_message_text(
            f"👤 حسابك في {BOT_NAME}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🆔 المعرف: {uid}\n"
            f"👤 الاسم: {fname}\n"
            f"{'💎 VIP' if vip else ''}\n"
            f"🌟 الخطة: {PLAN_NAMES.get(st, 'مجاني')}\n"
            f"📅 تنتهي: {'مدى الحياة' if exp == 'lifetime' else (exp[:10] if exp else 'لا يوجد')}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"⭐ النجوم: {stars}\n"
            f"🤖 البوتات: {bots_count}/{BOT_LIMITS.get(st, 0)}\n"
            f"👥 الإحالات: {inv}\n"
            f"📅 تاريخ الانضمام: {jdate[:10] if jdate else 'غير معروف'}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🔗 رابط إحالتك:\n`{ref_link}`",
            uid, c.message.message_id,
            reply_markup=k,
            parse_mode="Markdown"
        )


@bot.callback_query_handler(func=lambda c: c.data == "my_stars")
def _stars_cb(c):
    uid = c.from_user.id
    r = db.f("SELECT stars FROM users WHERE user_id=?", (uid,))
    stars = r[0] if r else 0
    history = db.fa("SELECT amount, description, created_at FROM stars_transactions WHERE user_id=? ORDER BY id DESC LIMIT 10", (uid,))
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("💳 شراء نجوم", callback_data="buy_stars"),
          types.InlineKeyboardButton("🎁 هدية يومية", callback_data="daily_stars"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    txt = f"⭐ نجومك: {stars}\n\n📜 آخر المعاملات:\n━━━━━━━━━━\n"
    for amt, desc, dt in history:
        sign = "+" if amt > 0 else ""
        emoji = "🟢" if amt > 0 else "🔴"
        txt += f"{emoji} {sign}{amt}⭐ | {desc}\n📅 {dt[:10]}\n━━━━━━━━━━\n"
    bot.edit_message_text(txt, uid, c.message.message_id, reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data == "daily_stars")
def _daily_stars(c):
    uid = c.from_user.id
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    r = db.f("SELECT daily_bonus_date FROM users WHERE user_id=?", (uid,))
    last = r[0] if r else None
    if last and last == today:
        bot.answer_callback_query(c.id, "❌ استلمت مكافأتك اليوم! عد غداً.", show_alert=True)
        return
    bonus = int(db.setting("daily_bonus", "10"))
    db.q("UPDATE users SET daily_bonus_date=? WHERE user_id=?", (today, uid))
    db.add_stars(uid, bonus, "المكافأة اليومية")
    bot.answer_callback_query(c.id, f"✅ حصلت على {bonus}⭐ مكافأة يومية!", show_alert=True)


@bot.callback_query_handler(func=lambda c: c.data == "buy_stars")
def _buy_stars_cb(c):
    uid = c.from_user.id
    k = types.InlineKeyboardMarkup(row_width=2)
    packs = [("50⭐", 50), ("100⭐", 100), ("250⭐", 250),
             ("500⭐", 500), ("1000⭐", 1000), ("2000⭐", 2000)]
    for label, amount in packs:
        k.add(types.InlineKeyboardButton(f"{label}", callback_data=f"buypack_{amount}"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="my_stars"))
    bot.edit_message_text("💳 اختر حزمة النجوم:", uid, c.message.message_id, reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data.startswith("buypack_"))
def _buypack(c):
    uid = c.from_user.id
    amount = int(c.data.split("_")[1])
    payload = _gen_payload()
    db.q("INSERT INTO payments (user_id, amount, currency, plan, status, payload, created_at) VALUES (?,?,?,?,?,?,?)",
         (uid, amount, "XTR", f"stars_{amount}", "pending", payload, datetime.datetime.now().isoformat()))
    bot.send_invoice(uid,
        f"شراء {amount} نجمة",
        f"إضافة {amount}⭐ إلى رصيد نجومك في {BOT_NAME}",
        payload, "", "XTR",
        [types.LabeledPrice(f"{amount} نجمة", amount)],
        start_parameter="stars"
    )


@bot.callback_query_handler(func=lambda c: c.data == "referrals")
def _referrals(c):
    uid = c.from_user.id
    me = bot.get_me()
    link = f"https://t.me/{me.username}?start={uid}"
    count = db.f("SELECT invited FROM users WHERE user_id=?", (uid,))[0] or 0
    reward = db.setting("referral_reward", "10")
    refs = db.fa("SELECT r.referred_id, u.first_name, r.created_at FROM referrals r JOIN users u ON r.referred_id=u.user_id WHERE r.referrer_id=? AND r.bot_id=0 ORDER BY r.id DESC LIMIT 10", (uid,))
    txt = f"👥 نظام الإحالات\n━━━━━━━━━━━━━━━\n🔗 رابطك:\n`{link}`\n\n📊 عدد الإحالات: {count}\n💰 مكافأة لكل إحالة: {reward}⭐\n\n"
    if refs:
        txt += "📋 آخر الإحالات:\n"
        for rid, rname, rdt in refs:
            txt += f"👤 {rname} | 📅 {rdt[:10]}\n"
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton("📤 مشاركة الرابط", url=f"https://t.me/share/url?url={link}&text=انضم+معي+في+{BOT_NAME}"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    bot.edit_message_text(txt, uid, c.message.message_id, reply_markup=k, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda c: c.data == "announcements")
def _announcements(c):
    uid = c.from_user.id
    now = datetime.datetime.now().isoformat()
    anns = db.fa("SELECT title, content, created_at FROM announcements WHERE bot_id=0 AND active=1 AND (expires_at IS NULL OR expires_at > ?) ORDER BY id DESC LIMIT 5", (now,))
    if not anns:
        bot.answer_callback_query(c.id, "❌ لا يوجد إعلانات حالياً.", show_alert=True)
        return
    txt = "📢 الإعلانات\n━━━━━━━━━━━━━━━\n"
    for title, content, dt in anns:
        txt += f"📌 {title}\n{content}\n📅 {dt[:10]}\n━━━━━━━━━━━━━━━\n"
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    bot.edit_message_text(txt, uid, c.message.message_id, reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data == "my_notifications")
def _notifications(c):
    uid = c.from_user.id
    notifs = db.fa("SELECT title, message, read, created_at FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 15", (uid,))
    db.q("UPDATE notifications SET read=1 WHERE user_id=?", (uid,))
    if not notifs:
        bot.answer_callback_query(c.id, "❌ لا يوجد إشعارات.", show_alert=True)
        return
    txt = "🔔 إشعاراتك\n━━━━━━━━━━━━━━━\n"
    for title, msg, read, dt in notifs:
        emoji = "🔴" if not read else "⚪"
        txt += f"{emoji} {title}\n{msg}\n📅 {dt[:10]}\n━━━━━━━━━━━━━━━\n"
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    bot.edit_message_text(txt, uid, c.message.message_id, reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data == "bot_store")
def _bot_store(c):
    uid = c.from_user.id
    bots_list = db.fa("SELECT id, bot_name, bot_username, bot_type, description, total_users FROM hosted_bots WHERE status='active' LIMIT 20")
    if not bots_list:
        bot.answer_callback_query(c.id, "❌ لا يوجد بوتات معروضة.", show_alert=True)
        return
    txt = "🏪 متجر البوتات\n━━━━━━━━━━━━━━━\n"
    k = types.InlineKeyboardMarkup(row_width=1)
    for bid, name, username, btype, desc, users in bots_list:
        t = "📨" if btype == "contact" else "🛒" if btype == "shop" else "📧"
        txt += f"{t} @{username or name}\n👥 {users} مستخدم\n📝 {desc or 'لا يوجد وصف'}\n━━━━━━━━━━━━━━━\n"
        if username:
            k.add(types.InlineKeyboardButton(f"{t} @{username}", url=f"https://t.me/{username}"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    bot.edit_message_text(txt, uid, c.message.message_id, reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data == "create_bot")
def _create(c):
    uid = c.from_user.id
    sub = db.f("SELECT sub_type FROM users WHERE user_id=?", (uid,))
    st = sub[0] if sub else "free"
    if st == "free":
        bot.answer_callback_query(c.id, "❌ يتطلب اشتراك برو لإنشاء بوتات!", show_alert=True)
        return
    max_bots = BOT_LIMITS.get(st, 0)
    bc = db.f("SELECT COUNT(*) FROM hosted_bots WHERE owner_id=? AND status='active'", (uid,))
    current = bc[0] if bc else 0
    if max_bots != 999 and current >= max_bots:
        bot.answer_callback_query(c.id, f"❌ وصلت للحد الأقصى ({max_bots} بوتات) لخطتك!", show_alert=True)
        return
    k = types.InlineKeyboardMarkup(row_width=1)
    k.add(types.InlineKeyboardButton("📨 بوت تواصل مع الإدارة", callback_data="type_contact"),
          types.InlineKeyboardButton("🛒 بوت متجر إلكتروني", callback_data="type_shop"),
          types.InlineKeyboardButton("📧 بوت إيميلات وهمية", callback_data="type_tempmail"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    bot.edit_message_text(
        f"🤖 إنشاء بوت جديد\n━━━━━━━━━━━━━━━\n"
        f"📊 بوتاتك: {current}/{max_bots}\n\n"
        f"اختر نوع البوت:",
        uid, c.message.message_id, reply_markup=k
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("type_"))
def _type_sel(c):
    uid = c.from_user.id
    btype = c.data.split("_")[1]
    type_names = {"contact": "تواصل 📨", "shop": "متجر 🛒", "tempmail": "إيميلات 📧"}
    msg = bot.send_message(uid,
        f"🤖 إنشاء بوت {type_names.get(btype, btype)}\n\n"
        f"📝 الخطوات:\n"
        f"1️⃣ اذهب إلى @BotFather\n"
        f"2️⃣ أرسل /newbot\n"
        f"3️⃣ اختر اسماً ومعرفاً للبوت\n"
        f"4️⃣ انسخ التوكن وأرسله هنا\n\n"
        f"📤 أرسل التوكن الآن:"
    )
    bot.register_next_step_handler(msg, lambda m: _proc_token(m, btype))


def _proc_token(m, btype):
    uid = m.from_user.id
    token = m.text.strip()
    if not re.match(r"^\d+:[A-Za-z0-9_-]{35,}$", token):
        bot.send_message(uid, "❌ صيغة التوكن غير صحيحة! يجب أن يكون بصيغة: 123456:ABCdef...", reply_markup=_main_kb(uid))
        return
    existing = db.f("SELECT 1 FROM hosted_bots WHERE bot_token=?", (token,))
    if existing:
        bot.send_message(uid, "❌ هذا التوكن مستخدم مسبقاً!", reply_markup=_main_kb(uid))
        return
    try:
        tb = telebot.TeleBot(token)
        me = tb.get_me()
        force_ch = json.dumps(REQUIRED_CHANNELS)
        default_welcome = f"👋 أهلاً بك!\n\n🔧 صنع بواسطة: {DEV_NAME}\n📞 {DEV_LINK}"
        db.q(
            "INSERT INTO hosted_bots (owner_id, bot_token, bot_type, bot_name, bot_username, created_at, admin_id, settings, force_channels, welcome_msg) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (uid, token, btype, me.first_name, me.username, datetime.datetime.now().isoformat(), uid, "{}", force_ch, default_welcome)
        )
        bid = db.f("SELECT id FROM hosted_bots WHERE bot_token=?", (token,))[0]
        db.log(bid, "created", f"owner={uid} type={btype}", uid)
        bot.send_message(uid,
            f"✅ تم إنشاء البوت بنجاح!\n\n"
            f"🤖 الاسم: {me.first_name}\n"
            f"📛 المعرف: @{me.username}\n"
            f"📦 النوع: {btype}\n\n"
            f"⚡ جاري تشغيل البوت...",
            reply_markup=_main_kb(uid)
        )
        _launch_bot(token, btype, uid)
    except telebot.apihelper.ApiTelegramException as e:
        if "Unauthorized" in str(e):
            bot.send_message(uid, "❌ التوكن غير صالح أو محذوف من BotFather!", reply_markup=_main_kb(uid))
        else:
            bot.send_message(uid, f"❌ خطأ: {e}", reply_markup=_main_kb(uid))
    except Exception as e:
        bot.send_message(uid, f"❌ خطأ غير متوقع: {e}", reply_markup=_main_kb(uid))


def _launch_bot(token, btype, owner_id):
    if token in active_bots:
        return
    try:
        tb = telebot.TeleBot(token)
        active_bots[token] = tb
        settings = db.f("SELECT force_channels, bot_plan_price, bot_plan_type, admin_id FROM hosted_bots WHERE bot_token=?", (token,))
        force_ch = json.loads(settings[0]) if settings and settings[0] else REQUIRED_CHANNELS
        plan_price = settings[1] if settings else 0
        plan_type = settings[2] if settings else "free"
        admin_id = settings[3] if settings else owner_id
        if btype == "contact":
            _setup_contact(tb, admin_id, force_ch, plan_price, plan_type)
        elif btype == "shop":
            _setup_shop(tb, admin_id, force_ch, plan_price, plan_type)
        elif btype == "tempmail":
            _setup_tempmail(tb, admin_id, force_ch, plan_price, plan_type)
        t = threading.Thread(target=lambda: _safe_polling(tb, token), daemon=True)
        t.start()
        logger.info(f"Bot launched: {token[:20]}... type={btype}")
    except Exception as e:
        logger.error(f"Launch bot error: {e}")
        if token in active_bots:
            del active_bots[token]


def _safe_polling(tb, token):
    while True:
        try:
            tb.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            logger.error(f"Polling error for {token[:20]}: {e}")
            time.sleep(15)


def _get_auto_reply(bot_id, trigger):
    r = db.f("SELECT response FROM auto_replies WHERE bot_id=? AND trigger=? AND active=1", (bot_id, trigger.lower()))
    if r:
        db.q("UPDATE auto_replies SET uses = uses + 1 WHERE bot_id=? AND trigger=?", (bot_id, trigger.lower()))
        return r[0]
    return None


def _owner_broadcast_fn(m, tb, bot_id, admin_id, btype):
    table = "bot_subscribers" if btype in ["contact", "tempmail"] else "shop_users"
    users = db.fa(f"SELECT user_id FROM {table} WHERE bot_id=?", (bot_id,))
    s = f = 0
    for u in users:
        try:
            if m.content_type == "text":
                tb.send_message(u[0], m.text)
            elif m.content_type == "photo":
                tb.send_photo(u[0], m.photo[-1].file_id, caption=m.caption)
            elif m.content_type == "video":
                tb.send_video(u[0], m.video.file_id, caption=m.caption)
            s += 1
            time.sleep(0.05)
        except:
            f += 1
    kb = _owner_contact_kb() if btype == "contact" else _owner_shop_kb() if btype == "shop" else _owner_tempmail_kb()
    tb.send_message(admin_id, f"📢 الإذاعة اكتملت\n✅ نجح: {s}\n❌ فشل: {f}", reply_markup=kb)


def _set_plan_fn(m, tb, admin_id, bot_id, kb_fn=None):
    try:
        price = int(m.text.strip())
        ptype = "free" if price == 0 else "premium"
        db.q("UPDATE hosted_bots SET bot_plan_price=?, bot_plan_type=? WHERE id=?", (price, ptype, bot_id))
        kb = kb_fn() if kb_fn else _owner_contact_kb()
        tb.send_message(admin_id, f"✅ تم تحديث خطة الاشتراك\n💰 السعر: {price}⭐\n📦 {'مجاني' if ptype=='free' else 'مدفوع'}", reply_markup=kb)
    except:
        tb.send_message(admin_id, "❌ أرسل رقماً صحيحاً")


def _set_channels_fn(m, tb, admin_id, bot_id, kb_fn=None):
    try:
        text = m.text.strip()
        kb = kb_fn() if kb_fn else _owner_contact_kb()
        if text == "0":
            db.q("UPDATE hosted_bots SET force_channels='[]' WHERE id=?", (bot_id,))
            tb.send_message(admin_id, "✅ تم إلغاء الاشتراك الإجباري", reply_markup=kb)
        else:
            chs = [c.strip() for c in text.split(",") if c.strip()]
            chs = [c if c.startswith("@") else f"@{c}" for c in chs]
            db.q("UPDATE hosted_bots SET force_channels=? WHERE id=?", (json.dumps(chs), bot_id))
            tb.send_message(admin_id, f"✅ تم تحديث القنوات الإجبارية\n📢 {len(chs)} قناة:\n{', '.join(chs)}", reply_markup=kb)
    except:
        tb.send_message(admin_id, "❌ خطأ في الصيغة")


def _add_auto_reply_fn(m, tb, bot_id, admin_id, kb_fn=None):
    try:
        kw, reply = m.text.split("|", 1)
        db.q("INSERT INTO auto_replies (bot_id, trigger, response, created_at) VALUES (?,?,?,?)",
             (bot_id, kw.strip().lower(), reply.strip(), datetime.datetime.now().isoformat()))
        kb = kb_fn() if kb_fn else _owner_contact_kb()
        tb.send_message(admin_id, f"✅ تم إضافة الرد التلقائي\n🔑 {kw.strip()}\n💬 {reply.strip()}", reply_markup=kb)
    except:
        tb.send_message(admin_id, "❌ خطأ في الصيغة. استخدم: كلمة|الرد")


def _del_auto_reply(m, tb, bot_id, admin_id, kb_fn=None):
    trigger = m.text.strip().lower()
    db.q("UPDATE auto_replies SET active=0 WHERE bot_id=? AND trigger=?", (bot_id, trigger))
    kb = kb_fn() if kb_fn else _owner_contact_kb()
    tb.send_message(admin_id, f"✅ تم حذف الرد التلقائي لـ: {trigger}", reply_markup=kb)


def _create_coupon(m, tb, bot_id, admin_id, kb_fn=None):
    try:
        parts = m.text.strip().split("|")
        code, dtype, dval, maxu = parts[0].strip().upper(), parts[1].strip(), int(parts[2]), int(parts[3])
        exp = (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
        db.q("INSERT INTO coupons (bot_id, code, discount_type, discount_value, max_uses, expires_at, created_at) VALUES (?,?,?,?,?,?,?)",
             (bot_id, code, dtype, dval, maxu, exp, datetime.datetime.now().isoformat()))
        kb = kb_fn() if kb_fn else _owner_contact_kb()
        tb.send_message(admin_id, f"✅ تم إنشاء الكوبون\n🎟️ الكود: {code}\n💰 الخصم: {dval}{'%' if dtype=='percent' else '⭐'}\n🔢 الاستخدامات: {maxu}", reply_markup=kb)
    except:
        tb.send_message(admin_id, "❌ خطأ في الصيغة. استخدم: كود|نوع|قيمة|عدد")


def _owner_announce(m, tb, bot_id, admin_id, btype="contact"):
    users = db.fa("SELECT user_id FROM bot_subscribers WHERE bot_id=?", (bot_id,))
    s = f = 0
    for u in users:
        try:
            tb.send_message(u[0], f"📣 إعلان:\n\n{m.text}")
            s += 1
            time.sleep(0.05)
        except:
            f += 1
    db.q("INSERT INTO announcements (bot_id, title, content, created_at, active) VALUES (?,?,?,?,1)",
         (bot_id, "إعلان", m.text, datetime.datetime.now().isoformat()))
    kb = _owner_contact_kb() if btype == "contact" else _owner_shop_kb() if btype == "shop" else _owner_tempmail_kb()
    tb.send_message(admin_id, f"✅ تم الإرسال\n📤 نجح: {s}\n❌ فشل: {f}", reply_markup=kb)


def _unban_user_fn(m, tb, bot_id, admin_id, kb_fn=None):
    try:
        uid_unban = int(m.text.strip())
        db.q("UPDATE bot_subscribers SET banned=0 WHERE user_id=? AND bot_id=?", (uid_unban, bot_id))
        kb = kb_fn() if kb_fn else _owner_contact_kb()
        tb.send_message(admin_id, f"✅ تم رفع حظر {uid_unban}", reply_markup=kb)
        try:
            tb.send_message(uid_unban, "✅ تم رفع حظرك! يمكنك استخدام البوت الآن.")
        except:
            pass
    except:
        tb.send_message(admin_id, "❌ معرف غير صالح")


def _set_welcome(m, tb, bot_id, admin_id, kb_fn=None):
    db.q("UPDATE hosted_bots SET welcome_msg=? WHERE id=?", (m.text, bot_id))
    kb = kb_fn() if kb_fn else _owner_contact_kb()
    tb.send_message(admin_id, "✅ تم تحديث رسالة الترحيب", reply_markup=kb)


def _add_custom_cmd(m, tb, bot_id, admin_id, kb_fn=None):
    try:
        cmd, resp = m.text.split("|", 1)
        sett = db.f("SELECT settings FROM hosted_bots WHERE id=?", (bot_id,))
        data = json.loads(sett[0]) if sett and sett[0] else {}
        if "custom_cmds" not in data:
            data["custom_cmds"] = {}
        data["custom_cmds"][cmd.strip()] = resp.strip()
        db.q("UPDATE hosted_bots SET settings=? WHERE id=?", (json.dumps(data), bot_id))
        kb = kb_fn() if kb_fn else _owner_contact_kb()
        tb.send_message(admin_id, f"✅ تم إضافة الأمر المخصص\n{cmd.strip()} → {resp.strip()}", reply_markup=kb)
    except:
        tb.send_message(admin_id, "❌ خطأ في الصيغة. استخدم: /أمر|الرد")


def _add_admin_fn(m, tb, bot_id, admin_id, kb_fn=None):
    try:
        new_admin = int(m.text.strip())
        sett = db.f("SELECT settings FROM hosted_bots WHERE id=?", (bot_id,))
        data = json.loads(sett[0]) if sett and sett[0] else {}
        if "admins" not in data:
            data["admins"] = []
        if new_admin not in data["admins"]:
            data["admins"].append(new_admin)
        db.q("UPDATE hosted_bots SET settings=? WHERE id=?", (json.dumps(data), bot_id))
        kb = kb_fn() if kb_fn else _owner_contact_kb()
        tb.send_message(admin_id, f"✅ تم إضافة المشرف {new_admin}", reply_markup=kb)
    except:
        tb.send_message(admin_id, "❌ معرف غير صالح")


def _owner_schedule_fn(m, tb, bot_id, admin_id, kb_fn=None):
    try:
        parts = m.text.strip().split("|")
        msg_text = parts[0].strip()
        delay_mins = int(parts[1].strip()) if len(parts) > 1 else 60
        scheduled_at = (datetime.datetime.now() + datetime.timedelta(minutes=delay_mins)).isoformat()
        db.q("INSERT INTO scheduled_messages (bot_id, message, scheduled_at, created_at) VALUES (?,?,?,?)",
             (bot_id, msg_text, scheduled_at, datetime.datetime.now().isoformat()))
        kb = kb_fn() if kb_fn else _owner_contact_kb()
        tb.send_message(admin_id, f"✅ تم جدولة الرسالة\n⏰ ستُرسل خلال {delay_mins} دقيقة", reply_markup=kb)
    except:
        tb.send_message(admin_id, "❌ الصيغة: الرسالة|الوقت_بالدقائق")


def _setup_contact(tb, admin_id, force_channels, plan_price, plan_type):
    bot_data = db.f("SELECT id, welcome_msg, settings FROM hosted_bots WHERE admin_id=? AND bot_type='contact'", (admin_id,))
    bot_id = bot_data[0] if bot_data else 0
    welcome_msg = bot_data[1] if bot_data else f"👋 أهلاً بك!\n{DEV_LINK}"

    @tb.message_handler(commands=["start"])
    def _cs(m):
        uid = m.from_user.id
        if not db.f("SELECT 1 FROM bot_subscribers WHERE user_id=? AND bot_id=?", (uid, bot_id)):
            db.q("INSERT INTO bot_subscribers (user_id, bot_id, sub_type, join_date, last_seen) VALUES (?,?,?,?,?)",
                 (uid, bot_id, "free", datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat()))
            db.q("UPDATE hosted_bots SET total_users = total_users + 1 WHERE id=?", (bot_id,))
        else:
            db.q("UPDATE bot_subscribers SET last_seen=? WHERE user_id=? AND bot_id=?",
                 (datetime.datetime.now().isoformat(), uid, bot_id))
        if uid == admin_id:
            stats = db.f("SELECT total_users, total_revenue FROM hosted_bots WHERE id=?", (bot_id,))
            uc = stats[0] if stats else 0
            tb.send_message(uid, f"👑 لوحة تحكم البوت\n👥 المشتركين: {uc}", reply_markup=_owner_contact_kb())
            return
        blocked = db.f("SELECT 1 FROM bot_subscribers WHERE user_id=? AND bot_id=? AND banned=1", (uid, bot_id))
        if blocked:
            tb.send_message(uid, "🚫 تم حظرك من هذا البوت.")
            return
        if not _check_bot_subscription(uid, force_channels, tb):
            tb.send_message(uid, "👋 أهلاً بك!\n\n⚠️ يجب الاشتراك في القنوات التالية:", reply_markup=_bot_sub_kb(force_channels))
            return
        sub = db.f("SELECT sub_type FROM bot_subscribers WHERE user_id=? AND bot_id=?", (uid, bot_id))
        if plan_type != "free" and (not sub or sub[0] == "free"):
            tb.send_message(uid, f"⭐ هذا البوت يتطلب اشتراك مدفوع\n💰 السعر: {plan_price} نجمة", reply_markup=_bot_upgrade_kb(bot_id, plan_price))
            return
        ar = _get_auto_reply(bot_id, "start")
        tb.send_message(uid, ar if ar else welcome_msg)

    @tb.message_handler(commands=["help"])
    def _help(m):
        tb.send_message(m.chat.id,
            f"📋 المساعدة\n━━━━━━━━━━━━━━━\n"
            f"📨 لإرسال رسالة للإدارة: أرسل رسالتك مباشرة\n"
            f"🎫 لفتح تذكرة دعم: /ticket\n"
            f"📊 معلوماتي: /info\n\n"
            f"🔧 {DEV_NAME} | {DEV_LINK}"
        )

    @tb.message_handler(commands=["ticket"])
    def _ticket_cmd(m):
        uid = m.from_user.id
        if uid == admin_id:
            return
        msg = tb.send_message(uid, "🎫 إنشاء تذكرة دعم\n\n📝 أرسل عنوان المشكلة:")
        tb.register_next_step_handler(msg, lambda msg2: _create_ticket(msg2, uid))

    def _create_ticket(m, uid):
        title = m.text[:100]
        ticket_id = db.q("INSERT INTO tickets (bot_id, user_id, title, created_at) VALUES (?,?,?,?)",
                          (bot_id, uid, title, datetime.datetime.now().isoformat())).lastrowid
        db.q("INSERT INTO ticket_replies (ticket_id, user_id, message, created_at) VALUES (?,?,?,?)",
             (ticket_id, uid, title, datetime.datetime.now().isoformat()))
        tb.send_message(uid, f"✅ تم فتح التذكرة #{ticket_id}\nسيتم الرد قريباً!")
        try:
            k = types.InlineKeyboardMarkup()
            k.add(types.InlineKeyboardButton(f"📨 رد على #T{ticket_id}", callback_data=f"reply_ticket_{ticket_id}_{uid}"))
            tb.send_message(admin_id, f"🎫 تذكرة جديدة #{ticket_id}\n👤 المستخدم: {uid}\n📝 {title}", reply_markup=k)
        except:
            pass

    @tb.message_handler(commands=["info"])
    def _info_cmd(m):
        uid = m.from_user.id
        r = db.f("SELECT sub_type, join_date, total_messages FROM bot_subscribers WHERE user_id=? AND bot_id=?", (uid, bot_id))
        if r:
            tb.send_message(uid, f"📊 معلوماتك\n🌟 الاشتراك: {r[0]}\n📅 الانضمام: {r[1][:10] if r[1] else 'غير معروف'}\n📨 الرسائل: {r[2]}")

    @tb.callback_query_handler(func=lambda c: c.data == "check_bot_sub")
    def _cb_sub(c):
        uid = c.from_user.id
        if _check_bot_subscription(uid, force_channels, tb):
            tb.answer_callback_query(c.id, "✅ تم التحقق!")
            sub = db.f("SELECT sub_type FROM bot_subscribers WHERE user_id=? AND bot_id=?", (uid, bot_id))
            if plan_type != "free" and (not sub or sub[0] == "free"):
                tb.send_message(uid, f"⭐ يتطلب اشتراك مدفوع\n💰 {plan_price} نجمة", reply_markup=_bot_upgrade_kb(bot_id, plan_price))
            else:
                tb.send_message(uid, "🎉 مرحباً! يمكنك الآن استخدام البوت.")
        else:
            tb.answer_callback_query(c.id, "❌ اشترك في جميع القنوات أولاً!", show_alert=True)

    @tb.callback_query_handler(func=lambda c: c.data.startswith("bot_upgrade_"))
    def _bot_upg(c):
        uid = c.from_user.id
        price = plan_price or 100
        payload = _gen_payload()
        db.q("INSERT INTO payments (user_id, bot_id, amount, currency, plan, status, payload, created_at) VALUES (?,?,?,?,?,?,?,?)",
             (uid, bot_id, price, "XTR", "bot_premium", "pending", payload, datetime.datetime.now().isoformat()))
        tb.send_invoice(uid, "اشتراك البوت", "ترقية للبرو", payload, "", "XTR",
                        [types.LabeledPrice("الاشتراك", price)], start_parameter="bot_sub")

    @tb.callback_query_handler(func=lambda c: c.data.startswith("reply_ticket_"))
    def _reply_ticket(c):
        if c.from_user.id != admin_id:
            return
        parts = c.data.split("_")
        tid = int(parts[2])
        tuid = int(parts[3])
        msg = tb.send_message(admin_id, f"✍️ اكتب ردك على التذكرة #{tid}:")
        tb.register_next_step_handler(msg, lambda m: _send_ticket_reply(m, tid, tuid))

    def _send_ticket_reply(m, tid, tuid):
        db.q("INSERT INTO ticket_replies (ticket_id, user_id, is_admin, message, created_at) VALUES (?,?,1,?,?)",
             (tid, admin_id, m.text, datetime.datetime.now().isoformat()))
        db.q("UPDATE tickets SET status='replied' WHERE id=?", (tid,))
        try:
            tb.send_message(tuid, f"📨 رد على تذكرتك #{tid}:\n\n{m.text}")
            tb.send_message(admin_id, f"✅ تم الرد على التذكرة #{tid}", reply_markup=_owner_contact_kb())
        except:
            tb.send_message(admin_id, "❌ فشل إرسال الرد", reply_markup=_owner_contact_kb())

    @tb.callback_query_handler(func=lambda c: c.data.startswith("ban_user_"))
    def _ban_user_cb(c):
        if c.from_user.id != admin_id:
            return
        uid_to_ban = int(c.data.split("_")[2])
        db.q("UPDATE bot_subscribers SET banned=1 WHERE user_id=? AND bot_id=?", (uid_to_ban, bot_id))
        tb.answer_callback_query(c.id, f"✅ تم حظر {uid_to_ban}")
        try:
            tb.send_message(uid_to_ban, "🚫 تم حظرك من هذا البوت.")
        except:
            pass

    @tb.callback_query_handler(func=lambda c: c.data.startswith("user_info_"))
    def _user_info_cb(c):
        if c.from_user.id != admin_id:
            return
        uid_info = int(c.data.split("_")[2])
        r = db.f("SELECT sub_type, join_date, total_messages, last_seen FROM bot_subscribers WHERE user_id=? AND bot_id=?", (uid_info, bot_id))
        if r:
            tb.answer_callback_query(c.id, f"👤 {uid_info}\n🌟 {r[0]}\n📅 {r[1][:10] if r[1] else '-'}\n📨 {r[2]} رسالة", show_alert=True)

    @tb.message_handler(func=lambda m: m.chat.id != admin_id,
                        content_types=["text", "photo", "video", "document", "audio", "voice", "sticker", "animation"])
    def _ch(m):
        uid = m.from_user.id
        if _anti_spam(uid):
            tb.send_message(uid, "⚠️ أنت ترسل رسائل بسرعة كبيرة! انتظر قليلاً.")
            return
        blocked = db.f("SELECT 1 FROM bot_subscribers WHERE user_id=? AND bot_id=? AND banned=1", (uid, bot_id))
        if blocked:
            return
        if not _check_bot_subscription(uid, force_channels, tb):
            tb.send_message(uid, "⚠️ يجب الاشتراك في القنوات أولاً!", reply_markup=_bot_sub_kb(force_channels))
            return
        sub = db.f("SELECT sub_type FROM bot_subscribers WHERE user_id=? AND bot_id=?", (uid, bot_id))
        if plan_type != "free" and (not sub or sub[0] == "free"):
            tb.send_message(uid, "⭐ يتطلب اشتراك مدفوع", reply_markup=_bot_upgrade_kb(bot_id, plan_price))
            return
        if m.content_type == "text":
            if _contains_banned_words(m.text):
                tb.send_message(uid, "⚠️ رسالتك تحتوي على كلمات محظورة!")
                return
            ar = _get_auto_reply(bot_id, m.text.lower().strip())
            if ar:
                tb.send_message(uid, ar)
                return
            sett_data = db.f("SELECT settings FROM hosted_bots WHERE id=?", (bot_id,))
            if sett_data and sett_data[0]:
                settings_json = json.loads(sett_data[0])
                custom_cmds = settings_json.get("custom_cmds", {})
                if m.text.strip() in custom_cmds:
                    tb.send_message(uid, custom_cmds[m.text.strip()])
                    return
        db.q("UPDATE bot_subscribers SET total_messages = total_messages + 1, last_seen=? WHERE user_id=? AND bot_id=?",
             (datetime.datetime.now().isoformat(), uid, bot_id))
        u = m.from_user
        ui = f"👤 {u.first_name} {u.last_name or ''}\n🆔 {u.id}\n📛 @{u.username or 'لا يوجد'}"
        try:
            sm = None
            if m.content_type == "text":
                sm = tb.send_message(admin_id, f"{ui}\n━━━━━━━━━\n📝 {m.text}", reply_markup=_ct_reply_kb(u.id, m.message_id))
            elif m.content_type == "photo":
                sm = tb.send_photo(admin_id, m.photo[-1].file_id, caption=f"{ui}\n📸 {m.caption or ''}", reply_markup=_ct_reply_kb(u.id, m.message_id))
            elif m.content_type == "video":
                sm = tb.send_video(admin_id, m.video.file_id, caption=f"{ui}\n🎬 {m.caption or ''}", reply_markup=_ct_reply_kb(u.id, m.message_id))
            elif m.content_type == "document":
                sm = tb.send_document(admin_id, m.document.file_id, caption=f"{ui}\n📄 {m.document.file_name}\n{m.caption or ''}", reply_markup=_ct_reply_kb(u.id, m.message_id))
            elif m.content_type == "voice":
                sm = tb.send_voice(admin_id, m.voice.file_id, caption=f"{ui}\n🎤", reply_markup=_ct_reply_kb(u.id, m.message_id))
            elif m.content_type == "sticker":
                tb.send_message(admin_id, f"{ui}\n🎭 ستيكر", reply_markup=_ct_reply_kb(u.id, m.message_id))
                sm = tb.send_sticker(admin_id, m.sticker.file_id)
            elif m.content_type == "animation":
                sm = tb.send_animation(admin_id, m.animation.file_id, caption=f"{ui}\n🎬 {m.caption or ''}", reply_markup=_ct_reply_kb(u.id, m.message_id))
            elif m.content_type == "audio":
                sm = tb.send_audio(admin_id, m.audio.file_id, caption=f"{ui}\n🎵 {m.caption or ''}", reply_markup=_ct_reply_kb(u.id, m.message_id))
            if sm:
                db.q("INSERT OR REPLACE INTO contact_replies (user_id, bot_id, msg_id, admin_msg_id, time) VALUES (?,?,?,?,?)",
                     (u.id, bot_id, m.message_id, sm.message_id, datetime.datetime.now().isoformat()))
                db.q("UPDATE hosted_bots SET last_activity=? WHERE id=?", (datetime.datetime.now().isoformat(), bot_id))
            tb.send_message(m.chat.id, "✅ تم إرسال رسالتك للإدارة")
        except apihelper.ApiTelegramException as e:
            if e.error_code == 403:
                db.log(bot_id, "user_blocked_bot", f"user={u.id}", u.id)

    @tb.callback_query_handler(func=lambda c: c.data.startswith("reply_") and not c.data.startswith("reply_ticket_"))
    def _cr(c):
        if c.from_user.id != admin_id:
            return
        d = c.data.split("_")
        if len(d) >= 2:
            uid_r = int(d[1])
            msg = tb.send_message(admin_id, f"✍️ اكتب ردك للمستخدم {uid_r}:")
            tb.register_next_step_handler(msg, lambda m: _send_reply_contact(m, uid_r))

    def _send_reply_contact(m, uid_r):
        try:
            if m.content_type == "text":
                tb.send_message(uid_r, f"📨 رد من الإدارة:\n\n{m.text}")
            elif m.content_type == "photo":
                tb.send_photo(uid_r, m.photo[-1].file_id, caption=f"📨 رد من الإدارة:\n{m.caption or ''}")
            elif m.content_type == "video":
                tb.send_video(uid_r, m.video.file_id, caption=f"📨 رد من الإدارة:\n{m.caption or ''}")
            elif m.content_type == "document":
                tb.send_document(uid_r, m.document.file_id, caption=f"📨 رد من الإدارة:\n{m.caption or ''}")
            elif m.content_type == "voice":
                tb.send_voice(uid_r, m.voice.file_id)
            elif m.content_type == "sticker":
                tb.send_sticker(uid_r, m.sticker.file_id)
            elif m.content_type == "animation":
                tb.send_animation(uid_r, m.animation.file_id, caption=f"📨 رد من الإدارة:\n{m.caption or ''}")
            tb.send_message(admin_id, "✅ تم إرسال الرد بنجاح", reply_markup=_owner_contact_kb())
        except Exception as e:
            tb.send_message(admin_id, f"❌ فشل الإرسال: {e}", reply_markup=_owner_contact_kb())

    @tb.callback_query_handler(func=lambda c: c.data.startswith("owner_"))
    def _owner_cb(c):
        uid = c.from_user.id
        if uid != admin_id:
            return
        d = c.data
        if d == "owner_stats":
            uc = db.f("SELECT COUNT(*) FROM bot_subscribers WHERE bot_id=?", (bot_id,))[0] or 0
            pc = db.f("SELECT COUNT(*) FROM bot_subscribers WHERE bot_id=? AND sub_type!='free'", (bot_id,))[0] or 0
            tc = db.f("SELECT COUNT(*) FROM tickets WHERE bot_id=? AND status='open'", (bot_id,))[0] or 0
            ms = db.f("SELECT SUM(total_messages) FROM bot_subscribers WHERE bot_id=?", (bot_id,))[0] or 0
            rev = db.f("SELECT SUM(amount) FROM payments WHERE bot_id=? AND status='completed'", (bot_id,))[0] or 0
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            new_today = db.f("SELECT COUNT(*) FROM bot_subscribers WHERE bot_id=? AND join_date LIKE ?", (bot_id, f"{today}%"))[0] or 0
            tb.edit_message_text(
                f"📊 إحصائيات البوت\n━━━━━━━━━━━━━━━\n"
                f"👥 المشتركين الكلي: {uc}\n"
                f"📅 جديد اليوم: {new_today}\n"
                f"🌟 مشتركي البرو: {pc}\n"
                f"📨 إجمالي الرسائل: {ms}\n"
                f"🎫 التذاكر المفتوحة: {tc}\n"
                f"💰 إجمالي الإيرادات: {rev}⭐\n"
                f"📈 معدل التحويل: {round((pc/uc)*100, 1) if uc else 0}%",
                uid, c.message.message_id, reply_markup=_owner_contact_kb()
            )
        elif d == "owner_analytics":
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            new_today = db.f("SELECT COUNT(*) FROM bot_subscribers WHERE bot_id=? AND join_date LIKE ?", (bot_id, f"{today}%"))[0] or 0
            active_week = db.f("SELECT COUNT(*) FROM bot_subscribers WHERE bot_id=? AND last_seen > ?",
                                (bot_id, (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()))[0] or 0
            active_month = db.f("SELECT COUNT(*) FROM bot_subscribers WHERE bot_id=? AND last_seen > ?",
                                 (bot_id, (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()))[0] or 0
            top_hour = datetime.datetime.now().strftime("%H")
            tb.send_message(uid,
                f"📈 التحليلات المتقدمة\n━━━━━━━━━━━━━━━\n"
                f"📅 جديد اليوم: {new_today}\n"
                f"⚡ نشط هذا الأسبوع: {active_week}\n"
                f"📆 نشط هذا الشهر: {active_month}\n",
                reply_markup=_owner_contact_kb()
            )
        elif d == "owner_broadcast":
            msg = tb.send_message(uid, "📝 أرسل الرسالة للإذاعة (نص/صورة/فيديو):")
            tb.register_next_step_handler(msg, lambda m: _owner_broadcast_fn(m, tb, bot_id, admin_id, "contact"))
        elif d == "owner_set_plan":
            msg = tb.send_message(uid, "💰 أرسل السعر بالنجوم (0 = مجاني):")
            tb.register_next_step_handler(msg, lambda m: _set_plan_fn(m, tb, admin_id, bot_id, _owner_contact_kb))
        elif d == "owner_set_channels":
            current_ch = json.loads(db.f("SELECT force_channels FROM hosted_bots WHERE id=?", (bot_id,))[0] or "[]")
            msg = tb.send_message(uid, f"📢 القنوات الحالية:\n{', '.join(current_ch)}\n\nأرسل القنوات مفصولة بفاصلة:\nمثال: @ch1,@ch2\n\nأرسل 0 لإلغاء الاشتراك الإجباري:")
            tb.register_next_step_handler(msg, lambda m: _set_channels_fn(m, tb, admin_id, bot_id, _owner_contact_kb))
        elif d == "owner_tickets":
            tks = db.fa("SELECT id, user_id, title, status, created_at FROM tickets WHERE bot_id=? ORDER BY id DESC LIMIT 15", (bot_id,))
            if not tks:
                tb.send_message(uid, "❌ لا يوجد تذاكر", reply_markup=_owner_contact_kb())
                return
            txt = "🎫 التذاكر:\n━━━━━━━━━━━━━━━\n"
            k = types.InlineKeyboardMarkup(row_width=1)
            for tid, tuid, title, status, dt in tks:
                emoji = "🟢" if status == "open" else "🔵" if status == "replied" else "🔴"
                txt += f"{emoji} #{tid} | 👤{tuid} | {title[:30]}\n📅 {dt[:10]}\n━━━━━━━━━━━━━━━\n"
                k.add(types.InlineKeyboardButton(f"{emoji} #{tid} - {title[:20]}", callback_data=f"reply_ticket_{tid}_{tuid}"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
            tb.send_message(uid, txt, reply_markup=k)
        elif d == "owner_users":
            users = db.fa("SELECT user_id, sub_type, total_messages, last_seen FROM bot_subscribers WHERE bot_id=? ORDER BY id DESC LIMIT 20", (bot_id,))
            txt = "👥 المستخدمين:\n━━━━━━━━━━━━━━━\n"
            for uu, st, msgs, ls in users:
                emoji = "🌟" if st != "free" else "👤"
                txt += f"{emoji} {uu} | 📨{msgs} | {ls[:10] if ls else '-'}\n"
            k = types.InlineKeyboardMarkup(row_width=2)
            k.add(types.InlineKeyboardButton("🚫 حظر مستخدم", callback_data="owner_ban_input"),
                  types.InlineKeyboardButton("🔓 رفع حظر", callback_data="owner_unban"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
            tb.send_message(uid, txt, reply_markup=k)
        elif d == "owner_ban_input":
            msg = tb.send_message(uid, "🚫 أرسل معرف المستخدم لحظره:")
            tb.register_next_step_handler(msg, lambda m: _ban_user_contact(m, tb, bot_id, admin_id))
        elif d == "owner_payments":
            pays = db.fa("SELECT user_id, amount, created_at FROM payments WHERE bot_id=? AND status='completed' ORDER BY id DESC LIMIT 10", (bot_id,))
            total = db.f("SELECT SUM(amount) FROM payments WHERE bot_id=? AND status='completed'", (bot_id,))[0] or 0
            txt = f"💰 المدفوعات\n━━━━━━━━━━━━━━━\n💎 الإجمالي: {total}⭐\n━━━━━━━━━━━━━━━\n"
            for uu, am, dt in pays:
                txt += f"👤{uu} | ⭐{am} | {dt[:10]}\n"
            tb.send_message(uid, txt or "❌ لا يوجد مدفوعات", reply_markup=_owner_contact_kb())
        elif d == "owner_ai_moderation":
            k = types.InlineKeyboardMarkup(row_width=1)
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
            tb.edit_message_text(
                "🤖 نظام الذكاء الاصطناعي:\n━━━━━━━━━━━━━━━\n"
                "✅ فلترة الروابط: مفعلة\n"
                "✅ كشف السبام: مفعل\n"
                "✅ فلترة الكلمات المسيئة: مفعلة\n"
                "✅ الردود التلقائية: مفعلة\n"
                "✅ حد الرسائل: 5/دقيقة",
                uid, c.message.message_id, reply_markup=k
            )
        elif d == "owner_auto_reply":
            ars = db.fa("SELECT trigger, response, uses FROM auto_replies WHERE bot_id=? AND active=1", (bot_id,))
            txt = "⚡ الردود التلقائية:\n━━━━━━━━━━━━━━━\n"
            for tr, res, uses in ars:
                txt += f"🔑 {tr}\n💬 {res[:50]}\n📊 {uses} استخدام\n━━━━━━━━━━━━━━━\n"
            k = types.InlineKeyboardMarkup(row_width=2)
            k.add(types.InlineKeyboardButton("➕ إضافة", callback_data="owner_add_ar"),
                  types.InlineKeyboardButton("🗑️ حذف", callback_data="owner_del_ar"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
            tb.send_message(uid, txt or "❌ لا يوجد ردود تلقائية\n\nالصيغة: كلمة|الرد", reply_markup=k)
        elif d == "owner_add_ar":
            msg = tb.send_message(uid, "📝 أرسل الكلمة المفتاحية والرد مفصولين بـ |\nمثال: مرحبا|أهلاً وسهلاً!")
            tb.register_next_step_handler(msg, lambda m: _add_auto_reply_fn(m, tb, bot_id, admin_id, _owner_contact_kb))
        elif d == "owner_del_ar":
            msg = tb.send_message(uid, "📝 أرسل الكلمة المفتاحية للحذف:")
            tb.register_next_step_handler(msg, lambda m: _del_auto_reply(m, tb, bot_id, admin_id, _owner_contact_kb))
        elif d == "owner_custom_cmds":
            sett = db.f("SELECT settings FROM hosted_bots WHERE id=?", (bot_id,))
            data = json.loads(sett[0]) if sett and sett[0] else {}
            cmds = data.get("custom_cmds", {})
            txt = "📋 الأوامر المخصصة:\n━━━━━━━━━━━━━━━\n"
            for cmd, resp in cmds.items():
                txt += f"🔹 {cmd}\n💬 {resp[:50]}\n━━━━━━━━━━━━━━━\n"
            msg = tb.send_message(uid, (txt or "❌ لا يوجد أوامر\n") + "\nأرسل الأمر والرد مفصولين بـ |\nمثال: /info|هذا البوت تواصل")
            tb.register_next_step_handler(msg, lambda m: _add_custom_cmd(m, tb, bot_id, admin_id, _owner_contact_kb))
        elif d == "owner_coupons":
            existing = db.fa("SELECT code, discount_value, discount_type, used_count, max_uses FROM coupons WHERE bot_id=? AND active=1", (bot_id,))
            txt = "🎟️ الكوبونات:\n━━━━━━━━━━━━━━━\n"
            for code, dval, dtype, used, maxu in existing:
                txt += f"🎫 {code} | {dval}{'%' if dtype=='percent' else '⭐'} | {used}/{maxu}\n"
            msg = tb.send_message(uid, (txt or "❌ لا يوجد كوبونات\n") + "\nإنشاء كوبون جديد:\nالصيغة: كود|نوع(percent/fixed)|قيمة|عدد\nمثال: SAVE20|percent|20|100")
            tb.register_next_step_handler(msg, lambda m: _create_coupon(m, tb, bot_id, admin_id, _owner_contact_kb))
        elif d == "owner_announce":
            msg = tb.send_message(uid, "📣 أرسل الإعلان (سيرسل لجميع المستخدمين):")
            tb.register_next_step_handler(msg, lambda m: _owner_announce(m, tb, bot_id, admin_id, "contact"))
        elif d == "owner_banned":
            banned = db.fa("SELECT user_id, notes FROM bot_subscribers WHERE bot_id=? AND banned=1", (bot_id,))
            txt = "🚫 المحظورين:\n━━━━━━━━━━━━━━━\n"
            for bu, notes in banned:
                txt += f"🆔 {bu} | {notes or 'لا يوجد سبب'}\n"
            k = types.InlineKeyboardMarkup()
            k.add(types.InlineKeyboardButton("🔓 رفع حظر", callback_data="owner_unban"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
            tb.send_message(uid, txt or "❌ لا يوجد محظورين", reply_markup=k)
        elif d == "owner_unban":
            msg = tb.send_message(uid, "🔓 أرسل معرف المستخدم لرفع الحظر:")
            tb.register_next_step_handler(msg, lambda m: _unban_user_fn(m, tb, bot_id, admin_id, _owner_contact_kb))
        elif d == "owner_admins":
            sett = db.f("SELECT settings FROM hosted_bots WHERE id=?", (bot_id,))
            data = json.loads(sett[0]) if sett and sett[0] else {}
            admins = data.get("admins", [])
            txt = f"🔑 المشرفون:\n👑 المالك: {admin_id}\n"
            for a in admins:
                txt += f"🔑 {a}\n"
            msg = tb.send_message(uid, txt + "\nأرسل معرف المشرف الجديد:")
            tb.register_next_step_handler(msg, lambda m: _add_admin_fn(m, tb, bot_id, admin_id, _owner_contact_kb))
        elif d == "owner_settings":
            k = types.InlineKeyboardMarkup(row_width=1)
            k.add(types.InlineKeyboardButton("✏️ تعديل رسالة الترحيب", callback_data="owner_edit_welcome"),
                  types.InlineKeyboardButton("📝 تعديل وصف البوت", callback_data="owner_edit_desc"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
            tb.send_message(uid, "⚙️ الإعدادات:", reply_markup=k)
        elif d == "owner_edit_welcome":
            msg = tb.send_message(uid, "⚙️ أرسل رسالة الترحيب الجديدة:")
            tb.register_next_step_handler(msg, lambda m: _set_welcome(m, tb, bot_id, admin_id, _owner_contact_kb))
        elif d == "owner_edit_desc":
            msg = tb.send_message(uid, "📝 أرسل الوصف الجديد للبوت:")
            tb.register_next_step_handler(msg, lambda m: _set_bot_desc(m, tb, bot_id, admin_id, _owner_contact_kb))
        elif d == "owner_leaderboard":
            leaders = db.fa("SELECT user_id, total_messages FROM bot_subscribers WHERE bot_id=? ORDER BY total_messages DESC LIMIT 10", (bot_id,))
            txt = "🏆 أكثر المتفاعلين:\n━━━━━━━━━━━━━━━\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, (ul, msgs) in enumerate(leaders):
                medal = medals[i] if i < 3 else f"{i+1}."
                txt += f"{medal} {ul} | 📨 {msgs} رسالة\n"
            tb.send_message(uid, txt or "❌ لا يوجد بيانات", reply_markup=_owner_contact_kb())
        elif d == "owner_schedule":
            msg = tb.send_message(uid, "📅 الصيغة: الرسالة|الوقت_بالدقائق\nمثال: مرحباً بالجميع|60")
            tb.register_next_step_handler(msg, lambda m: _owner_schedule_fn(m, tb, bot_id, admin_id, _owner_contact_kb))
        elif d == "owner_back":
            try:
                tb.edit_message_text("👑 لوحة تحكم البوت", uid, c.message.message_id, reply_markup=_owner_contact_kb())
            except:
                tb.send_message(uid, "👑 لوحة تحكم البوت", reply_markup=_owner_contact_kb())

    def _ban_user_contact(m, tb, bid, aid):
        try:
            uid_ban = int(m.text.strip())
            db.q("UPDATE bot_subscribers SET banned=1 WHERE user_id=? AND bot_id=?", (uid_ban, bid))
            tb.send_message(aid, f"✅ تم حظر {uid_ban}", reply_markup=_owner_contact_kb())
            try:
                tb.send_message(uid_ban, "🚫 تم حظرك من هذا البوت.")
            except:
                pass
        except:
            tb.send_message(aid, "❌ معرف غير صالح", reply_markup=_owner_contact_kb())

    def _set_bot_desc(m, tb, bid, aid, kb_fn=None):
        db.q("UPDATE hosted_bots SET description=? WHERE id=?", (m.text, bid))
        kb = kb_fn() if kb_fn else _owner_contact_kb()
        tb.send_message(aid, "✅ تم تحديث وصف البوت", reply_markup=kb)


def _setup_shop(tb, admin_id, force_channels, plan_price, plan_type):
    bot_data = db.f("SELECT id, welcome_msg FROM hosted_bots WHERE admin_id=? AND bot_type='shop'", (admin_id,))
    bot_id = bot_data[0] if bot_data else 0
    welcome_msg = bot_data[1] if bot_data else "👋 أهلاً بك في المتجر!"

    @tb.message_handler(commands=["start"])
    def _ss(m):
        uid = m.from_user.id
        parts = m.text.split()
        ref = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
        if not db.f("SELECT 1 FROM bot_subscribers WHERE user_id=? AND bot_id=?", (uid, bot_id)):
            db.q("INSERT INTO bot_subscribers (user_id, bot_id, sub_type, join_date) VALUES (?,?,?,?)",
                 (uid, bot_id, "free", datetime.datetime.now().isoformat()))
            db.q("UPDATE hosted_bots SET total_users = total_users + 1 WHERE id=?", (bot_id,))
        if not db.f("SELECT 1 FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id)):
            db.q("INSERT INTO shop_users (user_id, bot_id, balance, referred_by, join_date) VALUES (?,?,?,?,?)",
                 (uid, bot_id, 0, ref, datetime.datetime.now().isoformat()))
            if ref and ref != uid:
                reward = 10
                db.q("UPDATE shop_users SET balance = balance + ? WHERE user_id=? AND bot_id=?", (reward, ref, bot_id))
                db.q("UPDATE shop_users SET referral_count = referral_count + 1 WHERE user_id=? AND bot_id=?", (ref, bot_id))
                try:
                    tb.send_message(ref, f"🎉 انضم مستخدم جديد برابطك! +{reward}💎")
                except:
                    pass
        if uid == admin_id:
            stats = db.f("SELECT total_users FROM hosted_bots WHERE id=?", (bot_id,))
            tb.send_message(uid, f"⚙️ لوحة المتجر\n👥 المستخدمين: {stats[0] if stats else 0}", reply_markup=_owner_shop_kb())
            return
        blocked = db.f("SELECT 1 FROM bot_subscribers WHERE user_id=? AND bot_id=? AND banned=1", (uid, bot_id))
        if blocked:
            tb.send_message(uid, "🚫 تم حظرك من هذا المتجر.")
            return
        if not _check_bot_subscription(uid, force_channels, tb):
            tb.send_message(uid, "⚠️ اشترك في القنوات للوصول للمتجر:", reply_markup=_bot_sub_kb(force_channels))
            return
        sub = db.f("SELECT sub_type FROM bot_subscribers WHERE user_id=? AND bot_id=?", (uid, bot_id))
        if plan_type != "free" and (not sub or sub[0] == "free"):
            tb.send_message(uid, f"⭐ يتطلب اشتراك برو\n💰 {plan_price} نجمة", reply_markup=_bot_upgrade_kb(bot_id, plan_price))
            return
        bal = db.f("SELECT balance FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
        tb.send_message(uid, f"{welcome_msg}\n\n💰 رصيدك: {bal[0] if bal else 0}💎", reply_markup=_sh_main_kb(uid, bot_id))

    @tb.message_handler(commands=["balance"])
    def _bal(m):
        uid = m.from_user.id
        r = db.f("SELECT balance, total_spent, total_earned FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
        if r:
            tb.reply_to(m, f"💰 رصيدك: {r[0]}💎\n📤 أنفقت: {r[1]}💎\n📥 كسبت: {r[2]}💎")

    @tb.message_handler(commands=["leaderboard"])
    def _lb(m):
        leaders = db.fa("SELECT user_id, balance FROM shop_users WHERE bot_id=? ORDER BY balance DESC LIMIT 10", (bot_id,))
        txt = "🏆 لوحة الصدارة:\n━━━━━━━━━━━━━━━\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (ul, bl) in enumerate(leaders):
            medal = medals[i] if i < 3 else f"{i+1}."
            txt += f"{medal} {ul} | {bl}💎\n"
        tb.reply_to(m, txt)

    @tb.callback_query_handler(func=lambda c: c.data == "check_bot_sub")
    def _cb_sub(c):
        uid = c.from_user.id
        if _check_bot_subscription(uid, force_channels, tb):
            tb.answer_callback_query(c.id, "✅ تم!")
            bal = db.f("SELECT balance FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
            tb.send_message(uid, f"🎉 مرحباً بك!\n💰 رصيدك: {bal[0] if bal else 0}💎", reply_markup=_sh_main_kb(uid, bot_id))
        else:
            tb.answer_callback_query(c.id, "❌ اشترك أولاً!", show_alert=True)

    @tb.callback_query_handler(func=lambda c: c.data.startswith("bot_upgrade_"))
    def _bot_upg(c):
        uid = c.from_user.id
        price = plan_price or 100
        payload = _gen_payload()
        db.q("INSERT INTO payments (user_id, bot_id, amount, currency, plan, status, payload, created_at) VALUES (?,?,?,?,?,?,?,?)",
             (uid, bot_id, price, "XTR", "bot_premium", "pending", payload, datetime.datetime.now().isoformat()))
        tb.send_invoice(uid, "اشتراك المتجر", "ترقية للبرو", payload, "", "XTR",
                        [types.LabeledPrice("الاشتراك", price)], start_parameter="bot_sub")

    @tb.callback_query_handler(func=lambda c: not c.data.startswith("owner_") and not c.data.startswith("sh_add") and not c.data.startswith("sh_manage") and not c.data.startswith("manage_prod") and not c.data.startswith("toggle_prod") and not c.data.startswith("del_prod") and not c.data.startswith("edit_"))
    def _sh_cb(c):
        uid = c.from_user.id
        d = c.data
        if d == "sh_back":
            bal = db.f("SELECT balance FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
            try:
                tb.edit_message_text(f"🏠 القائمة الرئيسية\n💰 رصيدك: {bal[0] if bal else 0}💎", uid, c.message.message_id, reply_markup=_sh_main_kb(uid, bot_id))
            except:
                pass
        elif d == "sh_balance":
            r = db.f("SELECT balance, total_spent, total_earned, rank FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
            if r:
                tb.edit_message_text(
                    f"💰 محفظتك\n━━━━━━━━━━━━━━━\n"
                    f"💎 الرصيد: {r[0]}\n📤 الإنفاق: {r[1]}\n📥 الأرباح: {r[2]}\n🏅 الرتبة: {r[3]}",
                    uid, c.message.message_id, reply_markup=_sh_back_kb()
                )
        elif d == "sh_daily":
            r = db.f("SELECT last_daily, daily_streak FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
            last = r[0] if r else 0
            streak = r[1] if r else 0
            now_ts = int(time.time())
            if now_ts - last < 86400:
                remaining = 86400 - (now_ts - last)
                hrs = remaining // 3600
                mins = (remaining % 3600) // 60
                tb.edit_message_text(f"❌ عد لاحقاً\n⏰ متبقي: {hrs} ساعة و {mins} دقيقة", uid, c.message.message_id, reply_markup=_sh_back_kb())
                return
            bonus = 10 + (streak * int(db.setting("daily_streak_bonus", "2")))
            new_streak = streak + 1 if now_ts - last < 172800 else 1
            db.q("UPDATE shop_users SET balance=balance+?, last_daily=?, daily_streak=?, total_earned=total_earned+? WHERE user_id=? AND bot_id=?",
                 (bonus, now_ts, new_streak, bonus, uid, bot_id))
            tb.edit_message_text(
                f"🎁 مكافأة يومية!\n✅ +{bonus}💎\n🔥 السلسلة: {new_streak} يوم\n{'🌟 مكافأة السلسلة!' if streak > 0 else ''}",
                uid, c.message.message_id, reply_markup=_sh_back_kb()
            )
        elif d == "sh_refs":
            me = tb.get_me()
            link = f"https://t.me/{me.username}?start={uid}"
            r = db.f("SELECT referral_count FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
            count = r[0] if r else 0
            tb.edit_message_text(
                f"👥 نظام الإحالات\n━━━━━━━━━━━━━━━\n🔗 رابطك:\n`{link}`\n\n📊 عدد الإحالات: {count}\n💰 مكافأة كل إحالة: 10💎",
                uid, c.message.message_id, reply_markup=_sh_back_kb(), parse_mode="Markdown"
            )
        elif d == "sh_products":
            cats = db.fa("SELECT DISTINCT category FROM shop_products WHERE bot_id=? AND active=1", (bot_id,))
            if not cats:
                tb.answer_callback_query(c.id, "❌ لا يوجد منتجات حالياً")
                return
            k = types.InlineKeyboardMarkup(row_width=2)
            for cat in cats:
                k.add(types.InlineKeyboardButton(f"📁 {cat[0]}", callback_data=f"sh_cat_{cat[0]}"))
            k.add(types.InlineKeyboardButton("🔍 بحث", callback_data="sh_search"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="sh_back"))
            tb.edit_message_text("🛒 التصنيفات:", uid, c.message.message_id, reply_markup=k)
        elif d.startswith("sh_cat_"):
            cat = d.replace("sh_cat_", "")
            prods = db.fa("SELECT id, name, price, original_price, stock, discount FROM shop_products WHERE bot_id=? AND category=? AND active=1 AND (stock>0 OR stock=-1)", (bot_id, cat))
            k = types.InlineKeyboardMarkup(row_width=1)
            for pid, name, price, orig, stock, disc in prods:
                stock_txt = "∞" if stock == -1 else str(stock)
                disc_txt = f" 🔥-{disc}%" if disc > 0 else ""
                k.add(types.InlineKeyboardButton(f"{name} | {price}💎{disc_txt} | 📦{stock_txt}", callback_data=f"sh_prod_{pid}"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="sh_products"))
            tb.edit_message_text(f"📁 {cat}", uid, c.message.message_id, reply_markup=k)
        elif d.startswith("sh_prod_"):
            pid = int(d.split("_")[2])
            p = db.f("SELECT id, name, description, price, original_price, stock, delivery, discount, sold_count FROM shop_products WHERE id=? AND bot_id=?", (pid, bot_id))
            if not p:
                tb.answer_callback_query(c.id, "❌ المنتج غير موجود")
                return
            pid, name, desc, price, orig, stock, delivery, disc, sold = p
            stock_txt = "غير محدود" if stock == -1 else (f"{stock} متبقي" if stock > 0 else "نفدت الكمية")
            del_txt = "🚀 فوري" if delivery == "auto" else "⏰ يدوي"
            k = types.InlineKeyboardMarkup(row_width=2)
            k.add(types.InlineKeyboardButton("🛒 شراء الآن", callback_data=f"shbuy_{pid}"),
                  types.InlineKeyboardButton("❤️ أضف للمفضلة", callback_data=f"shwish_{pid}"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="sh_products"))
            disc_line = f"\n🔥 خصم: {disc}% (الأصلي: {orig}💎)" if disc > 0 else ""
            tb.edit_message_text(
                f"📦 {name}\n━━━━━━━━━━━━━━━\n📝 {desc or 'لا يوجد وصف'}\n💰 السعر: {price}💎{disc_line}\n📦 المخزون: {stock_txt}\n🚚 التسليم: {del_txt}\n✅ المبيعات: {sold}",
                uid, c.message.message_id, reply_markup=k
            )
        elif d.startswith("shbuy_"):
            pid = int(d.split("_")[1])
            p = db.f("SELECT name, price, delivery, content, stock FROM shop_products WHERE id=? AND bot_id=? AND active=1", (pid, bot_id))
            if not p or p[4] == 0:
                tb.answer_callback_query(c.id, "❌ المنتج غير متاح", show_alert=True)
                return
            name, price, delivery, content, stock = p
            r = db.f("SELECT balance FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
            bal = r[0] if r else 0
            if bal < price:
                tb.edit_message_text(
                    f"❌ رصيد غير كافٍ\n💰 رصيدك: {bal}💎\n🏷️ السعر: {price}💎\n\n💡 احصل على المزيد عبر المكافأة اليومية والإحالات!",
                    uid, c.message.message_id, reply_markup=_sh_back_kb()
                )
                return
            db.q("UPDATE shop_users SET balance=balance-?, total_spent=total_spent+?, total_purchases=total_purchases+1 WHERE user_id=? AND bot_id=?", (price, price, uid, bot_id))
            if stock != -1:
                db.q("UPDATE shop_products SET stock=stock-1, sold_count=sold_count+1 WHERE id=?", (pid,))
            order_id = db.q("INSERT INTO shop_orders (bot_id, user_id, product_id, total_price, created_at) VALUES (?,?,?,?,?)",
                             (bot_id, uid, pid, price, datetime.datetime.now().isoformat())).lastrowid
            if delivery == "auto":
                db.q("UPDATE shop_orders SET status='delivered', delivered_at=? WHERE id=?",
                     (datetime.datetime.now().isoformat(), order_id))
                tb.edit_message_text(
                    f"✅ تم الشراء بنجاح!\n━━━━━━━━━━━━━━━\n📦 {name}\n🔑 المحتوى:\n\n{content}\n━━━━━━━━━━━━━━━\n🧾 رقم الطلب: #{order_id}",
                    uid, c.message.message_id, reply_markup=_sh_back_kb()
                )
            else:
                tb.edit_message_text(
                    f"✅ تم الطلب!\n━━━━━━━━━━━━━━━\n📦 {name}\n🧾 رقم الطلب: #{order_id}\n\n⏰ سيتم التواصل معك قريباً",
                    uid, c.message.message_id, reply_markup=_sh_back_kb()
                )
            try:
                k_admin = types.InlineKeyboardMarkup()
                k_admin.add(types.InlineKeyboardButton(f"✅ تسليم #{order_id}", callback_data=f"deliver_{order_id}_{uid}"))
                tb.send_message(admin_id, f"🔔 طلب جديد #{order_id}\n👤 {uid}\n📦 {name}\n💰 {price}💎", reply_markup=k_admin)
            except:
                pass
        elif d.startswith("shwish_"):
            pid = int(d.split("_")[1])
            r = db.f("SELECT wishlist FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
            wishlist = json.loads(r[0]) if r and r[0] else []
            if pid not in wishlist:
                wishlist.append(pid)
                db.q("UPDATE shop_users SET wishlist=? WHERE user_id=? AND bot_id=?", (json.dumps(wishlist), uid, bot_id))
                tb.answer_callback_query(c.id, "✅ أضيف للمفضلة!")
            else:
                tb.answer_callback_query(c.id, "❌ موجود بالفعل في المفضلة")
        elif d == "sh_wishlist":
            r = db.f("SELECT wishlist FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
            wishlist = json.loads(r[0]) if r and r[0] else []
            if not wishlist:
                tb.answer_callback_query(c.id, "❌ قائمة المفضلة فارغة")
                return
            k = types.InlineKeyboardMarkup(row_width=1)
            for pid in wishlist:
                p = db.f("SELECT name, price FROM shop_products WHERE id=?", (pid,))
                if p:
                    k.add(types.InlineKeyboardButton(f"{p[0]} | {p[1]}💎", callback_data=f"sh_prod_{pid}"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="sh_back"))
            tb.edit_message_text("❤️ قائمة المفضلة:", uid, c.message.message_id, reply_markup=k)
        elif d == "sh_orders":
            orders = db.fa("SELECT o.id, p.name, o.total_price, o.status, o.created_at FROM shop_orders o JOIN shop_products p ON o.product_id=p.id WHERE o.user_id=? AND o.bot_id=? ORDER BY o.id DESC LIMIT 10", (uid, bot_id))
            if not orders:
                tb.answer_callback_query(c.id, "❌ لا يوجد طلبات")
                return
            txt = "🛍️ طلباتك:\n━━━━━━━━━━━━━━━\n"
            for oid, pname, price, status, dt in orders:
                s_emoji = "✅" if status == "delivered" else "⏰"
                txt += f"{s_emoji} #{oid} | {pname} | {price}💎 | {dt[:10]}\n"
            k = types.InlineKeyboardMarkup()
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="sh_back"))
            tb.edit_message_text(txt, uid, c.message.message_id, reply_markup=k)
        elif d == "sh_leaderboard":
            leaders = db.fa("SELECT user_id, balance FROM shop_users WHERE bot_id=? ORDER BY balance DESC LIMIT 10", (bot_id,))
            txt = "🏆 لوحة الصدارة:\n━━━━━━━━━━━━━━━\n"
            medals = ["🥇", "🥈", "🥉"]
            for i, (ul, bl) in enumerate(leaders):
                medal = medals[i] if i < 3 else f"{i+1}."
                txt += f"{medal} المستخدم {ul} | {bl}💎\n"
            k = types.InlineKeyboardMarkup()
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="sh_back"))
            tb.edit_message_text(txt, uid, c.message.message_id, reply_markup=k)
        elif d == "sh_coupon":
            msg = tb.send_message(uid, "🎟️ أرسل كود الكوبون:")
            tb.register_next_step_handler(msg, lambda m: _apply_shop_coupon(m, uid))
        elif d == "sh_mystats":
            r = db.f("SELECT balance, total_spent, total_earned, referral_count, total_purchases, daily_streak FROM shop_users WHERE user_id=? AND bot_id=?", (uid, bot_id))
            if r:
                tb.edit_message_text(
                    f"📊 إحصائياتك\n━━━━━━━━━━━━━━━\n"
                    f"💎 الرصيد: {r[0]}\n📤 الإنفاق: {r[1]}\n📥 الأرباح: {r[2]}\n"
                    f"👥 الإحالات: {r[3]}\n🛒 المشتريات: {r[4]}\n🔥 سلسلة يومية: {r[5]} يوم",
                    uid, c.message.message_id, reply_markup=_sh_back_kb()
                )
        elif d == "sh_search":
            msg = tb.send_message(uid, "🔍 أرسل اسم المنتج للبحث:")
            tb.register_next_step_handler(msg, lambda m: _search_product(m, uid))
        elif d.startswith("deliver_"):
            if uid != admin_id:
                return
            parts = d.split("_")
            oid = int(parts[1])
            ouid = int(parts[2])
            db.q("UPDATE shop_orders SET status='delivered', delivered_at=? WHERE id=?",
                 (datetime.datetime.now().isoformat(), oid))
            tb.answer_callback_query(c.id, "✅ تم التسليم")
            try:
                tb.send_message(ouid, f"✅ تم تسليم طلبك #{oid}!")
            except:
                pass

    def _apply_shop_coupon(m, uid):
        code = m.text.strip().upper()
        coupon = db.f("SELECT id, discount_type, discount_value, max_uses, used_count FROM coupons WHERE code=? AND bot_id=? AND active=1", (code, bot_id))
        if not coupon:
            tb.send_message(uid, "❌ الكوبون غير صالح", reply_markup=_sh_back_kb())
            return
        cid, dtype, dval, maxu, used = coupon
        if maxu > 0 and used >= maxu:
            tb.send_message(uid, "❌ تم استنفاد الكوبون", reply_markup=_sh_back_kb())
            return
        db.q("UPDATE coupons SET used_count=used_count+1 WHERE id=?", (cid,))
        if dtype == "fixed":
            db.q("UPDATE shop_users SET balance=balance+? WHERE user_id=? AND bot_id=?", (dval, uid, bot_id))
            tb.send_message(uid, f"✅ كوبون صالح! تم إضافة {dval}💎 لرصيدك!", reply_markup=_sh_main_kb(uid, bot_id))
        else:
            tb.send_message(uid, f"✅ كوبون صالح! خصم {dval}% على مشترياتك القادمة!", reply_markup=_sh_main_kb(uid, bot_id))

    def _search_product(m, uid):
        query = m.text.strip().lower()
        prods = db.fa("SELECT id, name, price FROM shop_products WHERE bot_id=? AND active=1 AND LOWER(name) LIKE ?", (bot_id, f"%{query}%"))
        if not prods:
            tb.send_message(uid, "❌ لم يتم العثور على منتجات", reply_markup=_sh_main_kb(uid, bot_id))
            return
        k = types.InlineKeyboardMarkup(row_width=1)
        for pid, name, price in prods:
            k.add(types.InlineKeyboardButton(f"{name} | {price}💎", callback_data=f"sh_prod_{pid}"))
        k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="sh_back"))
        tb.send_message(uid, f"🔍 نتائج '{query}':", reply_markup=k)

    @tb.callback_query_handler(func=lambda c: c.data.startswith("owner_") or c.data.startswith("sh_add") or c.data.startswith("sh_manage") or c.data.startswith("manage_prod") or c.data.startswith("toggle_prod") or c.data.startswith("del_prod") or c.data.startswith("edit_"))
    def _owner_shop_cb(c):
        uid = c.from_user.id
        if uid != admin_id:
            return
        d = c.data
        if d == "owner_stats":
            uc = db.f("SELECT COUNT(*) FROM shop_users WHERE bot_id=?", (bot_id,))[0] or 0
            sc = db.f("SELECT COUNT(*) FROM shop_products WHERE bot_id=? AND active=1", (bot_id,))[0] or 0
            oc = db.f("SELECT COUNT(*) FROM shop_orders WHERE bot_id=?", (bot_id,))[0] or 0
            rev = db.f("SELECT SUM(total_price) FROM shop_orders WHERE bot_id=? AND status='delivered'", (bot_id,))[0] or 0
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            new_today = db.f("SELECT COUNT(*) FROM shop_users WHERE bot_id=? AND join_date LIKE ?", (bot_id, f"{today}%"))[0] or 0
            tb.edit_message_text(
                f"📊 إحصائيات المتجر\n━━━━━━━━━━━━━━━\n"
                f"👥 المستخدمين: {uc}\n📅 جديد اليوم: {new_today}\n"
                f"📦 المنتجات: {sc}\n🛒 الطلبات: {oc}\n💰 الإيرادات: {rev}💎",
                uid, c.message.message_id, reply_markup=_owner_shop_kb()
            )
        elif d == "owner_analytics":
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            new_t = db.f("SELECT COUNT(*) FROM shop_users WHERE bot_id=? AND join_date LIKE ?", (bot_id, f"{today}%"))[0] or 0
            orders_t = db.f("SELECT COUNT(*) FROM shop_orders WHERE bot_id=? AND created_at LIKE ?", (bot_id, f"{today}%"))[0] or 0
            top_prod = db.f("SELECT name, sold_count FROM shop_products WHERE bot_id=? ORDER BY sold_count DESC LIMIT 1", (bot_id,))
            tb.send_message(uid,
                f"📈 التحليلات\n━━━━━━━━━━━━━━━\n"
                f"📅 جديد اليوم: {new_t}\n🛒 طلبات اليوم: {orders_t}\n"
                f"🏆 الأكثر مبيعاً: {top_prod[0] if top_prod else 'لا يوجد'} ({top_prod[1] if top_prod else 0} مبيعة)",
                reply_markup=_owner_shop_kb()
            )
        elif d == "owner_broadcast":
            msg = tb.send_message(uid, "📝 أرسل رسالة الإذاعة:")
            tb.register_next_step_handler(msg, lambda m: _owner_broadcast_fn(m, tb, bot_id, admin_id, "shop"))
        elif d == "owner_set_plan":
            msg = tb.send_message(uid, "💰 أرسل السعر (0 = مجاني):")
            tb.register_next_step_handler(msg, lambda m: _set_plan_fn(m, tb, admin_id, bot_id, _owner_shop_kb))
        elif d == "owner_set_channels":
            msg = tb.send_message(uid, "📢 أرسل القنوات مفصولة بفاصلة (0 للإلغاء):")
            tb.register_next_step_handler(msg, lambda m: _set_channels_fn(m, tb, admin_id, bot_id, _owner_shop_kb))
        elif d == "owner_payments":
            pays = db.fa("SELECT user_id, total_price, created_at FROM shop_orders WHERE bot_id=? AND status='delivered' ORDER BY id DESC LIMIT 15", (bot_id,))
            total = db.f("SELECT SUM(total_price) FROM shop_orders WHERE bot_id=? AND status='delivered'", (bot_id,))[0] or 0
            txt = f"💰 المدفوعات\n━━━━━━━━━━━━━━━\n💎 الإجمالي: {total}\n━━━━━━━━━━━━━━━\n"
            for uu, am, dt in pays:
                txt += f"👤{uu} | 💎{am} | {dt[:10]}\n"
            tb.send_message(uid, txt or "❌ لا يوجد", reply_markup=_owner_shop_kb())
        elif d == "owner_leaderboard":
            leaders = db.fa("SELECT user_id, balance, total_purchases FROM shop_users WHERE bot_id=? ORDER BY balance DESC LIMIT 10", (bot_id,))
            txt = "🏆 لوحة الصدارة:\n━━━━━━━━━━━━━━━\n"
            for i, (ul, bl, tp) in enumerate(leaders, 1):
                txt += f"{i}. 🆔{ul} | 💎{bl} | 🛒{tp}\n"
            tb.send_message(uid, txt, reply_markup=_owner_shop_kb())
        elif d == "sh_add_prod":
            msg = tb.send_message(uid, "📝 اسم المنتج:")
            tb.register_next_step_handler(msg, lambda m: _sh_step_name(m))
        elif d == "sh_manage":
            prods = db.fa("SELECT id, name, price, stock, active FROM shop_products WHERE bot_id=?", (bot_id,))
            if not prods:
                tb.send_message(uid, "❌ لا يوجد منتجات", reply_markup=_owner_shop_kb())
                return
            k = types.InlineKeyboardMarkup(row_width=1)
            for pid, name, price, stock, active in prods:
                status_e = "✅" if active else "❌"
                stock_t = "∞" if stock == -1 else str(stock)
                k.add(types.InlineKeyboardButton(f"{status_e} {name} | {price}💎 | 📦{stock_t}", callback_data=f"manage_prod_{pid}"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
            tb.send_message(uid, "📦 إدارة المنتجات:", reply_markup=k)
        elif d.startswith("manage_prod_"):
            pid = int(d.split("_")[2])
            p = db.f("SELECT name, price, stock, active, delivery FROM shop_products WHERE id=?", (pid,))
            if p:
                k = types.InlineKeyboardMarkup(row_width=2)
                k.add(types.InlineKeyboardButton("✏️ تعديل السعر", callback_data=f"edit_price_{pid}"),
                      types.InlineKeyboardButton("📦 تعديل المخزون", callback_data=f"edit_stock_{pid}"))
                k.add(types.InlineKeyboardButton("🚫 تعطيل" if p[3] else "✅ تفعيل", callback_data=f"toggle_prod_{pid}"),
                      types.InlineKeyboardButton("🗑️ حذف", callback_data=f"del_prod_{pid}"))
                k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="sh_manage"))
                tb.send_message(uid, f"📦 {p[0]}\n💰 {p[1]}💎 | 📦 {p[2]} | {'✅ نشط' if p[3] else '❌ معطل'}", reply_markup=k)
        elif d.startswith("toggle_prod_"):
            pid = int(d.split("_")[2])
            curr = db.f("SELECT active FROM shop_products WHERE id=?", (pid,))[0]
            db.q("UPDATE shop_products SET active=? WHERE id=?", (0 if curr else 1, pid))
            tb.answer_callback_query(c.id, "✅ تم التبديل")
        elif d.startswith("del_prod_"):
            pid = int(d.split("_")[2])
            db.q("DELETE FROM shop_products WHERE id=?", (pid,))
            tb.answer_callback_query(c.id, "✅ تم الحذف")
        elif d.startswith("edit_price_"):
            pid = int(d.split("_")[2])
            msg = tb.send_message(uid, "💰 أرسل السعر الجديد:")
            tb.register_next_step_handler(msg, lambda m: _edit_price(m, pid))
        elif d.startswith("edit_stock_"):
            pid = int(d.split("_")[2])
            msg = tb.send_message(uid, "📦 أرسل الكمية الجديدة (-1 = لا محدود):")
            tb.register_next_step_handler(msg, lambda m: _edit_stock(m, pid))
        elif d == "owner_coupons":
            msg = tb.send_message(uid, "🎟️ إنشاء كوبون\nالصيغة: كود|نوع(percent/fixed)|قيمة|عدد\nمثال: SAVE20|percent|20|100")
            tb.register_next_step_handler(msg, lambda m: _create_coupon(m, tb, bot_id, admin_id, _owner_shop_kb))
        elif d == "owner_banned":
            banned = db.fa("SELECT user_id FROM bot_subscribers WHERE bot_id=? AND banned=1", (bot_id,))
            txt = "🚫 المحظورين:\n"
            for bu in banned:
                txt += f"🆔 {bu[0]}\n"
            k = types.InlineKeyboardMarkup()
            k.add(types.InlineKeyboardButton("🔓 رفع حظر", callback_data="owner_unban"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
            tb.send_message(uid, txt or "❌ لا يوجد محظورين", reply_markup=k)
        elif d == "owner_unban":
            msg = tb.send_message(uid, "🔓 أرسل معرف المستخدم:")
            tb.register_next_step_handler(msg, lambda m: _unban_user_fn(m, tb, bot_id, admin_id, _owner_shop_kb))
        elif d == "owner_users":
            users = db.fa("SELECT user_id, balance, total_purchases FROM shop_users WHERE bot_id=? ORDER BY balance DESC LIMIT 20", (bot_id,))
            txt = "👥 المستخدمين:\n━━━━━━━━━━━━━━━\n"
            for uu, bal, tp in users:
                txt += f"🆔{uu} | 💎{bal} | 🛒{tp}\n"
            tb.send_message(uid, txt, reply_markup=_owner_shop_kb())
        elif d == "owner_admins":
            msg = tb.send_message(uid, "🔑 أرسل معرف المشرف الجديد:")
            tb.register_next_step_handler(msg, lambda m: _add_admin_fn(m, tb, bot_id, admin_id, _owner_shop_kb))
        elif d == "owner_schedule":
            msg = tb.send_message(uid, "📅 الصيغة: الرسالة|الوقت_بالدقائق\nمثال: عروض جديدة|60")
            tb.register_next_step_handler(msg, lambda m: _owner_schedule_fn(m, tb, bot_id, admin_id, _owner_shop_kb))
        elif d == "owner_back":
            try:
                tb.edit_message_text("⚙️ لوحة المتجر", uid, c.message.message_id, reply_markup=_owner_shop_kb())
            except:
                tb.send_message(uid, "⚙️ لوحة المتجر", reply_markup=_owner_shop_kb())

    def _sh_step_name(m):
        name = m.text
        msg = tb.send_message(m.chat.id, "📝 وصف المنتج (أو أرسل - للتخطي):")
        tb.register_next_step_handler(msg, lambda m2: _sh_step_desc(m2, name))

    def _sh_step_desc(m, name):
        desc = m.text if m.text != "-" else ""
        msg = tb.send_message(m.chat.id, "💰 السعر (بالعملة المحلية 💎):")
        tb.register_next_step_handler(msg, lambda m2: _sh_step_price(m2, name, desc))

    def _sh_step_price(m, name, desc):
        try:
            price = int(m.text)
            msg = tb.send_message(m.chat.id, "📦 الكمية (-1 = لا محدود):")
            tb.register_next_step_handler(msg, lambda m2: _sh_step_stock(m2, name, desc, price))
        except:
            tb.send_message(m.chat.id, "❌ أرسل رقماً صحيحاً", reply_markup=_owner_shop_kb())

    def _sh_step_stock(m, name, desc, price):
        try:
            stock = int(m.text)
            msg = tb.send_message(m.chat.id, "📁 الفئة:")
            tb.register_next_step_handler(msg, lambda m2: _sh_step_cat(m2, name, desc, price, stock))
        except:
            tb.send_message(m.chat.id, "❌ رقم غير صالح", reply_markup=_owner_shop_kb())

    def _sh_step_cat(m, name, desc, price, stock):
        cat = m.text.strip()
        k = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        k.add("🚀 تلقائي", "⏰ يدوي")
        msg = tb.send_message(m.chat.id, "🚚 نوع التسليم:", reply_markup=k)
        tb.register_next_step_handler(msg, lambda m2: _sh_step_del(m2, name, desc, price, stock, cat))

    def _sh_step_del(m, name, desc, price, stock, cat):
        delivery = "auto" if "تلقائي" in m.text else "manual"
        if delivery == "auto":
            tb.send_message(m.chat.id, "📝 أرسل محتوى التسليم التلقائي:", reply_markup=types.ReplyKeyboardRemove())
            tb.register_next_step_handler(m, lambda m2: _sh_save(m2, name, desc, price, stock, delivery, cat))
        else:
            _sh_save(m, name, desc, price, stock, delivery, cat, content="")

    def _sh_save(m, name, desc, price, stock, delivery, cat, content=None):
        c = content if content is not None else (m.text if delivery == "auto" else None)
        db.q("INSERT INTO shop_products (bot_id, name, description, price, stock, delivery, content, category, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
             (bot_id, name, desc, price, stock, delivery, c, cat, datetime.datetime.now().isoformat()))
        tb.send_message(m.chat.id,
            f"✅ تم إضافة المنتج!\n━━━━━━━━━━━━━━━\n"
            f"📦 {name}\n💰 {price}💎\n📁 {cat}\n🚚 {'تلقائي' if delivery=='auto' else 'يدوي'}",
            reply_markup=_owner_shop_kb()
        )

    def _edit_price(m, pid):
        try:
            price = int(m.text.strip())
            db.q("UPDATE shop_products SET price=? WHERE id=?", (price, pid))
            tb.send_message(admin_id, f"✅ تم تحديث السعر إلى {price}💎", reply_markup=_owner_shop_kb())
        except:
            tb.send_message(admin_id, "❌ رقم غير صالح", reply_markup=_owner_shop_kb())

    def _edit_stock(m, pid):
        try:
            stock = int(m.text.strip())
            db.q("UPDATE shop_products SET stock=? WHERE id=?", (stock, pid))
            tb.send_message(admin_id, f"✅ تم تحديث المخزون إلى {stock if stock!=-1 else 'لا محدود'}", reply_markup=_owner_shop_kb())
        except:
            tb.send_message(admin_id, "❌ رقم غير صالح", reply_markup=_owner_shop_kb())


def _setup_tempmail(tb, admin_id, force_channels, plan_price, plan_type):
    bot_data = db.f("SELECT id FROM hosted_bots WHERE admin_id=? AND bot_type='tempmail'", (admin_id,))
    bot_id = bot_data[0] if bot_data else 0

    @tb.message_handler(commands=["start"])
    def _ts(m):
        uid = m.from_user.id
        if uid == admin_id:
            uc = db.f("SELECT COUNT(*) FROM bot_subscribers WHERE bot_id=?", (bot_id,))[0] or 0
            tb.send_message(uid, f"👑 لوحة التحكم\n👥 المستخدمين: {uc}", reply_markup=_owner_tempmail_kb())
            return
        if not db.f("SELECT 1 FROM bot_subscribers WHERE user_id=? AND bot_id=?", (uid, bot_id)):
            db.q("INSERT INTO bot_subscribers (user_id, bot_id, sub_type, join_date) VALUES (?,?,?,?)",
                 (uid, bot_id, "free", datetime.datetime.now().isoformat()))
            db.q("UPDATE hosted_bots SET total_users=total_users+1 WHERE id=?", (bot_id,))
        if not _check_bot_subscription(uid, force_channels, tb):
            tb.send_message(uid, "⚠️ اشترك في القنوات:", reply_markup=_bot_sub_kb(force_channels))
            return
        sub = db.f("SELECT sub_type FROM bot_subscribers WHERE user_id=? AND bot_id=?", (uid, bot_id))
        if plan_type != "free" and (not sub or sub[0] == "free"):
            tb.send_message(uid, f"⭐ يتطلب اشتراك مدفوع\n💰 {plan_price} نجمة", reply_markup=_bot_upgrade_kb(bot_id, plan_price))
            return
        existing = db.f("SELECT email, svc FROM mail_sessions WHERE user_id=? AND bot_id=?", (uid, bot_id))
        if existing:
            tb.send_message(uid,
                f"👋 مرحباً بعودتك!\n\n📧 بريدك الحالي:\n`{existing[0]}`\n⚙️ الخدمة: {SVC_NAMES.get(existing[1], existing[1])}\n\n🔧 {DEV_NAME}",
                reply_markup=_tm_main_kb(existing[0], existing[1]), parse_mode="Markdown"
            )
        else:
            tb.send_message(uid,
                f"👋 أهلاً في بوت الإيميلات الوهمية!\n\n📧 اختر خدمة الإيميل:\n\n🔧 {DEV_NAME} | {DEV_LINK}",
                reply_markup=_tm_svc_kb()
            )

    @tb.message_handler(commands=["mymail"])
    def _mymail(m):
        uid = m.from_user.id
        r = db.f("SELECT email, svc, created_at FROM mail_sessions WHERE user_id=? AND bot_id=?", (uid, bot_id))
        if r:
            tb.reply_to(m, f"📧 بريدك:\n`{r[0]}`\n⚙️ {SVC_NAMES.get(r[1], r[1])}\n📅 {r[2][:10]}", parse_mode="Markdown")
        else:
            tb.reply_to(m, "❌ لا يوجد بريد. أنشئ واحداً!", reply_markup=_tm_svc_kb())

    @tb.message_handler(commands=["delete"])
    def _del_mail(m):
        uid = m.from_user.id
        db.q("DELETE FROM mail_sessions WHERE user_id=? AND bot_id=?", (uid, bot_id))
        tb.reply_to(m, "✅ تم حذف بريدك الإلكتروني.", reply_markup=_tm_svc_kb())

    @tb.callback_query_handler(func=lambda c: not c.data.startswith("owner_") and not c.data.startswith("tm_"))
    def _tm_cb(c):
        uid = c.from_user.id
        d = c.data
        if d.startswith("pick_"):
            svc = d.replace("pick_", "")
            _tm_create(tb, uid, c, svc, bot_id)
        elif d in ["create", "new", "svcs"]:
            try:
                tb.edit_message_text("⚙️ اختر خدمة الإيميل:", uid, c.message.message_id, reply_markup=_tm_svc_kb())
            except:
                tb.send_message(uid, "⚙️ اختر خدمة الإيميل:", reply_markup=_tm_svc_kb())
        elif d.startswith("get_") or d.startswith("ref_"):
            svc = d.split("_", 1)[1]
            _tm_inbox(tb, uid, c, svc, bot_id)
        elif d.startswith("cp_"):
            email = d[3:]
            tb.answer_callback_query(c.id, f"📋 {email}", show_alert=True)
        elif d == "del":
            db.q("DELETE FROM mail_sessions WHERE user_id=? AND bot_id=?", (uid, bot_id))
            try:
                tb.edit_message_text("✅ تم حذف البريد الإلكتروني", uid, c.message.message_id, reply_markup=_tm_svc_kb())
            except:
                pass
        elif d == "me":
            _tm_info(tb, uid, c, bot_id)
        elif d == "auto_check":
            tb.answer_callback_query(c.id, "🔔 سيتم التنبيه عند وصول رسائل جديدة!", show_alert=True)
        elif d == "check_bot_sub":
            if _check_bot_subscription(uid, force_channels, tb):
                tb.answer_callback_query(c.id, "✅ تم!")
                tb.send_message(uid, "🎉 يمكنك الآن استخدام البوت!", reply_markup=_tm_svc_kb())
            else:
                tb.answer_callback_query(c.id, "❌ اشترك أولاً!", show_alert=True)
        elif d.startswith("bot_upgrade_"):
            price = plan_price or 100
            payload = _gen_payload()
            db.q("INSERT INTO payments (user_id, bot_id, amount, currency, plan, status, payload, created_at) VALUES (?,?,?,?,?,?,?,?)",
                 (uid, bot_id, price, "XTR", "bot_premium", "pending", payload, datetime.datetime.now().isoformat()))
            tb.send_invoice(uid, "اشتراك البوت", "ترقية للبرو", payload, "", "XTR",
                            [types.LabeledPrice("الاشتراك", price)], start_parameter="bot_sub")

    @tb.callback_query_handler(func=lambda c: c.data.startswith("owner_") or c.data.startswith("tm_"))
    def _tm_owner_cb(c):
        uid = c.from_user.id
        if uid != admin_id:
            return
        d = c.data
        if d == "tm_broadcast":
            msg = tb.send_message(uid, "📝 أرسل رسالة الإذاعة:")
            tb.register_next_step_handler(msg, lambda m: _owner_broadcast_fn(m, tb, bot_id, admin_id, "tempmail"))
        elif d == "tm_stats":
            uc = db.f("SELECT COUNT(*) FROM mail_sessions WHERE bot_id=?", (bot_id,))[0] or 0
            tc = db.f("SELECT COUNT(*) FROM bot_subscribers WHERE bot_id=?", (bot_id,))[0] or 0
            svc_counts = db.fa("SELECT svc, COUNT(*) FROM mail_sessions WHERE bot_id=? GROUP BY svc", (bot_id,))
            txt = f"📊 إحصائيات البوت\n━━━━━━━━━━━━━━━\n👥 المشتركين: {tc}\n📧 جلسات البريد: {uc}\n\n📈 توزيع الخدمات:\n"
            for svc, cnt in svc_counts:
                txt += f"{SVC_NAMES.get(svc, svc)}: {cnt}\n"
            tb.send_message(uid, txt, reply_markup=_owner_tempmail_kb())
        elif d == "tm_users":
            users = db.fa("SELECT user_id, sub_type, last_seen FROM bot_subscribers WHERE bot_id=? ORDER BY id DESC LIMIT 20", (bot_id,))
            txt = "👥 المستخدمين:\n━━━━━━━━━━━━━━━\n"
            for uu, st, ls in users:
                txt += f"🆔{uu} | {st} | {ls[:10] if ls else '-'}\n"
            tb.send_message(uid, txt, reply_markup=_owner_tempmail_kb())
        elif d == "tm_analytics":
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            new_t = db.f("SELECT COUNT(*) FROM bot_subscribers WHERE bot_id=? AND join_date LIKE ?", (bot_id, f"{today}%"))[0] or 0
            active_w = db.f("SELECT COUNT(*) FROM bot_subscribers WHERE bot_id=? AND last_seen > ?",
                            (bot_id, (datetime.datetime.now()-datetime.timedelta(days=7)).isoformat()))[0] or 0
            tb.send_message(uid, f"📈 التحليلات\n📅 جديد اليوم: {new_t}\n⚡ نشط هذا الأسبوع: {active_w}", reply_markup=_owner_tempmail_kb())
        elif d == "owner_set_plan":
            msg = tb.send_message(uid, "💰 أرسل السعر (0 = مجاني):")
            tb.register_next_step_handler(msg, lambda m: _set_plan_fn(m, tb, admin_id, bot_id, _owner_tempmail_kb))
        elif d == "owner_set_channels":
            msg = tb.send_message(uid, "📢 أرسل القنوات مفصولة بفاصلة (0 للإلغاء):")
            tb.register_next_step_handler(msg, lambda m: _set_channels_fn(m, tb, admin_id, bot_id, _owner_tempmail_kb))
        elif d == "owner_banned":
            banned = db.fa("SELECT user_id FROM bot_subscribers WHERE bot_id=? AND banned=1", (bot_id,))
            txt = "🚫 المحظورين:\n"
            for bu in banned:
                txt += f"🆔 {bu[0]}\n"
            k = types.InlineKeyboardMarkup()
            k.add(types.InlineKeyboardButton("🔓 رفع حظر", callback_data="owner_unban_tm"))
            k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="owner_back"))
            tb.send_message(uid, txt or "❌ لا يوجد محظورين", reply_markup=k)
        elif d == "owner_unban_tm":
            msg = tb.send_message(uid, "🔓 أرسل معرف المستخدم:")
            tb.register_next_step_handler(msg, lambda m: _unban_user_fn(m, tb, bot_id, admin_id, _owner_tempmail_kb))
        elif d == "owner_coupons":
            msg = tb.send_message(uid, "🎟️ إنشاء كوبون\nالصيغة: كود|نوع(percent/fixed)|قيمة|عدد")
            tb.register_next_step_handler(msg, lambda m: _create_coupon(m, tb, bot_id, admin_id, _owner_tempmail_kb))
        elif d == "owner_back":
            try:
                tb.edit_message_text("👑 لوحة التحكم", uid, c.message.message_id, reply_markup=_owner_tempmail_kb())
            except:
                tb.send_message(uid, "👑 لوحة التحكم", reply_markup=_owner_tempmail_kb())


def _tm_create(tb, uid, c, svc, bot_id):
    if svc == "random":
        svc = random.choice(SVC_LIST)
    name = SVC_NAMES.get(svc, svc)
    try:
        tb.edit_message_text(f"⏳ جاري إنشاء بريد من {name}...", uid, c.message.message_id)
    except:
        pass
    res = mail_engine.create(svc)
    if not res:
        fallbacks = [s for s in SVC_LIST if s != svc]
        random.shuffle(fallbacks)
        for fb in fallbacks:
            res = mail_engine.create(fb)
            if res:
                svc = fb
                name = SVC_NAMES.get(svc, svc)
                break
    if not res:
        try:
            tb.edit_message_text("❌ جميع خدمات البريد غير متاحة حالياً.", uid, c.message.message_id, reply_markup=_tm_svc_kb())
        except:
            pass
        return
    email = res["email"]
    token = res.get("token")
    expires_at = (datetime.datetime.now() + datetime.timedelta(hours=24)).isoformat()
    db.q("INSERT OR REPLACE INTO mail_sessions (user_id, bot_id, email, svc, token, created_at, expires_at) VALUES (?,?,?,?,?,?,?)",
         (uid, bot_id, email, svc, token, datetime.datetime.now().isoformat(), expires_at))
    db.q("UPDATE hosted_bots SET last_activity=? WHERE id=?", (datetime.datetime.now().isoformat(), bot_id))
    try:
        tb.edit_message_text(
            f"✅ تم إنشاء البريد!\n━━━━━━━━━━━━━━━\n📧 العنوان:\n`{email}`\n\n⚙️ الخدمة: {name}\n⏰ يصلح لـ 24 ساعة\n━━━━━━━━━━━━━━━\n💡 اضغط 'فحص' لتحديث الرسائل",
            uid, c.message.message_id, parse_mode="Markdown", reply_markup=_tm_main_kb(email, svc)
        )
    except:
        pass


def _tm_inbox(tb, uid, c, svc, bot_id):
    r = db.f("SELECT email, svc, token FROM mail_sessions WHERE user_id=? AND bot_id=?", (uid, bot_id))
    if not r:
        tb.answer_callback_query(c.id, "❌ ليس لديك بريد! أنشئ واحداً.", show_alert=True)
        return
    email, email_svc, token = r
    name = SVC_NAMES.get(email_svc, email_svc)
    try:
        tb.edit_message_text(f"🔍 جاري فحص البريد من {name}...", uid, c.message.message_id)
    except:
        pass
    msgs = mail_engine.fetch(email, email_svc, token)
    db.q("UPDATE mail_sessions SET last_checked=?, message_count=? WHERE user_id=? AND bot_id=?",
         (datetime.datetime.now().isoformat(), len(msgs) if msgs else 0, uid, bot_id))
    if msgs is None:
        try:
            tb.edit_message_text(f"❌ {name} غير متاحة. حاول تجديد البريد.", uid, c.message.message_id, reply_markup=_tm_main_kb(email, email_svc))
        except:
            pass
        return
    if not msgs:
        try:
            tb.edit_message_text(
                f"📧 `{email}`\n━━━━━━━━━━━━━━━\n📭 لا يوجد رسائل\n\n⏰ تحقق: {datetime.datetime.now().strftime('%H:%M:%S')}",
                uid, c.message.message_id, parse_mode="Markdown", reply_markup=_tm_main_kb(email, email_svc)
            )
        except:
            pass
        return
    txt = f"📧 `{email}`\n⚙️ {name}\n📬 {len(msgs)} رسالة\n━━━━━━━━━━━━━━━\n"
    for i, msg_data in enumerate(msgs[:5], 1):
        fr = (msg_data.get("from", "") or "مجهول")[:30]
        sb = (msg_data.get("sub", "") or "بدون عنوان")[:40]
        bd = (msg_data.get("body", "") or "")[:200]
        if len(bd) == 200:
            bd += "..."
        t = (msg_data.get("time", "") or "")[:16]
        txt += f"📩 {i} | 👤 {fr}\n📌 {sb}\n💬 {bd}\n📅 {t}\n━━━━━━━━━━━━━━━\n"
    if len(msgs) > 5:
        txt += f"📌 و {len(msgs)-5} رسالة إضافية..."
    try:
        tb.edit_message_text(txt, uid, c.message.message_id, parse_mode="Markdown", reply_markup=_tm_main_kb(email, email_svc))
    except:
        try:
            tb.edit_message_text(txt[:4000], uid, c.message.message_id, reply_markup=_tm_main_kb(email, email_svc))
        except:
            pass


def _tm_info(tb, uid, c, bot_id):
    r = db.f("SELECT email, svc, created_at, expires_at, message_count FROM mail_sessions WHERE user_id=? AND bot_id=?", (uid, bot_id))
    if r:
        e, s, t, exp, mc = r
        n = SVC_NAMES.get(s, s)
        try:
            tb.edit_message_text(
                f"📊 معلومات بريدك\n━━━━━━━━━━━━━━━\n📧 العنوان:\n`{e}`\n\n⚙️ الخدمة: {n}\n📬 الرسائل المستلمة: {mc or 0}\n📅 أنشئ: {t[:16] if t else '-'}\n⏰ ينتهي: {exp[:16] if exp else 'غير محدود'}\n🆔 معرفك: {uid}",
                uid, c.message.message_id, parse_mode="Markdown", reply_markup=_tm_main_kb(e, s)
            )
        except:
            pass
    else:
        try:
            tb.edit_message_text("❌ لا يوجد بريد. أنشئ واحداً!", uid, c.message.message_id, reply_markup=_tm_svc_kb())
        except:
            pass


@bot.callback_query_handler(func=lambda c: c.data == "my_bots")
def _my_bots(c):
    uid = c.from_user.id
    bots_list = db.fa("SELECT id, bot_name, bot_username, bot_type, status, bot_plan_type, total_users, created_at FROM hosted_bots WHERE owner_id=? ORDER BY id DESC", (uid,))
    if not bots_list:
        bot.answer_callback_query(c.id, "❌ لا يوجد بوتات. أنشئ بوتك الأول!")
        return
    k = types.InlineKeyboardMarkup(row_width=1)
    txt = f"🤖 بوتاتك ({len(bots_list)})\n━━━━━━━━━━━━━━━\n"
    for i, (bid, name, username, btype, status, ptype, users, dt) in enumerate(bots_list, 1):
        t = "📨" if btype == "contact" else "🛒" if btype == "shop" else "📧"
        s = "🟢" if status == "active" else "🔴"
        txt += f"{i}. {t} {s} @{username or name}\n👥 {users} مستخدم | {'🌟 مدفوع' if ptype!='free' else '🔶 مجاني'}\n📅 {dt[:10] if dt else '-'}\n━━━━━━━━━━━━━━━\n"
        k.add(types.InlineKeyboardButton(f"{t} @{username or name}", callback_data=f"bot_manage_{bid}"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    bot.edit_message_text(txt, uid, c.message.message_id, reply_markup=k)


@bot.callback_query_handler(func=lambda c: c.data.startswith("bot_manage_"))
def _bot_manage(c):
    uid = c.from_user.id
    bid = int(c.data.split("_")[2])
    b = db.f("SELECT bot_name, bot_username, bot_type, status, total_users, created_at, bot_plan_type, bot_plan_price FROM hosted_bots WHERE id=? AND owner_id=?", (bid, uid))
    if not b:
        bot.answer_callback_query(c.id, "❌ البوت غير موجود")
        return
    name, username, btype, status, users, dt, ptype, pprice = b
    k = types.InlineKeyboardMarkup(row_width=2)
    k.add(types.InlineKeyboardButton("🔴 إيقاف" if status == "active" else "🟢 تشغيل", callback_data=f"bot_toggle_{bid}"),
          types.InlineKeyboardButton("🗑️ حذف البوت", callback_data=f"bot_delete_{bid}"))
    k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="my_bots"))
    bot.edit_message_text(
        f"🤖 {name}\n━━━━━━━━━━━━━━━\n"
        f"📛 @{username or 'غير محدد'}\n"
        f"📦 النوع: {btype}\n"
        f"{'🟢 نشط' if status=='active' else '🔴 متوقف'}\n"
        f"👥 المستخدمين: {users}\n"
        f"💰 الخطة: {'مجاني' if ptype=='free' else f'مدفوع ({pprice}⭐)'}\n"
        f"📅 أنشئ: {dt[:10] if dt else '-'}",
        uid, c.message.message_id, reply_markup=k
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith("bot_toggle_"))
def _bot_toggle(c):
    uid = c.from_user.id
    bid = int(c.data.split("_")[2])
    b = db.f("SELECT status, bot_token, bot_type, owner_id FROM hosted_bots WHERE id=?", (bid,))
    if not b or b[3] != uid:
        bot.answer_callback_query(c.id, "❌ ليس لديك صلاحية")
        return
    status, token, btype, _ = b
    if status == "active":
        db.q("UPDATE hosted_bots SET status='stopped' WHERE id=?", (bid,))
        if token in active_bots:
            try:
                active_bots[token].stop_polling()
            except:
                pass
            del active_bots[token]
        bot.answer_callback_query(c.id, "🔴 تم إيقاف البوت")
    else:
        db.q("UPDATE hosted_bots SET status='active' WHERE id=?", (bid,))
        _launch_bot(token, btype, uid)
        bot.answer_callback_query(c.id, "🟢 تم تشغيل البوت")


@bot.callback_query_handler(func=lambda c: c.data.startswith("bot_delete_"))
def _bot_delete(c):
    uid = c.from_user.id
    bid = int(c.data.split("_")[2])
    b = db.f("SELECT bot_token, owner_id FROM hosted_bots WHERE id=?", (bid,))
    if not b or b[1] != uid:
        bot.answer_callback_query(c.id, "❌ ليس لديك صلاحية")
        return
    token = b[0]
    if token in active_bots:
        try:
            active_bots[token].stop_polling()
        except:
            pass
        del active_bots[token]
    db.q("UPDATE hosted_bots SET status='deleted' WHERE id=?", (bid,))
    bot.answer_callback_query(c.id, "✅ تم حذف البوت")
    bot.edit_message_text("✅ تم حذف البوت بنجاح.", uid, c.message.message_id, reply_markup=_main_kb(uid))


@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
def _adm(c):
    if c.from_user.id != ADMIN_ID:
        return
    a = c.data
    if a == "adm_stats":
        u = db.f("SELECT COUNT(*) FROM users")[0]
        b = db.f("SELECT COUNT(*) FROM hosted_bots WHERE status='active'")[0]
        p = db.f("SELECT SUM(amount) FROM payments WHERE status='completed'")[0] or 0
        prem = db.f("SELECT COUNT(*) FROM users WHERE sub_type!='free'")[0]
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        new_today = db.f("SELECT COUNT(*) FROM users WHERE join_date LIKE ?", (f"{today}%",))[0] or 0
        week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
        active_week = db.f("SELECT COUNT(*) FROM users WHERE last_seen > ?", (week_ago,))[0] or 0
        bot.edit_message_text(
            f"📊 إحصائيات المصنع\n━━━━━━━━━━━━━━━\n"
            f"👥 المستخدمين الكلي: {u}\n"
            f"📅 جديد اليوم: {new_today}\n"
            f"⚡ نشط هذا الأسبوع: {active_week}\n"
            f"🌟 المشتركين المدفوعين: {prem}\n"
            f"🤖 البوتات النشطة: {b}\n"
            f"💰 إجمالي الإيرادات: {p}⭐\n"
            f"📈 معدل التحويل: {round((prem/u)*100, 2) if u else 0}%\n"
            f"━━━━━━━━━━━━━━━\n🔧 v{VERSION} | {DEV_NAME}",
            ADMIN_ID, c.message.message_id, reply_markup=_admin_kb()
        )
    elif a == "adm_broadcast":
        msg = bot.send_message(ADMIN_ID, "📢 أرسل رسالة الإذاعة (نص/صورة/فيديو):")
        bot.register_next_step_handler(msg, _adm_broadcast)
    elif a == "adm_add_stars":
        msg = bot.send_message(ADMIN_ID, "⭐ أرسل: معرف_المستخدم|الكمية|السبب\nمثال: 123456|100|مكافأة")
        bot.register_next_step_handler(msg, _adm_add_stars)
    elif a == "adm_bots":
        bots_list = db.fa("SELECT id, bot_name, bot_username, owner_id, bot_type, status, total_users FROM hosted_bots ORDER BY id DESC LIMIT 20")
        txt = f"🤖 البوتات ({len(bots_list)}):\n━━━━━━━━━━━━━━━\n"
        for bid, name, username, oid, btype, status, users in bots_list:
            s = "🟢" if status == "active" else "🔴"
            txt += f"{s} #{bid} @{username or name} ({btype})\n👤 {oid} | 👥 {users}\n━━━━━━━━━━━━━━━\n"
        bot.send_message(ADMIN_ID, txt or "❌ لا يوجد بوتات", reply_markup=_admin_kb())
    elif a == "adm_users":
        users = db.fa("SELECT user_id, username, first_name, sub_type, stars, join_date FROM users ORDER BY id DESC LIMIT 30")
        txt = f"👥 المستخدمين ({len(users)} أحدث):\n━━━━━━━━━━━━━━━\n"
        for uid, uname, fname, st, stars, jdt in users:
            sub_e = "🌟" if st != "free" else "👤"
            txt += f"{sub_e} {uid} | @{uname or '-'} | {fname}\n{PLAN_NAMES.get(st,'مجاني')} | ⭐{stars} | {jdt[:10] if jdt else '-'}\n━━━━━━━━━━\n"
        k = types.InlineKeyboardMarkup(row_width=2)
        k.add(types.InlineKeyboardButton("🔍 بحث عن مستخدم", callback_data="adm_search_user"),
              types.InlineKeyboardButton("🚫 حظر مستخدم", callback_data="adm_ban_user"))
        k.add(types.InlineKeyboardButton("🔓 رفع حظر", callback_data="adm_unban_user"),
              types.InlineKeyboardButton("🔙 رجوع", callback_data="adm_back"))
        bot.send_message(ADMIN_ID, txt, reply_markup=k)
    elif a == "adm_payments":
        pays = db.fa("SELECT user_id, amount, plan, created_at FROM payments WHERE status='completed' ORDER BY id DESC LIMIT 20")
        total = db.f("SELECT SUM(amount) FROM payments WHERE status='completed'")[0] or 0
        txt = f"💰 المدفوعات\n━━━━━━━━━━━━━━━\n💎 الإجمالي: {total}⭐\n━━━━━━━━━━━━━━━\n"
        for uu, am, pl, dt in pays:
            txt += f"👤{uu} | ⭐{am} | {pl} | {dt[:10]}\n"
        bot.send_message(ADMIN_ID, txt or "❌ لا يوجد مدفوعات", reply_markup=_admin_kb())
    elif a == "adm_tickets":
        tks = db.fa("SELECT id, bot_id, user_id, title, status, created_at FROM tickets ORDER BY id DESC LIMIT 20")
        txt = "🎫 التذاكر:\n━━━━━━━━━━━━━━━\n"
        for tid, tbid, tuid, title, status, dt in tks:
            emoji = "🟢" if status == "open" else "🔵" if status == "replied" else "🔴"
            txt += f"{emoji} #{tid} | بوت#{tbid} | 👤{tuid}\n📝 {title[:30]}\n📅 {dt[:10]}\n━━━━━━━━━━━━━━━\n"
        bot.send_message(ADMIN_ID, txt or "❌ لا يوجد تذاكر", reply_markup=_admin_kb())
    elif a == "adm_analytics":
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        new_today = db.f("SELECT COUNT(*) FROM users WHERE join_date LIKE ?", (f"{today}%",))[0] or 0
        new_yesterday = db.f("SELECT COUNT(*) FROM users WHERE join_date LIKE ?", (f"{yesterday}%",))[0] or 0
        total_bots = db.f("SELECT COUNT(*) FROM hosted_bots WHERE status='active'")[0] or 0
        total_orders = db.f("SELECT COUNT(*) FROM shop_orders WHERE status='delivered'")[0] or 0
        total_mails = db.f("SELECT COUNT(*) FROM mail_sessions")[0] or 0
        growth = round(((new_today - new_yesterday) / new_yesterday * 100), 1) if new_yesterday else 0
        bot.edit_message_text(
            f"📈 التحليلات المتقدمة\n━━━━━━━━━━━━━━━\n"
            f"📅 جديد اليوم: {new_today}\n"
            f"📅 جديد أمس: {new_yesterday}\n"
            f"📊 النمو: {growth:+}%\n"
            f"🤖 بوتات نشطة: {total_bots}\n"
            f"🛒 طلبات مكتملة: {total_orders}\n"
            f"📧 جلسات بريد: {total_mails}",
            ADMIN_ID, c.message.message_id, reply_markup=_admin_kb()
        )
    elif a == "adm_factory_settings":
        settings = db.fa("SELECT key, value FROM factory_settings ORDER BY key")
        txt = "🔧 إعدادات المصنع:\n━━━━━━━━━━━━━━━\n"
        for key, val in settings:
            txt += f"🔹 {key}: {val}\n"
        k = types.InlineKeyboardMarkup(row_width=1)
        k.add(types.InlineKeyboardButton("✏️ تعديل إعداد", callback_data="adm_edit_setting"),
              types.InlineKeyboardButton("🔧 وضع الصيانة", callback_data="adm_toggle_maintenance"))
        k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="adm_back"))
        bot.edit_message_text(txt, ADMIN_ID, c.message.message_id, reply_markup=k)
    elif a == "adm_toggle_maintenance":
        current = db.setting("maintenance", "0")
        new_val = "0" if current == "1" else "1"
        db.set_setting("maintenance", new_val)
        bot.answer_callback_query(c.id, f"{'🔧 وضع الصيانة مفعل' if new_val=='1' else '✅ البوت متاح'}", show_alert=True)
    elif a == "adm_edit_setting":
        msg = bot.send_message(ADMIN_ID, "⚙️ أرسل: المفتاح|القيمة\nمثال: referral_reward|20")
        bot.register_next_step_handler(msg, _adm_edit_setting)
    elif a == "adm_banned":
        banned = db.fa("SELECT user_id, first_name, ban_reason FROM users WHERE banned=1 ORDER BY id DESC LIMIT 20")
        txt = "🚫 المحظورين:\n━━━━━━━━━━━━━━━\n"
        for uid, fname, reason in banned:
            txt += f"🆔 {uid} | {fname or '-'} | {reason or 'لا يوجد سبب'}\n"
        k = types.InlineKeyboardMarkup(row_width=2)
        k.add(types.InlineKeyboardButton("🚫 حظر مستخدم", callback_data="adm_ban_user"),
              types.InlineKeyboardButton("🔓 رفع حظر", callback_data="adm_unban_user"))
        k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="adm_back"))
        bot.send_message(ADMIN_ID, txt or "❌ لا يوجد محظورين", reply_markup=k)
    elif a == "adm_ban_user":
        msg = bot.send_message(ADMIN_ID, "🚫 أرسل معرف المستخدم للحظر (يمكن إضافة سبب: معرف|السبب):")
        bot.register_next_step_handler(msg, _adm_ban)
    elif a == "adm_unban_user":
        msg = bot.send_message(ADMIN_ID, "🔓 أرسل معرف المستخدم لرفع الحظر:")
        bot.register_next_step_handler(msg, _adm_unban)
    elif a == "adm_search_user":
        msg = bot.send_message(ADMIN_ID, "🔍 أرسل معرف المستخدم أو اسم المستخدم:")
        bot.register_next_step_handler(msg, _adm_search_user)
    elif a == "adm_add_announcement":
        msg = bot.send_message(ADMIN_ID, "📣 أرسل الإعلان (عنوان|المحتوى):\nمثال: عروض جديدة|لدينا خصومات حصرية اليوم!")
        bot.register_next_step_handler(msg, _adm_add_announcement)
    elif a == "adm_coupons":
        coupons = db.fa("SELECT code, discount_type, discount_value, used_count, max_uses, active FROM coupons WHERE bot_id=0 ORDER BY id DESC LIMIT 10")
        txt = "🎟️ كوبونات المصنع:\n━━━━━━━━━━━━━━━\n"
        for code, dtype, dval, used, maxu, active in coupons:
            status = "✅" if active else "❌"
            txt += f"{status} {code} | {dval}{'%' if dtype=='percent' else '⭐'} | {used}/{maxu}\n"
        k = types.InlineKeyboardMarkup(row_width=2)
        k.add(types.InlineKeyboardButton("➕ إنشاء كوبون", callback_data="adm_create_coupon"),
              types.InlineKeyboardButton("🗑️ حذف كوبون", callback_data="adm_del_coupon"))
        k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="adm_back"))
        bot.send_message(ADMIN_ID, txt or "❌ لا يوجد كوبونات", reply_markup=k)
    elif a == "adm_create_coupon":
        msg = bot.send_message(ADMIN_ID, "🎟️ إنشاء كوبون للمصنع\nالصيغة: كود|نوع(percent/fixed)|قيمة|عدد\nمثال: FACTORY50|percent|50|100")
        bot.register_next_step_handler(msg, lambda m: _create_coupon(m, bot, 0, ADMIN_ID, _admin_kb))
    elif a == "adm_del_coupon":
        msg = bot.send_message(ADMIN_ID, "🗑️ أرسل كود الكوبون للحذف:")
        bot.register_next_step_handler(msg, _adm_del_coupon)
    elif a == "adm_scheduled":
        sched = db.fa("SELECT id, bot_id, message, scheduled_at, sent FROM scheduled_messages WHERE sent=0 ORDER BY scheduled_at ASC LIMIT 10")
        txt = "📅 الرسائل المجدولة:\n━━━━━━━━━━━━━━━\n"
        for sid, sbid, smsg, sat, sent in sched:
            txt += f"#{sid} | بوت#{sbid}\n💬 {smsg[:50]}\n⏰ {sat[:16]}\n━━━━━━━━━━━━━━━\n"
        bot.send_message(ADMIN_ID, txt or "❌ لا يوجد رسائل مجدولة", reply_markup=_admin_kb())
    elif a == "adm_vip":
        msg = bot.send_message(ADMIN_ID, "💎 ترقية VIP\nأرسل: معرف_المستخدم|عدد_الأيام\nمثال: 123456|30")
        bot.register_next_step_handler(msg, _adm_vip)
    elif a == "adm_logs":
        logs = db.fa("SELECT bot_id, event, details, user_id, created_at FROM bot_logs ORDER BY id DESC LIMIT 20")
        txt = "🗂️ سجل النشاط:\n━━━━━━━━━━━━━━━\n"
        for bid, event, details, uid_l, dt in logs:
            txt += f"#{bid} | {event}\n📝 {details[:50]}\n👤 {uid_l} | {dt[:16]}\n━━━━━━━━━━━━━━━\n"
        bot.send_message(ADMIN_ID, txt or "❌ السجل فارغ", reply_markup=_admin_kb())
    elif a == "adm_factory_store":
        bots_list = db.fa("SELECT bot_name, bot_username, bot_type, total_users FROM hosted_bots WHERE status='active' ORDER BY total_users DESC LIMIT 10")
        txt = "🏪 أفضل بوتات المصنع:\n━━━━━━━━━━━━━━━\n"
        for name, username, btype, users in bots_list:
            t = "📨" if btype == "contact" else "🛒" if btype == "shop" else "📧"
            txt += f"{t} @{username or name} | 👥 {users}\n"
        bot.send_message(ADMIN_ID, txt or "❌ لا يوجد بوتات", reply_markup=_admin_kb())
    elif a == "adm_restart_bots":
        count = 0
        bots_db = db.fa("SELECT bot_token, bot_type, owner_id FROM hosted_bots WHERE status='active'")
        for token, btype, owner_id in bots_db:
            if token not in active_bots:
                _launch_bot(token, btype, owner_id)
                count += 1
        bot.answer_callback_query(c.id, f"✅ تم إعادة تشغيل {count} بوت", show_alert=True)
    elif a == "adm_plans":
        txt = "💳 إدارة الخطط:\n━━━━━━━━━━━━━━━\n"
        for plan, price in PLAN_PRICES.items():
            txt += f"{PLAN_NAMES.get(plan, plan)}: {price}⭐\n"
        k = types.InlineKeyboardMarkup(row_width=1)
        k.add(types.InlineKeyboardButton("✏️ تعديل سعر خطة", callback_data="adm_edit_plan"))
        k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="adm_back"))
        bot.edit_message_text(txt, ADMIN_ID, c.message.message_id, reply_markup=k)
    elif a == "adm_export":
        u = db.f("SELECT COUNT(*) FROM users")[0]
        b = db.f("SELECT COUNT(*) FROM hosted_bots")[0]
        p = db.f("SELECT SUM(amount) FROM payments WHERE status='completed'")[0] or 0
        bot.send_message(ADMIN_ID,
            f"📤 تصدير البيانات\n━━━━━━━━━━━━━━━\n"
            f"👥 مستخدمين: {u}\n"
            f"🤖 بوتات: {b}\n"
            f"💰 إيرادات: {p}⭐\n\n"
            f"📁 ملف قاعدة البيانات: {DB_FILE}",
            reply_markup=_admin_kb()
        )
    elif a == "adm_settings":
        k = types.InlineKeyboardMarkup(row_width=1)
        k.add(types.InlineKeyboardButton("🔧 تعديل إعداد", callback_data="adm_edit_setting"),
              types.InlineKeyboardButton("🔧 وضع الصيانة", callback_data="adm_toggle_maintenance"))
        k.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="adm_back"))
        bot.send_message(ADMIN_ID, "⚙️ إعدادات المصنع:", reply_markup=k)
    elif a == "adm_back":
        try:
            bot.edit_message_text("👑 لوحة التحكم", ADMIN_ID, c.message.message_id, reply_markup=_admin_kb())
        except:
            bot.send_message(ADMIN_ID, "👑 لوحة التحكم", reply_markup=_admin_kb())


def _adm_broadcast(m):
    users = db.fa("SELECT user_id FROM users WHERE banned=0")
    s = f = 0
    for u in users:
        try:
            if m.content_type == "text":
                bot.send_message(u[0], m.text)
            elif m.content_type == "photo":
                bot.send_photo(u[0], m.photo[-1].file_id, caption=m.caption)
            elif m.content_type == "video":
                bot.send_video(u[0], m.video.file_id, caption=m.caption)
            elif m.content_type == "document":
                bot.send_document(u[0], m.document.file_id, caption=m.caption)
            s += 1
            time.sleep(0.05)
        except:
            f += 1
    bot.send_message(ADMIN_ID, f"📢 اكتملت الإذاعة\n✅ نجح: {s}\n❌ فشل: {f}", reply_markup=_admin_kb())


def _adm_add_stars(m):
    try:
        parts = m.text.strip().split("|")
        uid = int(parts[0].strip())
        amount = int(parts[1].strip())
        desc = parts[2].strip() if len(parts) > 2 else "إضافة من الإدارة"
        db.add_stars(uid, amount, desc)
        db.notify(uid, f"تمت إضافة نجوم! ⭐", f"تمت إضافة {amount}⭐ لحسابك")
        bot.send_message(ADMIN_ID, f"✅ تمت إضافة {amount}⭐ للمستخدم {uid}", reply_markup=_admin_kb())
        try:
            bot.send_message(uid, f"⭐ تمت إضافة {amount} نجمة لحسابك!\n📝 {desc}")
        except:
            pass
    except:
        bot.send_message(ADMIN_ID, "❌ خطأ في الصيغة. استخدم: معرف|الكمية|السبب", reply_markup=_admin_kb())


def _adm_ban(m):
    try:
        parts = m.text.strip().split("|")
        uid = int(parts[0].strip())
        reason = parts[1].strip() if len(parts) > 1 else "لا يوجد سبب"
        db.q("UPDATE users SET banned=1, ban_reason=? WHERE user_id=?", (reason, uid))
        bot.send_message(ADMIN_ID, f"✅ تم حظر المستخدم {uid}\n📝 السبب: {reason}", reply_markup=_admin_kb())
        try:
            bot.send_message(uid, f"🚫 تم حظرك من البوت.\n📝 السبب: {reason}")
        except:
            pass
    except:
        bot.send_message(ADMIN_ID, "❌ خطأ. أرسل: معرف|السبب", reply_markup=_admin_kb())


def _adm_unban(m):
    try:
        uid = int(m.text.strip())
        db.q("UPDATE users SET banned=0, ban_reason=NULL WHERE user_id=?", (uid,))
        bot.send_message(ADMIN_ID, f"✅ تم رفع حظر المستخدم {uid}", reply_markup=_admin_kb())
        try:
            bot.send_message(uid, "✅ تم رفع حظرك! يمكنك استخدام البوت الآن.")
        except:
            pass
    except:
        bot.send_message(ADMIN_ID, "❌ معرف غير صالح", reply_markup=_admin_kb())


def _adm_search_user(m):
    query = m.text.strip()
    if query.isdigit():
        u = db.f("SELECT user_id, username, first_name, sub_type, stars, join_date, banned FROM users WHERE user_id=?", (int(query),))
    else:
        uname = query.replace("@", "")
        u = db.f("SELECT user_id, username, first_name, sub_type, stars, join_date, banned FROM users WHERE username=?", (uname,))
    if u:
        uid, uname, fname, st, stars, jdt, banned = u
        bc = db.f("SELECT COUNT(*) FROM hosted_bots WHERE owner_id=?", (uid,))
        bots_count = bc[0] if bc else 0
        k = types.InlineKeyboardMarkup(row_width=2)
        k.add(types.InlineKeyboardButton("⭐ إضافة نجوم", callback_data=f"adm_give_stars_{uid}"),
              types.InlineKeyboardButton("🚫 حظر" if not banned else "🔓 رفع حظر",
                                         callback_data=f"adm_toggle_ban_{uid}"))
        k.add(types.InlineKeyboardButton("💎 ترقية VIP", callback_data=f"adm_give_vip_{uid}"))
        bot.send_message(ADMIN_ID,
            f"👤 معلومات المستخدم\n━━━━━━━━━━━━━━━\n"
            f"🆔 {uid}\n👤 {fname}\n📛 @{uname or '-'}\n"
            f"🌟 {PLAN_NAMES.get(st,'مجاني')}\n⭐ {stars} نجمة\n"
            f"🤖 {bots_count} بوت\n📅 {jdt[:10] if jdt else '-'}\n"
            f"{'🚫 محظور' if banned else '✅ نشط'}",
            reply_markup=k
        )
    else:
        bot.send_message(ADMIN_ID, "❌ المستخدم غير موجود", reply_markup=_admin_kb())


def _adm_add_announcement(m):
    try:
        parts = m.text.strip().split("|", 1)
        title = parts[0].strip()
        content = parts[1].strip() if len(parts) > 1 else title
        expires = (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat()
        db.q("INSERT INTO announcements (bot_id, title, content, created_at, expires_at, active) VALUES (0,?,?,?,?,1)",
             (title, content, datetime.datetime.now().isoformat(), expires))
        bot.send_message(ADMIN_ID, f"✅ تم نشر الإعلان!\n📌 {title}\n📝 {content}", reply_markup=_admin_kb())
    except:
        bot.send_message(ADMIN_ID, "❌ خطأ. الصيغة: العنوان|المحتوى", reply_markup=_admin_kb())


def _adm_del_coupon(m):
    code = m.text.strip().upper()
    db.q("UPDATE coupons SET active=0 WHERE code=? AND bot_id=0", (code,))
    bot.send_message(ADMIN_ID, f"✅ تم تعطيل الكوبون: {code}", reply_markup=_admin_kb())


def _adm_vip(m):
    try:
        parts = m.text.strip().split("|")
        uid = int(parts[0].strip())
        days = int(parts[1].strip())
        exp = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()
        db.q("UPDATE users SET vip=1, vip_expiry=? WHERE user_id=?", (exp, uid))
        bot.send_message(ADMIN_ID, f"✅ تم ترقية {uid} إلى VIP لمدة {days} يوم", reply_markup=_admin_kb())
        try:
            bot.send_message(uid, f"💎 تمت ترقيتك إلى VIP لمدة {days} يوم!")
        except:
            pass
    except:
        bot.send_message(ADMIN_ID, "❌ خطأ. الصيغة: معرف|عدد_الأيام", reply_markup=_admin_kb())


def _adm_edit_setting(m):
    try:
        key, val = m.text.strip().split("|", 1)
        db.set_setting(key.strip(), val.strip())
        bot.send_message(ADMIN_ID, f"✅ تم تحديث الإعداد\n🔹 {key.strip()}: {val.strip()}", reply_markup=_admin_kb())
    except:
        bot.send_message(ADMIN_ID, "❌ خطأ. الصيغة: المفتاح|القيمة", reply_markup=_admin_kb())


def _scheduler_loop():
    while True:
        try:
            now = datetime.datetime.now().isoformat()
            pending = db.fa("SELECT id, bot_id, message FROM scheduled_messages WHERE sent=0 AND scheduled_at <= ?", (now,))
            for sid, sbid, smsg in pending:
                users = db.fa("SELECT user_id FROM bot_subscribers WHERE bot_id=?", (sbid,))
                b_info = db.f("SELECT bot_token FROM hosted_bots WHERE id=?", (sbid,))
                if b_info and b_info[0] in active_bots:
                    tb = active_bots[b_info[0]]
                    for u in users:
                        try:
                            tb.send_message(u[0], f"📅 رسالة مجدولة:\n\n{smsg}")
                            time.sleep(0.05)
                        except:
                            pass
                db.q("UPDATE scheduled_messages SET sent=1 WHERE id=?", (sid,))
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        time.sleep(60)


def _sub_expiry_checker():
    while True:
        try:
            now = datetime.datetime.now().isoformat()
            expired = db.fa("SELECT user_id FROM users WHERE sub_type!='free' AND sub_expiry!='lifetime' AND sub_expiry IS NOT NULL AND sub_expiry < ?", (now,))
            for (uid,) in expired:
                db.q("UPDATE users SET sub_type='free', sub_expiry=NULL WHERE user_id=?", (uid,))
                db.notify(uid, "انتهى اشتراكك! ⚠️", "انتهى اشتراكك. جدد الاشتراك للاستمرار.")
                try:
                    bot.send_message(uid, "⚠️ انتهى اشتراكك!\nجدد اشتراكك للاستمرار في استخدام خدماتنا.", reply_markup=_plans_kb())
                except:
                    pass
        except Exception as e:
            logger.error(f"Expiry checker error: {e}")
        time.sleep(3600)


def _load_existing_bots():
    bots_db = db.fa("SELECT bot_token, bot_type, owner_id FROM hosted_bots WHERE status='active'")
    logger.info(f"Loading {len(bots_db)} existing bots...")
    for token, btype, owner_id in bots_db:
        try:
            _launch_bot(token, btype, owner_id)
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error loading bot: {e}")


if __name__ == "__main__":
    logger.info(f"🚀 {BOT_NAME} v{VERSION} - بدء التشغيل")
    logger.info(f"🔧 {DEV_NAME} | {DEV_LINK}")
    logger.info(f"📢 القنوات الإجبارية: {', '.join(REQUIRED_CHANNELS)}")

    _load_existing_bots()

    scheduler_thread = threading.Thread(target=_scheduler_loop, daemon=True)
    scheduler_thread.start()

    expiry_thread = threading.Thread(target=_sub_expiry_checker, daemon=True)
    expiry_thread.start()

    logger.info("✅ جاهز للعمل - بدء الاستماع للرسائل")

    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            logger.error(f"Main polling error: {e}")
            time.sleep(15)

