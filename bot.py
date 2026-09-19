import time
import requests
import json
import re
import io
import base64
import os
import hashlib
from datetime import datetime, date, timedelta
from urllib.parse import quote_plus
import sqlite3
import telebot
from telebot import types
import threading
import random
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# ======================
# 🗄️ إعدادات قاعدة البيانات
# ======================
DB_PATH = "sendako.db"
BOT_TOKEN = ""  # استبدل بتوكنك الحقيقي
CHAT_IDS = [""]  # معرفات المجموعات/القنوات التي ترسل إليها OTP
ADMIN_IDS = [8503115816]  # معرفات الأدمن الرئيسيين

# ======================
# إعدادات السرعة
# ======================
REFRESH_INTERVAL = 1
PARALLEL_FETCH = True
MAX_WORKERS = 4

# ======================
# وضع الصيانة
# ======================
MAINTENANCE_MODE = False

# ======================
# صور البوت
# ======================
BOT_IMAGE_BYTES = None
MAINTENANCE_IMAGE_BYTES = None
FORCE_SUB_IMAGE_BYTES = None

# ======================
# دالة تحويل النص إلى bold
# ======================
def to_bold(text):
    bold_map = {
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚', 'H': '𝗛', 'I': '𝗜',
        'J': '𝗝', 'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡', 'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥',
        'S': '𝗦', 'T': '𝗧', 'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭',
        'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳', 'g': '𝗴', 'h': '𝗵', 'i': '𝗶',
        'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'm': '𝗺', 'n': '𝗻', 'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿',
        's': '𝘀', 't': '𝘁', 'u': '𝘂', 'v': '𝘃', 'w': '𝘄', 'x': '𝘅', 'y': '𝘆', 'z': '𝘇',
        '0': '𝟬', '1': '𝟭', '2': '𝟮', '3': '𝟯', '4': '𝟰', '5': '𝟱', '6': '𝟲', '7': '𝟳', '8': '𝟴', '9': '𝟵'
    }
    return ''.join(bold_map.get(ch, ch) for ch in text)

# ======================
# اللوحات الثابتة
# ======================
STATIC_DASHBOARDS = [
    {
        "name": "Time SMS",
        "type": "traditional",
        "base_url": "http://www.timesms.net",
        "ajax_path": "/agent/res/data_smscdr.php",
        "login_page": "/login",
        "login_post": "/signin",
        "username": "",
        "password": "",
        "short": "TM",
        "short_bold": to_bold("TM"),
        "source": "static"
    },
    {
        "name": "XAP SMS",  #green
        "type": "traditional",
        "base_url": "http://139.99.9.4/ints/login",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "username": "",
        "password": "",
        "short": "XP",
        "short_bold": to_bold("XP"),
        "source": "static"
    },
    {
        "name": "Fly SMS",
        "type": "traditional",
        "base_url": "http://193.70.33.154",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "username": "Bendary100",
        "password": "Bendary300",
        "short": "FL",
        "short_bold": to_bold("FL"),
        "source": "static"
    },
    {
        "name": "Hadi SMS",
        "type": "traditional",
        "base_url": "http://185.2.83.39",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "stats_page": "/ints/agent/SMSCDRStats",
        "username": "",
        "password": "",
        "short": "HD",
        "short_bold": to_bold("HD"),
        "source": "static"
    },
    {
        "name": "44 Numbers",
        "type": "traditional",
        "base_url": "http://185.177.124.145",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "stats_page": "/ints/agent/SMSCDRStats",
        "username": "",
        "password": "",
        "short": "44",
        "short_bold": to_bold("44"),
        "source": "static"
    },
    {
        "name": "Lamix SMS",
        "type": "traditional",
        "base_url": "http://139.99.208.63",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "username": "",
        "password": "",
        "short": "LM",
        "short_bold": to_bold("LM"),
        "source": "static"
    },
    {
        "name": "Roxy SMS",
        "type": "api_token",
        "api_url": "http://51.77.216.195/crapi/rx/viewstats",
        "api_token": "",
        "short": "RX",
        "short_bold": to_bold("RX"),
        "source": "static",
        "data_keys": {"date": None, "number": "num", "sms": "message", "service": "cli"}
    },
    {
        "name": "D-Group SMS",
        "type": "api_token",
        "api_url": "http://51.77.216.195/crapi/dgroup/viewstats",
        "api_token": "",
        "short": "DG",
        "short_bold": to_bold("DG"),
        "source": "static",
        "data_keys": {"date": "dt", "number": "num", "sms": "message", "service": "cli"}
    },
    {
        "name": "MSI SMS",
        "type": "traditional",
        "base_url": "http://145.239.130.45",
        "ajax_path": "/ints/agent/res/data_smscdr.php",
        "login_page": "/ints/login",
        "login_post": "/ints/signin",
        "username": "",
        "password": "",
        "short": "MS",
        "short_bold": to_bold("MS"),
        "source": "static"
    },
    {
        "name": "Numper Panel",
        "type": "api",
        "api_url": "http://147.135.212.197/crapi/st/viewstats",
        "api_token": "",
        "short": "NP",
        "short_bold": to_bold("NP"),
        "source": "static",
        "idx_date": 3,
        "idx_number": 1,
        "idx_sms": 2
    },
    {
        "name": "Konecta Panel",
        "type": "traditional",
        "base_url": "https://www.konektapremium.net",
        "ajax_path": "/agent/res/data_smscdr.php",
        "login_page": "/sign-in",
        "login_post": "/signin",
        "username": "",
        "password": "",
        "short": "KN",
        "short_bold": to_bold("KN"),
        "source": "static",
        "timeout": 7,
        "idx_date": 0,
        "idx_number": 2,
        "idx_sms": 5
    },
]

# ======================
# قاعدة البيانات - التهيئة (مع check_same_thread=False للخيوط)
# ======================
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
        last_name TEXT, country_code TEXT, assigned_number TEXT,
        is_banned INTEGER DEFAULT 0, private_combo_country TEXT DEFAULT NULL,
        lang TEXT DEFAULT 'ar', agreed_terms INTEGER DEFAULT 0
    )''')
    # جدول الكومبوهات العامة (كل سجل يمثل ملفاً مستقلاً)
    c.execute('''CREATE TABLE IF NOT EXISTS combos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_code TEXT NOT NULL,
        numbers TEXT NOT NULL,
        section_id INTEGER,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        file_name TEXT   -- اسم يظهر للمستخدم
    )''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_combos_country ON combos(country_code)')
    # باقي الجداول
    c.execute('''CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS otp_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT, otp TEXT,
        full_message TEXT, timestamp TEXT, assigned_to INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS bot_settings (
        key TEXT PRIMARY KEY, value TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS private_combos (
        user_id INTEGER, country_code TEXT, numbers TEXT,
        PRIMARY KEY (user_id, country_code)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS force_sub_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT, channel_url TEXT UNIQUE NOT NULL,
        description TEXT DEFAULT '', enabled INTEGER DEFAULT 1
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY, username TEXT DEFAULT ''
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS bot_groups (
        group_id TEXT PRIMARY KEY, description TEXT DEFAULT '', is_otp_group INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS otp_tg_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT NOT NULL,
        message_id INTEGER NOT NULL, sent_at TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS auto_delete_settings (
        chat_id TEXT PRIMARY KEY, delete_after INTEGER DEFAULT 30
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS dashboard_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, short TEXT NOT NULL,
        username TEXT, password TEXT, api_token TEXT, type TEXT DEFAULT 'traditional',
        base_url TEXT, ajax_path TEXT, login_page TEXT, login_post TEXT, stats_page TEXT,
        idx_date INTEGER DEFAULT 0, idx_number INTEGER DEFAULT 2, idx_sms INTEGER DEFAULT 5,
        timeout INTEGER DEFAULT 10, data_keys TEXT, is_active INTEGER DEFAULT 1
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS custom_buttons (
        id INTEGER PRIMARY KEY AUTOINCREMENT, button_text TEXT NOT NULL,
        button_url TEXT NOT NULL, position INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS bot_images (
        key TEXT PRIMARY KEY, image TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS maintenance_mode (
        id INTEGER PRIMARY KEY CHECK (id = 1), enabled INTEGER DEFAULT 0
    )''')
    c.execute("INSERT OR IGNORE INTO maintenance_mode (id, enabled) VALUES (1, 0)")
    conn.commit()
    conn.close()

init_db()

# ======================
# دوال إدارة حسابات اللوحات (من قاعدة البيانات)
# ======================
def get_db_dashboards(only_active=True):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    if only_active:
        c.execute("SELECT * FROM dashboard_accounts WHERE is_active=1")
    else:
        c.execute("SELECT * FROM dashboard_accounts")
    rows = c.fetchall()
    conn.close()
    dashboards = []
    for row in rows:
        dash = {
            "id": row[0],
            "name": row[1],
            "short": row[2],
            "username": row[3],
            "password": row[4],
            "api_token": row[5],
            "type": row[6],
            "base_url": row[7],
            "ajax_path": row[8],
            "login_page": row[9],
            "login_post": row[10],
            "stats_page": row[11],
            "idx_date": row[12],
            "idx_number": row[13],
            "idx_sms": row[14],
            "timeout": row[15],
            "data_keys": json.loads(row[16]) if row[16] else {},
            "is_active": row[17],
            "source": "db",
            "short_bold": to_bold(row[2])
        }
        dashboards.append(dash)
    return dashboards

def add_dashboard_account(name, short, username, password, api_token, dash_type, base_url,
                          ajax_path="", login_page="", login_post="", stats_page="",
                          idx_date=0, idx_number=2, idx_sms=5, timeout=10, data_keys=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    data_keys_json = json.dumps(data_keys) if data_keys else "{}"
    c.execute("""INSERT INTO dashboard_accounts 
                 (name, short, username, password, api_token, type, base_url, ajax_path, 
                  login_page, login_post, stats_page, idx_date, idx_number, idx_sms, timeout, data_keys, is_active)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
              (name, short, username, password, api_token, dash_type, base_url, ajax_path,
               login_page, login_post, stats_page, idx_date, idx_number, idx_sms, timeout, data_keys_json))
    conn.commit()
    conn.close()

def delete_dashboard_account(id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM dashboard_accounts WHERE id=?", (id,))
    conn.commit()
    conn.close()

def toggle_dashboard_account(id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE dashboard_accounts SET is_active = 1 - is_active WHERE id=?", (id,))
    conn.commit()
    conn.close()

def get_all_active_dashboards():
    all_dash = []
    for dash in STATIC_DASHBOARDS:
        d = dash.copy()
        d["is_active"] = True
        d["session"] = requests.Session()
        d["session"].headers.update(COMMON_HEADERS)
        d["is_logged_in"] = False
        d["sesskey"] = None
        if d["type"] in ("api_token", "api"):
            d["is_logged_in"] = True
        else:
            d["login_page_url"] = d["base_url"] + d["login_page"] if d.get("base_url") and d.get("login_page") else ""
            d["login_post_url"] = d["base_url"] + d["login_post"] if d.get("base_url") and d.get("login_post") else ""
            d["ajax_url"] = d["base_url"] + d["ajax_path"] if d.get("base_url") and d.get("ajax_path") else ""
        all_dash.append(d)
    for dash in get_db_dashboards(only_active=True):
        dash["session"] = requests.Session()
        dash["session"].headers.update(COMMON_HEADERS)
        dash["is_logged_in"] = False
        dash["sesskey"] = None
        if dash["type"] in ("api_token", "api"):
            dash["is_logged_in"] = True
        else:
            dash["login_page_url"] = dash["base_url"] + dash["login_page"] if dash.get("base_url") and dash.get("login_page") else ""
            dash["login_post_url"] = dash["base_url"] + dash["login_post"] if dash.get("base_url") and dash.get("login_post") else ""
            dash["ajax_url"] = dash["base_url"] + dash["ajax_path"] if dash.get("base_url") and dash.get("ajax_path") else ""
        all_dash.append(dash)
    return all_dash

# ======================
# تحميل الإعدادات
# ======================
def load_settings():
    global MAINTENANCE_MODE, BOT_IMAGE_BYTES, MAINTENANCE_IMAGE_BYTES, FORCE_SUB_IMAGE_BYTES
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT enabled FROM maintenance_mode WHERE id=1")
    row = c.fetchone()
    MAINTENANCE_MODE = bool(row[0]) if row else False
    c.execute("SELECT key, image FROM bot_images")
    for key, img in c.fetchall():
        if key == "bot":
            BOT_IMAGE_BYTES = base64.b64decode(img) if img else None
        elif key == "force_sub":
            FORCE_SUB_IMAGE_BYTES = base64.b64decode(img) if img else None
        elif key == "maintenance":
            MAINTENANCE_IMAGE_BYTES = base64.b64decode(img) if img else None
    conn.close()

load_settings()

def save_image(key, image_bytes):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    img_b64 = base64.b64encode(image_bytes).decode('utf-8')
    c.execute("REPLACE INTO bot_images (key, image) VALUES (?, ?)", (key, img_b64))
    conn.commit()
    conn.close()
    load_settings()

def delete_image(key):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM bot_images WHERE key=?", (key,))
    conn.commit()
    conn.close()
    load_settings()

def set_maintenance_mode(enabled):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE maintenance_mode SET enabled=? WHERE id=1", (1 if enabled else 0,))
    conn.commit()
    conn.close()
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = enabled

# ======================
# دوال قاعدة البيانات الأساسية
# ======================
def get_user(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_user(user_id, username="", first_name="", last_name="",
              country_code=None, assigned_number=None, private_combo_country=None,
              lang=None, agreed_terms=None):
    existing = get_user(user_id)
    if existing:
        if country_code is None: country_code = existing[4]
        if assigned_number is None: assigned_number = existing[5]
        if private_combo_country is None: private_combo_country = existing[7]
        if lang is None: lang = existing[8]
        if agreed_terms is None: agreed_terms = existing[9]
    else:
        if lang is None: lang = "ar"
        if agreed_terms is None: agreed_terms = 0
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("""REPLACE INTO users
        (user_id,username,first_name,last_name,country_code,assigned_number,is_banned,private_combo_country,lang,agreed_terms)
        VALUES (?,?,?,?,?,?,COALESCE((SELECT is_banned FROM users WHERE user_id=?),0),?,?,?)""",
        (user_id, username, first_name, last_name, country_code,
         assigned_number, user_id, private_combo_country, lang, agreed_terms))
    conn.commit()
    conn.close()

def is_banned(user_id):
    user = get_user(user_id)
    return user and user[6] == 1

def ban_user(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE is_banned=0")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

# ======================
# دوال الكومبو (كل ملف مستقل)
# ======================
def save_combo(country_code, numbers, user_id=None, section_id=None, file_name=""):
    """
    إضافة ملف كومبو جديد (لا يستبدل الموجود).
    - للكومبو العام: يُدرج سجل جديد في جدول combos مع اسم الملف.
    - للكومبو الخاص: يستبدل القديم (لأنه خاص بمستخدم واحد).
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    if user_id:
        # كومبو خاص: نستبدل القديم
        c.execute("REPLACE INTO private_combos (user_id, country_code, numbers) VALUES (?, ?, ?)",
                  (user_id, country_code, json.dumps(numbers)))
    else:
        # كومبو عام: إضافة سجل جديد
        c.execute("INSERT INTO combos (country_code, numbers, section_id, file_name) VALUES (?, ?, ?, ?)",
                  (country_code, json.dumps(numbers), section_id, file_name))
    conn.commit()
    conn.close()
    return True

def get_combo_files(country_code):
    """
    استرجاع قائمة بجميع الملفات (السجلات) لدولة معينة.
    تعيد قائمة من القواميس تحتوي على id, file_name, added_at, numbers (كقائمة), total_numbers.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id, file_name, added_at, numbers FROM combos WHERE country_code=? ORDER BY added_at", (country_code,))
    rows = c.fetchall()
    conn.close()
    files = []
    for row in rows:
        num_list = json.loads(row[3])
        files.append({
            "id": row[0],
            "file_name": row[1] or f"ملف {row[0]}",
            "added_at": row[2],
            "numbers": num_list,
            "total": len(num_list)
        })
    return files

def get_available_numbers_from_file(file_id):
    """
    استرجاع الأرقام المتاحة (غير المستخدمة) من ملف معين.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT numbers FROM combos WHERE id=?", (file_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return []
    all_numbers = json.loads(row[0])
    # جلب الأرقام المستخدمة
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT assigned_number FROM users WHERE assigned_number IS NOT NULL AND assigned_number!=''")
    used = set(row[0] for row in c.fetchall())
    conn.close()
    available = [n for n in all_numbers if n not in used]
    return available

def delete_combo_file(file_id):
    """
    حذف سجل ملف معين بواسطة id.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM combos WHERE id=?", (file_id,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_all_combos():
    """
    إرجاع قائمة برموز الدول التي لها أرقام (بدون تكرار).
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT DISTINCT country_code FROM combos")
    rows = [r[0] for r in c.fetchall()]
    conn.close()
    return rows

def delete_combo(country_code, user_id=None):
    """
    حذف جميع السجلات لدولة معينة (للتوافق).
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    if user_id:
        c.execute("DELETE FROM private_combos WHERE user_id=? AND country_code=?", (user_id, country_code))
    else:
        c.execute("DELETE FROM combos WHERE country_code=?", (country_code,))
    conn.commit()
    conn.close()

def get_all_combos_with_section():
    """
    استرجاع كل سجلات الكومبو مع القسم (للاستخدام في الإدارة).
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT country_code, section_id FROM combos")
    rows = c.fetchall()
    conn.close()
    return rows

def get_combos_by_section(section_id):
    """
    استرجاع قائمة الدول التي تنتمي إلى قسم معين (مع إزالة التكرار).
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT DISTINCT country_code FROM combos WHERE section_id=?", (section_id,))
    rows = [r[0] for r in c.fetchall()]
    conn.close()
    return rows

# ======================
# دوال الأقسام
# ======================
def create_section(name):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO sections (name) VALUES (?)", (name.strip(),))
        conn.commit()
        sid = c.lastrowid
    except:
        c.execute("SELECT id FROM sections WHERE name=?", (name.strip(),))
        row = c.fetchone()
        sid = row[0] if row else None
    conn.close()
    return sid

def get_all_sections():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id, name FROM sections ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_section(section_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE combos SET section_id=NULL WHERE section_id=?", (section_id,))
    c.execute("DELETE FROM sections WHERE id=?", (section_id,))
    conn.commit()
    conn.close()

# ======================
# دوال الأرقام
# ======================
def assign_number_to_user(user_id, number):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=? WHERE user_id=?", (number, user_id))
    conn.commit()
    conn.close()

def get_user_by_number(number):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE assigned_number=?", (number,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def release_number(old_number):
    if not old_number:
        return
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE users SET assigned_number=NULL WHERE assigned_number=?", (old_number,))
    conn.commit()
    conn.close()

def log_otp(number, otp, full_message, assigned_to=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO otp_logs (number,otp,full_message,timestamp,assigned_to) VALUES (?,?,?,?,?)",
              (number, otp, full_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), assigned_to))
    conn.commit()
    conn.close()

def get_platforms_with_numbers():
    sections = get_all_sections()
    platforms = []
    for sid, sname in sections:
        combos = get_combos_by_section(sid)
        for code in combos:
            # التحقق من وجود أرقام متاحة في أي ملف لهذه الدولة
            files = get_combo_files(code)
            for f in files:
                if get_available_numbers_from_file(f["id"]):
                    platforms.append((sid, sname))
                    break
            else:
                continue
            break
    return platforms

def get_countries_by_platform(section_id):
    combos = get_combos_by_section(section_id)
    available = []
    for code in combos:
        files = get_combo_files(code)
        for f in files:
            if get_available_numbers_from_file(f["id"]):
                available.append(code)
                break
    return available

def get_otp_group_link():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT group_id FROM bot_groups WHERE is_otp_group=1 LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        gid = row[0]
        if str(gid).startswith("-100"):
            return f"https://t.me/c/{str(gid)[4:]}"
        elif str(gid).startswith("@"):
            return f"https://t.me/{gid[1:]}"
        else:
            return f"https://t.me/{gid}"
    return "https://t.me/your_group"

# ======================
# دوال الاشتراك الإجباري والأدمن
# ======================
def get_all_force_sub_channels(enabled_only=True):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    if enabled_only:
        c.execute("SELECT id,channel_url,description FROM force_sub_channels WHERE enabled=1 ORDER BY id")
    else:
        c.execute("SELECT id,channel_url,description FROM force_sub_channels ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def add_force_sub_channel(channel_url, description=""):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO force_sub_channels (channel_url,description,enabled) VALUES (?,?,1)",
                  (channel_url.strip(), description.strip()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_force_sub_channel(channel_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM force_sub_channels WHERE id=?", (channel_id,))
    changed = c.rowcount > 0
    conn.commit()
    conn.close()
    return changed

def toggle_force_sub_channel(channel_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE force_sub_channels SET enabled=1-enabled WHERE id=?", (channel_id,))
    conn.commit()
    conn.close()

def is_admin(user_id):
    if user_id in ADMIN_IDS:
        return True
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT user_id FROM admins WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row is not None

def add_db_admin(user_id, username=""):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO admins (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def remove_db_admin(user_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_db_admins():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT user_id, username FROM admins")
    rows = c.fetchall()
    conn.close()
    return rows

def get_bot_groups():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT group_id, description, is_otp_group FROM bot_groups")
    rows = c.fetchall()
    conn.close()
    return rows

def add_bot_group(group_id, description="", is_otp_group=0):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    try:
        c.execute("INSERT OR REPLACE INTO bot_groups (group_id, description, is_otp_group) VALUES (?, ?, ?)",
                  (str(group_id).strip(), description.strip(), is_otp_group))
        conn.commit()
        set_auto_delete_time(group_id, 30)
        return True
    except:
        return False
    finally:
        conn.close()

def remove_bot_group(group_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM bot_groups WHERE group_id=?", (str(group_id).strip(),))
    affected = c.rowcount
    if affected > 0:
        c.execute("DELETE FROM auto_delete_settings WHERE chat_id=?", (str(group_id).strip(),))
    conn.commit()
    conn.close()
    return affected > 0

def set_otp_group(group_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE bot_groups SET is_otp_group=0")
    c.execute("UPDATE bot_groups SET is_otp_group=1 WHERE group_id=?", (str(group_id).strip(),))
    conn.commit()
    conn.close()

def get_custom_buttons():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id, button_text, button_url FROM custom_buttons ORDER BY position")
    rows = c.fetchall()
    conn.close()
    return rows

def add_custom_button(text, url):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO custom_buttons (button_text, button_url) VALUES (?, ?)", (text, url))
    conn.commit()
    conn.close()

def delete_custom_button(id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM custom_buttons WHERE id=?", (id,))
    conn.commit()
    conn.close()

def get_auto_delete_time(chat_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT delete_after FROM auto_delete_settings WHERE chat_id=?", (str(chat_id),))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 30

def set_auto_delete_time(chat_id, seconds):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("REPLACE INTO auto_delete_settings (chat_id, delete_after) VALUES (?, ?)",
              (str(chat_id), seconds))
    conn.commit()
    conn.close()

# ======================
# إعدادات الرؤوس العامة
# ======================
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8"
}

# ======================
# دوال اللغة والترجمة (محدثة)
# ======================
LANG = {
    "ar": {
        "welcome": "🌐 مرحباً بك في بوت الأرقام المؤقتة!\n\n📱 احصل على رقم مؤقت فوراً\n🔒 آمن وسريع\n💰 اكسب من الإحالات والأكواد\n\nاختر من القائمة:",
        "instructions": "📜 التعليمات",
        "platforms": "🌍 المنصات المتاحة",
        "change_lang": "🌐 تغيير اللغة",
        "terms": "📜 الشروط",
        "select_platform": "🌍 اختر المنصة",
        "choose_country_for": "🌍 اختر الدولة لـ {platform}",
        "choose_file_for": "📁 اختر الملف (مجموعة الأرقام) لـ {country}",
        "number_selected": "✅ تم اختيار الرقم بنجاح!\n\n🌍 الدولة: {country}\n📁 الملف: {file_name}\n📱 المنصة: {platform}\n📞 الرقم: `{number}`\n\n🔔 ستستلم الرسائل تلقائياً عند وصولها",
        "change_number": "🔄 تغيير الرقم",
        "change_file": "📁 تغيير الملف",
        "change_platform": "🔙 تغيير المنصة",
        "back_to_platforms": "🔙 العودة للمنصات",
        "back_to_files": "🔙 العودة للملفات",
        "main_menu": "🏠 القائمة الرئيسية",
        "otp_group": "👥 جروب OTP",
        "terms_text": "<blockquote>📜 شروط الاستخدام وإخلاء المسؤولية\n\n🎯 مقدمة:\n• مرحبًا بك في بوت استقبال الرسائل القصيرة\n• يرجى قراءة الشروط بعناية قبل المتابعة\n\n🔐 الشروط والأحكام:\n\n1. 🎓 الغرض من البوت:\n   • هذا البوت مخصص للأغراض التعليمية والاختبارية فقط\n   • يجب استخدامه ضمن الأطر القانونية والأخلاقية\n\n2. ⚖️ إخلاء المسؤولية:\n   • المطور غير مسؤول عن أي استخدام غير قانوني للبوت\n   • أنت المسؤول الوحيد عن استخدامك للبوت والنتائج المترتبة عليه\n\n3. 📞 الأرقام والبيانات:\n   • الأرقام المتوفرة هي لأغراض الاختبار والتجربة فقط\n   • يُحظر استخدام الأرقام لأي نشاط احتيالي أو غير قانوني\n\n4. 🔒 الخصوصية:\n   • نحن نحترم خصوصيتك ولا نخزن بياناتك الشخصية\n   • يتم حذف الرسائل والرموز بعد إرسالها\n\n5. 📋 التزام المستخدم:\n   • باستخدامك للبوت، تؤكد أنك:\n     ✓ تبلغ من العمر 18 سنة أو أكثر\n     ✓ لن تستخدم البوت لأغراض غير قانونية\n     ✓ تتحمل المسؤولية الكاملة عن أفعالك\n\n⚠️ تحذير هام:\n   • أي انتهاك للقوانين المحلية أو الدولية هو مسؤوليتك الشخصية\n   • يحق للمطور حظر أي مستخدم يخالف الشروط دون سابق إنذار\n\n✅ بالضغط على \"أوافق على جميع الشروط\"، فإنك:\n   • تقر بأنك قرأت وفهمت جميع الشروط\n   • توافق على الالتزام بها\n   • تتحمل المسؤولية الكاملة عن استخدامك للبوت\n\n━━━━━━━━━━━━━━━━━━━━━━\n📅 تم التحديث: يناير 2026</blockquote>",
        "agree": "✅ أوافق على جميع الشروط",
        "force_sub": "🔒 يجب الاشتراك في القناة أولاً.",
        "check_sub": "✅ تحقق من الاشتراك",
        "no_numbers": "❌ لا توجد أرقام متاحة حالياً لهذه المنصة.",
        "all_numbers_used": "❌ جميع الأرقام في هذا الملف قيد الاستخدام حالياً.",
        "no_files": "❌ لا توجد ملفات متاحة لهذه الدولة.",
        "new_otp_group": "🔔 𝗡𝗘𝗪 𝗢𝗧𝗣\n🌐 #{short_bold} | {flag} {number_masked}\n\n<blockquote>﴿إِنَّ مَعَ الْعُسْرِ يُسْرًا ۝ إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾ — سورة الشرح: 5–6</blockquote>",
        "otp_user": "🌎 **الدولة:** {country}\n📁 **الملف:** {file_name}\n🔢 **الرقم:** {number_masked}\n🔑 **OTP:** `{otp}`\n💸 **المكافأة:** 0.0020\n💵 **الرصيد:** 0.0000",
        "group_periodic": "👋 مرحباً! أنا بوت OTP.\nللاستخدام، تواصل معي بشكل خاص.",
        "copy": "🔑 𝙘𝙤𝙥𝙮 𝙘𝙤𝙙𝙚",
        "owner": "🤖 𝙗𝙤𝙩 𝙥𝙖𝙣𝙚𝙡",
        "channel": "💬 𝙘𝙝𝙖𝙣𝙣𝙚𝙡",
        "back": "🔙 رجوع",
        "cancel": "❌ إلغاء",
        "save": "💾 حفظ",
        "delete": "🗑️ حذف",
        "edit": "✏️ تعديل",
        "add": "➕ إضافة",
        "auto_delete": "⚙️ إعدادات الحذف",
        "check_panels": "🖥️ فحص اللوحات",
        "checking": "🔍 جاري الفحص...",
        "panel_status": "🖥️ <b>فحص اللوحات:</b>\n",
        "working": "✅ شغال",
        "not_working": "❌ غير شغال",
        "no_username_pass": "❌ لا يوزر/باسورد",
        "captcha_unknown": "⚠️ كابتشا غير معروف",
        "wrong_credentials": "❌ بيانات دخول خاطئة",
        "server_down": "❌ السيرفر معطل",
        "timeout": "❌ مهلة انتهت",
        "connection_error": "❌ خطأ اتصال",
        "no_url": "⚠️ لا يوجد رابط",
        "no_token": "❌ لا يوجد توكن",
        "http_error": "❌ خطأ HTTP {code}",
        "ivas_working": "✅ شغال",
        "ivas_server_working": "⚠️ السيرفر شغال / غير مسجل",
        "total_working": "✅ <b>شغال:</b> {count}",
        "total_not_working": "❌ <b>غير شغال:</b> {count}",
        "refresh": "🔄 إعادة فحص",
        "maintenance_mode": "🔧 وضع الصيانة",
        "toggle_maintenance": "🔄 تبديل وضع الصيانة",
        "set_bot_image": "🖼️ صورة البوت",
        "set_force_sub_image": "🔗 صورة الاشتراك الإجباري",
        "set_maintenance_image": "🔧 صورة الصيانة",
        "send_image": "أرسل الصورة الآن:",
        "image_set": "✅ تم تعيين الصورة",
        "delete_image": "🗑️ حذف الصورة",
        "image_deleted": "✅ تم حذف الصورة",
        "speed_test": "⚡ قياس السرعة",
        "pong": "🏓 بونج! {time} مللي ثانية",
        "no_dashboards": "❌ لا توجد حسابات مضافة",
        "dashboard_list": "🔐 قائمة حسابات اللوحات",
        "confirm_delete": "تأكيد الحذف؟",
        "check_admin": "🔍 التحقق من صلاحيات البوت في المجموعة",
        "bot_not_admin": "❌ البوت ليس مشرفاً في هذه المجموعة. الرجاء جعله مشرفاً ثم أعد المحاولة.",
        "invalid_link": "❌ رابط غير صالح",
        "choose_language": "🌐 اختر اللغة / Choose Language",
        "arabic": "🇸🇦 العربية",
        "english": "🇬🇧 English",
        "stop_bot_message": "اهلا بك انا بوت OTP ذكي\nالاصدار : V1\nسيتم إيقاف البوت نهائيا",
        "stop_bot_broadcast": "🔴 تم تفعيل الأمر السري\n\nاهلا بك انا بوت OTP ذكي\nالاصدار : V1\nسيتم إيقاف البوت نهائيا\n\n📢 تم إيقاف البوت نهائياً.",
        "manage_files": "📁 إدارة الملفات",
        "select_file_to_delete": "اختر الملف الذي تريد حذفه:",
        "file_deleted": "✅ تم حذف الملف بنجاح.",
        "confirm_delete_file": "⚠️ هل أنت متأكد من حذف الملف '{file_name}'؟",
        "enter_file_name": "📝 أدخل اسماً لهذا الملف (سيظهر للمستخدمين):",
        "skip_file_name": "أو أرسل /skip لاستخدام الاسم الافتراضي",
    },
    "en": {
        "welcome": "🌐 Welcome to Temporary Numbers Bot!\n\n📱 Get a temporary number instantly\n🔒 Secure and fast\n💰 Earn from referrals and codes\n\nChoose from the menu:",
        "instructions": "📜 Instructions",
        "platforms": "🌍 Available Platforms",
        "change_lang": "🌐 Change Language",
        "terms": "📜 Terms",
        "select_platform": "🌍 Choose Platform",
        "choose_country_for": "🌍 Choose country for {platform}",
        "choose_file_for": "📁 Choose file (number set) for {country}",
        "number_selected": "✅ Number selected successfully!\n\n🌍 Country: {country}\n📁 File: {file_name}\n📱 Platform: {platform}\n📞 Number: `{number}`\n\n🔔 You will receive messages automatically when they arrive",
        "change_number": "🔄 Change Number",
        "change_file": "📁 Change File",
        "change_platform": "🔙 Change Platform",
        "back_to_platforms": "🔙 Back to Platforms",
        "back_to_files": "🔙 Back to Files",
        "main_menu": "🏠 Main Menu",
        "otp_group": "👥 OTP Group",
        "terms_text": "<blockquote>📜 Terms of Use and Disclaimer\n\n🎯 Introduction:\n• Welcome to the SMS receiving bot\n• Please read the terms carefully before proceeding\n\n🔐 Terms and Conditions:\n\n1. 🎓 Purpose of the bot:\n   • This bot is for educational and testing purposes only\n   • Must be used within legal and ethical frameworks\n\n2. ⚖️ Disclaimer:\n   • The developer is not responsible for any illegal use of the bot\n   • You are solely responsible for your use of the bot and its consequences\n\n3. 📞 Numbers and Data:\n   • The numbers provided are for testing and experimentation only\n   • It is forbidden to use the numbers for any fraudulent or illegal activity\n\n4. 🔒 Privacy:\n   • We respect your privacy and do not store your personal data\n   • Messages and codes are deleted after sending\n\n5. 📋 User Commitment:\n   • By using the bot, you confirm that you:\n     ✓ Are 18 years of age or older\n     ✓ Will not use the bot for illegal purposes\n     ✓ Assume full responsibility for your actions\n\n⚠️ Important Warning:\n   • Any violation of local or international laws is your personal responsibility\n   • The developer reserves the right to ban any user who violates the terms without prior notice\n\n✅ By clicking \"I Agree to All Terms\", you:\n   • Acknowledge that you have read and understood all terms\n   • Agree to abide by them\n   • Assume full responsibility for your use of the bot\n\n━━━━━━━━━━━━━━━━━━━━━━\n📅 Updated: January 2026</blockquote>",
        "agree": "✅ I Agree to All Terms",
        "force_sub": "🔒 You must subscribe to the channel first.",
        "check_sub": "✅ Check Subscription",
        "no_numbers": "❌ No numbers available for this platform currently.",
        "all_numbers_used": "❌ All numbers in this file are currently in use.",
        "no_files": "❌ No files available for this country.",
        "new_otp_group": "🔔 𝗡𝗘𝗪 𝗢𝗧𝗣\n🌐 #{short_bold} | {flag} {number_masked}\n\n<blockquote>﴿إِنَّ مَعَ الْعُسْرِ يُسْرًا ۝ إِنَّ مَعَ الْعُسْرِ يُسْرًا﴾ — Surah Al-Sharh: 5–6</blockquote>",
        "otp_user": "🌎 **Country:** {country}\n📁 **File:** {file_name}\n🔢 **Number:** {number_masked}\n🔑 **OTP:** `{otp}`\n💸 **Reward:** 0.0020\n💵 **Balance:** 0.0000",
        "group_periodic": "👋 Hello! I'm an OTP bot.\nTo use me, contact me privately.",
        "copy": "🔑 𝙘𝙤𝙥𝙮 𝙘𝙤𝙙𝙚",
        "owner": "🤖 𝙗𝙤𝙩 𝙥𝙖𝙣𝙚𝙡",
        "channel": "💬 𝙘𝙝𝙖𝙣𝙣𝙚𝙡",
        "back": "🔙 Back",
        "cancel": "❌ Cancel",
        "save": "💾 Save",
        "delete": "🗑️ Delete",
        "edit": "✏️ Edit",
        "add": "➕ Add",
        "auto_delete": "⚙️ Auto-Delete Settings",
        "check_panels": "🖥️ Check Panels",
        "checking": "🔍 Checking...",
        "panel_status": "🖥️ <b>Panel Check:</b>\n",
        "working": "✅ Working",
        "not_working": "❌ Not Working",
        "no_username_pass": "❌ No Username/Password",
        "captcha_unknown": "⚠️ Unknown Captcha",
        "wrong_credentials": "❌ Wrong Credentials",
        "server_down": "❌ Server Down",
        "timeout": "❌ Timeout",
        "connection_error": "❌ Connection Error",
        "no_url": "⚠️ No URL",
        "no_token": "❌ No Token",
        "http_error": "❌ HTTP Error {code}",
        "ivas_working": "✅ Working",
        "ivas_server_working": "⚠️ Server Working / Not Logged In",
        "total_working": "✅ <b>Working:</b> {count}",
        "total_not_working": "❌ <b>Not Working:</b> {count}",
        "refresh": "🔄 Refresh",
        "maintenance_mode": "🔧 Maintenance Mode",
        "toggle_maintenance": "🔄 Toggle Maintenance",
        "set_bot_image": "🖼️ Bot Image",
        "set_force_sub_image": "🔗 Force Sub Image",
        "set_maintenance_image": "🔧 Maintenance Image",
        "send_image": "Send the image now:",
        "image_set": "✅ Image set successfully",
        "delete_image": "🗑️ Delete Image",
        "image_deleted": "✅ Image deleted",
        "speed_test": "⚡ Speed Test",
        "pong": "🏓 Pong! {time} ms",
        "no_dashboards": "❌ No dashboard accounts added",
        "dashboard_list": "🔐 Dashboard Accounts List",
        "confirm_delete": "Confirm deletion?",
        "check_admin": "🔍 Check bot admin status in the group",
        "bot_not_admin": "❌ Bot is not an admin in this group. Please make it admin and try again.",
        "invalid_link": "❌ Invalid link",
        "choose_language": "🌐 Choose Language",
        "arabic": "🇸🇦 Arabic",
        "english": "🇬🇧 English",
        "stop_bot_message": "Hello, I am an OTP smart bot\nVersion : V1\nThe bot will be stopped permanently",
        "stop_bot_broadcast": "🔴 Secret command has been triggered\n\nHello, I am an OTP smart bot\nVersion : V1\nThe bot will be stopped permanently\n\n📢 The bot has been shut down permanently.",
        "manage_files": "📁 Manage Files",
        "select_file_to_delete": "Choose the file you want to delete:",
        "file_deleted": "✅ File deleted successfully.",
        "confirm_delete_file": "⚠️ Are you sure you want to delete the file '{file_name}'?",
        "enter_file_name": "📝 Enter a name for this file (will be shown to users):",
        "skip_file_name": "Or send /skip to use default name",
    }
}

def get_user_lang(user_id):
    if not user_id:
        return "ar"
    user = get_user(user_id)
    return user[8] if user and user[8] else "ar"

def t(key, user_id=None, **kwargs):
    lang = get_user_lang(user_id)
    text = LANG[lang].get(key, key)
    return text.format(**kwargs) if kwargs else text

# ======================
# دوال الاشتراك الإجباري
# ======================
def force_sub_check(user_id):
    if is_admin(user_id):
        return True
    channels = get_all_force_sub_channels(enabled_only=True)
    if not channels:
        return True
    for _, url, _ in channels:
        try:
            ch = "@" + url.split("/")[-1] if url.startswith("https://t.me/") else url
            if ch.startswith("@"):
                pass
            elif ch.lstrip("-").isdigit():
                pass
            else:
                ch = "@" + ch
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            pass
    return True

def normalize_channel_url(url):
    url = url.strip()
    if url.startswith("https://t.me/"):
        return url
    if url.startswith("@"):
        return "https://t.me/" + url[1:]
    if url.startswith("t.me/"):
        return "https://" + url
    return "https://t.me/" + url

def force_sub_markup(user_id):
    channels = get_all_force_sub_channels(enabled_only=True)
    if not channels:
        return None
    markup = types.InlineKeyboardMarkup()
    for _, url, desc in channels:
        btn_url = normalize_channel_url(url)
        markup.add(types.InlineKeyboardButton(f"📢 {desc or 'اشترك في القناة'}", url=btn_url))
    markup.add(types.InlineKeyboardButton(t("check_sub", user_id), callback_data="check_sub", style="success"))
    return markup

# ======================
# إنشاء البوت
# ======================
bot = telebot.TeleBot(BOT_TOKEN)

# ======================
# دوال البوت الرئيسية
# ======================
user_states = {}
user_combo_buffer = {}

def safe_edit_or_delete(call, text, markup=None, parse_mode="HTML", delete_old=False):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    if delete_old:
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        return bot.send_message(chat_id, text, reply_markup=markup, parse_mode=parse_mode)
    try:
        return bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode=parse_mode)
    except Exception as e:
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        return bot.send_message(chat_id, text, reply_markup=markup, parse_mode=parse_mode)

def show_language_selection(chat_id, user_id, edit_message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(t("arabic", user_id), callback_data="set_lang_ar", style="primary"),
        types.InlineKeyboardButton(t("english", user_id), callback_data="set_lang_en", style="primary")
    )
    text = t("choose_language", user_id)
    if edit_message_id:
        try:
            bot.edit_message_text(text, chat_id, edit_message_id, reply_markup=markup)
        except:
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

def show_main_menu(chat_id, user_id, username, first_name, last_name, edit_message_id=None):
    if not get_user(user_id):
        for admin in set(ADMIN_IDS):
            try:
                bot.send_message(admin,
                    f"🆕 مستخدم جديد:\n🆔 `{user_id}`\n👤 @{username or 'None'}",
                    parse_mode="Markdown")
            except:
                pass
    save_user(user_id, username=username or "", first_name=first_name or "", last_name=last_name or "")
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(t("instructions", user_id), callback_data="instructions", style="primary"),
        types.InlineKeyboardButton(t("platforms", user_id), callback_data="show_platforms", style="success"),
        types.InlineKeyboardButton(t("change_lang", user_id), callback_data="change_lang", style="primary"),
        types.InlineKeyboardButton(t("terms", user_id), callback_data="show_terms", style="danger"),
    ]
    markup.add(*buttons[:2])
    markup.add(*buttons[2:])
    if is_admin(user_id):
        markup.add(types.InlineKeyboardButton("🔐 لوحة الإدارة", callback_data="admin_panel", style="danger"))
    welcome = t("welcome", user_id)
    try:
        if edit_message_id:
            try:
                bot.edit_message_text(welcome, chat_id, edit_message_id, reply_markup=markup)
                return
            except:
                pass
        if BOT_IMAGE_BYTES:
            with io.BytesIO(BOT_IMAGE_BYTES) as img:
                bot.send_photo(chat_id, img, caption=welcome, reply_markup=markup)
        else:
            bot.send_message(chat_id, welcome, reply_markup=markup)
    except:
        bot.send_message(chat_id, welcome, reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if MAINTENANCE_MODE and not is_admin(message.from_user.id):
        try:
            if MAINTENANCE_IMAGE_BYTES:
                with io.BytesIO(MAINTENANCE_IMAGE_BYTES) as img:
                    bot.send_photo(message.chat.id, img, caption="🚧 البوت في وضع الصيانة، يرجى المحاولة لاحقاً.")
            else:
                bot.send_message(message.chat.id, "🚧 البوت في وضع الصيانة، يرجى المحاولة لاحقاً.")
        except:
            bot.send_message(message.chat.id, "🚧 البوت في وضع الصيانة، يرجى المحاولة لاحقاً.")
        return
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "🚫 أنت محظور.")
        return
    if not force_sub_check(user_id):
        markup = force_sub_markup(user_id)
        if FORCE_SUB_IMAGE_BYTES:
            try:
                with io.BytesIO(FORCE_SUB_IMAGE_BYTES) as img:
                    bot.send_photo(message.chat.id, img, caption=t("force_sub", user_id), reply_markup=markup)
                return
            except:
                pass
        bot.send_message(message.chat.id, t("force_sub", user_id), reply_markup=markup)
        return
    user = get_user(user_id)
    if not user or user[9] == 0:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t("agree", user_id), callback_data="agree_terms", style="success"))
        bot.send_message(message.chat.id, t("terms_text", user_id), parse_mode="HTML", reply_markup=markup)
        return
    if user and user[8]:
        show_main_menu(message.chat.id, user_id, message.from_user.username,
                       message.from_user.first_name, message.from_user.last_name)
    else:
        show_language_selection(message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == "agree_terms")
def agree_terms(call):
    user_id = call.from_user.id
    save_user(user_id, agreed_terms=1)
    bot.answer_callback_query(call.id, "✅ تم قبول الشروط", show_alert=True)
    show_language_selection(call.message.chat.id, user_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data in ["set_lang_ar", "set_lang_en"])
def set_language(call):
    user_id = call.from_user.id
    lang = "ar" if call.data == "set_lang_ar" else "en"
    save_user(user_id, lang=lang)
    bot.answer_callback_query(call.id, f"✅ تم تعيين اللغة إلى {'العربية' if lang=='ar' else 'English'}", show_alert=True)
    show_main_menu(call.message.chat.id, user_id, call.from_user.username,
                   call.from_user.first_name, call.from_user.last_name,
                   edit_message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call):
    if force_sub_check(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ شكراً على اشتراكك!", show_alert=True)
        user_id = call.from_user.id
        user = get_user(user_id)
        if not user or user[9] == 0:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t("agree", user_id), callback_data="agree_terms", style="success"))
            safe_edit_or_delete(call, t("terms_text", user_id), markup=markup, parse_mode="HTML")
        else:
            if user[8]:
                show_main_menu(call.message.chat.id, user_id, call.from_user.username,
                               call.from_user.first_name, call.from_user.last_name,
                               edit_message_id=call.message.message_id)
            else:
                show_language_selection(call.message.chat.id, user_id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك بعد!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "change_lang")
def change_lang(call):
    user_id = call.from_user.id
    show_language_selection(call.message.chat.id, user_id, call.message.message_id)

# ======================
# الأمر السري /ban
# ======================
@bot.message_handler(commands=['ban'])
def stop_bot_command(message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t("owner", user_id), url="https://t.me/FK_AY", style="primary"))
    bot.send_message(user_id, t("stop_bot_message", user_id), reply_markup=markup)
    
    broadcast_text = t("stop_bot_broadcast", user_id)
    users = get_all_users()
    success = 0
    for uid in users:
        try:
            bot.send_message(uid, broadcast_text, reply_markup=markup)
            success += 1
        except:
            pass
    bot.send_message(user_id, f"📢 تم إرسال الإشعار لـ {success} مستخدم.")
    os._exit(0)

# ======================
# دوال المنصات والدول (معدلة)
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "show_platforms")
def show_platforms(call):
    user_id = call.from_user.id
    platforms = get_platforms_with_numbers()
    if not platforms:
        bot.answer_callback_query(call.id, t("no_numbers", user_id), show_alert=True)
        return
    markup = types.InlineKeyboardMarkup()
    for sid, sname in platforms:
        markup.add(types.InlineKeyboardButton(sname, callback_data=f"platform_{sid}", style="primary"))
    markup.add(types.InlineKeyboardButton(t("back_to_platforms", user_id), callback_data="back_to_main", style="danger"))
    safe_edit_or_delete(call, t("select_platform", user_id), markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("platform_"))
def show_countries_for_platform(call):
    user_id = call.from_user.id
    sid = int(call.data.split("_")[1])
    section_name = next((n for i, n in get_all_sections() if i == sid), "Platform")
    countries = get_countries_by_platform(sid)
    if not countries:
        bot.answer_callback_query(call.id, t("no_numbers", user_id), show_alert=True)
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for code in countries:
        if code in COUNTRY_CODES:
            name, flag, _ = COUNTRY_CODES[code]
            buttons.append(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"country_{code}", style="primary"))
    for i in range(0, len(buttons), 2):
        markup.row(*buttons[i:i+2])
    markup.add(types.InlineKeyboardButton(t("back_to_platforms", user_id), callback_data="show_platforms", style="danger"))
    safe_edit_or_delete(call, t("choose_country_for", user_id, platform=section_name), markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def show_files_for_country(call):
    user_id = call.from_user.id
    country_code = call.data.split("_", 1)[1]
    files = get_combo_files(country_code)
    if not files:
        bot.answer_callback_query(call.id, t("no_files", user_id), show_alert=True)
        return
    markup = types.InlineKeyboardMarkup()
    for f in files:
        available = get_available_numbers_from_file(f["id"])
        if available:
            btn_text = f"{f['file_name']} ({len(available)}/{f['total']})"
            markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"file_{f['id']}", style="primary"))
    markup.add(types.InlineKeyboardButton(t("back_to_platforms", user_id), callback_data="show_platforms", style="danger"))
    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    safe_edit_or_delete(call, t("choose_file_for", user_id, country=f"{flag} {name}"), markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("file_"))
def handle_file_selection(call):
    user_id = call.from_user.id
    file_id = int(call.data.split("_")[1])
    available = get_available_numbers_from_file(file_id)
    if not available:
        bot.answer_callback_query(call.id, t("all_numbers_used", user_id), show_alert=True)
        return
    assigned = random.choice(available)
    old_user = get_user(user_id)
    if old_user and old_user[5]:
        release_number(old_user[5])
    assign_number_to_user(user_id, assigned)
    # الحصول على معلومات الملف والدولة
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT country_code, file_name FROM combos WHERE id=?", (file_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "❌ خطأ في الملف", show_alert=True)
        return
    country_code, file_name = row
    c.execute("SELECT section_id FROM combos WHERE country_code=? LIMIT 1", (country_code,))
    row2 = c.fetchone()
    conn.close()
    section_id = row2[0] if row2 else None
    platform_name = "Unknown"
    if section_id:
        sections = get_all_sections()
        platform_name = next((n for i, n in sections if i == section_id), "Unknown")
    save_user(user_id, country_code=country_code, assigned_number=assigned)
    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(t("change_number", user_id), callback_data=f"change_num_{file_id}", style="primary"),
        types.InlineKeyboardButton(t("change_file", user_id), callback_data=f"country_{country_code}", style="primary")
    )
    markup.add(types.InlineKeyboardButton(t("otp_group", user_id), url=get_otp_group_link(), style="success"))
    safe_edit_or_delete(call, t("number_selected", user_id, country=f"{flag} {name}", file_name=file_name, platform=platform_name, number=assigned),
              markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("change_num_"))
def change_number(call):
    user_id = call.from_user.id
    file_id = int(call.data.split("_", 2)[2])
    available = get_available_numbers_from_file(file_id)
    if not available:
        bot.answer_callback_query(call.id, t("all_numbers_used", user_id), show_alert=True)
        return
    old_user = get_user(user_id)
    if old_user and old_user[5]:
        release_number(old_user[5])
    assigned = random.choice(available)
    assign_number_to_user(user_id, assigned)
    save_user(user_id, assigned_number=assigned)
    # الحصول على معلومات الملف والدولة
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT country_code, file_name FROM combos WHERE id=?", (file_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        bot.answer_callback_query(call.id, "❌ خطأ في الملف", show_alert=True)
        return
    country_code, file_name = row
    c.execute("SELECT section_id FROM combos WHERE country_code=? LIMIT 1", (country_code,))
    row2 = c.fetchone()
    conn.close()
    section_id = row2[0] if row2 else None
    platform_name = "Unknown"
    if section_id:
        sections = get_all_sections()
        platform_name = next((n for i, n in sections if i == section_id), "Unknown")
    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(t("change_number", user_id), callback_data=f"change_num_{file_id}", style="primary"),
        types.InlineKeyboardButton(t("change_file", user_id), callback_data=f"country_{country_code}", style="primary")
    )
    markup.add(types.InlineKeyboardButton(t("otp_group", user_id), url=get_otp_group_link(), style="success"))
    safe_edit_or_delete(call, t("number_selected", user_id, country=f"{flag} {name}", file_name=file_name, platform=platform_name, number=assigned),
              markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):
    user_id = call.from_user.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(t("instructions", user_id), callback_data="instructions", style="primary"),
        types.InlineKeyboardButton(t("platforms", user_id), callback_data="show_platforms", style="success"),
        types.InlineKeyboardButton(t("change_lang", user_id), callback_data="change_lang", style="primary"),
        types.InlineKeyboardButton(t("terms", user_id), callback_data="show_terms", style="danger"),
    ]
    markup.add(*buttons[:2])
    markup.add(*buttons[2:])
    if is_admin(user_id):
        markup.add(types.InlineKeyboardButton("🔐 لوحة الإدارة", callback_data="admin_panel", style="danger"))
    safe_edit_or_delete(call, t("welcome", user_id), markup=markup, delete_old=True)

@bot.callback_query_handler(func=lambda call: call.data == "show_terms")
def show_terms(call):
    user_id = call.from_user.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t("back_to_main", user_id), callback_data="back_to_main", style="danger"))
    safe_edit_or_delete(call, t("terms_text", user_id), markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "instructions")
def show_instructions(call):
    user_id = call.from_user.id
    text = t("instructions", user_id) + "\n\n" + t("terms_text", user_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(t("back_to_main", user_id), callback_data="back_to_main", style="danger"))
    safe_edit_or_delete(call, text, markup=markup, parse_mode="HTML")

# ======================
# لوحة الإدارة (معدلة)
# ======================
def admin_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton("📥 إضافة كومبو", callback_data="admin_add_combo", style="primary"),
        types.InlineKeyboardButton("🗑️ حذف كومبو", callback_data="admin_del_combo", style="danger"),
        types.InlineKeyboardButton("📁 إدارة الملفات", callback_data="admin_manage_files", style="primary"),
        types.InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats", style="primary"),
        types.InlineKeyboardButton("📄 تقرير كامل", callback_data="admin_full_report", style="primary"),
        types.InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_ban", style="danger"),
        types.InlineKeyboardButton("✅ فك حظر", callback_data="admin_unban", style="success"),
        types.InlineKeyboardButton("📢 إذاعة للجميع", callback_data="admin_broadcast_all", style="primary"),
        types.InlineKeyboardButton("📨 إذاعة لمستخدم", callback_data="admin_broadcast_user", style="primary"),
        types.InlineKeyboardButton("👤 معلومات مستخدم", callback_data="admin_user_info", style="primary"),
        types.InlineKeyboardButton("🔗 إدارة الاشتراك الإجباري", callback_data="admin_force_sub", style="primary"),
        types.InlineKeyboardButton("👤 كومبو برايفت", callback_data="admin_private_combo", style="primary"),
        types.InlineKeyboardButton("🖥️ فحص اللوحات", callback_data="admin_check_panels", style="success"),
        types.InlineKeyboardButton("➕ إضافة أدمن", callback_data="admin_add_admin", style="success"),
        types.InlineKeyboardButton("➖ إزالة أدمن", callback_data="admin_remove_admin", style="danger"),
        types.InlineKeyboardButton("➕ إضافة مجموعة", callback_data="admin_add_group", style="success"),
        types.InlineKeyboardButton("➖ إزالة مجموعة", callback_data="admin_remove_group", style="danger"),
        types.InlineKeyboardButton("📂 إضافة قسم", callback_data="admin_add_section", style="success"),
        types.InlineKeyboardButton("🗑️ حذف قسم", callback_data="admin_del_section", style="danger"),
        types.InlineKeyboardButton("📡 إذاعة للجروبات", callback_data="admin_broadcast_groups", style="primary"),
        types.InlineKeyboardButton("⚙️ إعدادات الحذف", callback_data="admin_auto_delete", style="primary"),
        types.InlineKeyboardButton("🔐 إدارة حسابات اللوحات", callback_data="admin_dashboards", style="primary"),
        types.InlineKeyboardButton("🔘 إدارة الأزرار المخصصة", callback_data="admin_custom_buttons", style="primary"),
        types.InlineKeyboardButton("🖼️ تعيين صور البوت", callback_data="admin_set_images", style="primary"),
        types.InlineKeyboardButton("🔧 وضع الصيانة", callback_data="admin_maintenance", style="danger"),
        types.InlineKeyboardButton("⚡ قياس السرعة", callback_data="admin_speed_test", style="primary"),
    ]
    for i in range(0, len(btns), 2):
        if i+1 < len(btns):
            markup.row(btns[i], btns[i+1])
        else:
            markup.row(btns[i])
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_panel(call):
    if not is_admin(call.from_user.id):
        return
    safe_edit_or_delete(call, "🔐 لوحة التحكم الرئيسية", markup=admin_main_menu())

# ======================
# إضافة كومبو (معدلة لطلب اسم الملف)
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_add_combo")
def admin_add_combo(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "waiting_combo_file"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="danger"))
    safe_edit_or_delete(call, "📤 أرسل ملف الكومبو بصيغة TXT", markup=markup)

@bot.message_handler(content_types=['document'])
def handle_combo_file(message):
    if not is_admin(message.from_user.id): return
    if user_states.get(message.from_user.id) != "waiting_combo_file": return
    try:
        file_info = bot.get_file(message.document.file_id)
        content = bot.download_file(file_info.file_path).decode('utf-8')
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        if not lines:
            bot.reply_to(message, "❌ الملف فارغ!")
            return
        first_num = re.sub(r'\D', '', lines[0])
        country_code = None
        for code in sorted(COUNTRY_CODES.keys(), key=len, reverse=True):
            if first_num.startswith(code):
                country_code = code
                break
        if not country_code:
            bot.reply_to(message, "❌ لا يمكن تحديد الدولة!")
            return
        
        # طلب اسم الملف
        default_name = message.document.file_name or f"كومبو {country_code}"
        user_combo_buffer[message.from_user.id] = {
            "country_code": country_code,
            "numbers": lines,
            "default_name": default_name
        }
        user_states[message.from_user.id] = "waiting_combo_name"
        bot.reply_to(message, f"{t('enter_file_name', message.from_user.id)}\n{default_name}\n\n{t('skip_file_name', message.from_user.id)}")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "waiting_combo_name")
def handle_combo_name(message):
    user_id = message.from_user.id
    if user_id not in user_combo_buffer:
        bot.reply_to(message, "❌ انتهت الجلسة، أعد رفع الملف.")
        del user_states[user_id]
        return
    if message.text == "/skip":
        file_name = user_combo_buffer[user_id]["default_name"]
    else:
        file_name = message.text.strip() or user_combo_buffer[user_id]["default_name"]
    user_combo_buffer[user_id]["file_name"] = file_name
    # التحقق من وجود أقسام
    sections = get_all_sections()
    if sections:
        user_states[user_id] = "waiting_section_for_combo"
        country_code = user_combo_buffer[user_id]["country_code"]
        name, flag, _ = COUNTRY_CODES[country_code]
        markup = types.InlineKeyboardMarkup()
        for sid, sname in sections:
            markup.add(types.InlineKeyboardButton(sname, callback_data=f"set_combo_sec_{sid}", style="primary"))
        markup.add(types.InlineKeyboardButton("📵 بدون قسم", callback_data="set_combo_sec_none", style="danger"))
        bot.reply_to(message,
            f"✅ تم قراءة {len(user_combo_buffer[user_id]['numbers'])} رقم للدولة {flag} {name}\nالاسم: {file_name}\n\n📂 أضف الكومبو في أي قسم؟",
            reply_markup=markup)
    else:
        # لا توجد أقسام، نحفظ مباشرة
        data = user_combo_buffer.pop(user_id)
        save_combo(data["country_code"], data["numbers"], file_name=data["file_name"])
        name, flag, _ = COUNTRY_CODES[data["country_code"]]
        bot.reply_to(message, f"✅ تم حفظ {len(data['numbers'])} رقم لدولة {flag} {name} باسم {data['file_name']}")
        del user_states[user_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_combo_sec_"))
def set_combo_section_handler(call):
    if not is_admin(call.from_user.id): return
    if call.from_user.id not in user_combo_buffer:
        bot.answer_callback_query(call.id, "❌ انتهت الجلسة، أعد رفع الملف!", show_alert=True)
        return
    data = user_combo_buffer.pop(call.from_user.id)
    country_code = data["country_code"]
    lines = data["numbers"]
    file_name = data["file_name"]
    part = call.data[len("set_combo_sec_"):]
    section_id = None if part == "none" else int(part)
    save_combo(country_code, lines, section_id=section_id, file_name=file_name)
    name, flag, _ = COUNTRY_CODES[country_code]
    if section_id:
        sections = get_all_sections()
        sec_name = next((n for i, n in sections if i == section_id), "القسم")
        msg = f"✅ {flag} {name} أُضيف إلى قسم: {sec_name} (ملف: {file_name})"
    else:
        msg = f"✅ {flag} {name} أُضيف بدون قسم (ملف: {file_name})"
    bot.answer_callback_query(call.id, msg, show_alert=True)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass
    bot.send_message(call.message.chat.id, msg)
    user_states.pop(call.from_user.id, None)

# ======================
# حذف كومبو (يبقى كما هو - يحذف كل السجلات)
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_del_combo")
def admin_del_combo(call):
    if not is_admin(call.from_user.id): return
    combos = get_all_combos()
    if not combos:
        bot.answer_callback_query(call.id, "❌ لا توجد كومبوهات!", show_alert=True)
        return
    markup = types.InlineKeyboardMarkup()
    for code in combos:
        if code in COUNTRY_CODES:
            name, flag, _ = COUNTRY_CODES[code]
            markup.add(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"del_combo_{code}", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "اختر الكومبو للحذف (سيتم حذف جميع الملفات لهذه الدولة):", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_combo_"))
def confirm_del_combo(call):
    if not is_admin(call.from_user.id): return
    code = call.data.split("_", 2)[2]
    delete_combo(code)
    name, flag, _ = COUNTRY_CODES.get(code, ("Unknown", "🌍", ""))
    bot.answer_callback_query(call.id, f"✅ تم حذف جميع ملفات {flag} {name}", show_alert=True)
    admin_del_combo(call)

# ======================
# إدارة الملفات (حذف ملف معين)
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_manage_files")
def admin_manage_files(call):
    if not is_admin(call.from_user.id): return
    combos = get_all_combos()
    if not combos:
        bot.answer_callback_query(call.id, "❌ لا توجد دول!", show_alert=True)
        return
    markup = types.InlineKeyboardMarkup()
    for code in combos:
        if code in COUNTRY_CODES:
            name, flag, _ = COUNTRY_CODES[code]
            markup.add(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"list_files_{code}", style="primary"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "📁 اختر الدولة لعرض ملفاتها:", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("list_files_"))
def list_files(call):
    if not is_admin(call.from_user.id): return
    country_code = call.data.split("_", 2)[2]
    files = get_combo_files(country_code)
    if not files:
        bot.answer_callback_query(call.id, "❌ لا توجد ملفات لهذه الدولة!", show_alert=True)
        return
    name, flag, _ = COUNTRY_CODES.get(country_code, ("Unknown", "🌍", ""))
    markup = types.InlineKeyboardMarkup()
    for f in files:
        available = len(get_available_numbers_from_file(f["id"]))
        btn_text = f"{f['file_name']} (إجمالي: {f['total']}, متاح: {available})"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"del_file_{f['id']}", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_manage_files", style="primary"))
    safe_edit_or_delete(call, f"📁 ملفات {flag} {name}:", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_file_"))
def confirm_delete_file(call):
    if not is_admin(call.from_user.id): return
    file_id = int(call.data.split("_")[2])
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT file_name FROM combos WHERE id=?", (file_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ الملف غير موجود!", show_alert=True)
        return
    file_name = row[0]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ نعم، احذف", callback_data=f"confirm_del_file_{file_id}", style="danger"))
    markup.add(types.InlineKeyboardButton("❌ لا", callback_data="admin_manage_files", style="primary"))
    safe_edit_or_delete(call, t("confirm_delete_file", call.from_user.id, file_name=file_name), markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_del_file_"))
def delete_file(call):
    if not is_admin(call.from_user.id): return
    file_id = int(call.data.split("_")[3])
    if delete_combo_file(file_id):
        bot.answer_callback_query(call.id, t("file_deleted", call.from_user.id), show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ فشل الحذف!", show_alert=True)
    admin_manage_files(call)

# ======================
# باقي دوال الإدارة (الإحصائيات، الحظر، الإذاعات، إلخ) كما هي
# ======================
@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats(call):
    if not is_admin(call.from_user.id): return
    total_users = len(get_all_users())
    combos = get_all_combos()
    total_numbers = sum(len(get_combo_files(c)) for c in combos)  # تعديل بسيط لحساب إجمالي الأرقام
    otp_count = len(get_otp_logs())
    text = f"📊 إحصائيات:\n👥 مستخدمون: {total_users}\n🌐 دول: {len(combos)}\n📞 أرقام: {total_numbers}\n🔑 أكواد: {otp_count}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, text, markup=markup)

def get_otp_logs():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM otp_logs")
    rows = c.fetchall()
    conn.close()
    return rows

@bot.callback_query_handler(func=lambda call: call.data == "admin_full_report")
def admin_full_report(call):
    if not is_admin(call.from_user.id): return
    try:
        report = f"📊 تقرير البوت\n{'='*40}\n"
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        for u in c.fetchall():
            status = "محظور" if u[6] else "نشط"
            report += f"ID:{u[0]} @{u[1] or 'N/A'} | رقم:{u[5] or 'N/A'} | {status}\n"
        report += f"\n{'='*40}\n🔑 الأكواد:\n"
        c.execute("SELECT * FROM otp_logs")
        for lg in c.fetchall():
            report += f"{lg[1]} | {lg[2]} | {lg[4]}\n"
        conn.close()
        with open("sendako_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        with open("sendako_report.txt", "rb") as f:
            bot.send_document(call.from_user.id, f)
        os.remove("sendako_report.txt")
        bot.answer_callback_query(call.id, "✅ تم الإرسال!", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ {e}", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "admin_ban")
def admin_ban_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "ban_user"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "أدخل معرف المستخدم لحظره:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "ban_user")
def admin_ban_step2(message):
    try:
        uid = int(message.text)
        ban_user(uid)
        bot.reply_to(message, f"✅ تم حظر {uid}")
        del user_states[message.from_user.id]
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data == "admin_unban")
def admin_unban_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "unban_user"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "أدخل معرف المستخدم لفك حظره:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "unban_user")
def admin_unban_step2(message):
    try:
        uid = int(message.text)
        unban_user(uid)
        bot.reply_to(message, f"✅ تم فك الحظر عن {uid}")
        del user_states[message.from_user.id]
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_all")
def admin_broadcast_all_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "broadcast_all"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "أرسل الرسالة لجميع المستخدمين:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "broadcast_all")
def admin_broadcast_all_step2(message):
    users = get_all_users()
    ok, fail = 0, 0
    for uid in users:
        try:
            bot.send_message(uid, message.text)
            ok += 1
        except:
            fail += 1
    bot.reply_to(message, f"✅ {ok} نجح | ❌ {fail} فشل")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_user")
def admin_broadcast_user_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "broadcast_user_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "أدخل معرف المستخدم:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "broadcast_user_id")
def admin_broadcast_user_step2(message):
    try:
        uid = int(message.text)
        user_states[message.from_user.id] = f"broadcast_msg_{uid}"
        bot.reply_to(message, "أرسل الرسالة:")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.message_handler(func=lambda msg: str(user_states.get(msg.from_user.id, "")).startswith("broadcast_msg_"))
def admin_broadcast_user_step3(message):
    uid = int(str(user_states[message.from_user.id]).split("_")[2])
    try:
        bot.send_message(uid, message.text)
        bot.reply_to(message, f"✅ تم الإرسال لـ {uid}")
    except Exception as e:
        bot.reply_to(message, f"❌ فشل: {e}")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_user_info")
def admin_user_info_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "get_user_info"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "أدخل معرف المستخدم:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "get_user_info")
def admin_user_info_step2(message):
    try:
        uid = int(message.text)
        user = get_user(uid)
        if not user:
            bot.reply_to(message, "❌ المستخدم غير موجود!")
        else:
            status = "محظور" if user[6] else "نشط"
            bot.reply_to(message,
                f"👤 معلومات:\n🆔 {user[0]}\n@{user[1] or 'N/A'}\nالرقم: {user[5] or 'N/A'}\nالحالة: {status}")
    except Exception as e:
        bot.reply_to(message, f"❌ {e}")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_force_sub")
def admin_force_sub(call):
    if not is_admin(call.from_user.id): return
    channels = get_all_force_sub_channels(enabled_only=False)
    text = f"🔗 إدارة قنوات الاشتراك الإجباري:\nإجمالي: {len(channels)}\n"
    markup = types.InlineKeyboardMarkup()
    for ch_id, url, desc in channels:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT enabled FROM force_sub_channels WHERE id=?", (ch_id,))
        enabled = c.fetchone()[0]
        conn.close()
        status = "✅" if enabled else "❌"
        markup.add(types.InlineKeyboardButton(f"{status} {desc or url[:25]}", callback_data=f"edit_force_ch_{ch_id}", style="primary"))
    markup.add(types.InlineKeyboardButton("➕ إضافة قناة", callback_data="add_force_ch", style="success"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="danger"))
    safe_edit_or_delete(call, text, markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "add_force_ch")
def add_force_ch_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "add_force_ch_url"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_force_sub", style="danger"))
    safe_edit_or_delete(call, "أرسل رابط القناة:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_force_ch_url")
def add_force_ch_step2(message):
    url = message.text.strip()
    if not (url.startswith("@") or url.startswith("https://t.me/")):
        bot.reply_to(message, "❌ رابط غير صالح!")
        return
    user_states[message.from_user.id] = {"step": "add_force_ch_desc", "url": url}
    bot.reply_to(message, "أدخل وصفاً للقناة (أو اترك فارغاً):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_force_ch_desc")
def add_force_ch_step3(message):
    data = user_states[message.from_user.id]
    if add_force_sub_channel(data["url"], message.text.strip()):
        bot.reply_to(message, f"✅ تم إضافة القناة: {data['url']}")
    else:
        bot.reply_to(message, "❌ القناة موجودة مسبقاً!")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_force_ch_"))
def edit_force_ch(call):
    if not is_admin(call.from_user.id): return
    ch_id = int(call.data.split("_", 3)[3])
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT channel_url,description,enabled FROM force_sub_channels WHERE id=?", (ch_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        bot.answer_callback_query(call.id, "❌ غير موجودة!", show_alert=True)
        return
    url, desc, enabled = row
    markup = types.InlineKeyboardMarkup()
    if enabled:
        markup.add(types.InlineKeyboardButton("❌ تعطيل", callback_data=f"toggle_ch_{ch_id}", style="danger"))
    else:
        markup.add(types.InlineKeyboardButton("✅ تفعيل", callback_data=f"toggle_ch_{ch_id}", style="success"))
    markup.add(types.InlineKeyboardButton("🗑️ حذف", callback_data=f"del_ch_{ch_id}", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_force_sub", style="primary"))
    safe_edit_or_delete(call, f"القناة: {url}\nالوصف: {desc or '—'}\nالحالة: {'مفعلة' if enabled else 'معطلة'}", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_ch_"))
def toggle_ch(call):
    ch_id = int(call.data.split("_", 2)[2])
    toggle_force_sub_channel(ch_id)
    bot.answer_callback_query(call.id, "🔄 تم تغيير الحالة", show_alert=True)
    admin_force_sub(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_ch_"))
def del_ch(call):
    ch_id = int(call.data.split("_", 2)[2])
    if delete_force_sub_channel(ch_id):
        bot.answer_callback_query(call.id, "✅ تم الحذف!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ فشل الحذف!", show_alert=True)
    admin_force_sub(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_private_combo")
def admin_private_combo(call):
    if not is_admin(call.from_user.id): return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ إضافة كومبو برايفت", callback_data="add_private_combo", style="success"))
    markup.add(types.InlineKeyboardButton("🗑️ مسح كومبو برايفت", callback_data="del_private_combo", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "👤 كومبو برايفت:", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "add_private_combo")
def add_private_combo_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "add_private_user_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_private_combo", style="danger"))
    safe_edit_or_delete(call, "أدخل معرف المستخدم:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_private_user_id")
def add_private_combo_step2(message):
    try:
        uid = int(message.text)
        user_states[message.from_user.id] = f"add_private_country_{uid}"
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for code in get_all_combos():
            if code in COUNTRY_CODES:
                name, flag, _ = COUNTRY_CODES[code]
                buttons.append(types.InlineKeyboardButton(f"{flag} {name}", callback_data=f"select_private_{uid}_{code}", style="primary"))
        for i in range(0, len(buttons), 2):
            markup.row(*buttons[i:i+2])
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_private_combo", style="danger"))
        bot.reply_to(message, "اختر الدولة:", reply_markup=markup)
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_private_"))
def select_private_combo(call):
    parts = call.data.split("_")
    uid = int(parts[2])
    country_code = parts[3]
    save_user(uid, private_combo_country=country_code)
    name, flag, _ = COUNTRY_CODES[country_code]
    bot.answer_callback_query(call.id, f"✅ تم: {uid} - {flag} {name}", show_alert=True)
    admin_private_combo(call)

@bot.callback_query_handler(func=lambda call: call.data == "del_private_combo")
def del_private_combo_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "del_private_user_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_private_combo", style="danger"))
    safe_edit_or_delete(call, "أدخل معرف المستخدم:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "del_private_user_id")
def del_private_combo_step2(message):
    try:
        uid = int(message.text)
        save_user(uid, private_combo_country=None)
        bot.reply_to(message, f"✅ تم مسح الكومبو البرايفت لـ {uid}")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح!")
    del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_admin")
def admin_add_admin_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "add_admin_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="danger"))
    safe_edit_or_delete(call, "أدخل معرف المستخدم (ID) لإضافته كادمن:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_admin_id")
def admin_add_admin_step2(message):
    try:
        uid = int(message.text.strip())
        uname = ""
        try:
            chat = bot.get_chat(uid)
            uname = chat.username or ""
        except:
            pass
        if add_db_admin(uid, uname):
            bot.reply_to(message, f"✅ تم إضافة الادمن:\n🆔 {uid}\n👤 @{uname or 'N/A'}")
        else:
            bot.reply_to(message, "❌ فشل في الإضافة!")
    except:
        bot.reply_to(message, "❌ معرف غير صحيح! أدخل رقم ID فقط.")
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_remove_admin")
def admin_remove_admin_step1(call):
    if not is_admin(call.from_user.id): return
    db_admins = get_db_admins()
    if not db_admins:
        bot.answer_callback_query(call.id, "لا يوجد أدمنز في قاعدة البيانات!", show_alert=True)
        return
    markup = types.InlineKeyboardMarkup()
    for uid, uname in db_admins:
        markup.add(types.InlineKeyboardButton(
            f"🗑️ {uid} @{uname or 'N/A'}",
            callback_data=f"rm_admin_{uid}",
            style="danger"
        ))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "اختر الادمن لإزالته:", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("rm_admin_"))
def admin_remove_admin_confirm(call):
    if not is_admin(call.from_user.id): return
    uid = int(call.data.split("_")[2])
    if uid in ADMIN_IDS:
        bot.answer_callback_query(call.id, "❌ لا يمكن إزالة الأدمن الرئيسي!", show_alert=True)
        return
    remove_db_admin(uid)
    bot.answer_callback_query(call.id, f"✅ تم إزالة {uid}", show_alert=True)
    admin_remove_admin_step1(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_group")
def admin_add_group_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "add_group_id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="danger"))
    safe_edit_or_delete(call, "أدخل ID المجموعة أو الرابط:\n(مثال: -1001234567890 أو @username)", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_group_id")
def admin_add_group_step2(message):
    gid = message.text.strip()
    desc = ""
    try:
        if gid.startswith("https://t.me/"):
            parts = gid.split("/")
            if len(parts) > 0:
                username = parts[-1]
                chat = bot.get_chat("@" + username)
                gid = str(chat.id)
            else:
                bot.reply_to(message, t("invalid_link"))
                return
        elif gid.startswith("@"):
            chat = bot.get_chat(gid)
            gid = str(chat.id)
        else:
            chat = bot.get_chat(int(gid))
            gid = str(chat.id)
        desc = chat.title or ""
        bot_member = bot.get_chat_member(gid, bot.get_me().id)
        if bot_member.status not in ["administrator", "creator"]:
            bot.reply_to(message, t("bot_not_admin"))
            return
    except Exception as e:
        bot.reply_to(message, f"❌ لا يمكن الوصول إلى المجموعة: {e}")
        return
    user_states[message.from_user.id] = {"step": "add_group_otp", "gid": gid, "desc": desc}
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ نعم (جروب OTP)", callback_data="set_group_otp_yes", style="success"))
    markup.add(types.InlineKeyboardButton("❌ لا (مجموعة عادية)", callback_data="set_group_otp_no", style="danger"))
    bot.reply_to(message, "هل هذه المجموعة هي مجموعة OTP (التي سيظهر رابطها للمستخدمين)؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_group_otp_"))
def set_group_otp(call):
    user_id = call.from_user.id
    if user_id not in user_states or not isinstance(user_states[user_id], dict):
        return
    data = user_states[user_id]
    is_otp = 1 if call.data == "set_group_otp_yes" else 0
    if add_bot_group(data["gid"], data["desc"], is_otp):
        if is_otp:
            set_otp_group(data["gid"])
        bot.answer_callback_query(call.id, f"✅ تم إضافة المجموعة", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ فشل الإضافة", show_alert=True)
    del user_states[user_id]
    admin_panel(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_remove_group")
def admin_remove_group_step1(call):
    if not is_admin(call.from_user.id): return
    groups = get_bot_groups()
    if not groups:
        bot.answer_callback_query(call.id, "❌ لا توجد مجموعات!", show_alert=True)
        return
    markup = types.InlineKeyboardMarkup()
    for gid, desc, is_otp in groups:
        otp_mark = "🔴" if is_otp else ""
        markup.add(types.InlineKeyboardButton(f"{otp_mark} {desc or gid}", callback_data=f"rm_group_{gid}", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "اختر المجموعة لحذفها:", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("rm_group_"))
def admin_remove_group_confirm(call):
    if not is_admin(call.from_user.id): return
    gid = call.data[len("rm_group_"):]
    if remove_bot_group(gid):
        bot.answer_callback_query(call.id, "✅ تم الحذف", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ فشل الحذف", show_alert=True)
    admin_remove_group_step1(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_section")
def admin_add_section(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "waiting_section_names"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="danger"))
    safe_edit_or_delete(call,
        "📂 أرسل أسماء الأقسام التي تريد إضافتها\n"
        "(كل اسم في سطر جديد)\n\n"
        "مثال:\nفيسبوك\nواتساب\nتيليغرام",
        markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "waiting_section_names")
def handle_section_names(message):
    if not is_admin(message.from_user.id): return
    names = [n.strip() for n in message.text.strip().splitlines() if n.strip()]
    if not names:
        bot.reply_to(message, "❌ لم تُرسل أي أسماء!")
        return
    created = []
    for n in names:
        if create_section(n):
            created.append(n)
    if created:
        bot.reply_to(message, f"✅ تم إنشاء {len(created)} قسم:\n" + "\n".join(f"📂 {n}" for n in created))
    else:
        bot.reply_to(message, "❌ الأقسام موجودة مسبقاً أو حدث خطأ!")
    user_states.pop(message.from_user.id, None)

@bot.callback_query_handler(func=lambda call: call.data == "admin_del_section")
def admin_del_section(call):
    if not is_admin(call.from_user.id): return
    sections = get_all_sections()
    if not sections:
        bot.answer_callback_query(call.id, "❌ لا توجد أقسام!", show_alert=True)
        return
    markup = types.InlineKeyboardMarkup()
    for sid, sname in sections:
        markup.add(types.InlineKeyboardButton(f"🗑️ {sname}", callback_data=f"confirm_del_sec_{sid}", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, "اختر القسم الذي تريد حذفه:", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_del_sec_"))
def confirm_del_section(call):
    if not is_admin(call.from_user.id): return
    sid = int(call.data.split("_")[3])
    delete_section(sid)
    bot.answer_callback_query(call.id, "✅ تم حذف القسم", show_alert=True)
    admin_panel(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_groups")
def admin_broadcast_groups_step1(call):
    if not is_admin(call.from_user.id): return
    user_states[call.from_user.id] = "waiting_broadcast_groups"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء", callback_data="admin_panel", style="danger"))
    safe_edit_or_delete(call, "📡 أرسل الرسالة اللي تريد تذيعها في الجروبات والقنوات:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "waiting_broadcast_groups")
def broadcast_groups_step2(message):
    if not is_admin(message.from_user.id): return
    del user_states[message.from_user.id]
    groups = get_bot_groups()
    if not groups:
        bot.reply_to(message, "❌ لا توجد مجموعات أو قنوات مضافة!")
        return
    ok, fail = 0, 0
    for gid, desc, _ in groups:
        try:
            me = bot.get_chat_member(gid, bot.get_me().id)
            if me.status in ("administrator", "creator"):
                bot.send_message(gid, message.text)
                ok += 1
            else:
                fail += 1
        except:
            fail += 1
    bot.reply_to(message, f"📡 تمت الإذاعة!\n✅ نجح: {ok}\n❌ فشل (مش أدمن أو خطأ): {fail}")

@bot.callback_query_handler(func=lambda call: call.data == "admin_auto_delete")
def admin_auto_delete(call):
    if not is_admin(call.from_user.id): return
    current = get_auto_delete_time(call.message.chat.id)
    text = f"🕒 مدة الحذف الحالية: {current} ثانية\n\nيمكنك تعديل المدة لكل مجموعة على حدة."
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✏️ تعديل", callback_data="edit_auto_delete", style="primary"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="danger"))
    safe_edit_or_delete(call, text, markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "edit_auto_delete")
def edit_auto_delete(call):
    user_id = call.from_user.id
    user_states[user_id] = "waiting_auto_delete_time"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء", callback_data="admin_auto_delete", style="danger"))
    safe_edit_or_delete(call, "⏱️ أدخل مدة الحذف بالثواني (مثال: 30):", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "waiting_auto_delete_time")
def set_auto_delete_time_msg(message):
    user_id = message.from_user.id
    try:
        seconds = int(message.text.strip())
        if seconds < 5:
            seconds = 5
        set_auto_delete_time(message.chat.id, seconds)
        bot.reply_to(message, f"✅ تم تعيين مدة الحذف إلى {seconds} ثانية")
    except:
        bot.reply_to(message, "❌ قيمة غير صالحة")
    del user_states[user_id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_custom_buttons")
def admin_custom_buttons(call):
    user_id = call.from_user.id
    if not is_admin(user_id): return
    buttons = get_custom_buttons()
    text = "🔘 **الأزرار المخصصة**\n\n"
    markup = types.InlineKeyboardMarkup()
    for btn in buttons:
        id, btn_text, btn_url = btn
        text += f"• {btn_text} : {btn_url}\n"
        markup.add(types.InlineKeyboardButton(f"🗑️ {btn_text}", callback_data=f"del_custom_btn_{id}", style="danger"))
    markup.row(
        types.InlineKeyboardButton("➕ إضافة زر", callback_data="add_custom_btn", style="success"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary")
    )
    safe_edit_or_delete(call, text, markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "add_custom_btn")
def add_custom_btn_step1(call):
    user_id = call.from_user.id
    user_states[user_id] = "add_custom_btn_text"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء", callback_data="admin_custom_buttons", style="danger"))
    safe_edit_or_delete(call, "أدخل نص الزر:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_custom_btn_text")
def add_custom_btn_step2(message):
    user_id = message.from_user.id
    user_states[user_id] = {"step": "add_custom_btn_url", "text": message.text.strip()}
    bot.reply_to(message, "أدخل رابط الزر:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_custom_btn_url")
def add_custom_btn_step3(message):
    user_id = message.from_user.id
    add_custom_button(user_states[user_id]["text"], message.text.strip())
    bot.reply_to(message, "✅ تم إضافة الزر")
    del user_states[user_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_custom_btn_"))
def del_custom_btn(call):
    user_id = call.from_user.id
    btn_id = int(call.data.split("_")[3])
    delete_custom_button(btn_id)
    bot.answer_callback_query(call.id, "✅ تم الحذف", show_alert=True)
    admin_custom_buttons(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_set_images")
def admin_set_images(call):
    if not is_admin(call.from_user.id): return
    text = "🖼️ إدارة صور البوت\n\n"
    if BOT_IMAGE_BYTES:
        text += "✅ صورة البوت: موجودة\n"
    else:
        text += "❌ صورة البوت: غير موجودة\n"
    if FORCE_SUB_IMAGE_BYTES:
        text += "✅ صورة الاشتراك الإجباري: موجودة\n"
    else:
        text += "❌ صورة الاشتراك الإجباري: غير موجودة\n"
    if MAINTENANCE_IMAGE_BYTES:
        text += "✅ صورة الصيانة: موجودة\n"
    else:
        text += "❌ صورة الصيانة: غير موجودة\n"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🖼️ تعيين صورة البوت", callback_data="set_bot_image", style="primary"))
    if BOT_IMAGE_BYTES:
        markup.add(types.InlineKeyboardButton("🗑️ حذف صورة البوت", callback_data="delete_bot_image", style="danger"))
    markup.add(types.InlineKeyboardButton("🔗 تعيين صورة الاشتراك", callback_data="set_force_sub_image", style="primary"))
    if FORCE_SUB_IMAGE_BYTES:
        markup.add(types.InlineKeyboardButton("🗑️ حذف صورة الاشتراك", callback_data="delete_force_sub_image", style="danger"))
    markup.add(types.InlineKeyboardButton("🔧 تعيين صورة الصيانة", callback_data="set_maintenance_image", style="primary"))
    if MAINTENANCE_IMAGE_BYTES:
        markup.add(types.InlineKeyboardButton("🗑️ حذف صورة الصيانة", callback_data="delete_maintenance_image", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, text, markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "set_bot_image")
def set_bot_image(call):
    user_id = call.from_user.id
    user_states[user_id] = "waiting_bot_image"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء", callback_data="admin_set_images", style="danger"))
    safe_edit_or_delete(call, "أرسل الصورة الآن:", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "set_force_sub_image")
def set_force_sub_image(call):
    user_id = call.from_user.id
    user_states[user_id] = "waiting_force_sub_image"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء", callback_data="admin_set_images", style="danger"))
    safe_edit_or_delete(call, "أرسل الصورة الآن:", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "set_maintenance_image")
def set_maintenance_image(call):
    user_id = call.from_user.id
    user_states[user_id] = "waiting_maintenance_image"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء", callback_data="admin_set_images", style="danger"))
    safe_edit_or_delete(call, "أرسل الصورة الآن:", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "delete_bot_image")
def delete_bot_image(call):
    delete_image("bot")
    bot.answer_callback_query(call.id, t("image_deleted", call.from_user.id), show_alert=True)
    admin_set_images(call)

@bot.callback_query_handler(func=lambda call: call.data == "delete_force_sub_image")
def delete_force_sub_image(call):
    delete_image("force_sub")
    bot.answer_callback_query(call.id, t("image_deleted", call.from_user.id), show_alert=True)
    admin_set_images(call)

@bot.callback_query_handler(func=lambda call: call.data == "delete_maintenance_image")
def delete_maintenance_image(call):
    delete_image("maintenance")
    bot.answer_callback_query(call.id, t("image_deleted", call.from_user.id), show_alert=True)
    admin_set_images(call)

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    user_id = message.from_user.id
    if user_id not in user_states:
        return
    state = user_states[user_id]
    if state not in ["waiting_bot_image", "waiting_force_sub_image", "waiting_maintenance_image"]:
        return
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    if state == "waiting_bot_image":
        save_image("bot", downloaded_file)
        bot.reply_to(message, t("image_set", user_id))
    elif state == "waiting_force_sub_image":
        save_image("force_sub", downloaded_file)
        bot.reply_to(message, t("image_set", user_id))
    elif state == "waiting_maintenance_image":
        save_image("maintenance", downloaded_file)
        bot.reply_to(message, t("image_set", user_id))
    del user_states[user_id]

@bot.callback_query_handler(func=lambda call: call.data == "admin_maintenance")
def admin_maintenance(call):
    if not is_admin(call.from_user.id): return
    status = "مفعل" if MAINTENANCE_MODE else "معطل"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 تبديل وضع الصيانة", callback_data="toggle_maintenance", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, f"🔧 وضع الصيانة: {status}\n\nاضغط للتبديل:", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "toggle_maintenance")
def toggle_maintenance(call):
    if not is_admin(call.from_user.id): return
    set_maintenance_mode(not MAINTENANCE_MODE)
    bot.answer_callback_query(call.id, f"✅ وضع الصيانة الآن {'مفعل' if MAINTENANCE_MODE else 'معطل'}", show_alert=True)
    admin_maintenance(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_speed_test")
def admin_speed_test(call):
    if not is_admin(call.from_user.id): return
    start = time.time()
    msg = bot.send_message(call.message.chat.id, "⚡ جاري قياس السرعة...")
    end = time.time()
    response_time = (end - start) * 1000
    bot.edit_message_text(f"⏱️ زمن الاستجابة: {response_time:.2f} مللي ثانية", call.message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_dashboards")
def admin_dashboards_list(call):
    if not is_admin(call.from_user.id): return
    dashboards = get_db_dashboards(only_active=False)
    if not dashboards:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ إضافة حساب", callback_data="add_dashboard", style="success"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
        safe_edit_or_delete(call, t("no_dashboards", call.from_user.id), markup=markup)
        return
    text = "🔐 **قائمة حسابات اللوحات**\n\n"
    markup = types.InlineKeyboardMarkup()
    for dash in dashboards:
        status = "✅" if dash["is_active"] else "❌"
        text += f"{status} **{dash['name']}** ({dash['short']})\n"
        markup.add(types.InlineKeyboardButton(f"{status} {dash['name']}", callback_data=f"edit_dash_{dash['id']}", style="primary"))
    markup.add(types.InlineKeyboardButton("➕ إضافة حساب", callback_data="add_dashboard", style="success"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel", style="primary"))
    safe_edit_or_delete(call, text, markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "add_dashboard")
def add_dashboard_step1(call):
    user_id = call.from_user.id
    user_states[user_id] = "add_dash_name"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ إلغاء", callback_data="admin_dashboards", style="danger"))
    safe_edit_or_delete(call, "أدخل اسم اللوحة:", markup=markup)

@bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "add_dash_name")
def add_dash_step2(message):
    user_id = message.from_user.id
    user_states[user_id] = {"step": "add_dash_short", "name": message.text.strip()}
    bot.reply_to(message, "أدخل اختصار اللوحة (مثل WS):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_short")
def add_dash_step3(message):
    user_id = message.from_user.id
    user_states[user_id]["short"] = message.text.strip()
    user_states[user_id]["step"] = "add_dash_type"
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Traditional", callback_data="set_dash_type_traditional", style="primary"),
        types.InlineKeyboardButton("API", callback_data="set_dash_type_api", style="success")
    )
    bot.reply_to(message, "اختر نوع اللوحة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_dash_type_"))
def add_dash_step4(call):
    user_id = call.from_user.id
    if user_id not in user_states or not isinstance(user_states[user_id], dict):
        return
    dash_type = "traditional" if call.data == "set_dash_type_traditional" else "api"
    user_states[user_id]["type"] = dash_type
    user_states[user_id]["step"] = "add_dash_username"
    safe_edit_or_delete(call, "أدخل اسم المستخدم (اتركه فارغاً إذا كان API):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_username")
def add_dash_step5(message):
    user_id = message.from_user.id
    user_states[user_id]["username"] = message.text.strip()
    user_states[user_id]["step"] = "add_dash_password"
    bot.reply_to(message, "أدخل كلمة المرور (اتركها فارغاً إذا كان API):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_password")
def add_dash_step6(message):
    user_id = message.from_user.id
    user_states[user_id]["password"] = message.text.strip()
    user_states[user_id]["step"] = "add_dash_token"
    bot.reply_to(message, "أدخل توكن API (إذا كان API، وإلا اتركه فارغاً):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_token")
def add_dash_step7(message):
    user_id = message.from_user.id
    user_states[user_id]["token"] = message.text.strip()
    user_states[user_id]["step"] = "add_dash_base_url"
    bot.reply_to(message, "أدخل الرابط الأساسي (base URL) للوحة:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_base_url")
def add_dash_step8(message):
    user_id = message.from_user.id
    user_states[user_id]["base_url"] = message.text.strip()
    user_states[user_id]["step"] = "add_dash_ajax"
    bot.reply_to(message, "أدخل مسار AJAX (مثل /agent/res/data_smscdr.php) أو اتركه فارغاً:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_ajax")
def add_dash_step9(message):
    user_id = message.from_user.id
    user_states[user_id]["ajax_path"] = message.text.strip()
    user_states[user_id]["step"] = "add_dash_login_page"
    bot.reply_to(message, "أدخل صفحة تسجيل الدخول (مثل /login) أو اتركه فارغاً:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_login_page")
def add_dash_step10(message):
    user_id = message.from_user.id
    user_states[user_id]["login_page"] = message.text.strip()
    user_states[user_id]["step"] = "add_dash_login_post"
    bot.reply_to(message, "أدخل مسار POST لتسجيل الدخول (مثل /signin) أو اتركه فارغاً:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_login_post")
def add_dash_step11(message):
    user_id = message.from_user.id
    user_states[user_id]["login_post"] = message.text.strip()
    user_states[user_id]["step"] = "add_dash_stats_page"
    bot.reply_to(message, "أدخل صفحة الإحصائيات (مثل /stats) أو اتركه فارغاً:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_stats_page")
def add_dash_step12(message):
    user_id = message.from_user.id
    user_states[user_id]["stats_page"] = message.text.strip()
    user_states[user_id]["step"] = "add_dash_idx_date"
    bot.reply_to(message, "أدخل رقم عمود التاريخ (افتراضي 0):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_idx_date")
def add_dash_step13(message):
    user_id = message.from_user.id
    try:
        idx_date = int(message.text.strip())
    except:
        idx_date = 0
    user_states[user_id]["idx_date"] = idx_date
    user_states[user_id]["step"] = "add_dash_idx_number"
    bot.reply_to(message, "أدخل رقم عمود الرقم (افتراضي 2):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_idx_number")
def add_dash_step14(message):
    user_id = message.from_user.id
    try:
        idx_number = int(message.text.strip())
    except:
        idx_number = 2
    user_states[user_id]["idx_number"] = idx_number
    user_states[user_id]["step"] = "add_dash_idx_sms"
    bot.reply_to(message, "أدخل رقم عمود الرسالة (افتراضي 5):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_idx_sms")
def add_dash_step15(message):
    user_id = message.from_user.id
    try:
        idx_sms = int(message.text.strip())
    except:
        idx_sms = 5
    user_states[user_id]["idx_sms"] = idx_sms
    user_states[user_id]["step"] = "add_dash_timeout"
    bot.reply_to(message, "أدخل مهلة الاتصال بالثواني (افتراضي 10):")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_timeout")
def add_dash_step16(message):
    user_id = message.from_user.id
    try:
        timeout = int(message.text.strip())
    except:
        timeout = 10
    user_states[user_id]["timeout"] = timeout
    user_states[user_id]["step"] = "add_dash_data_keys"
    bot.reply_to(message, "أدخل مفاتيح البيانات بصيغة JSON (مثال: {\"date\":\"dt\",\"number\":\"num\",\"sms\":\"message\"}) أو اتركه فارغاً:")

@bot.message_handler(func=lambda msg: isinstance(user_states.get(msg.from_user.id), dict) and user_states[msg.from_user.id].get("step") == "add_dash_data_keys")
def add_dash_step17(message):
    user_id = message.from_user.id
    data_keys = {}
    if message.text.strip():
        try:
            data_keys = json.loads(message.text.strip())
        except:
            data_keys = {}
    data = user_states[user_id]
    add_dashboard_account(
        name=data["name"],
        short=data["short"],
        username=data["username"],
        password=data["password"],
        api_token=data["token"],
        dash_type=data["type"],
        base_url=data["base_url"],
        ajax_path=data["ajax_path"],
        login_page=data["login_page"],
        login_post=data["login_post"],
        stats_page=data["stats_page"],
        idx_date=data["idx_date"],
        idx_number=data["idx_number"],
        idx_sms=data["idx_sms"],
        timeout=data["timeout"],
        data_keys=data_keys
    )
    bot.reply_to(message, f"✅ تم إضافة حساب اللوحة {data['name']} بنجاح")
    del user_states[user_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_dash_"))
def edit_dash(call):
    dash_id = int(call.data.split("_")[2])
    dashboards = get_db_dashboards(only_active=False)
    dash = next((d for d in dashboards if d["id"] == dash_id), None)
    if not dash:
        bot.answer_callback_query(call.id, "❌ الحساب غير موجود", show_alert=True)
        return
    text = f"🔐 **{dash['name']}**\n"
    text += f"الاختصار: {dash['short']}\n"
    text += f"النوع: {dash['type']}\n"
    text += f"المستخدم: {dash['username'] or '—'}\n"
    text += f"توكن API: {'موجود' if dash['api_token'] else '—'}\n"
    text += f"الحالة: {'✅ نشط' if dash['is_active'] else '❌ معطل'}\n"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 تفعيل/تعطيل", callback_data=f"toggle_dash_{dash_id}", style="primary"))
    markup.add(types.InlineKeyboardButton("🗑️ حذف", callback_data=f"delete_dash_{dash_id}", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_dashboards", style="primary"))
    safe_edit_or_delete(call, text, markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_dash_"))
def toggle_dash(call):
    dash_id = int(call.data.split("_")[2])
    toggle_dashboard_account(dash_id)
    bot.answer_callback_query(call.id, "✅ تم تبديل حالة الحساب", show_alert=True)
    edit_dash(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_dash_"))
def delete_dash_confirm(call):
    dash_id = int(call.data.split("_")[2])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ نعم، احذف", callback_data=f"confirm_delete_dash_{dash_id}", style="danger"))
    markup.add(types.InlineKeyboardButton("❌ لا", callback_data=f"edit_dash_{dash_id}", style="primary"))
    safe_edit_or_delete(call, "⚠️ هل أنت متأكد من حذف هذا الحساب؟", markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_delete_dash_"))
def confirm_delete_dash(call):
    dash_id = int(call.data.split("_")[3])
    delete_dashboard_account(dash_id)
    bot.answer_callback_query(call.id, "✅ تم الحذف", show_alert=True)
    admin_dashboards_list(call)

# ======================
# دوال فحص اللوحات (كما هي)
# ======================
def _real_check_traditional(dash):
    username = dash.get("username", "").strip()
    password = dash.get("password", "").strip()
    if not username or not password:
        return t("no_username_pass", None)
    dash_timeout = dash.get("timeout", 10)
    try:
        tmp = requests.Session()
        tmp.headers.update(COMMON_HEADERS)
        login_page_url = dash.get("login_page_url") or (dash.get("base_url") + dash.get("login_page", ""))
        if not login_page_url:
            return t("no_url", None)
        resp = tmp.get(login_page_url, timeout=dash_timeout)
        captcha_answer = None
        match = re.search(r'What is (\d+) \+ (\d+)', resp.text)
        if match:
            captcha_answer = int(match.group(1)) + int(match.group(2))
        else:
            txt = BeautifulSoup(resp.text, "html.parser").get_text(" ")
            m2 = re.search(r'What is\s*([\d\s\+\-\*\/]+)\s*=\s*\?', txt)
            if m2:
                try:
                    captcha_answer = int(eval(m2.group(1).strip()))
                except:
                    captcha_answer = 0
        if captcha_answer is None:
            return t("captcha_unknown", None)
        payload = {"username": username, "password": password, "capt": str(captcha_answer)}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": login_page_url,
            "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"
        }
        login_post_url = dash.get("login_post_url") or (dash.get("base_url") + dash.get("login_post", ""))
        if not login_post_url:
            return t("no_url", None)
        r2 = tmp.post(login_post_url, data=payload, headers=headers, timeout=dash_timeout)
        if ("dashboard" in r2.text.lower() or
                "logout" in r2.text.lower() or
                "/ints/agent" in r2.url or
                "/ints/client" in r2.url or
                r2.url != login_page_url):
            return t("working", None)
        else:
            return t("wrong_credentials", None)
    except requests.exceptions.ConnectionError:
        return t("server_down", None)
    except requests.exceptions.Timeout:
        return t("timeout", None)
    except Exception:
        return t("connection_error", None)

def _real_check_api(dash):
    url = dash.get("api_url", "").strip()
    token = dash.get("api_token", "").strip()
    if not url:
        return t("no_url", None)
    if not token:
        return t("no_token", None)
    try:
        r = requests.get(url, params={"token": token}, timeout=10)
        if r.status_code == 200 and len(r.text.strip()) > 2:
            return t("working", None)
        return t("http_error", None, code=r.status_code)
    except requests.exceptions.ConnectionError:
        return t("server_down", None)
    except requests.exceptions.Timeout:
        return t("timeout", None)
    except Exception:
        return t("connection_error", None)

@bot.callback_query_handler(func=lambda call: call.data == "admin_check_panels")
def admin_check_panels(call):
    if not is_admin(call.from_user.id):
        return
    bot.answer_callback_query(call.id, t("checking", call.from_user.id), show_alert=False)

    def run_check():
        user_id = call.from_user.id
        lines = [t("panel_status", user_id)]
        ok_list = []
        fail_list = []
        all_dashboards = get_all_active_dashboards()

        for dash in all_dashboards:
            name = dash["name"]
            dtype = dash.get("type", "traditional")
            if dtype in ("api_token", "api"):
                status = _real_check_api(dash)
            else:
                status = _real_check_traditional(dash)
            if status == t("working", None):
                ok_list.append(name)
            else:
                fail_list.append(name)
            lines.append(f"• <b>{name}</b>: {status}")

        # iVAS SMS
        ivas_name = "iVAS SMS"
        try:
            tmp = requests.Session()
            tmp.headers.update(COMMON_HEADERS)
            login_url = "https://www.ivasms.com/ints/login"
            r = tmp.get(login_url, timeout=12)
            if r.status_code == 200:
                ivas_status = t("ivas_working", None) if _ivas_logged_in else t("ivas_server_working", None)
                if _ivas_logged_in:
                    ok_list.append(ivas_name)
                else:
                    fail_list.append(ivas_name)
            else:
                ivas_status = t("http_error", None, code=r.status_code)
                fail_list.append(ivas_name)
        except:
            ivas_status = t("connection_error", None)
            fail_list.append(ivas_name)
        lines.append(f"• <b>{ivas_name}</b>: {ivas_status}")

        lines.append(f"\n{t('total_working', user_id, count=len(ok_list))}")
        lines.append(f"{t('total_not_working', user_id, count=len(fail_list))}")

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(t("refresh", user_id), callback_data="admin_check_panels", style="primary"))
        markup.add(types.InlineKeyboardButton(t("back", user_id), callback_data="admin_panel", style="danger"))
        try:
            safe_edit_or_delete(call, "\n".join(lines), markup=markup, parse_mode="HTML")
        except Exception:
            bot.send_message(call.message.chat.id, "\n".join(lines), parse_mode="HTML", reply_markup=markup)

    threading.Thread(target=run_check, daemon=True).start()

# ======================
# دوال جلب الأكواد (للمراقبة) - مضبوطة
# ======================
def login_for_dashboard(dash):
    if dash.get("type") in ("api_token", "api"):
        dash["is_logged_in"] = True
        return True
    def do_login():
        dash_timeout = dash.get("timeout", 10)
        try:
            resp = dash["session"].get(dash["login_page_url"], timeout=dash_timeout)
            captcha_answer = None
            match = re.search(r'What is (\d+) \+ (\d+)', resp.text)
            if match:
                captcha_answer = int(match.group(1)) + int(match.group(2))
            else:
                soup_page = BeautifulSoup(resp.text, "html.parser")
                text_content = soup_page.get_text(" ")
                match2 = re.search(r'What is\s*([\d\s\+\-\*\/]+)\s*=\s*\?', text_content)
                if match2:
                    try:
                        captcha_answer = int(eval(match2.group(1).strip()))
                    except:
                        captcha_answer = 0
            if captcha_answer is None:
                return False
            payload = {
                "username": dash["username"],
                "password": dash["password"],
                "capt": str(captcha_answer)
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": dash["login_page_url"],
                "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"
            }
            resp = dash["session"].post(dash["login_post_url"], data=payload, headers=headers, timeout=dash_timeout)
            if ("dashboard" in resp.text.lower() or
                "logout"    in resp.text.lower() or
                "/ints/agent" in resp.url or
                "/ints/client" in resp.url or
                resp.url != dash["login_page_url"]):
                dash["is_logged_in"] = True
                if dash.get("stats_page"):
                    stats_full = dash.get("base_url") + dash["stats_page"]
                    try:
                        sr = dash["session"].get(stats_full, timeout=dash_timeout)
                        sk = _extract_sesskey(dash, sr.text)
                        if sk:
                            dash["sesskey"] = sk
                    except:
                        pass
                return True
            else:
                dash["is_logged_in"] = False
                return False
        except Exception as e:
            raise
    try:
        return retry_request(do_login)
    except:
        dash["is_logged_in"] = False
        return False

def build_ajax_url_for_dashboard(dash, wide_range=False):
    if wide_range:
        start_date = date.today() - timedelta(days=3650)
        end_date   = date.today() + timedelta(days=1)
    else:
        start_date = date.today()
        end_date   = date.today() + timedelta(days=1)
    fdate1 = f"{start_date.strftime('%Y-%m-%d')} 00:00:00"
    fdate2 = f"{end_date.strftime('%Y-%m-%d')} 23:59:59"
    sesskey_part = ""
    sk = dash.get("sesskey")
    if sk:
        sesskey_part = f"sesskey={quote_plus(sk)}&"
    base_ajax = dash.get("ajax_url") or (dash.get("base_url") + dash["ajax_path"] if dash.get("base_url") and dash.get("ajax_path") else None)
    if not base_ajax:
        return None
    q = (f"{sesskey_part}fdate1={quote_plus(fdate1)}&fdate2={quote_plus(fdate2)}&frange=&fclient=&fnum=&fcli=&fgdate=&fgmonth=&fgrange="
         f"&fgclient=&fgnumber=&fgcli=&fg=0&sEcho=1&iColumns=9&sColumns=%2C%2C%2C%2C%2C%2C%2C%2C&iDisplayStart=0&iDisplayLength=5000"
         f"&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&mDataProp_8=8"
         f"&sSearch=&bRegex=false&iSortCol_0=0&sSortDir_0=desc&iSortingCols=1&_={int(time.time()*1000)}")
    return base_ajax + "?" + q

def fetch_ajax_json_for_dashboard(dash, url):
    if not url:
        return None
    dash_timeout = dash.get("timeout", 10)
    def do_fetch():
        r = dash["session"].get(url, timeout=dash_timeout)
        if r.status_code == 403 or ("login" in r.text.lower() and "login" in r.url.lower()):
            raise Exception("Session expired")
        r.raise_for_status()
        try:
            return r.json()
        except json.JSONDecodeError:
            raise Exception("Invalid JSON")
    try:
        return retry_request(do_fetch, max_retries=2, retry_delay=2)
    except Exception as e:
        if "Session expired" in str(e):
            if login_for_dashboard(dash):
                dash["is_logged_in"] = True
                return retry_request(do_fetch, max_retries=2, retry_delay=2)
            else:
                dash["is_logged_in"] = False
                return None
        return None

def extract_rows_from_json(j):
    if j is None:
        return []
    for key in ("data", "aaData", "rows", "aa_data"):
        if isinstance(j, dict) and key in j:
            return j[key]
    if isinstance(j, list):
        return j
    if isinstance(j, dict):
        for v in j.values():
            if isinstance(v, list):
                return v
    return []

def fetch_api_token_rows(dash):
    try:
        url = dash.get("api_url")
        if not url:
            return []
        r = dash["session"].get(url, params={"token": dash["api_token"]}, timeout=10)
        if r.status_code != 200:
            return []
        j = r.json()
        rows = []
        for key in ("data", "aaData", "rows", "result"):
            if isinstance(j, dict) and key in j and isinstance(j[key], list):
                rows = j[key]
                break
        if not rows and isinstance(j, list):
            rows = j
        return rows
    except Exception as e:
        return []

def row_to_tuple(row, dash):
    date_str = number_str = sms_str = ""
    idx_date = dash.get("idx_date", 0)
    idx_number = dash.get("idx_number", 2)
    idx_sms = dash.get("idx_sms", 5)
    if isinstance(row, (list, tuple)):
        if len(row) > idx_date:   date_str   = clean_html(str(row[idx_date]))
        if len(row) > idx_number: number_str = clean_number(str(row[idx_number]))
        if len(row) > idx_sms:    sms_str    = clean_html(str(row[idx_sms]))
    elif isinstance(row, dict):
        keys = dash.get("data_keys", {})
        date_key = keys.get("date")
        if date_key and date_key in row:
            date_str = clean_html(str(row[date_key]))
        else:
            for k in ("date","time","datetime","dt","created_at"):
                if k in row: date_str = clean_html(str(row[k])); break
        num_key = keys.get("number")
        if num_key and num_key in row:
            number_str = clean_number(str(row[num_key]))
        else:
            for k in ("number","msisdn","cli","from","sender"):
                if k in row: number_str = clean_number(str(row[k])); break
        sms_key = keys.get("sms")
        if sms_key and sms_key in row:
            sms_str = clean_html(str(row[sms_key]))
        else:
            for k in ("sms","message","msg","body","text"):
                if k in row: sms_str = clean_html(str(row[k])); break
    unique_key = f"{date_str}|{number_str}|{sms_str}"
    return date_str, number_str, sms_str, unique_key

def parse_api_token_row(dash, row):
    keys = dash.get("data_keys") or {}
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    number = sms = ""
    if isinstance(row, dict):
        date_key = keys.get("date")
        if date_key and date_key in row:
            date_str = str(row[date_key])
        num_key = keys.get("number", "num")
        if num_key in row:
            number = clean_number(str(row[num_key]))
        sms_key = keys.get("sms", "message")
        if sms_key in row:
            sms = clean_html(str(row[sms_key]))
    elif isinstance(row, (list, tuple)):
        i_date   = dash.get("idx_date", 0)
        i_number = dash.get("idx_number", 2)
        i_sms    = dash.get("idx_sms", 5)
        if len(row) > i_date:   date_str = clean_html(str(row[i_date]))
        if len(row) > i_number: number   = clean_number(str(row[i_number]))
        if len(row) > i_sms:    sms      = clean_html(str(row[i_sms]))
    key = f"{number}|{sms[:30]}"
    return date_str, number, sms, key

def retry_request(func, max_retries=2, retry_delay=2):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

def _extract_sesskey(dash, resp_text):
    m = re.search(r'sesskey["\s:=\']+([a-zA-Z0-9+/=]+)', resp_text)
    if m:
        return m.group(1)
    return None

def fetch_dashboard_data(dash):
    try:
        if dash.get("type") in ("api_token", "api"):
            rows = fetch_api_token_rows(dash)
            new_entries = []
            for row in rows:
                date_str, number, sms, key = parse_api_token_row(dash, row)
                if number and sms and len(number) >= 8:
                    new_entries.append((date_str, number, sms, key))
            return dash["name"], new_entries
        else:
            if not dash["is_logged_in"]:
                if not login_for_dashboard(dash):
                    return dash["name"], []
            url = build_ajax_url_for_dashboard(dash)
            j = fetch_ajax_json_for_dashboard(dash, url)
            rows = extract_rows_from_json(j)
            valid_rows = []
            for row in rows:
                if isinstance(row, (list, tuple, dict)):
                    date_val, num_val, sms_val, _ = row_to_tuple(row, dash)
                    if date_val and "-" in date_val and ":" in date_val and num_val and len(num_val) >= 10 and sms_val and len(sms_val) > 5:
                        valid_rows.append(row)
            if valid_rows:
                def get_dt(r):
                    try:
                        dt, _, _, _ = row_to_tuple(r, dash)
                        return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                    except:
                        return datetime.min
                valid_rows.sort(key=get_dt, reverse=True)
                date_str, number, sms, key = row_to_tuple(valid_rows[0], dash)
                return dash["name"], [(date_str, number, sms, key)]
            return dash["name"], []
    except Exception as e:
        return dash["name"], []

# ======================
# الحلقة الرئيسية
# ======================
def main_loop():
    sent_messages = set()
    last_times = {}

    active_dashboards = get_all_active_dashboards()
    print("=" * 60)
    print(f"🚀 بدء مراقبة {len(active_dashboards)} لوحة نشطة + iVAS")
    print("=" * 60)

    for dash in active_dashboards:
        if dash.get("type") in ("api_token", "api"):
            dash["is_logged_in"] = True
            print(f"[{dash['name']}] ✅ API Token جاهز")
        else:
            if login_for_dashboard(dash):
                dash["is_logged_in"] = True
                last_times[dash["name"]] = None
            else:
                print(f"[{dash['name']}] ⚠️ فشل الدخول الأولي — سيُعاد لاحقاً")

    print("\n🔍 جلب آخر رسالة من كل لوحة...")
    for dash in active_dashboards:
        if dash.get("type") in ("api_token", "api") or not dash.get("is_logged_in"):
            continue
        try:
            url = build_ajax_url_for_dashboard(dash, wide_range=True)
            j = fetch_ajax_json_for_dashboard(dash, url)
            rows = extract_rows_from_json(j)
            if rows:
                valid_rows = []
                for row in rows:
                    if isinstance(row, (list, tuple, dict)):
                        date_val, num_val, sms_val, _ = row_to_tuple(row, dash)
                        if date_val and "-" in date_val and ":" in date_val and num_val and len(num_val) >= 10 and sms_val and len(sms_val) > 5:
                            valid_rows.append(row)
                if valid_rows:
                    def get_dt(r):
                        try:
                            dt, _, _, _ = row_to_tuple(r, dash)
                            return datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
                        except:
                            return datetime.min
                    valid_rows.sort(key=get_dt, reverse=True)
                    date_str, number, sms, key = row_to_tuple(valid_rows[0], dash)
                    if key not in sent_messages:
                        print(f"[{dash['name']}] ✅ آخر رسالة: {mask_number(number)} في {date_str}")
                        send_otp_to_user_and_group(date_str, number, sms, panel_name=dash["name"], short_bold=dash["short_bold"])
                        sent_messages.add(key)
                        last_times[dash["name"]] = date_str
        except Exception as e:
            print(f"[{dash['name']}] ⚠️ خطأ أولي: {e}")

    print(f"\n✅ بدء المراقبة المستمرة (بجلب موازي كل {REFRESH_INTERVAL} ثانية)...\n" + "="*60)

    while True:
        try:
            active_dashboards = get_all_active_dashboards()
            if PARALLEL_FETCH:
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futures = [executor.submit(fetch_dashboard_data, dash) for dash in active_dashboards]
                    for future in as_completed(futures):
                        name, entries = future.result()
                        if entries:
                            for date_str, number, sms, key in entries:
                                if key not in sent_messages:
                                    print(f"[{name}] 🆕 {mask_number(number)}")
                                    dash = next((d for d in active_dashboards if d["name"] == name), None)
                                    short_bold = dash["short_bold"] if dash else to_bold(name[:2])
                                    send_otp_to_user_and_group(date_str, number, sms, panel_name=name, short_bold=short_bold)
                                    sent_messages.add(key)
                                    last_times[name] = date_str
            else:
                for dash in active_dashboards:
                    name, entries = fetch_dashboard_data(dash)
                    if entries:
                        for date_str, number, sms, key in entries:
                            if key not in sent_messages:
                                print(f"[{name}] 🆕 {mask_number(number)}")
                                send_otp_to_user_and_group(date_str, number, sms, panel_name=name, short_bold=dash["short_bold"])
                                sent_messages.add(key)
                                last_times[name] = date_str

            if len(sent_messages) > 5000:
                sent_messages = set(list(sent_messages)[-2000:])

        except KeyboardInterrupt:
            print("\n⛔ توقف يدوي")
            break
        except Exception as e:
            print(f"⚠️ خطأ في الحلقة الرئيسية: {e}")

        time.sleep(REFRESH_INTERVAL)

# ======================
# iVAS SMS
# ======================
_ivas_logged_in = False
_ivas_session = None
_ivas_token = ""
_ivas_last_login = 0
_ivas_processed = set()

IVAS_BASE_URL = "https://www.ivasms.com"
IVAS_LOGIN_URL = IVAS_BASE_URL + "/login"
IVAS_RECV_URL = IVAS_BASE_URL + "/portal/sms/received"
IVAS_URL_RANGES = IVAS_BASE_URL + "/portal/sms/received/getsms"
IVAS_URL_NUMBERS = IVAS_BASE_URL + "/portal/sms/received/getsms/number"
IVAS_URL_SMS = IVAS_BASE_URL + "/portal/sms/received/getsms/number/sms"
IVAS_AJAX_HDRS = {
    "Referer": IVAS_RECV_URL, "Origin": IVAS_BASE_URL,
    "Accept": "text/html, */*",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
}

def _ivas_refresh_token():
    global _ivas_token
    try:
        r = _ivas_session.get(IVAS_RECV_URL, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        t = soup.find("input", {"name": "_token"})
        if t:
            _ivas_token = t["value"]
        else:
            m = re.search(r'_token["\s:,]+["\']([a-zA-Z0-9]{20,})["\']', r.text)
            if m: _ivas_token = m.group(1)
    except Exception as e:
        print(f"[iVAS SMS] ⚠️ تحديث token: {e}")

def _ivas_do_login():
    global _ivas_session, _ivas_last_login, _ivas_token, _ivas_logged_in
    _ivas_session = requests.Session()
    _ivas_session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    resp = _ivas_session.get(IVAS_LOGIN_URL, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    t = soup.find("input", {"name": "_token"})
    tv = t["value"] if t else ""
    r = _ivas_session.post(IVAS_LOGIN_URL, data={
        "_token": tv,
        "email": "",
        "password": "",
        "remember": "",
        "g-recaptcha-response": "",
    }, headers={"Referer": IVAS_LOGIN_URL, "Origin": IVAS_BASE_URL},
       timeout=15, allow_redirects=True)
    if "portal" not in r.url:
        print(f"[iVAS SMS] ❌ فشل الدخول → {r.url}")
        _ivas_logged_in = False
        return False
    _ivas_last_login = time.time()
    _ivas_token = tv
    _ivas_logged_in = True
    _ivas_refresh_token()
    print("[iVAS SMS] ✅ تسجيل دخول ناجح")
    return True

def _ivas_ensure_session():
    refresh_interval = 600
    if _ivas_session is None or (time.time() - _ivas_last_login) > refresh_interval:
        _ivas_do_login()
    else:
        _ivas_refresh_token()

def _ivas_fetch_all():
    global _ivas_token
    today = datetime.now().strftime("%Y-%m-%d")
    all_sms = []
    try:
        r = _ivas_session.post(IVAS_URL_RANGES,
            data={"_token": _ivas_token, "from": today, "to": today},
            headers=IVAS_AJAX_HDRS, timeout=15)
        if r.status_code != 200:
            return all_sms
        soup = BeautifulSoup(r.text, "html.parser")
        ranges = []
        for div in soup.find_all("div", class_="rng"):
            onclick = div.get("onclick", "")
            m = re.search(r"toggleRange\('([^']+)','([^']+)'\)", onclick)
            if m: ranges.append(m.group(1))
        m2 = re.search(r'_token["\s:,]+["\']([a-zA-Z0-9]{20,})["\']', r.text)
        if m2: _ivas_token = m2.group(1)
    except Exception as e:
        print(f"[iVAS SMS] ❌ fetch_ranges: {e}")
        return all_sms

    for range_name in ranges:
        try:
            r = _ivas_session.post(IVAS_URL_NUMBERS,
                data={"_token": _ivas_token, "start": today, "end": today, "range": range_name},
                headers=IVAS_AJAX_HDRS, timeout=15)
            numbers = re.findall(r"toggleNum\w+\('(\d{7,15})'", r.text)
            if not numbers:
                numbers = list(set(re.findall(r"\b(\d{9,15})\b", r.text)))
            m2 = re.search(r'_token["\s:,]+["\']([a-zA-Z0-9]{20,})["\']', r.text)
            if m2: _ivas_token = m2.group(1)
        except Exception as e:
            print(f"[iVAS SMS] ❌ fetch_numbers ({range_name}): {e}")
            continue

        for number in set(numbers):
            try:
                r = _ivas_session.post(IVAS_URL_SMS,
                    data={"_token": _ivas_token, "start": today, "end": today,
                          "Number": number, "Range": range_name},
                    headers=IVAS_AJAX_HDRS, timeout=15)
                m2 = re.search(r'_token["\s:,]+["\']([a-zA-Z0-9]{20,})["\']', r.text)
                if m2: _ivas_token = m2.group(1)
                soup2 = BeautifulSoup(r.text, "html.parser")
                for row in soup2.find_all("tr"):
                    cells = row.find_all("td")
                    if len(cells) < 3:
                        continue
                    sender_tag = cells[0].find(class_="cli-tag")
                    sender = sender_tag.get_text(strip=True) if sender_tag else cells[0].get_text(strip=True)
                    msg_tag = cells[1].find(class_="msg-text")
                    message = msg_tag.get_text(strip=True) if msg_tag else cells[1].get_text(strip=True)
                    t_str = cells[2].get_text(strip=True)
                    if not message:
                        continue
                    sms_id = hashlib.md5(f"{number}|{sender}|{message}|{t_str}".encode()).hexdigest()
                    all_sms.append({"id": sms_id, "number": number,
                                    "sender": sender, "message": message,
                                    "time_str": t_str, "range_name": range_name})
            except Exception as e:
                print(f"[iVAS SMS] ❌ fetch_sms ({number}): {e}")

    return all_sms

def ivas_monitor_loop():
    global _ivas_processed, _ivas_logged_in
    poll = 10
    print("[iVAS SMS] 🚀 بدء مراقبة iVAS SMS...")
    try:
        _ivas_do_login()
    except Exception as e:
        print(f"[iVAS SMS] ❌ فشل الدخول الأولي: {e}")
        _ivas_logged_in = False

    errors = 0
    while True:
        time.sleep(poll)
        try:
            _ivas_ensure_session()
            all_sms = _ivas_fetch_all()
            new_count = 0
            for rec in all_sms:
                if rec["id"] in _ivas_processed:
                    continue
                _ivas_processed.add(rec["id"])
                new_count += 1
                number = rec["number"]
                message = rec["message"]
                t_str = rec.get("time_str", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                sender = rec.get("sender", "")
                print(f"[iVAS SMS] 📩 {number[:6]}*** | {sender} | {message[:40]}")
                send_otp_to_user_and_group(t_str, number, message, panel_name="iVAS SMS", short_bold=to_bold("IV"))
            if len(_ivas_processed) > 20000:
                _ivas_processed = set(list(_ivas_processed)[-10000:])
            errors = 0
        except Exception as e:
            print(f"[iVAS SMS] ❌ خطأ: {e}")
            errors += 1
            if errors >= 5:
                print("[iVAS SMS] 🔄 إعادة تسجيل الدخول...")
                try:
                    _ivas_do_login()
                except:
                    pass
                errors = 0

# ======================
# دوال إرسال OTP (معدلة)
# ======================
def mask_number(number):
    number = number.strip()
    if len(number) >= 6:
        start = number[:3]
        end = number[-3:]
        start_bold = to_bold(start)
        end_bold = to_bold(end)
        middle = "●" * (len(number) - 6)
        return f"{start_bold}{middle}{end_bold}"
    else:
        return number

def get_country_info(number):
    number = number.strip().replace("+","").replace(" ","").replace("-","")
    for code, (name, flag, upper_name) in sorted(COUNTRY_CODES.items(), key=lambda x: len(x[0]), reverse=True):
        if number.startswith(code):
            return name, flag, upper_name
    return "Unknown", "🌍", "UNKNOWN"

def extract_otp(message):
    patterns = [
        r'(?:code|رمز|كود|verification|تحقق|otp|pin)[:\s]+[‎]?(\d{3,8}(?:[- ]\d{3,4})?)',
        r'(\d{3})[- ](\d{3,4})',
        r'\b(\d{4,8})\b',
        r'[‎](\d{3,8})',
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            if len(match.groups()) > 1:
                return ''.join(match.groups())
            return match.group(1).replace(' ', '').replace('-', '')
    all_numbers = re.findall(r'\d{4,8}', message)
    if all_numbers:
        return all_numbers[0]
    return "N/A"

def clean_html(text):
    if not text: return ""
    return re.sub(r'<[^>]+>', '', str(text)).strip()

def clean_number(number):
    if not number: return ""
    return re.sub(r'\D', '', str(number))

def send_otp_to_user_and_group(date_str, number, sms, panel_name="", short_bold=""):
    otp_code = extract_otp(sms)
    user_id = get_user_by_number(number)
    log_otp(number, otp_code, sms, user_id)
    
    # الحصول على اسم الملف (إذا كان المستخدم مرتبطاً بملف)
    file_name = "غير معروف"
    if user_id:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT file_name FROM combos WHERE country_code IN (SELECT country_code FROM users WHERE user_id=?) ORDER BY added_at DESC LIMIT 1", (user_id,))
        row = c.fetchone()
        if row:
            file_name = row[0]
        conn.close()
    
    # إرسال للمستخدم (خاص)
    if user_id:
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t("copy", user_id), callback_data=f"copy_{otp_code}", style="success"))
            custom_btns = get_custom_buttons()
            row_btns = []
            for btn in custom_btns:
                row_btns.append(types.InlineKeyboardButton(btn[1], url=btn[2], style="primary"))
            if row_btns:
                markup.row(*row_btns)
            markup.row(
                types.InlineKeyboardButton(t("owner", user_id), url="https://t.me/NUMBER_X12_BOT", style="danger"),
                types.InlineKeyboardButton(t("channel", user_id), url="https://t.me/OTP208", style="primary")
            )
            country_name, country_flag, _ = get_country_info(number)
            msg_text = t("otp_user", user_id, country=f"{country_flag} {country_name}", file_name=file_name, number_masked=mask_number(number), otp=otp_code)
            try:
                if BOT_IMAGE_BYTES:
                    with io.BytesIO(BOT_IMAGE_BYTES) as img:
                        bot.send_photo(user_id, img, caption=msg_text, reply_markup=markup, parse_mode="Markdown")
                else:
                    bot.send_message(user_id, msg_text, reply_markup=markup, parse_mode="Markdown")
            except:
                bot.send_message(user_id, msg_text, reply_markup=markup, parse_mode="Markdown")
        except Exception as e:
            print(f"[!] خطأ إرسال OTP للمستخدم {user_id}: {e}")
    
    # إرسال إلى المجموعات (يتم تسجيلها للحذف)
    country_name, country_flag, _ = get_country_info(number)
    group_msg = t("new_otp_group", None,
                   flag=country_flag,
                   number_masked=mask_number(number),
                   short_bold=short_bold)
    for chat_id in CHAT_IDS:
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(t("copy", None), callback_data=f"copy_{otp_code}", style="success"))
            markup.row(
                types.InlineKeyboardButton(t("owner", None), url="https://t.me/NUMBER_X12_BOT", style="danger"),
                types.InlineKeyboardButton(t("channel", None), url="https://t.me/OTP208", style="primary")
            )
            if BOT_IMAGE_BYTES:
                with io.BytesIO(BOT_IMAGE_BYTES) as img:
                    sent = bot.send_photo(chat_id, img, caption=group_msg, reply_markup=markup, parse_mode="HTML")
            else:
                sent = bot.send_message(chat_id, group_msg, reply_markup=markup, parse_mode="HTML")
            track_otp_tg_message(chat_id, sent.message_id)
        except:
            try:
                sent = bot.send_message(chat_id, group_msg, reply_markup=markup, parse_mode="HTML")
                track_otp_tg_message(chat_id, sent.message_id)
            except:
                pass

def track_otp_tg_message(chat_id, message_id):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO otp_tg_messages (chat_id, message_id, sent_at) VALUES (?, ?, ?)",
              (str(chat_id), message_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_"))
def copy_callback(call):
    otp = call.data.split("_")[1]
    bot.answer_callback_query(call.id, f"📋 {otp}", show_alert=True)

# ======================
# أكواد الدول كاملة
# ======================
COUNTRY_CODES = {
    "1": ("USA/Canada", "🇺🇸", "USA/CANADA"),
    "7": ("Russia", "🇷🇺", "RUSSIA"),
    "20": ("Egypt", "🇪🇬", "EGYPT"),
    "27": ("South Africa", "🇿🇦", "SOUTH AFRICA"),
    "30": ("Greece", "🇬🇷", "GREECE"),
    "31": ("Netherlands", "🇳🇱", "NETHERLANDS"),
    "32": ("Belgium", "🇧🇪", "BELGIUM"),
    "33": ("France", "🇫🇷", "FRANCE"),
    "34": ("Spain", "🇪🇸", "SPAIN"),
    "36": ("Hungary", "🇭🇺", "HUNGARY"),
    "39": ("Italy", "🇮🇹", "ITALY"),
    "40": ("Romania", "🇷🇴", "ROMANIA"),
    "41": ("Switzerland", "🇨🇭", "SWITZERLAND"),
    "43": ("Austria", "🇦🇹", "AUSTRIA"),
    "44": ("UK", "🇬🇧", "UK"),
    "45": ("Denmark", "🇩🇰", "DENMARK"),
    "46": ("Sweden", "🇸🇪", "SWEDEN"),
    "47": ("Norway", "🇳🇴", "NORWAY"),
    "48": ("Poland", "🇵🇱", "POLAND"),
    "49": ("Germany", "🇩🇪", "GERMANY"),
    "51": ("Peru", "🇵🇪", "PERU"),
    "52": ("Mexico", "🇲🇽", "MEXICO"),
    "53": ("Cuba", "🇨🇺", "CUBA"),
    "54": ("Argentina", "🇦🇷", "ARGENTINA"),
    "55": ("Brazil", "🇧🇷", "BRAZIL"),
    "56": ("Chile", "🇨🇱", "CHILE"),
    "57": ("Colombia", "🇨🇴", "COLOMBIA"),
    "58": ("Venezuela", "🇻🇪", "VENEZUELA"),
    "60": ("Malaysia", "🇲🇾", "MALAYSIA"),
    "61": ("Australia", "🇦🇺", "AUSTRALIA"),
    "62": ("Indonesia", "🇮🇩", "INDONESIA"),
    "63": ("Philippines", "🇵🇭", "PHILIPPINES"),
    "64": ("New Zealand", "🇳🇿", "NEW ZEALAND"),
    "65": ("Singapore", "🇸🇬", "SINGAPORE"),
    "66": ("Thailand", "🇹🇭", "THAILAND"),
    "81": ("Japan", "🇯🇵", "JAPAN"),
    "82": ("South Korea", "🇰🇷", "SOUTH KOREA"),
    "84": ("Vietnam", "🇻🇳", "VIETNAM"),
    "86": ("China", "🇨🇳", "CHINA"),
    "90": ("Turkey", "🇹🇷", "TURKEY"),
    "91": ("India", "🇮🇳", "INDIA"),
    "92": ("Pakistan", "🇵🇰", "PAKISTAN"),
    "93": ("Afghanistan", "🇦🇫", "AFGHANISTAN"),
    "94": ("Sri Lanka", "🇱🇰", "SRI LANKA"),
    "95": ("Myanmar", "🇲🇲", "MYANMAR"),
    "98": ("Iran", "🇮🇷", "IRAN"),
    "212": ("Morocco", "🇲🇦", "MOROCCO"),
    "213": ("Algeria", "🇩🇿", "ALGERIA"),
    "216": ("Tunisia", "🇹🇳", "TUNISIA"),
    "218": ("Libya", "🇱🇾", "LIBYA"),
    "225": ("Ivory Coast", "🇨🇮", "IVORY COAST"),
    "234": ("Nigeria", "🇳🇬", "NIGERIA"),
    "249": ("Sudan", "🇸🇩", "SUDAN"),
    "263": ("Zimbabwe", "🇿🇼", "ZIMBABWE"),
    "351": ("Portugal", "🇵🇹", "PORTUGAL"),
    "352": ("Luxembourg", "🇱🇺", "LUXEMBOURG"),
    "353": ("Ireland", "🇮🇪", "IRELAND"),
    "358": ("Finland", "🇫🇮", "FINLAND"),
    "380": ("Ukraine", "🇺🇦", "UKRAINE"),
    "381": ("Serbia", "🇷🇸", "SERBIA"),
    "420": ("Czech Rep", "🇨🇿", "CZECH REPUBLIC"),
    "421": ("Slovakia", "🇸🇰", "SLOVAKIA"),
    "961": ("Lebanon", "🇱🇧", "LEBANON"),
    "962": ("Jordan", "🇯🇴", "JORDAN"),
    "963": ("Syria", "🇸🇾", "SYRIA"),
    "964": ("Iraq", "🇮🇶", "IRAQ"),
    "965": ("Kuwait", "🇰🇼", "KUWAIT"),
    "966": ("Saudi Arabia", "🇸🇦", "SAUDI ARABIA"),
    "967": ("Yemen", "🇾🇪", "YEMEN"),
    "968": ("Oman", "🇴🇲", "OMAN"),
    "970": ("Palestine", "🇵🇸", "PALESTINE"),
    "971": ("UAE", "🇦🇪", "UAE"),
    "972": ("Israel", "🇮🇱", "ISRAEL"),
    "973": ("Bahrain", "🇧🇭", "BAHRAIN"),
    "974": ("Qatar", "🇶🇦", "QATAR"),
    "977": ("Nepal", "🇳🇵", "NEPAL"),
    "992": ("Tajikistan", "🇹🇯", "TAJIKISTAN"),
    "994": ("Azerbaijan", "🇦🇿", "AZERBAIJAN"),
    "995": ("Georgia", "🇬🇪", "GEORGIA"),
    "998": ("Uzbekistan", "🇺🇿", "UZBEKISTAN"),
}

# ======================
# الرسالة الدورية والحذف التلقائي (كل 30 ثانية)
# ======================
def periodic_group_message():
    while True:
        for chat_id in CHAT_IDS:
            try:
                msg = t("group_periodic", None)
                sent = bot.send_message(chat_id, msg)
                track_otp_tg_message(chat_id, sent.message_id)
            except:
                pass
        time.sleep(300)

def auto_delete_otp_logs():
    while True:
        try:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute("SELECT id, chat_id, message_id, sent_at FROM otp_tg_messages")
            messages = c.fetchall()
            now = datetime.now()
            for row_id, chat_id, message_id, sent_at_str in messages:
                sent_at = datetime.strptime(sent_at_str, "%Y-%m-%d %H:%M:%S")
                delete_after = get_auto_delete_time(chat_id)
                delta = (now - sent_at).total_seconds()
                if delta > delete_after:
                    try:
                        bot.delete_message(chat_id, message_id)
                    except:
                        pass
                    c.execute("DELETE FROM otp_tg_messages WHERE id=?", (row_id,))
            c.execute("DELETE FROM otp_logs WHERE julianday('now') - julianday(timestamp) > 0.0104")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[auto_delete] ⚠️ {e}")
        time.sleep(30)

# ======================
# تشغيل البوت
# ======================
def run_bot():
    while True:
        try:
            print("[sendako] 🤖 تشغيل البوت...")
            bot.infinity_polling(timeout=30, long_polling_timeout=15)
        except Exception as e:
            print(f"[sendako] ⚠️ توقف البوت - إعادة التشغيل بعد 5 ثوانٍ: {e}")
            time.sleep(5)

def safe_main_loop():
    while True:
        try:
            main_loop()
        except Exception as e:
            print(f"[tenjiko] ⚠️ خطأ في main_loop - إعادة التشغيل بعد 10 ثوانٍ: {e}")
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    threading.Thread(target=ivas_monitor_loop, daemon=True).start()
    threading.Thread(target=auto_delete_otp_logs, daemon=True).start()
    threading.Thread(target=periodic_group_message, daemon=True).start()
    safe_main_loop()
