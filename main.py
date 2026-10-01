# -*- coding: utf-8 -*-
import json, os, time, telebot, requests, threading, random, string, traceback, re
from datetime import datetime

gggggto = '8773672677:AAENLyoVsU2RDkrdB73AddQga93el0l6YAw'
golden = telebot.TeleBot(gggggto, threaded=True)

G1='users.json'; G2='stats.json'; G5='black.txt'; G6='gifts.json'
G7='@LoFYqq'; G8=6759191586
CONFIG_FILE='config.json'
CUSTOM_SERVICES_FILE='custom_services.json'
BASE_OVERRIDES_FILE='base_overrides.json'

E_STAR="5463289097336405244"; E_LINK="4958689671950369798"
E_GIFT="5203996991054432397"; E_CROSS="5210952531676504517"
E_BOLT="5258203794772085854"; E_BROKEN="5273842895978251304"
E_SPARK="5463297803235113601"; E_DIAMOND="5235630047959727475"
E_HEART="5397890811436213746"; E_YES="5413794461152978282"
E_NO="5413472879771658264"; E_TG="5330237710655306682"
E_SEARCH="5330237710655306683"; E_EYE="5427009714745517609"
E_WELCOME="5282999122008221435"; E_CROWN="5357189931888093985"
E_LOCK="5309913199851496372"; E_ROCKET="5364000017707212408"
E_FIRE="5424978187263869632"

def ee(eid, fb): return f'<tg-emoji emoji-id="{eid}">{fb}</tg-emoji>'
def strip_emoji_tags(text): return re.sub(r'<tg-emoji[^>]*>([^<]*)</tg-emoji>', r'\1', text)
def strip_all_html(text): return re.sub(r'<[^>]+>', '', text)

def send_h(chat_id, text, markup=None, silent_fail=True):
    try: return golden.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        if "message is not modified" in str(e).lower(): return None
    try:
        plain = strip_emoji_tags(text)
        return golden.send_message(chat_id, plain, reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        if "message is not modified" in str(e).lower(): return None
    try:
        plain = strip_all_html(text)
        return golden.send_message(chat_id, plain, reply_markup=markup)
    except: pass
    try: return golden.send_message(chat_id, strip_all_html(text))
    except: return None

def edit_h(cid, mid, text, markup=None):
    try: return golden.edit_message_text(text=text, chat_id=cid, message_id=mid, reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        if "message is not modified" in str(e).lower(): return None
    try:
        plain = strip_emoji_tags(text)
        return golden.edit_message_text(text=plain, chat_id=cid, message_id=mid, reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        if "message is not modified" in str(e).lower(): return None
    try:
        plain = strip_all_html(text)
        return golden.edit_message_text(text=plain, chat_id=cid, message_id=mid, reply_markup=markup)
    except Exception as e:
        if "message is not modified" in str(e).lower(): return None
    try: return golden.send_message(cid, text, reply_markup=markup, parse_mode='HTML')
    except: pass
    try: return golden.send_message(cid, strip_emoji_tags(text), reply_markup=markup, parse_mode='HTML')
    except: pass
    try: return golden.send_message(cid, strip_all_html(text), reply_markup=markup)
    except: pass
    return None

def force_send(chat_id, text, markup=None):
    try: golden.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML'); return True
    except: pass
    try: golden.send_message(chat_id, strip_emoji_tags(text), reply_markup=markup, parse_mode='HTML'); return True
    except: pass
    try: golden.send_message(chat_id, strip_all_html(text), reply_markup=markup); return True
    except: pass
    try: golden.send_message(chat_id, strip_all_html(text)); return True
    except Exception as e: print(f"❌ force_send: {e}"); return False

SMM_ERROR_TRANSLATIONS = {
    "neworder.error.link_duplicate": "هذا الرابط مطلوب مسبقاً لنفس الخدمة ❌\n💡 انتظر انتهاء الطلب السابق",
    "neworder.error.not_enough_funds": "رصيد المزود غير كافٍ ⚠️\n💡 تواصل مع الإدارة",
    "neworder.error.invalid_link": "الرابط غير صالح ❌",
    "neworder.error.invalid_quantity": "الكمية غير صالحة ⚠️",
    "neworder.error.service_not_found": "الخدمة غير متوفرة ❌",
    "neworder.error.too_many_orders": "طلبات كثيرة على الرابط ⚠️",
    "neworder.error.not_enough_quantity": "الكمية أكبر من المتاح ⚠️",
    "neworder.error": "فشل إنشاء الطلب ⚠️",
    "order.error": "خطأ من المزود ⚠️",
}

def translate_smm_error(err):
    if not err: return "حدث خطأ غير معروف ⚠️"
    e = str(err).strip().lower()
    for key, msg in SMM_ERROR_TRANSLATIONS.items():
        if key.lower() == e: return msg
    for key, msg in SMM_ERROR_TRANSLATIONS.items():
        if key.lower() in e: return msg
    return f"فشـل إنشاء الطلب ❌\n⚠️ <b>التفاصيل :</b> <code>{str(err)[:100]}</code>"

class CustomEmojiButton(telebot.types.InlineKeyboardButton):
    def __init__(self, text, callback_data=None, url=None, icon_custom_emoji_id=None, style=None, **kw):
        super().__init__(text=text, callback_data=callback_data, url=url, **kw)
        self.icon_custom_emoji_id = icon_custom_emoji_id
        self.style = style
    def to_dict(self):
        d = super().to_dict()
        if self.icon_custom_emoji_id: d['icon_custom_emoji_id'] = self.icon_custom_emoji_id
        if self.style: d['style'] = self.style
        return d

def btn(text, callback_data=None, url=None, emoji=None, style=None):
    if not text.strip().startswith('‹') and not text.strip().startswith('«'):
        text = f"‹ {text} ›"
    try:
        return CustomEmojiButton(text, callback_data=callback_data, url=url, icon_custom_emoji_id=emoji, style=style)
    except:
        return telebot.types.InlineKeyboardButton(text, callback_data=callback_data, url=url)

# ═══════════ قالب التحذير للخدمات الخاصة (يُستخدم عند تفعيل الخاصية) ═══════════
DEFAULT_TELE_REAL_WARNING = (
    f"{ee(E_CROWN,'👑')} <b>متابعين تيليجرام حقيقيين 100%</b>\n"
    f"━━━━━━━━━━━━━━━\n"
    f"{ee(E_DIAMOND,'💎')} <b>السعر</b> : {{final_price}} نقطة لـ {{pack}} متابع\n"
    f"{ee(E_STAR,'⭐')} <b>الكمية</b> : {{min}} - {{max}}\n"
    f"━━━━━━━━━━━━━━━\n"
    f"{ee(E_LOCK,'🔒')} <b>شروط إجبارية :</b>\n\n"
    f"1️⃣ إضافة البوت <b>@{{bot}}</b> كأدمن في قناتك\n"
    f"2️⃣ منح البوت صلاحية إضافة أعضاء\n"
    f"3️⃣ البوت سيتم فحصه تلقائياً كل دقيقة\n"
    f"━━━━━━━━━━━━━━━\n"
    f"{ee(E_BROKEN,'💔')} <b>تحذير مهم جداً :</b>\n"
    f"إذا قمت بإزالة البوت من القناة لاحقاً :\n"
    f"{ee(E_CROSS,'❌')} سيتم إنهاء اشتراكك مباشرة\n"
    f"{ee(E_CROSS,'❌')} سيتم إنزال المتابعين من قناتك\n"
    f"{ee(E_CROSS,'❌')} ستنتهي الخدمة نهائياً بدون رجعة\n"
    f"━━━━━━━━━━━━━━━\n"
    f"{ee(E_FIRE,'🔥')} <b>لا يوجد استرجاع للنقاط بعد الموافقة نهائياً</b>\n"
    f"━━━━━━━━━━━━━━━\n"
    f"{ee(E_SPARK,'✨')} اضغط <b>موافق</b> للمتابعة"
)

# ✅ تم إفراغ الخدمات والمزودين
BASE_SERVICES = {}
BASE_EMOJI_MAP = {}
RANDOM_EMOJIS=[E_STAR,E_BOLT,E_SPARK,E_DIAMOND,E_HEART,E_GIFT,E_SEARCH,E_EYE]
RANDOM_STYLES=["primary","success"]

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path,'r',encoding='utf-8') as f: return json.load(f)
        except: return default
    return default

def save_json(path, data):
    try:
        with open(path,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=4)
    except Exception as e: print(f"save {path}: {e}")

def load_config():
    c = load_json(CONFIG_FILE, {})
    defaults = {
        "daily_gift_points":10, "daily_gift_cooldown":172800,
        "referral_reward":25, "activation_channel":"",
        "login_notify":True, "hidden_services":[],
        "service_order": [],
        "channel_followers_reward_points": 5,
        "points_prices":["1$ = 50 نقـطة","2$ = 100 نقـطة","5$ = 250 نقـطة","10$ = 500 نقـطة"],
        "forced_channels":[], "welcome_image":"", "channel_rewards":[],
        "providers": {}   # ✅ لا يوجد مزودين افتراضيين
    }
    for k,v in defaults.items():
        if k not in c: c[k]=v
    if "providers" not in c or not isinstance(c.get("providers"), dict): c["providers"] = {}
    # ✅ لا نضيف p1/p2 بعد الآن
    for pk, pv in c["providers"].items():
        for f in ["name","url","api_key"]:
            if f not in pv: pv[f] = ""
        if "active" not in pv: pv["active"] = True
        if "default" not in pv: pv["default"] = False
    save_json(CONFIG_FILE, c)
    return c

config = load_config()
custom_services = load_json(CUSTOM_SERVICES_FILE, {})
def save_custom_services(d): save_json(CUSTOM_SERVICES_FILE, d)

SERVICES = {}
SERVICES.update(BASE_SERVICES)
SERVICES.update(custom_services)

# ✅ لا نضيف tele_real_followers تلقائياً

try:
    _ov = load_json(BASE_OVERRIDES_FILE, {})
    for k, v in _ov.items():
        if k in SERVICES: SERVICES[k].update(v)
except: pass
for k, svc in SERVICES.items():
    if 'unit' not in svc or not isinstance(svc.get('unit'), int) or svc.get('unit', 0) <= 0:
        svc['unit'] = svc.get('min', 100)
    if 'final_price' not in svc:
        svc['final_price'] = svc.get('price', 0)

def calc_cost(qty, svc):
    unit = svc.get('unit', 100)
    final_price = svc.get('final_price', svc.get('price', 0))
    if unit <= 0: unit = 100
    return (int(qty) * final_price + unit - 1) // unit

def get_active_providers(): return {k: v for k, v in config.get("providers", {}).items() if v.get("active", True)}
def get_provider(pk): return config.get("providers", {}).get(pk)
def get_default_provider():
    provs = config.get("providers", {})
    for pk, pv in provs.items():
        if pv.get("default") and pv.get("active", True): return pk, pv
    for pk, pv in provs.items():
        if pv.get("active", True): return pk, pv
    return None, None

def get_srv_props(key, svc):
    if key in BASE_EMOJI_MAP: return BASE_EMOJI_MAP[key]
    if 'emoji' in svc and 'style' in svc: return svc['emoji'], svc['style']
    return E_STAR, "primary"

def get_ordered_services():
    hidden = config.get('hidden_services', [])
    order = config.get('service_order', [])
    all_keys = [k for k in SERVICES.keys() if k != "tele_real_followers"]
    result = []
    for k in order:
        if k in all_keys and k not in result:
            result.append(k)
    for k in all_keys:
        if k not in result:
            result.append(k)
    final = []
    if "tele_real_followers" in SERVICES:
        final.append("tele_real_followers")
    final.extend(result)
    return final

def visible_services():
    hidden = config.get('hidden_services', [])
    ordered_keys = get_ordered_services()
    result = {}
    for k in ordered_keys:
        if k in SERVICES and k not in hidden:
            result[k] = SERVICES[k]
    return result

def move_service_up(sk):
    order = [k for k in get_ordered_services() if k != "tele_real_followers"]
    if sk in order:
        i = order.index(sk)
        if i > 0:
            order[i], order[i-1] = order[i-1], order[i]
            config['service_order'] = order
            save_json(CONFIG_FILE, config)

def move_service_down(sk):
    order = [k for k in get_ordered_services() if k != "tele_real_followers"]
    if sk in order:
        i = order.index(sk)
        if i < len(order)-1:
            order[i], order[i+1] = order[i+1], order[i]
            config['service_order'] = order
            save_json(CONFIG_FILE, config)

realtime_tasks = load_json('realtime_tasks.json', {})
auto_tasks = load_json('auto_tasks.json', {})
def save_realtime_tasks(t): save_json('realtime_tasks.json', t)
def save_auto_tasks(t): save_json('auto_tasks.json', t)

Gq = load_json(G1, {})
Gr = load_json(G2, {"total_users":0,"total_requests":0,"total_invites":0})
Gt = load_json(G6, {})

def load_black():
    if os.path.exists(G5):
        with open(G5,'r',encoding='utf-8') as f: return [x.strip() for x in f if x.strip()]
    return []
def save_black(lst):
    with open(G5,'w',encoding='utf-8') as f:
        for x in lst: f.write(str(x)+'\n')

Gu = load_black()
for k in ["total_users","total_requests","total_invites"]:
    if k not in Gr: Gr[k]=0
if "service_sales" not in Gr: Gr["service_sales"] = {}
save_json(G2, Gr)

def bump_service_sale(svc_key):
    try:
        if "service_sales" not in Gr: Gr["service_sales"] = {}
        Gr["service_sales"][svc_key] = Gr["service_sales"].get(svc_key, 0) + 1
        save_json(G2, Gr)
    except: pass

def X8(uid, uname="", invited_by=None, first_name=""):
    s = str(uid)
    if s not in Gq:
        Gq[s] = {"id":uid,"username":uname,"first_name":first_name,"points":0,"requests":0,"transfers":0,
                 "gifts_collected":0,"gift_points":0,"last_gift":0,
                 "invited_count":0,"invited_by":invited_by,"invited_users":[],
                 "invite_rewarded":False,"join_time":time.time(),
                 "completed_requests":[],"realtime_tasks":[],"auto_tasks":[],"orders":[],
                 "claimed_channels":[], "pending_gift":""}
        Gr["total_users"]+=1
        if invited_by and invited_by in Gq:
            Gq[invited_by].setdefault("invited_users",[]).append(s)
        save_json(G1,Gq); save_json(G2,Gr)
        return Gq[s], True
    u = Gq[s]
    changed = False
    if uname and not u.get("username"):
        u["username"]=uname; changed = True
    if first_name and not u.get("first_name"):
        u["first_name"]=first_name; changed = True
    for k, v in {"points":0,"requests":0,"transfers":0,"gifts_collected":0,"gift_points":0,
                 "last_gift":0,"invited_count":0,"invite_rewarded":False,"orders":[],"claimed_channels":[],
                 "first_name":"", "pending_gift":""}.items():
        if k not in u:
            u[k] = v if not isinstance(v, list) else list(v); changed = True
    for o in u.get("orders", []):
        if isinstance(o, dict) and "status" not in o: o["status"] = "pending"
    if changed: save_json(G1,Gq)
    return u, False

def get_user(uid):
    s = str(uid)
    if s not in Gq: X8(uid)
    return Gq[s]

_sub_cache = {}

def X12(uid):
    if uid == G8: return True
    now = time.time()
    cached = _sub_cache.get(uid)
    if cached:
        ts, val = cached
        ttl = 120 if val else 3
        if now - ts < ttl:
            return val
    result = True
    forced = config.get("forced_channels", [])
    if not forced:
        try: result = golden.get_chat_member(G7, uid).status in ['member','administrator','creator']
        except: result = True
    else:
        for ch in forced:
            chat_id = ch.get("chat_id", "").strip()
            if not chat_id:
                link = ch.get("link", "").strip()
                if "t.me/+" in link or "joinchat" in link: continue
                if "t.me/" in link:
                    uname = link.split("t.me/")[-1].strip("/").split("?")[0]
                    if uname.startswith("+"): continue
                    chat_id = "@" + uname
                elif link.startswith("@"): chat_id = link
                elif link.startswith("-") or link.isdigit(): chat_id = link
                else: continue
            try:
                status = golden.get_chat_member(chat_id, uid).status
                if status in ['left', 'kicked']:
                    result = False
                    break
            except: continue
    _sub_cache[uid] = (now, result)
    return result

def X13(uid): return str(uid) in Gu
def clear_user_state(uid):
    try: golden.clear_step_handler_by_chat_id(uid)
    except: pass

def restart_kb():
    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(btn("إعادة البداية", callback_data="back_main", emoji=E_ROCKET, style="success"))
    return kb

def error_restart(uid, msg): send_h(uid, f"{ee(E_CROSS,'❌')} <b>{msg}</b>", markup=restart_kb())

def build_sub_kb():
    forced = config.get("forced_channels", [])
    kb = telebot.types.InlineKeyboardMarkup()
    if not forced:
        kb.row(btn("بوتات تفاعل", url="https://t.me/LoFYqq", emoji=E_TG, style="primary"))
        return kb
    emoji_pool = [E_TG, E_LINK, E_STAR, E_HEART, E_GIFT, E_FIRE, E_CROWN, E_DIAMOND]
    for i, ch in enumerate(forced):
        name = ch.get("name", "قناة"); link = ch.get("link", "")
        emoji = ch.get("emoji") or emoji_pool[i % len(emoji_pool)]
        style = ch.get("style") or ("primary" if i % 2 == 0 else "success")
        if link: kb.row(btn(name, url=link, emoji=emoji, style=style))
    return kb

def send_sub_msg(chat_id):
    forced = config.get("forced_channels", [])
    txt = f"{ee(E_LOCK,'🔒')} <b>عليـك الاشـتـراك بالقـنوات أولاً</b>\n━━━━━━━━━━━━━━━\n"
    if forced:
        emoji_pool = [E_TG, E_LINK, E_STAR, E_HEART, E_GIFT, E_FIRE, E_CROWN, E_DIAMOND]
        for i, ch in enumerate(forced):
            emoji = ch.get("emoji") or emoji_pool[i % len(emoji_pool)]
            txt += f"{ee(emoji, '📢')} <b>{ch.get('name', 'قناة')}</b>\n"
    else: txt += f"{ee(E_TG,'📢')} <b>قناة LoFYqq</b>\n"
    txt += f"━━━━━━━━━━━━━━━\n{ee(E_SPARK,'✨')} بعـد الاشـتراك اضغـط تحـقق"
    kb = build_sub_kb()
    kb.row(btn("تحـقق", callback_data="verify_sub", emoji=E_YES, style="success"))
    send_h(chat_id, txt, markup=kb)

def notify_admin_login(user_id, username, first_name, invited_by=None):
    if not config.get("login_notify", True): return
    try:
        uname = f"@{username}" if username else "بدون يوزر"
        now = datetime.now().strftime("%Y-%m-%d | %H:%M")
        txt = (f"{ee(E_SPARK,'✨')} <b>◈ مستخدم جديد دخل البوت ◈</b> {ee(E_SPARK,'✨')}\n"
               f"╔══════════════════════╗\n"
               f"║ {ee(E_WELCOME,'👋')} <b>مرحباً بك في M7</b>\n"
               f"╠══════════════════════╣\n"
               f"║ {ee(E_CROWN,'👑')} <b>الاسم</b> : {first_name}\n"
               f"║ {ee(E_TG,'📱')} <b>اليوزر</b> : {uname}\n"
               f"║ {ee(E_EYE,'👁')} <b>الآيدي</b> : <code>{user_id}</code>\n")
        if invited_by: txt += f"║ {ee(E_LINK,'🔗')} <b>من إحالة</b> : <code>{invited_by}</code>\n"
        txt += (f"║ ⏰ <b>الوقت</b> : {now}\n"
                f"╠══════════════════════╣\n"
                f"║ {ee(E_STAR,'⭐')} <b>إجمالي المستخدمين</b>\n"
                f"║        <b>→ {Gr['total_users']} ←</b>\n"
                f"╚══════════════════════╝\n{ee(E_FIRE,'🔥')} <i>M7 Bot System</i>")
        force_send(G8, txt)
    except: pass

def notify_activation_channel(text):
    ch = config.get("activation_channel","").strip()
    if not ch: return
    force_send(ch, text)

def notify_referral_reward(inviter_id, reward, new_username="", new_name="مستخدم", new_id=""):
    try:
        u = Gq[str(inviter_id)]
        uname_disp = f"@{new_username}" if new_username else "بدون يوزر"
        txt = (f"{ee(E_GIFT,'🎁')} <b>تهـانينـا لـك</b> {ee(E_SPARK,'✨')}\n"
               f"━━━━━━━━━━━━━━━\n"
               f"{ee(E_ROCKET,'🚀')} <b>شخص جديد دخل عبر رابط الدعوة</b>\n"
               f"━━━━━━━━━━━━━━━\n"
               f"{ee(E_CROWN,'👑')} <b>الاسم</b> : {new_name}\n"
               f"{ee(E_TG,'📱')} <b>اليوزر</b> : {uname_disp}\n"
               f"{ee(E_EYE,'👁')} <b>الآيدي</b> : <code>{new_id}</code>\n"
               f"━━━━━━━━━━━━━━━\n"
               f"{ee(E_DIAMOND,'💎')} <b>المكافأة</b> : <b>+{reward}</b> نقطة\n"
               f"{ee(E_CROWN,'👑')} <b>نقاطك الآن</b> : <b>{u.get('points',0)}</b>\n"
               f"{ee(E_STAR,'⭐')} <b>إجمالي المدعوين</b> : <b>{u.get('invited_count',0)}</b>\n"
               f"━━━━━━━━━━━━━━━\n"
               f"{ee(E_FIRE,'🔥')} <i>استمر بالمشاركة لجمع المزيد</i>")
        force_send(inviter_id, txt)
    except: pass

def process_invitation_reward(inviter_id, new_user_id):
    istr, nstr = str(inviter_id), str(new_user_id)
    if istr not in Gq or istr == nstr: return False
    nu = Gq.get(nstr)
    if not nu or nu.get("invite_rewarded"): return False
    reward = int(config.get("referral_reward", 25))
    Gq[istr]["points"] = Gq[istr].get("points",0) + reward
    Gq[istr]["invited_count"] = Gq[istr].get("invited_count", 0) + 1
    nu["invite_rewarded"] = True
    Gr["total_invites"] += 1
    new_username = nu.get("username", "")
    new_name = nu.get("first_name", "") or "مستخدم"
    notify_referral_reward(inviter_id, reward, new_username, new_name, new_user_id)
    try:
        force_send(int(new_user_id),
            f"{ee(E_WELCOME,'👋')} <b>مرحبـاً بـك</b>\n\n"
            f"{ee(E_SPARK,'✨')} لقد دخلت عبر رابط دعوة أحد المستخدمين\n"
            f"{ee(E_ROCKET,'🚀')} يمكنك الآن استخدام البوت")
    except: pass
    save_json(G1,Gq); save_json(G2,Gr)
    return True

# ✅✅✅ دالة آمنة لمعالجة الهدية (تم إصلاح الثغرة)
def apply_gift_code(uid, code):
    """ترجع (نجاح: bool, رسالة: str أو None)"""
    if not code or code not in Gt:
        return False, None
    g = Gt[code]
    used_by = [str(x) for x in g.get('used_by', [])]
    # ✅ منع نفس المستخدم من استخدام نفس الهدية أكثر من مرة
    if str(uid) in used_by:
        return False, f"{ee(E_BROKEN,'💔')} <b>لقد استخدمت هذه الهدية مسبقاً</b>"
    # ✅ منع تجاوز العدد الأقصى
    if g.get('used_count', 0) >= g.get('max_users', 1):
        return False, f"{ee(E_BROKEN,'💔')} <b>عذراً، هذه الهدية انتهت</b>"
    # ✅ إضافة النقاط
    g['used_count'] = g.get('used_count', 0) + 1
    g.setdefault('used_by', []).append(uid)
    pts = int(g.get('points', 0))
    Gq[str(uid)]["points"] = Gq[str(uid)].get("points", 0) + pts
    save_json(G6, Gt); save_json(G1, Gq)
    return True, f"{ee(E_GIFT,'🎁')} <b>هدية!</b>\n💰 حصلت على {pts} نقطة"

def validate_url(url, platform):
    url = (url or "").lower().strip()
    if not url: return False
    if platform=='instagram': return any(x in url for x in ['instagram.com','instagr.am'])
    if platform=='tiktok': return any(x in url for x in ['tiktok.com','vm.tiktok.com'])
    if platform=='telegram': return any(x in url for x in ['t.me/','telegram.me/'])
    return True

def send_order(sid, link, qty, provider_key=None):
    try:
        if not provider_key: pk, pv = get_default_provider()
        else: pk = provider_key; pv = get_provider(pk)
        if not pv: return False, "provider_not_found"
        if not pv.get("active", True): return False, "provider_inactive"
        url = pv.get("url", "").strip(); api_key = pv.get("api_key", "").strip()
        if not url or not api_key: return False, "provider_incomplete"
        data = {'key':api_key,'action':'add','service':str(sid),'link':link,'quantity':int(qty)}
        r = requests.post(url, data=data, timeout=30)
        if r.status_code==200:
            try:
                j = r.json()
                if 'order' in j: return True, j['order']
                if 'error' in j: return False, j['error']
            except: pass
        return False, "server error"
    except Exception as e: return False, str(e)

def get_order_status(oid, provider_key=None):
    try:
        if not provider_key: pk, pv = get_default_provider()
        else: pk = provider_key; pv = get_provider(pk)
        if not pv: return None
        url = pv.get("url", "").strip(); api_key = pv.get("api_key", "").strip()
        if not url or not api_key: return None
        data = {'key':api_key,'action':'status','order':str(oid)}
        r = requests.post(url, data=data, timeout=20)
        if r.status_code==200:
            try: return r.json()
            except: return None
    except: return None
    return None

def save_order(user_id, svc_name, link, qty, order_id=None, provider_key=None):
    try:
        u = get_user(user_id)
        u.setdefault("orders",[]).append({"service":str(svc_name),"link":str(link),"qty":int(qty),
            "order_id":str(order_id) if order_id else None,"created_at":time.time(),
            "status":"pending","provider":provider_key})
        if len(u["orders"])>50: u["orders"]=u["orders"][-50:]
        save_json(G1,Gq)
    except: pass

def mark_order_completed(user_id, oid):
    try:
        u = get_user(user_id)
        for o in u.get("orders", []):
            if isinstance(o, dict) and str(o.get("order_id")) == str(oid):
                o["status"] = "completed"; save_json(G1,Gq); return True
    except: pass
    return False

def has_claimed_channel(uid, ch_id):
    u = get_user(uid)
    return str(ch_id) in [str(c) for c in u.get("claimed_channels", [])]

def add_claimed_channel(uid, ch_id):
    u = get_user(uid)
    if "claimed_channels" not in u: u["claimed_channels"] = []
    if str(ch_id) not in [str(c) for c in u["claimed_channels"]]:
        u["claimed_channels"].append(str(ch_id)); save_json(G1, Gq); return True
    return False

def welcome_text(uid):
    return (f"{ee(E_SPARK,'✨')} <b>اهـلا بـك عزيـزي فَـي بـوت M7</b> {ee(E_FIRE,'🔥')}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{ee(E_BOLT,'⚡')} البوت متفَـوق بسَـرعة تنَـفيذ الطلـب\n"
            f"{ee(E_ROCKET,'🚀')} جَـميع المسـتخدمين حقيقـي والرشـق كذَالك\n"
            f"{ee(E_DIAMOND,'💎')} خدمات مميزة بأسعـار خـياليـة\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{ee(E_CROWN,'👑')} <b>ID</b> ← <code>{uid}</code>")

def send_welcome(uid, ud):
    send_h(uid, welcome_text(uid), markup=main_menu(uid, ud))

def main_menu(uid, ud):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(btn(f"نقاطي : {ud.get('points',0)}", callback_data="noop", emoji=E_DIAMOND, style="primary"))
    kb.row(btn("قسم الخدمات", callback_data="services_menu", emoji=E_BOLT, style="success"))
    kb.row(btn("الهـدية", callback_data="gift", emoji=E_GIFT, style="success"),
           btn("حسـابي", callback_data="account", emoji=E_EYE, style="primary"))
    kb.row(btn("الاحصـائيات", callback_data="stats", emoji=E_STAR, style="danger"),
           btn("طلباتـي", callback_data="my_orders", emoji=E_SEARCH, style="danger"))
    kb.row(btn("تجميع نقاط", callback_data="collect_points_menu", emoji=E_LINK, style="success"),
           btn("تحويل نقاط", callback_data="transfer", emoji=E_HEART, style="primary"))
    kb.row(btn("شراء نقاط", callback_data="buy_points", emoji=E_DIAMOND, style="success"))
    kb.row(btn("معلومات طلب", callback_data="request_info", emoji=E_SEARCH, style="primary"))
    kb.row(btn("المطور", url="https://t.me/zzmmkj", emoji=E_TG, style="primary"),
           btn("القـناة", url="https://t.me/LoFYqq", emoji=E_TG, style="primary"))
    kb.row(btn(f"عدد الطلبات : {Gr.get('total_requests',0)}", callback_data="noop", emoji=E_STAR, style="primary"))
    return kb

def build_collect_points_menu(uid):
    u = get_user(uid)
    rewards = config.get("channel_rewards", [])
    claimed = [str(x) for x in u.get("claimed_channels", [])]
    available_channels = [c for c in rewards if str(c.get("id","")) not in claimed]
    total_available = sum(int(c.get("points",0)) for c in available_channels)
    txt = (f"{ee(E_LINK,'🔗')} <b>تـجـمـيـع الـنـقـاط</b> {ee(E_SPARK,'✨')}\n"
           f"━━━━━━━━━━━━━━━\n"
           f"{ee(E_DIAMOND,'💎')} اختر طريقة تجميع النقاط :\n")
    if total_available > 0: txt += f"{ee(E_STAR,'⭐')} نقاط متاحة : <b>{total_available}</b>\n"
    txt += f"━━━━━━━━━━━━━━━"
    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(btn("من خلال رابط الدعوة", callback_data="collect_referral", emoji=E_LINK, style="primary"))
    ch_count = len(available_channels)
    ch_label = "من خلال الاشتراك بالقنوات"
    if ch_count > 0: ch_label += f" ({ch_count})"
    else: ch_label += " ✅"
    kb.row(btn(ch_label, callback_data="collect_channels", emoji=E_TG, style="success"))
    kb.row(btn("الهدية اليومية", callback_data="collect_daily_gift", emoji=E_GIFT, style="success"))
    kb.row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
    return txt, kb

def build_channels_view(uid):
    rewards = config.get("channel_rewards", [])
    u = get_user(uid)
    claimed = [str(x) for x in u.get("claimed_channels", [])]
    available = [(i, ch) for i, ch in enumerate(rewards) if str(ch.get("id", str(i))) not in claimed]
    kb = telebot.types.InlineKeyboardMarkup()
    txt = (f"{ee(E_TG,'📢')} <b>الاشـتـراك بالقـنوات</b>\n"
           f"━━━━━━━━━━━━━━━\n")
    if not rewards:
        txt += f"{ee(E_BROKEN,'💔')} لا يوجد قنوات حالياً"
        kb.row(btn("رجوع", callback_data="collect_points_menu", emoji=E_NO, style="danger"))
        return txt, kb
    if not available:
        txt += (f"{ee(E_YES,'✅')} <b>مبـروك !</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"{ee(E_CROWN,'👑')} لقد اشتركت بجميع القنوات المتاحة\n"
                f"{ee(E_SPARK,'✨')} لا يوجد قنوات جديدة حالياً\n"
                f"{ee(E_BOLT,'⚡')} تابعنا للمزيد قريباً\n"
                f"━━━━━━━━━━━━━━━")
        kb.row(btn("رجوع", callback_data="collect_points_menu", emoji=E_NO, style="danger"))
        return txt, kb
    txt += f"{ee(E_SPARK,'✨')} اشترك بالقنوات ثم اضغط تحقق\n\n"
    has_unclaimed = False
    for i, ch in available:
        name = ch.get("name", "?"); link = ch.get("link", "")
        points = ch.get("points", 0)
        emoji = ch.get("emoji") or E_TG; style = ch.get("style") or "primary"
        label = f"{name} [+{points}]"
        if link:
            kb.row(btn(label, url=link, emoji=emoji, style=style))
            has_unclaimed = True
        else:
            kb.row(btn(label, callback_data="noop", emoji=emoji, style=style))
    if has_unclaimed:
        kb.row(btn("تحـقق من الاشـتـراك", callback_data="chr_verify_all", emoji=E_YES, style="success"))
    kb.row(btn("رجوع", callback_data="collect_points_menu", emoji=E_NO, style="danger"))
    return txt, kb

def build_admin_panel():
    notif_state = config.get("login_notify", True)
    notif_emoji = E_YES if notif_state else E_CROSS
    notif_text = f"إشعار الدخول : {'مفعّل' if notif_state else 'معطّل'}"
    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(btn("إدارة الخدمات", callback_data="admin_services", emoji=E_BOLT, style="success"))
    kb.row(btn("إدارة القنوات", callback_data="admin_channels", emoji=E_TG, style="success"))
    kb.row(btn("اذاعة عامـة", callback_data="admin_broadcast", emoji=E_TG, style="primary"))
    kb.row(btn("حظر", callback_data="admin_ban", emoji=E_CROSS, style="danger"),
           btn("فك حظر", callback_data="admin_unban", emoji=E_YES, style="success"))
    kb.row(btn("الإعدادات", callback_data="admin_settings", emoji=E_EYE, style="primary"))
    kb.row(btn("صنع هدية", callback_data="admin_gift", emoji=E_GIFT, style="success"),
           btn("شحن نقاط", callback_data="admin_charge", emoji=E_DIAMOND, style="primary"))
    kb.row(btn("إدارة النقاط", callback_data="admin_points_mgr", emoji=E_DIAMOND, style="success"))
    kb.row(btn("الأكثر مبيعاً", callback_data="admin_top_services", emoji=E_STAR, style="success"))
    kb.row(btn("إعدادات الهدية", callback_data="admin_gift_settings", emoji=E_GIFT, style="success"),
           btn("إعدادات الدعوة", callback_data="admin_ref_settings", emoji=E_LINK, style="primary"))
    kb.row(btn("أسعار النقاط", callback_data="admin_points_prices", emoji=E_DIAMOND, style="success"))
    kb.row(btn(notif_text, callback_data="admin_toggle_login", emoji=notif_emoji,
               style="success" if notif_state else "danger"))
    kb.row(btn(f"عدد الطلبات : {Gr.get('total_requests',0)}", callback_data="noop", emoji=E_STAR, style="primary"))
    return kb

def build_admin_channels_menu():
    rewards = config.get("channel_rewards", [])
    forced = config.get("forced_channels", [])
    act_ch = config.get("activation_channel", "") or "غير محددة"
    reward_pts = config.get("channel_followers_reward_points", 5)
    txt = (f"{ee(E_TG,'📢')} <b>إدارة القنوات</b>\n"
           f"━━━━━━━━━━━━━━━\n"
           f"{ee(E_STAR,'⭐')} نقاط الاشتراك ← <b>{len(rewards)}</b> قناة\n"
           f"{ee(E_LOCK,'🔒')} الاشتراك الإجباري ← <b>{len(forced)}</b> قناة\n"
           f"{ee(E_ROCKET,'🚀')} قناة التفعيلات ← <code>{act_ch}</code>\n"
           f"{ee(E_DIAMOND,'💎')} نقاط قناة المشتري ← <b>{reward_pts}</b>\n"
           f"━━━━━━━━━━━━━━━")
    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(btn(f"نقاط الاشتراك ({len(rewards)})", callback_data="admin_channel_rewards", emoji=E_GIFT, style="success"))
    kb.row(btn(f"الاشتراك الإجباري ({len(forced)})", callback_data="admin_forced_subs", emoji=E_LOCK, style="success"))
    kb.row(btn("قناة التفعيلات", callback_data="admin_activation_ch", emoji=E_ROCKET, style="primary"))
    kb.row(btn(f"نقاط قناة المشتري : {reward_pts}", callback_data="admin_buyer_reward_pts", emoji=E_DIAMOND, style="primary"))
    kb.row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
    return txt, kb

def build_reorder_menu():
    ordered = [k for k in get_ordered_services() if k != "tele_real_followers"]
    kb = telebot.types.InlineKeyboardMarkup()
    txt = (f"{ee(E_BOLT,'⚙️')} <b>ترتيب الخدمات</b>\n"
           f"━━━━━━━━━━━━━━━\n")
    if "tele_real_followers" in SERVICES:
        txt += (f"{ee(E_CROWN,'👑')} متابعين تيليجرام (مثبت أول)\n"
                f"{ee(E_LOCK,'🔒')} لا يمكن تحريكها\n"
                f"━━━━━━━━━━━━━━━\n")
    txt += f"{ee(E_SPARK,'✨')} استخدم ⬆️ ⬇️ لترتيب الباقي\n\n"
    if not ordered:
        txt += f"{ee(E_BROKEN,'💔')} لا يوجد خدمات"
    else:
        for i, k in enumerate(ordered):
            svc = SERVICES.get(k, {})
            name = svc.get('name','')[:22]
            emoji, style = get_srv_props(k, svc)
            is_hidden = k in config.get('hidden_services', [])
            hidden_mark = " (مخفي)" if is_hidden else ""
            nav = []
            if i > 0:
                nav.append(btn("⬆️", callback_data=f"sord_up_{k}", emoji=E_ROCKET, style="primary"))
            if i < len(ordered)-1:
                nav.append(btn("⬇️", callback_data=f"sord_dn_{k}", emoji=E_ROCKET, style="primary"))
            kb.row(btn(f"{name}{hidden_mark}", callback_data="noop", emoji=emoji, style=style), *nav)
    kb.row(btn("رجوع", callback_data="admin_services", emoji=E_NO, style="danger"))
    return txt, kb

def build_toggle_services_menu():
    kb = telebot.types.InlineKeyboardMarkup()
    txt = (f"{ee(E_EYE,'👁')} <b>إخفاء / إظهار الخدمات</b>\n"
           f"━━━━━━━━━━━━━━━\n"
           f"{ee(E_YES,'✅')} = ظاهر | {ee(E_CROSS,'❌')} = مخفي\n"
           f"{ee(E_SPARK,'✨')} اضغط على الخدمة للتبديل\n\n")
    hidden = config.get('hidden_services', [])
    ordered = get_ordered_services()
    if not ordered:
        txt += f"{ee(E_BROKEN,'💔')} لا يوجد خدمات"
    for k in ordered:
        if k not in SERVICES: continue
        svc = SERVICES[k]
        is_hidden = k in hidden
        status = "❌ مخفي" if is_hidden else "✅ ظاهر"
        if k == "tele_real_followers":
            status += " ⭐"
        name = svc.get('name','')[:20]
        style = "danger" if is_hidden else "success"
        emoji = E_CROSS if is_hidden else E_YES
        kb.row(btn(f"{name} | {status}", callback_data=f"stog_{k}", emoji=emoji, style=style))
    kb.row(btn("رجوع", callback_data="admin_services", emoji=E_NO, style="danger"))
    return txt, kb

def build_channel_rewards_admin():
    rewards = config.get("channel_rewards", [])
    kb = telebot.types.InlineKeyboardMarkup()
    txt = (f"{ee(E_TG,'📢')} <b>نقاط الاشتراك بالقنوات</b>\n"
           f"━━━━━━━━━━━━━━━\n"
           f"{ee(E_STAR,'⭐')} <b>عدد القنوات</b> ← {len(rewards)}\n"
           f"━━━━━━━━━━━━━━━\n\n")
    if not rewards:
        txt += f"{ee(E_BROKEN,'💔')} <i>لا يوجد قنوات مضافة</i>\n"
    else:
        for i, ch in enumerate(rewards):
            name = ch.get("name", "?"); link = ch.get("link", "")[:35]
            points = ch.get("points", 0); chat_id = ch.get("chat_id", "") or "غير محدد"
            auto_mark = " 🤖" if ch.get("from_service") else ""
            txt += (f"<b>{i+1}.</b> {name}{auto_mark}\n   🔗 <code>{link}</code>\n"
                    f"   🆔 <code>{chat_id}</code>\n   💎 النقاط ← {points}\n\n")
            kb.row(btn(f"تعديل {name[:20]}", callback_data=f"chr_edit_{i}", emoji=E_SEARCH, style="primary"))
    kb.row(btn("➕ إضافة قناة", callback_data="chr_add", emoji=E_SPARK, style="success"))
    kb.row(btn("رجوع", callback_data="admin_channels", emoji=E_NO, style="danger"))
    return txt, kb

def build_services_menu():
    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(btn("⚙️ ترتيب الخدمات", callback_data="admin_srv_order", emoji=E_BOLT, style="primary"))
    kb.row(btn("👁 إخفاء / إظهار", callback_data="admin_srv_toggle", emoji=E_EYE, style="success"))
    kb.row(btn("تعديل خدمة", callback_data="srv_edit_list", emoji=E_SEARCH, style="primary"))
    kb.row(btn("إضافة خدمة", callback_data="srv_add", emoji=E_SPARK, style="success"))
    kb.row(btn("حذف خدمة", callback_data="srv_del_list", emoji=E_CROSS, style="danger"))
    kb.row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
    return kb

def build_points_mgr_menu(page=0):
    try:
        users_list = sorted(Gq.items(), key=lambda x: x[1].get('points', 0), reverse=True)
        users_list = [u for u in users_list if u[1].get('points',0) > 0]
        total = len(users_list); per_page = 8
        start = page * per_page; end = start + per_page
        page_users = users_list[start:end]
        kb = telebot.types.InlineKeyboardMarkup()
        for uid_key, u in page_users:
            pts = u.get('points', 0); uname = u.get('username', '')
            label = f"{uname or uid_key} : {pts}"[:45]
            kb.row(btn(label, callback_data=f"pm_{uid_key}", emoji=E_DIAMOND, style="primary"))
        nav = []
        if page > 0: nav.append(btn("السابق", callback_data=f"pm_page_{page-1}", emoji=E_NO, style="primary"))
        if end < total: nav.append(btn("التالي", callback_data=f"pm_page_{page+1}", emoji=E_ROCKET, style="success"))
        if nav: kb.row(*nav)
        kb.row(btn("بحث بالـ ID", callback_data="pm_search", emoji=E_SEARCH, style="success"))
        kb.row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
        header = (f"{ee(E_CROWN,'👑')} <b>إدارة النقاط</b>\n━━━━━━━━━━━━━━━\n"
                  f"{ee(E_STAR,'⭐')} إجمالي المستخدمين بالنقاط ← <b>{total}</b>\n"
                  f"{ee(E_EYE,'👁')} الصفحة ← <b>{page+1}</b>")
        return header, kb
    except:
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
        return f"{ee(E_BROKEN,'💔')} خطأ", kb

def build_forced_subs_menu():
    forced = config.get("forced_channels", [])
    kb = telebot.types.InlineKeyboardMarkup()
    txt = f"{ee(E_LOCK,'🔒')} <b>الاشتراك الإجباري</b>\n━━━━━━━━━━━━━━━\n"
    if not forced: txt += f"{ee(E_BROKEN,'💔')} <i>لا يوجد قنوات</i>\n"
    else:
        txt += f"{ee(E_STAR,'⭐')} <b>القنوات</b> ← {len(forced)}\n━━━━━━━━━━━━━━━\n"
        emoji_pool = [E_TG, E_LINK, E_STAR, E_HEART, E_GIFT, E_FIRE, E_CROWN, E_DIAMOND]
        for i, ch in enumerate(forced):
            name = ch.get("name", "?"); link = ch.get("link", "")
            emoji = ch.get("emoji") or emoji_pool[i % len(emoji_pool)]
            style = ch.get("style") or "primary"
            txt += f"\n{ee(emoji, '📢')} <b>{i+1}.</b> {name}\n   🔗 <code>{link[:40]}</code>\n"
            kb.row(btn(f"تعديل {name[:20]}", callback_data=f"fsub_edit_{i}", emoji=E_SEARCH, style=style))
    kb.row(btn("إضافة قناة", callback_data="fsub_add", emoji=E_SPARK, style="success"))
    kb.row(btn("رجوع", callback_data="admin_channels", emoji=E_NO, style="danger"))
    return txt, kb

def build_top_services_menu():
    try:
        sales = Gr.get("service_sales", {})
        total_sales = sum(sales.values()) if sales else 0
        all_services_ranked = []
        for key, svc in SERVICES.items():
            count = sales.get(key, 0); all_services_ranked.append((key, svc, count))
        all_services_ranked.sort(key=lambda x: x[2], reverse=True)
        txt = (f"{ee(E_CROWN,'👑')} <b>الأكثـر مبيعـاً</b> {ee(E_FIRE,'🔥')}\n"
               f"━━━━━━━━━━━━━━━\n"
               f"{ee(E_STAR,'⭐')} <b>إجمالي الطلبات</b> ← <b>{total_sales}</b>\n"
               f"{ee(E_BOLT,'⚡')} <b>عدد الخدمات</b> ← {len(SERVICES)}\n"
               f"━━━━━━━━━━━━━━━\n\n")
        medals = ["🥇","🥈","🥉"]
        kb = telebot.types.InlineKeyboardMarkup()
        if not SERVICES:
            txt += f"{ee(E_BROKEN,'💔')} لا يوجد خدمات"
        for i, (key, svc, count) in enumerate(all_services_ranked):
            name = svc.get('name', key); price = svc.get('price', 0); unit = svc.get('unit', 100)
            prov = svc.get('provider', 'p1')
            prov_name = get_provider(prov).get('name','?') if get_provider(prov) else '?'
            if prov == "internal": prov_name = "نظام داخلي"
            is_hidden = key in config.get('hidden_services', [])
            hidden_mark = " (مخفية)" if is_hidden else ""
            if count > 0 and i < 3:
                rank = medals[i]
                txt += (f"{rank} <b>{name}</b>{hidden_mark}\n"
                        f"   {ee(E_STAR,'⭐')} الطلبات ← <b>{count}</b>\n"
                        f"   {ee(E_DIAMOND,'💎')} السعر ← {price} لكل {unit}\n"
                        f"   {ee(E_ROCKET,'🚀')} المزود ← {prov_name}\n"
                        f"   🆔 <code>{key}</code>\n━━━━━━━━━━━━━━━\n\n")
            elif count > 0:
                txt += (f"<b>{i+1}.</b> {name}{hidden_mark}\n"
                        f"   {ee(E_STAR,'⭐')} <b>{count}</b> طلب | {price}/{unit} | {prov_name}\n\n")
            elif count == 0 and i < 15:
                txt += (f"<b>{i+1}.</b> {name}{hidden_mark}\n"
                        f"   {ee(E_BROKEN,'💔')} لا يوجد طلبات | {price}/{unit}\n\n")
        kb.row(btn("🔄 تحديث", callback_data="admin_top_services", emoji=E_ROCKET, style="success"))
        kb.row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
        return txt, kb
    except:
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
        return f"{ee(E_BROKEN,'💔')} خطأ", kb

def build_providers_menu():
    provs = config.get("providers", {})
    txt = (f"{ee(E_ROCKET,'🚀')} <b>إدارة المزودين</b>\n━━━━━━━━━━━━━━━\n"
           f"{ee(E_STAR,'⭐')} <b>إجمالي المزودين</b> ← {len(provs)}\n"
           f"{ee(E_YES,'✅')} <b>النشطين</b> ← {len(get_active_providers())}\n━━━━━━━━━━━━━━━\n\n")
    kb = telebot.types.InlineKeyboardMarkup()
    emoji_pool = [E_TG, E_LINK, E_STAR, E_HEART, E_GIFT, E_FIRE]
    if not provs:
        txt += f"{ee(E_BROKEN,'💔')} <i>لا يوجد مزودين - أضف مزود أولاً</i>\n"
    for i, (pk, pv) in enumerate(provs.items()):
        name = pv.get('name','?'); url = pv.get('url','')[:30]
        active = pv.get('active', True); is_default = pv.get('default', False)
        emoji = emoji_pool[i % len(emoji_pool)]
        status = "🟢 نشط" if active else "🔴 معطّل"
        default_mark = " ⭐" if is_default else ""
        txt += f"{ee(emoji, '📢')} <b>{name}</b>{default_mark}\n   {ee(E_LINK,'🔗')} <code>{url}</code>\n   {status}\n\n"
        kb.row(btn(f"تعديل {name[:15]}{default_mark}", callback_data=f"prov_edit_{pk}", emoji=E_SEARCH, style="primary"))
    kb.row(btn("➕ إضافة مزود", callback_data="prov_add", emoji=E_SPARK, style="success"))
    kb.row(btn("رجوع", callback_data="admin_settings", emoji=E_NO, style="danger"))
    return txt, kb

admin_add_srv = {}; admin_edit_srv = {}; pending_orders = {}; pm_state = {}; fsub_state = {}
prov_state = {}; gift_state = {}; charge_state = {}; chr_state = {}; edit_link_state = {}

def clean_msgs(uid, state):
    if not state: return
    for mid in state.get('msgs', []):
        try: golden.delete_message(uid, mid)
        except: pass
    clear_user_state(uid)

def extract_channel_identifier(link):
    if not link: return None
    link = link.strip()
    if link.startswith('@'): return link
    if 't.me/' in link:
        uname = link.split('t.me/')[-1].strip('/').split('?')[0]
        if uname and not uname.startswith('+') and not uname.startswith('joinchat'):
            return '@' + uname
    if link.startswith('-') and link[1:].isdigit(): return link
    return None

def verify_bot_admin_in_channel(ch_id):
    try:
        bot_id = golden.get_me().id
        st = golden.get_chat_member(ch_id, bot_id)
        return st.status in ['administrator', 'creator']
    except Exception as e:
        print(f"verify_bot_admin: {e}")
        return False

def add_buyer_channel_to_rewards(uid, ch_id, link, order_id, qty=0):
    rewards = config.get("channel_rewards", [])
    for r in rewards:
        if r.get("chat_id") == ch_id or (r.get("link") and r.get("link") == link):
            return False
    try:
        chat_info = golden.get_chat(ch_id)
        ch_name = chat_info.title or f"قناة {ch_id}"
    except:
        ch_name = f"قناة {ch_id}"
    points = int(config.get("channel_followers_reward_points", 5))
    new_id = f"auto_{int(time.time())}_{random.randint(100,999)}"
    rewards.append({
        "id": new_id,
        "name": ch_name,
        "link": link,
        "chat_id": ch_id,
        "points": points,
        "emoji": random.choice([E_TG, E_LINK, E_STAR, E_HEART, E_GIFT, E_FIRE]),
        "style": random.choice(["primary", "success"]),
        "owner_id": str(uid),
        "from_service": True,
        "order_id": str(order_id) if order_id else None,
        "order_qty": int(qty),
        "verified_count": 0
    })
    config["channel_rewards"] = rewards
    save_json(CONFIG_FILE, config)
    return new_id

def remove_buyer_channel_from_rewards(ch_id):
    rewards = config.get("channel_rewards", [])
    new_rewards = [r for r in rewards if not (r.get("from_service") and r.get("chat_id") == ch_id)]
    if len(new_rewards) != len(rewards):
        config["channel_rewards"] = new_rewards
        save_json(CONFIG_FILE, config)
        return True
    return False

def monitor_channel_orders():
    while True:
        try:
            time.sleep(60)
            try: bot_id = golden.get_me().id
            except: bot_id = None
            if not bot_id: continue
            for uid_str, u in list(Gq.items()):
                orders = u.get("orders", [])
                changed = False
                for o in orders:
                    if not isinstance(o, dict): continue
                    if o.get("status") in ("ended", "completed"): continue

                    if o.get("is_internal"):
                        if not o.get("monitored"): continue
                        ch_id = o.get("channel_id")
                        if not ch_id: continue
                        try:
                            st = golden.get_chat_member(ch_id, bot_id)
                            if st.status not in ('administrator', 'creator'):
                                o["status"] = "ended"
                                changed = True
                                try: remove_buyer_channel_from_rewards(ch_id)
                                except: pass
                                try:
                                    force_send(int(uid_str),
                                        f"{ee(E_BROKEN,'💔')} <b>تم إنهاء اشتراكك</b>\n"
                                        f"━━━━━━━━━━━━━━━\n"
                                        f"{ee(E_LOCK,'🔒')} تم إزالة البوت من قناتك\n"
                                        f"{ee(E_CROSS,'❌')} الخدمة توقفت مباشرة\n"
                                        f"{ee(E_TG,'📢')} قناتك أُزيلت من قسم تجميع النقاط\n"
                                        f"━━━━━━━━━━━━━━━\n"
                                        f"{ee(E_SPARK,'✨')} لإعادة التفعيل أضف البوت مرة أخرى")
                                except: pass
                        except Exception as e:
                            err_str = str(e).lower()
                            if "chat not found" in err_str or "user not found" in err_str or "chat_id is empty" in err_str:
                                o["status"] = "ended"
                                changed = True
                                try: remove_buyer_channel_from_rewards(ch_id)
                                except: pass
                                try:
                                    force_send(int(uid_str),
                                        f"{ee(E_BROKEN,'💔')} <b>تم إنهاء اشتراكك</b>\n"
                                        f"━━━━━━━━━━━━━━━\n"
                                        f"{ee(E_CROSS,'❌')} تعذر الوصول لقناتك\n"
                                        f"━━━━━━━━━━━━━━━\n"
                                        f"{ee(E_LOCK,'🔒')} لإعادة التفعيل أضف البوت مرة أخرى")
                                except: pass
                        continue

                    oid = o.get("order_id")
                    if not oid: continue
                    prov_key = o.get("provider")
                    if prov_key == "internal": continue
                    try:
                        st = get_order_status(oid, prov_key)
                        if st and 'error' not in st:
                            status = st.get("status","")
                            if status in ['Completed', 'Partial']:
                                o["status"] = "completed"
                                changed = True
                                try:
                                    force_send(int(uid_str),
                                        f"{ee(E_YES,'✅')} <b>اكتمل طلبك</b>\n"
                                        f"━━━━━━━━━━━━━━━\n"
                                        f"{ee(E_SEARCH,'🔍')} <code>{oid}</code>\n"
                                        f"{ee(E_STAR,'⭐')} {o.get('service','')}\n"
                                        f"{ee(E_HEART,'💗')} شكراً لاستخدامك")
                                except: pass
                            elif status in ['Canceled', 'Cancelled']:
                                o["status"] = "ended"
                                changed = True
                                try:
                                    force_send(int(uid_str),
                                        f"{ee(E_BROKEN,'💔')} <b>تم إلغاء طلبك</b>\n"
                                        f"━━━━━━━━━━━━━━━\n"
                                        f"{ee(E_SEARCH,'🔍')} <code>{oid}</code>\n"
                                        f"{ee(E_STAR,'⭐')} {o.get('service','')}")
                                except: pass
                    except: pass
                if changed:
                    try: save_json(G1, Gq)
                    except: pass
        except Exception as e:
            print(f"monitor thread error: {e}")
            time.sleep(30)

@golden.message_handler(commands=['start'])
def cmd_start(m):
    try:
        uid = m.from_user.id
        if X13(uid): send_h(uid, "📛 أنت محظور"); return
        clear_user_state(uid)
        gift_state.pop(uid, None); charge_state.pop(uid, None)
        chr_state.pop(uid, None); edit_link_state.pop(uid, None)
        _sub_cache.pop(uid, None)
        uname = m.from_user.username or ""
        fname = m.from_user.first_name or "المستخدم"
        parts = m.text.split()
        ref, gift_code = None, None
        if len(parts)==2:
            p = parts[1]
            if p.isdigit(): ref = p
            elif p.startswith('Xbot_'): gift_code = p
        ud, is_new = X8(uid, uname, invited_by=ref, first_name=fname)
        if is_new: notify_admin_login(uid, uname, fname, invited_by=ref)

        # ✅ نحفظ كود الهدية مؤقتاً لمعالجته بعد التحقق من الاشتراك
        if gift_code and gift_code in Gt:
            ud["pending_gift"] = gift_code
            save_json(G1, Gq)

        # ✅ فحص الاشتراك أولاً
        if not X12(uid): send_sub_msg(uid); return

        # ✅ الآن نعالج الهدية بعد التحقق من الاشتراك (إصلاح الثغرة)
        if ud.get("pending_gift"):
            ok, msg = apply_gift_code(uid, ud["pending_gift"])
            ud["pending_gift"] = ""
            save_json(G1, Gq)
            if msg: send_h(uid, msg)

        if ref and ref != str(uid) and ref in Gq: process_invitation_reward(int(ref), uid)
        send_welcome(uid, ud)
    except Exception as e: print(f"start err: {e}"); traceback.print_exc()

@golden.message_handler(commands=['admin'])
def cmd_admin(m):
    if m.from_user.id != G8: return
    clear_user_state(G8)
    try:
        golden.send_message(G8, f"{ee(E_CROWN,'👑')} <b>لوحة الأدمن</b>", reply_markup=build_admin_panel(), parse_mode='HTML'); return
    except: pass
    try: golden.send_message(G8, "👑 لوحة الأدمن", reply_markup=build_admin_panel())
    except: pass

@golden.callback_query_handler(func=lambda c: True)
def on_cb(call):
    def _bg_answer():
        try:
            time.sleep(1.2)
            golden.answer_callback_query(call.id)
        except: pass
    try:
        threading.Thread(target=_bg_answer, daemon=True).start()
    except: pass
    try: _handle_cb(call)
    except Exception as e:
        print(f"❌ CB ERR: {e}"); traceback.print_exc()
        try: golden.answer_callback_query(call.id)
        except: pass
        try: send_h(call.from_user.id, f"{ee(E_BROKEN,'💔')} <b>خطأ مؤقت</b>", markup=restart_kb())
        except: pass
        return
    try: golden.answer_callback_query(call.id)
    except: pass

def _handle_cb(call):
    uid = call.from_user.id
    if X13(uid):
        try: golden.answer_callback_query(call.id, "📛 محظور", show_alert=True)
        except: pass
        return
    ud = get_user(uid)
    d = call.data; cid = call.message.chat.id; mid = call.message.message_id

    if d == "verify_sub":
        _sub_cache.pop(uid, None)
        if not X12(uid):
            golden.answer_callback_query(call.id, "❌ لم تشترك بكل القنوات بعد", show_alert=True)
            send_sub_msg(uid); return
        golden.answer_callback_query(call.id, "✅ تم التحقق", show_alert=True)
        # ✅ معالجة الهدية المعلقة
        if ud.get("pending_gift"):
            ok, msg = apply_gift_code(uid, ud["pending_gift"])
            ud["pending_gift"] = ""
            save_json(G1, Gq)
            if msg: send_h(uid, msg)
        inv = ud.get("invited_by")
        if inv and str(inv) != str(uid) and str(inv) in Gq: process_invitation_reward(int(inv), uid)
        edit_h(cid, mid, welcome_text(uid), main_menu(uid, ud)); return

    if d.startswith("verify_"):
        _sub_cache.pop(uid, None)
        if not X12(uid):
            golden.answer_callback_query(call.id, "انضـم للقـناة ثـم اضغـط تحـقق", show_alert=True); return
        golden.answer_callback_query(call.id, "✅ تم التحقق", show_alert=True)
        # ✅ معالجة الهدية المعلقة
        if ud.get("pending_gift"):
            ok, msg = apply_gift_code(uid, ud["pending_gift"])
            ud["pending_gift"] = ""
            save_json(G1, Gq)
            if msg: send_h(uid, msg)
        inv = ud.get("invited_by")
        if inv and str(inv) != str(uid) and str(inv) in Gq: process_invitation_reward(int(inv), uid)
        edit_h(cid, mid, welcome_text(uid), main_menu(uid, ud)); return

    if not X12(uid) and uid != G8:
        send_sub_msg(uid); return

    if d.startswith("upd_link_"):
        oid = d.replace("upd_link_","")
        target_order = None
        for o in ud.get("orders", []):
            if isinstance(o, dict) and str(o.get("order_id"))==str(oid) and o.get("is_internal"):
                target_order = o; break
        if not target_order:
            golden.answer_callback_query(call.id, "❌ الطلب غير موجود", show_alert=True); return
        edit_link_state[uid] = {'order_id': oid, 'old_channel_id': target_order.get('channel_id'), 'msgs': [mid]}
        kb = telebot.types.InlineKeyboardMarkup().row(
            btn("إلغاء", callback_data="upd_link_cancel", emoji=E_CROSS, style="danger"))
        txt = (f"{ee(E_LINK,'🔗')} <b>تحديث رابط القناة</b>\n"
               f"━━━━━━━━━━━━━━━\n"
               f"{ee(E_LOCK,'🔒')} <b>الشروط :</b>\n"
               f"• البوت يجب أن يكون أدمن في القناة الجديدة\n"
               f"• الرابط يجب أن يكون صحيحاً\n"
               f"━━━━━━━━━━━━━━━\n"
               f"{ee(E_SPARK,'✨')} أرسل الرابط الجديد الآن :")
        try:
            golden.edit_message_text(text=txt, chat_id=cid, message_id=mid, reply_markup=kb, parse_mode='HTML')
        except: pass
        golden.register_next_step_handler_by_chat_id(uid, process_update_link)
        return

    if d == "upd_link_cancel":
        edit_link_state.pop(uid, None); clear_user_state(uid)
        show_my_orders(uid, call.message, "active"); return

    if d == "collect_points_menu":
        txt, kb = build_collect_points_menu(uid); edit_h(cid, mid, txt, kb); return

    if d == "collect_referral":
        link = f"https://t.me/{golden.get_me().username}?start={uid}"
        rw = config.get("referral_reward",25)
        txt = (f"{ee(E_LINK,'🔗')} <b>رابط الدعوة الخاص بك</b>\n━━━━━━━━━━━━━━━\n"
               f"<code>{link}</code>\n\n"
               f"{ee(E_GIFT,'🎁')} مكافأتك ← <b>{rw} نقطة</b> لكل شخص\n"
               f"{ee(E_STAR,'⭐')} عدد المدعوين ← <b>{ud.get('invited_count',0)}</b>\n"
               f"━━━━━━━━━━━━━━━\n"
               f"{ee(E_SPARK,'✨')} أرسل الرابط لأصدقائك")
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(telebot.types.InlineKeyboardButton("📋 نسخ رابط الإحالة", switch_inline_query=link))
        kb.row(btn("أفضل المدعين", callback_data="top_referrers", emoji=E_CROWN, style="success"))
        kb.row(btn("رجوع", callback_data="collect_points_menu", emoji=E_NO, style="danger"))
        edit_h(cid, mid, txt, kb); return

    if d == "copy_referral_link":
        link = f"https://t.me/{golden.get_me().username}?start={uid}"
        try: golden.answer_callback_query(call.id, f"📋 الرابط:\n{link}", show_alert=True)
        except: pass
        return

    if d == "collect_channels":
        txt, kb = build_channels_view(uid); edit_h(cid, mid, txt, kb); return

    if d.startswith("chr_done_"):
        golden.answer_callback_query(call.id, "✅ تم استلام نقاط هذه القناة مسبقاً", show_alert=True); return

    if d == "chr_verify_all":
        rewards = config.get("channel_rewards", [])
        if not rewards:
            golden.answer_callback_query(call.id, "❌ لا يوجد قنوات", show_alert=True); return
        new_claimed = []
        failed = []
        already = []
        for i, ch in enumerate(rewards):
            ch_id = str(ch.get("id", str(i)))
            if has_claimed_channel(uid, ch_id):
                already.append(ch.get("name","?")); continue
            chat_id = ch.get("chat_id", "").strip()
            if not chat_id:
                link = ch.get("link", "").strip()
                if "t.me/+" in link or "joinchat" in link:
                    failed.append(ch.get("name","?")); continue
                if "t.me/" in link:
                    uname = link.split("t.me/")[-1].strip("/").split("?")[0]
                    if uname.startswith("+"):
                        failed.append(ch.get("name","?")); continue
                    chat_id = "@" + uname
                elif link.startswith("@"): chat_id = link
                else:
                    failed.append(ch.get("name","?")); continue
            try:
                status = golden.get_chat_member(chat_id, uid).status
                if status in ['member','administrator','creator']:
                    add_claimed_channel(uid, ch_id)
                    pts = int(ch.get("points",0))
                    Gq[str(uid)]["points"] = Gq[str(uid)].get("points",0) + pts
                    save_json(G1, Gq)
                    new_claimed.append({"name": ch.get("name","?"), "points": pts})
                    if ch.get("from_service"):
                        for r in config.get("channel_rewards", []):
                            if str(r.get("id")) == ch_id:
                                r["verified_count"] = r.get("verified_count", 0) + 1
                                break
                else:
                    failed.append(ch.get("name","?"))
            except Exception as e:
                print(f"chr_verify {chat_id}: {str(e)[:80]}")
                failed.append(ch.get("name","?"))
        save_json(CONFIG_FILE, config)
        txt = f"{ee(E_SPARK,'✨')} <b>نتيجة التحقق</b> {ee(E_SPARK,'✨')}\n━━━━━━━━━━━━━━━\n"
        if new_claimed:
            total = sum(c["points"] for c in new_claimed)
            txt += f"{ee(E_YES,'✅')} <b>تم إضافة النقاط بنجاح</b>\n"
            for c in new_claimed:
                txt += f"   {ee(E_GIFT,'🎁')} {c['name']} ← <b>+{c['points']}</b>\n"
            txt += f"━━━━━━━━━━━━━━━\n{ee(E_DIAMOND,'💎')} <b>إجمالي النقاط المضافة</b> ← <b>{total}</b>\n"
        if already:
            txt += f"\n{ee(E_STAR,'⭐')} <b>مستلمة مسبقاً :</b> {', '.join(already[:3])}\n"
        if failed:
            txt += f"\n{ee(E_BROKEN,'💔')} <b>لم تشترك بـ :</b> {', '.join(failed[:3])}\n"
        if not new_claimed and not failed and not already:
            txt += f"{ee(E_BROKEN,'💔')} لا يوجد قنوات"
        txt += f"\n{ee(E_CROWN,'👑')} <b>نقاطك الآن</b> ← <code>{Gq[str(uid)].get('points',0)}</code>"
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(btn("رجوع للقنوات", callback_data="collect_channels", emoji=E_TG, style="primary"))
        kb.row(btn("القائمة الرئيسية", callback_data="back_main", emoji=E_ROCKET, style="success"))
        edit_h(cid, mid, txt, kb)
        if new_claimed:
            golden.answer_callback_query(call.id, f"✅ تم إضافة {sum(c['points'] for c in new_claimed)} نقطة", show_alert=True)
        else:
            golden.answer_callback_query(call.id, "❌ لم تحقق شروط أي قناة", show_alert=True)
        return

    if d == "collect_daily_gift":
        now = time.time(); cd = int(config.get("daily_gift_cooldown",172800)); gp = int(config.get("daily_gift_points",10))
        if now - ud.get("last_gift",0) >= cd:
            ud["points"] = ud.get("points",0) + gp
            ud["gifts_collected"] = ud.get("gifts_collected",0) + 1
            ud["gift_points"] = ud.get("gift_points",0) + gp
            ud["last_gift"] = now; save_json(G1,Gq)
            txt = (f"{ee(E_GIFT,'🎁')} <b>الهدية اليومية</b> {ee(E_SPARK,'✨')}\n"
                   f"━━━━━━━━━━━━━━━\n"
                   f"{ee(E_YES,'✅')} تم استلام الهدية\n"
                   f"{ee(E_DIAMOND,'💎')} <b>+{gp} نقطة</b>\n"
                   f"{ee(E_CROWN,'👑')} <b>نقاطك الآن</b> ← <code>{ud.get('points',0)}</code>")
        else:
            h = int((cd-(now-ud.get("last_gift",0)))//3600)+1
            txt = f"{ee(E_LOCK,'🔒')} <b>انتظر</b> {h} ساعة للحصول على الهدية القادمة"
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(btn("رجوع", callback_data="collect_points_menu", emoji=E_NO, style="danger"))
        edit_h(cid, mid, txt, kb); return

    if d == "services_menu":
        clear_user_state(uid)
        kb = telebot.types.InlineKeyboardMarkup()
        vis = visible_services()
        if not vis:
            txt = (f"{ee(E_BOLT,'⚡')} <b>قسـم الخـدمات</b>\n━━━━━━━━━━━━━━━\n"
                   f"{ee(E_BROKEN,'💔')} لا يوجد خدمات حالياً\n"
                   f"{ee(E_SPARK,'✨')} تابعنا قريباً")
            kb.row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
            edit_h(cid, mid, txt, kb); return
        for k, svc in vis.items():
            emoji, style = get_srv_props(k, svc)
            kb.row(btn(svc.get('name',''), callback_data=f"srvsel_{k}", emoji=emoji, style=style))
        kb.row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
        edit_h(cid, mid, f"{ee(E_BOLT,'⚡')} <b>قسـم الخـدمات</b>\n━━━━━━━━━━━━━━━\n{ee(E_SPARK,'✨')} اخـتر نـوع الخـدمة", kb); return

    if d.startswith("srvsel_"):
        sk = d.replace("srvsel_","")
        if sk not in SERVICES or sk in config.get('hidden_services',[]):
            golden.answer_callback_query(call.id, "❌ خدمة غير متوفرة", show_alert=True); return
        svc = SERVICES[sk]
        if svc.get('special') == 'channel_followers':
            final_price = svc.get('final_price', svc.get('price', 0))
            pack = svc.get('unit', 1000)
            min_q = svc.get('min', 100); max_q = svc.get('max', 100000)
            try: bot_username = golden.get_me().username
            except: bot_username = "Bot"
            template = svc.get('warning_text') or DEFAULT_TELE_REAL_WARNING
            warn = template
            warn = warn.replace('{bot}', bot_username)
            warn = warn.replace('{price}', str(final_price))
            warn = warn.replace('{final_price}', str(final_price))
            warn = warn.replace('{pack}', str(pack))
            warn = warn.replace('{unit}', str(pack))
            warn = warn.replace('{min}', str(min_q))
            warn = warn.replace('{max}', str(max_q))
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("موافق ✅", callback_data=f"spcf_ok_{sk}", emoji=E_YES, style="success"),
                   btn("إلغاء ❌", callback_data=f"back_main", emoji=E_CROSS, style="danger"))
            edit_h(cid, mid, warn, kb)
            return
        final_price = svc.get('final_price', svc.get('price', 0))
        pack = svc.get('unit', 100)
        min_q = svc.get('min', 0); max_q = svc.get('max', 0)
        qty_line = f"{min_q}" if min_q == max_q else f"{min_q} - {max_q}"
        text = (f"{ee(E_BOLT,'⚡')} <b>اسم الخـدمة :</b>\n{svc.get('name','')}\n\n")
        if svc.get('description'): text += f"{ee(E_SPARK,'✨')} <b>الوصف :</b>\n{svc.get('description')}\n\n"
        text += (f"{ee(E_DIAMOND,'💎')} <b>السعر النهائي :</b> {final_price} نقطة لـ {pack}\n"
                 f"{ee(E_STAR,'⭐')} <b>الكمية :</b> {qty_line}\n\n━━━━━━━━━━━━━━━\n"
                 f"{ee(E_ROCKET,'🚀')} أرسل <b>{qty_line}</b> للتأكيد")
        kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="services_menu", emoji=E_NO, style="danger"))
        edit_h(cid, mid, text, kb)
        clear_user_state(cid)
        golden.register_next_step_handler(call.message, handle_qty_step, sk); return

    if d.startswith("spcf_ok_"):
        sk = d.replace("spcf_ok_","")
        if sk not in SERVICES: golden.answer_callback_query(call.id, "❌"); return
        svc = SERVICES[sk]
        min_q = svc.get('min', 100); max_q = svc.get('max', 100000)
        qty_line = f"{min_q}" if min_q == max_q else f"{min_q} - {max_q}"
        try: bot_username = golden.get_me().username
        except: bot_username = "Bot"
        text = (f"{ee(E_BOLT,'⚡')} <b>متابعين تيليجرام حقيقيين</b>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"{ee(E_LOCK,'🔒')} <b>الخطوة 1 :</b> أضف البوت <b>@{bot_username}</b> كأدمن في قناتك\n"
                f"{ee(E_SPARK,'✨')} <b>الخطوة 2 :</b> أرسل الكمية المطلوبة\n"
                f"━━━━━━━━━━━━━━━\n"
                f"{ee(E_STAR,'⭐')} <b>الكمية</b> : {qty_line}\n\n"
                f"{ee(E_ROCKET,'🚀')} أرسل الكمية الآن")
        kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="services_menu", emoji=E_NO, style="danger"))
        edit_h(cid, mid, text, kb)
        clear_user_state(cid)
        golden.register_next_step_handler(call.message, handle_qty_step, sk); return

    if d == "my_orders": show_my_orders(uid, call.message, "active"); return
    if d == "my_orders_completed": show_my_orders(uid, call.message, "completed"); return
    if d == "my_orders_all": show_my_orders(uid, call.message, "active"); return

    if d == "user_update_all_orders":
        golden.answer_callback_query(call.id, "🔄 جاري فحص طلباتك...")
        try:
            u = get_user(uid)
            updated = 0; completed_now = 0; still = 0; internal_checked = 0; internal_ended = 0
            for o in u.get("orders", []):
                if not isinstance(o, dict): continue
                if o.get("status") in ("completed", "ended"): continue
                if o.get("is_internal"):
                    ch_id = o.get("channel_id")
                    if not ch_id: continue
                    try:
                        bot_id = golden.get_me().id
                        st = golden.get_chat_member(ch_id, bot_id)
                        if st.status not in ('administrator', 'creator'):
                            o["status"] = "ended"
                            remove_buyer_channel_from_rewards(ch_id)
                            internal_ended += 1
                        else:
                            internal_checked += 1
                    except:
                        o["status"] = "ended"
                        remove_buyer_channel_from_rewards(ch_id)
                        internal_ended += 1
                    continue
                oid = o.get("order_id")
                if not oid: continue
                prov_key = o.get("provider")
                st = get_order_status(oid, prov_key)
                if not st: still += 1; continue
                if 'error' in st: still += 1; continue
                status = st.get("status","")
                if status in ['Completed', 'Partial']:
                    mark_order_completed(uid, oid)
                    completed_now += 1
                else:
                    still += 1
                updated += 1
            save_json(G1, Gq)
            summary = (f"{ee(E_SPARK,'✨')} <b>نتيجة التحديث</b>\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"{ee(E_SEARCH,'🔍')} تم فحص : <b>{updated}</b>\n"
                       f"{ee(E_YES,'✅')} اكتملت : <b>{completed_now}</b>\n"
                       f"{ee(E_BOLT,'⚡')} ما زالت : <b>{still}</b>")
            if internal_checked > 0 or internal_ended > 0:
                summary += (f"\n{ee(E_TG,'📢')} طلبات القنوات :\n"
                            f"   • نشطة : <b>{internal_checked}</b>\n"
                            f"   • منتهية : <b>{internal_ended}</b>")
            send_h(uid, summary, markup=telebot.types.InlineKeyboardMarkup().row(
                btn("طلباتي", callback_data="my_orders", emoji=E_SEARCH, style="primary")))
        except Exception as e:
            print(f"user_update_all: {e}")
            send_h(uid, f"{ee(E_BROKEN,'💔')} <b>خطأ في التحديث</b>")
        return

    if d == "top_referrers":
        try:
            all_u = [(k, v) for k, v in Gq.items() if v.get("invited_count", 0) > 0]
            all_u.sort(key=lambda x: x[1].get("invited_count", 0), reverse=True)
            top = all_u[:10]
            text = f"{ee(E_CROWN,'👑')} <b>أفضـل المـدعين</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            if not top: text += f"{ee(E_BROKEN,'💔')} <i>لا يوجد مدعوين</i>"
            else:
                medals = ["🥇","🥈","🥉"]
                for i,(k,u) in enumerate(top):
                    uname = u.get("username", ""); uname_disp = f"@{uname}" if uname else "بدون يوزر"
                    count = u.get("invited_count", 0)
                    if i < 3:
                        rank_name = ["الأولى","الثانية","الثالثة"][i]
                        text += (f"{medals[i]} <b>المرتبة {rank_name}</b>\n"
                                 f"{ee(E_TG,'📱')} <b>اليوزر</b> ← {uname_disp}\n"
                                 f"{ee(E_EYE,'👁')} <b>الآيدي</b> ← <code>{k}</code>\n"
                                 f"{ee(E_LINK,'🔗')} <b>الدعوات</b> ← <b>{count}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n")
                    else:
                        text += f"<b>{i+1}.</b> {uname_disp}\n    {ee(E_EYE,'👁')} <code>{k}</code> | {ee(E_LINK,'🔗')} <b>{count}</b>\n\n"
                text += f"{ee(E_STAR,'⭐')} إجمالي المدعوين ← <b>{Gr.get('total_invites',0)}</b>"
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="collect_points_menu", emoji=E_NO, style="danger"))
            edit_h(cid, mid, text, kb)
        except: pass
        return

    if d.startswith("refresh_order_"):
        oid = d.replace("refresh_order_","")
        golden.answer_callback_query(call.id, "⚡ جـاري التحـديث ...")
        is_internal = False
        target_order = None
        for o in ud.get("orders", []):
            if isinstance(o, dict) and str(o.get("order_id"))==str(oid):
                if o.get("is_internal"):
                    is_internal = True
                target_order = o
                break
        if is_internal and target_order:
            ch_id = target_order.get("channel_id")
            bot_ok = False
            try:
                bot_id = golden.get_me().id
                st = golden.get_chat_member(ch_id, bot_id)
                bot_ok = st.status in ('administrator', 'creator')
            except: bot_ok = False
            if not bot_ok:
                target_order["status"] = "ended"
                remove_buyer_channel_from_rewards(ch_id)
                save_json(G1, Gq)
                send_h(uid, f"{ee(E_BROKEN,'💔')} <b>تم إنهاء الاشتراك</b>\n"
                           f"━━━━━━━━━━━━━━━\n"
                           f"{ee(E_CROSS,'❌')} البوت غير موجود في قناتك\n"
                           f"{ee(E_TG,'📢')} القناة أُزيلت من قسم النقاط",
                       markup=telebot.types.InlineKeyboardMarkup().row(
                           btn("القائمة", callback_data="back_main", emoji=E_ROCKET, style="success")))
                return
            order_qty = target_order.get("qty", 0)
            verified = 0
            for r in config.get("channel_rewards", []):
                if str(r.get("chat_id")) == str(ch_id) and r.get("from_service"):
                    verified = r.get("verified_count", 0)
                    order_qty = r.get("order_qty", order_qty)
                    break
            remaining = max(0, order_qty - verified)
            progress = int((verified / order_qty * 100)) if order_qty > 0 else 0
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("🔄 تحديث الرابط", callback_data=f"upd_link_{oid}", emoji=E_LINK, style="success"))
            kb.row(btn("القائمة", callback_data="back_main", emoji=E_ROCKET, style="primary"))
            send_h(uid, f"{ee(E_CROWN,'👑')} <b>إحصائيات طلبك</b>\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"{ee(E_SEARCH,'🔍')} <b>رقم الطلب</b> : <code>{oid}</code>\n"
                       f"{ee(E_TG,'📢')} <b>القناة</b> : <code>{ch_id}</code>\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"{ee(E_STAR,'⭐')} <b>المطلوب</b> : <b>{order_qty}</b> متابع\n"
                       f"{ee(E_YES,'✅')} <b>تم التحقق</b> : <b>{verified}</b>\n"
                       f"{ee(E_BOLT,'⚡')} <b>المتبقي</b> : <b>{remaining}</b>\n"
                       f"{ee(E_FIRE,'🔥')} <b>نسبة الإنجاز</b> : <b>{progress}%</b>\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"{ee(E_LOCK,'🔒')} طالما البوت أدمن، الاشتراك مستمر",
                   markup=kb)
            return
        prov_key = None
        for o in ud.get("orders", []):
            if isinstance(o, dict) and str(o.get("order_id"))==str(oid):
                prov_key = o.get("provider"); break
        st = get_order_status(oid, prov_key)
        if not st:
            send_h(uid, f"{ee(E_BROKEN,'💔')} <b>تعذر جلب الحالة</b>", markup=restart_kb()); return
        if 'error' in st:
            send_h(uid, f"{ee(E_BROKEN,'💔')} <b>خطأ</b> ← {st['error']}", markup=restart_kb()); return
        status = st.get('status','غير معروف')
        start = st.get('start_count','0'); rem = st.get('remains','0')
        sa = {'Pending':'⏳ قيد الانتظار','In progress':'🚀 قيد التنفيذ','Processing':'⚙️ قيد المعالجة',
              'In Progress':'🚀 قيد التنفيذ','Completed':'✅ مكتمل','Partial':'⚠️ مكتمل جزئياً',
              'Canceled':'❌ ملغي','Cancelled':'❌ ملغي'}.get(status,status)
        if status in ['Completed', 'Partial']: mark_order_completed(uid, oid)
        text = (f"{ee(E_SEARCH,'🔍')} <b>حـالـة الـطـلـب</b>\n━━━━━━━━━━━━━━━\n"
                f"{ee(E_STAR,'⭐')} <b>رقم الطلب</b> ← <code>{oid}</code>\n"
                f"{ee(E_BOLT,'⚡')} <b>الحالة</b> ← {sa}\n"
                f"📥 <b>البداية</b> ← {start}\n📤 <b>المتبقي</b> ← {rem}\n"
                f"━━━━━━━━━━━━━━━\n{ee(E_HEART,'💗')} شـكراً لاستـخدامك")
        kb = telebot.types.InlineKeyboardMarkup().row(btn("القائمة", callback_data="back_main", emoji=E_ROCKET, style="success"))
        send_h(uid, text, markup=kb); return

    if d == "oc_yes":
        pending = pending_orders.pop(uid, None)
        if not pending:
            golden.answer_callback_query(call.id, "❌ انتهت صلاحية الطلب", show_alert=True); return
        sk = pending.get('sk'); qty = pending.get('qty',0)
        cost = pending.get('cost',0); link = pending.get('link','')
        if sk not in SERVICES:
            golden.answer_callback_query(call.id, "❌ خدمة غير متوفرة", show_alert=True); return
        svc = SERVICES[sk]
        if ud.get("points",0) < cost:
            golden.answer_callback_query(call.id, "❌ نقاطك غير كافية", show_alert=True); return
        golden.answer_callback_query(call.id, "⚡ جاري التنفيذ ...")
        edit_h(cid, mid, f"{ee(E_BOLT,'⚡')} <b>جـاري تنفيـذ الطـلب</b> ...")

        if pending.get('special') and pending.get('channel_id'):
            internal_oid = f"INT_{int(time.time())}_{random.randint(1000,9999)}"
            ud["points"] = ud.get("points",0) - cost
            ud["requests"] = ud.get("requests",0) + 1
            Gr["total_requests"] = Gr.get("total_requests",0) + 1
            bump_service_sale(sk)
            save_json(G1,Gq); save_json(G2,Gr)
            try: add_buyer_channel_to_rewards(uid, pending.get('channel_id'), link, internal_oid, qty)
            except Exception as e: print(f"add_buyer_channel: {e}")
            u2 = get_user(uid)
            u2.setdefault("orders",[]).append({
                "service": svc.get('name',''),
                "link": link,
                "qty": int(qty),
                "order_id": internal_oid,
                "created_at": time.time(),
                "status": "active",
                "provider": "internal",
                "is_internal": True,
                "monitored": True,
                "channel_id": pending.get('channel_id')
            })
            if len(u2["orders"])>50: u2["orders"]=u2["orders"][-50:]
            save_json(G1, Gq)

            uname = f"@{ud.get('username')}" if ud.get('username') else "بدون يوزر"
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            act = (f"{ee(E_BOLT,'⚡')} <b>تفعيـل طـلـب جديـد (داخلي)</b>\n━━━━━━━━━━━━━━━\n"
                   f"{ee(E_WELCOME,'👋')} <b>المستخدم</b> ← {uname}\n"
                   f"{ee(E_EYE,'👁')} <b>ID</b> ← <code>{uid}</code>\n"
                   f"{ee(E_STAR,'⭐')} <b>الخدمة</b> ← {svc.get('name','')}\n"
                   f"{ee(E_DIAMOND,'💎')} <b>الكمية</b> ← {qty}\n"
                   f"{ee(E_HEART,'💗')} <b>التكلفة</b> ← {cost} نقطة\n"
                   f"{ee(E_SEARCH,'🔍')} <b>رقم الطلب</b> ← <code>{internal_oid}</code>\n"
                   f"{ee(E_TG,'📢')} <b>القناة</b> ← <code>{pending.get('channel_id')}</code>\n"
                   f"{ee(E_LINK,'🔗')} <b>الرابط</b> ← <a href=\"{link}\">اضغط هنا</a>\n"
                   f"⏰ <b>الوقت</b> ← {now}")
            notify_activation_channel(act)
            succ = (f"{ee(E_SPARK,'✨')} <b>تـم إنشـاء الاشـتـراك بـنجـاح</b> {ee(E_SPARK,'✨')}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"{ee(E_SEARCH,'🔍')} <b>رقم الطلب</b> ← <code>{internal_oid}</code>\n"
                    f"{ee(E_STAR,'⭐')} <b>الخدمة</b> ← {svc.get('name','')}\n"
                    f"{ee(E_BOLT,'⚡')} <b>الكمية</b> ← {qty}\n"
                    f"{ee(E_DIAMOND,'💎')} <b>التكلفة</b> ← {cost} نقطة\n"
                    f"{ee(E_DIAMOND,'💎')} <b>نقاطك المتبقية</b> ← {ud.get('points',0)}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"{ee(E_CROWN,'👑')} <b>ماذا حدث الآن ؟</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"{ee(E_TG,'📢')} <b>قناتك أُضيفت تلقائياً</b> إلى قسم\n"
                    f"<b>«تجميع النقاط» ← «الاشتراك بالقنوات»</b>\n\n"
                    f"{ee(E_DIAMOND,'💎')} <b>كيف يستفيد الآخرون ؟</b>\n"
                    f"المستخدمون سيشتركون بقناتك ويربحون نقاط\n\n"
                    f"{ee(E_ROCKET,'🚀')} <b>ماذا تربح أنت ؟</b>\n"
                    f"مشتركين حقيقيين 100% بشكل مستمر\n\n"
                    f"{ee(E_SEARCH,'🔍')} <b>كيف تتابع الإحصائيات ؟</b>\n"
                    f"من «طلباتي» ← تحديث الطلب ← سترى:\n"
                    f"المطلوب / تم التحقق / المتبقي\n\n"
                    f"{ee(E_LOCK,'🔒')} <b>تنبيه :</b> لا تزيل البوت من القناة\n"
                    f"وإلا سينتهي الاشتراك فوراً\n"
                    f"{ee(E_CROSS,'❌')} <b>لا يوجد استرجاع للنقاط بعد الموافقة</b>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"{ee(E_HEART,'💗')} شـكراً لاستـخدامك")
            kb = telebot.types.InlineKeyboardMarkup().row(btn("القائمة الرئيسية", callback_data="back_main", emoji=E_ROCKET, style="success"))
            if not edit_h(cid, mid, succ, kb): send_h(uid, succ, markup=kb)
            return

        prov_key = svc.get('provider') or None
        ok, result = send_order(svc.get('id',''), link, qty, prov_key)
        if ok:
            ud["points"] = ud.get("points",0) - cost
            ud["requests"] = ud.get("requests",0) + 1
            Gr["total_requests"] = Gr.get("total_requests",0) + 1
            bump_service_sale(sk)
            save_json(G1,Gq); save_json(G2,Gr)
            save_order(uid, svc.get('name',''), link, qty, order_id=result, provider_key=prov_key)
            uname = f"@{ud.get('username')}" if ud.get('username') else "بدون يوزر"
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            prov_name = get_provider(prov_key).get('name','?') if get_provider(prov_key) else '?'
            act = (f"{ee(E_BOLT,'⚡')} <b>تفعيـل طـلـب جديـد</b>\n━━━━━━━━━━━━━━━\n"
                   f"{ee(E_WELCOME,'👋')} <b>المستخدم</b> ← {uname}\n"
                   f"{ee(E_EYE,'👁')} <b>ID</b> ← <code>{uid}</code>\n"
                   f"{ee(E_STAR,'⭐')} <b>الخدمة</b> ← {svc.get('name','')}\n"
                   f"{ee(E_DIAMOND,'💎')} <b>الكمية</b> ← {qty}\n"
                   f"{ee(E_HEART,'💗')} <b>التكلفة</b> ← {cost} نقطة\n"
                   f"{ee(E_SEARCH,'🔍')} <b>رقم الطلب</b> ← <code>{result}</code>\n"
                   f"{ee(E_ROCKET,'🚀')} <b>المزود</b> ← {prov_name}\n"
                   f"{ee(E_LINK,'🔗')} <b>الرابط</b> ← <a href=\"{link}\">اضغط هنا</a>\n"
                   f"⏰ <b>الوقت</b> ← {now}")
            notify_activation_channel(act)
            succ = (f"{ee(E_SPARK,'✨')} <b>تـم إنشـاء الـطـلـب بـنجـاح</b> {ee(E_SPARK,'✨')}\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"{ee(E_SEARCH,'🔍')} <b>رقم الطلب</b> ← <code>{result}</code>\n"
                    f"{ee(E_STAR,'⭐')} <b>الخدمة</b> ← {svc.get('name','')}\n"
                    f"{ee(E_BOLT,'⚡')} <b>الكمية</b> ← {qty}\n"
                    f"{ee(E_DIAMOND,'💎')} <b>التكلفة</b> ← {cost} نقطة\n"
                    f"{ee(E_DIAMOND,'💎')} <b>نقاطك المتبقية</b> ← {ud.get('points',0)}\n"
                    f"━━━━━━━━━━━━━━━\n{ee(E_HEART,'💗')} شـكراً لاستـخدامك")
            kb = telebot.types.InlineKeyboardMarkup().row(btn("القائمة الرئيسية", callback_data="back_main", emoji=E_ROCKET, style="success"))
            if not edit_h(cid, mid, succ, kb): send_h(uid, succ, markup=kb)
        else:
            translated = translate_smm_error(result)
            err = f"{ee(E_BROKEN,'💔')} <b>فشـل إنـشـاء الـطـلـب</b>\n━━━━━━━━━━━━━━━\n{translated}"
            if not edit_h(cid, mid, err, restart_kb()): send_h(uid, err, markup=restart_kb())
        return

    if d == "oc_no":
        pending_orders.pop(uid, None)
        golden.answer_callback_query(call.id, "تم الإلغاء")
        edit_h(cid, mid, welcome_text(uid), main_menu(uid, ud)); return

    if uid == G8:
        if d == "admin_channels":
            txt, kb = build_admin_channels_menu(); edit_h(cid, mid, txt, kb); return

        if d == "admin_buyer_reward_pts":
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_channels", emoji=E_NO, style="danger"))
            cur = config.get("channel_followers_reward_points", 5)
            try:
                golden.edit_message_text(text=f"{ee(E_DIAMOND,'💎')} <b>نقاط قناة المشتري</b>\n━━━━━━━━━━━━━━━\n{ee(E_SPARK,'✨')} النقاط الحالية : <b>{cur}</b>\n━━━━━━━━━━━━━━━\nأرسل عدد النقاط الجديد",
                    chat_id=cid, message_id=mid, reply_markup=kb, parse_mode='HTML')
            except: pass
            golden.register_next_step_handler(call.message, buyer_reward_pts_step); return

        if d == "admin_srv_order":
            txt, kb = build_reorder_menu(); edit_h(cid, mid, txt, kb); return
        if d.startswith("sord_up_"):
            sk = d.replace("sord_up_","")
            move_service_up(sk)
            golden.answer_callback_query(call.id, "✅ تم الرفع")
            txt, kb = build_reorder_menu(); edit_h(cid, mid, txt, kb); return
        if d.startswith("sord_dn_"):
            sk = d.replace("sord_dn_","")
            move_service_down(sk)
            golden.answer_callback_query(call.id, "✅ تم الإنزال")
            txt, kb = build_reorder_menu(); edit_h(cid, mid, txt, kb); return

        if d == "admin_srv_toggle":
            txt, kb = build_toggle_services_menu(); edit_h(cid, mid, txt, kb); return
        if d.startswith("stog_"):
            sk = d.replace("stog_","")
            if sk not in SERVICES:
                golden.answer_callback_query(call.id, "❌"); return
            hidden = config.get('hidden_services', [])
            if sk in hidden:
                hidden.remove(sk); st = "✅ ظاهر"
            else:
                hidden.append(sk); st = "❌ مخفي"
            config['hidden_services'] = hidden; save_json(CONFIG_FILE, config)
            golden.answer_callback_query(call.id, st, show_alert=False)
            txt, kb = build_toggle_services_menu(); edit_h(cid, mid, txt, kb); return

        if d == "admin_channel_rewards":
            txt, kb = build_channel_rewards_admin(); edit_h(cid, mid, txt, kb); return

        if d == "chr_add":
            chr_state[uid] = {'step':'name', 'data':{}, 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="chr_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : إضافة قناة نقاط .\n\n‹ أرسل <b>اسم القناة</b> .",
                chat_id=cid, message_id=mid, reply_markup=kb, parse_mode='HTML')
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, chr_add_name); return

        if d == "chr_cancel":
            chr_state.pop(uid, None); clear_user_state(uid)
            txt, kb = build_channel_rewards_admin(); edit_h(cid, mid, txt, kb); return

        if d.startswith("chr_edit_"):
            try: idx = int(d.replace("chr_edit_",""))
            except: idx = -1
            rewards = config.get("channel_rewards", [])
            if idx < 0 or idx >= len(rewards):
                golden.answer_callback_query(call.id, "❌", show_alert=True); return
            ch = rewards[idx]
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("تعديل الاسم", callback_data=f"chred_name_{idx}", emoji=E_SEARCH, style="primary"))
            kb.row(btn("تعديل الرابط", callback_data=f"chred_link_{idx}", emoji=E_LINK, style="primary"))
            kb.row(btn("تعديل chat_id", callback_data=f"chred_chatid_{idx}", emoji=E_TG, style="primary"))
            kb.row(btn("تعديل النقاط", callback_data=f"chred_points_{idx}", emoji=E_DIAMOND, style="success"))
            kb.row(btn("حذف القناة", callback_data=f"chred_del_{idx}", emoji=E_CROSS, style="danger"))
            kb.row(btn("رجوع", callback_data="admin_channel_rewards", emoji=E_NO, style="danger"))
            extra = ""
            if ch.get("from_service"):
                extra = f"\n{ee(E_STAR,'⭐')} المطلوب ← {ch.get('order_qty',0)}\n{ee(E_YES,'✅')} تم التحقق ← {ch.get('verified_count',0)}"
            txt = (f"{ee(E_TG,'📢')} <b>تعديل قناة</b>\n━━━━━━━━━━━━━━━\n"
                   f"📌 الاسم ← {ch.get('name','')}\n"
                   f"{ee(E_LINK,'🔗')} الرابط ← <code>{ch.get('link','')}</code>\n"
                   f"🆔 chat_id ← <code>{ch.get('chat_id','') or 'غير محدد'}</code>\n"
                   f"{ee(E_DIAMOND,'💎')} النقاط ← {ch.get('points',0)}{extra}")
            edit_h(cid, mid, txt, kb); return

        if d.startswith("chred_name_"):
            try: idx = int(d.replace("chred_name_",""))
            except: idx = -1
            chr_state[uid] = {'step':'edit_name', 'idx':idx, 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="chr_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : أرسل الاسم الجديد .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, chr_edit_name); return

        if d.startswith("chred_link_"):
            try: idx = int(d.replace("chred_link_",""))
            except: idx = -1
            chr_state[uid] = {'step':'edit_link', 'idx':idx, 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="chr_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : أرسل الرابط الجديد .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, chr_edit_link); return

        if d.startswith("chred_chatid_"):
            try: idx = int(d.replace("chred_chatid_",""))
            except: idx = -1
            chr_state[uid] = {'step':'edit_chatid', 'idx':idx, 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="chr_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : أرسل chat_id أو @username .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, chr_edit_chatid); return

        if d.startswith("chred_points_"):
            try: idx = int(d.replace("chred_points_",""))
            except: idx = -1
            chr_state[uid] = {'step':'edit_points', 'idx':idx, 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="chr_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : أرسل عدد النقاط الجديد .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, chr_edit_points); return

        if d.startswith("chred_del_"):
            try: idx = int(d.replace("chred_del_",""))
            except: idx = -1
            rewards = config.get("channel_rewards", [])
            if idx < 0 or idx >= len(rewards):
                golden.answer_callback_query(call.id, "❌", show_alert=True); return
            ch = rewards.pop(idx)
            config["channel_rewards"] = rewards; save_json(CONFIG_FILE, config)
            golden.answer_callback_query(call.id, f"✅ تم حذف: {ch.get('name','')}", show_alert=True)
            txt, kb = build_channel_rewards_admin(); edit_h(cid, mid, txt, kb); return

        if d == "admin_providers":
            txt, kb = build_providers_menu(); edit_h(cid, mid, txt, kb); return
        if d == "prov_add":
            prov_state[uid] = {'step':'name', 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="prov_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : إضافة مزود .\n\n‹ أرسل <b>اسم المزود</b> .",
                chat_id=cid, message_id=mid, reply_markup=kb, parse_mode='HTML')
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, prov_add_name); return
        if d == "prov_cancel":
            prov_state.pop(uid, None); clear_user_state(uid)
            txt, kb = build_providers_menu(); edit_h(cid, mid, txt, kb); return
        if d.startswith("prov_edit_"):
            pk = d.replace("prov_edit_",""); pv = get_provider(pk)
            if not pv: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("تعديل الاسم", callback_data=f"prov_setname_{pk}", emoji=E_SEARCH, style="primary"))
            kb.row(btn("تعديل الرابط", callback_data=f"prov_seturl_{pk}", emoji=E_LINK, style="primary"))
            kb.row(btn("تعديل API Key", callback_data=f"prov_setapi_{pk}", emoji=E_LOCK, style="primary"))
            if pv.get("active", True):
                kb.row(btn("تعطيل المزود", callback_data=f"prov_toggle_{pk}", emoji=E_CROSS, style="danger"))
            else:
                kb.row(btn("تفعيل المزود", callback_data=f"prov_toggle_{pk}", emoji=E_YES, style="success"))
            if not pv.get("default"):
                kb.row(btn("تعيين كافتراضي", callback_data=f"prov_default_{pk}", emoji=E_STAR, style="success"))
            kb.row(btn("حذف المزود", callback_data=f"prov_del_{pk}", emoji=E_BROKEN, style="danger"))
            kb.row(btn("رجوع", callback_data="admin_providers", emoji=E_NO, style="danger"))
            txt = (f"{ee(E_ROCKET,'🚀')} <b>تعديل المزود</b>\n━━━━━━━━━━━━━━━\n"
                   f"📌 <b>الاسم</b> ← {pv.get('name','')}\n"
                   f"{ee(E_LINK,'🔗')} <b>الرابط</b> ← <code>{pv.get('url','')}</code>\n"
                   f"{ee(E_LOCK,'🔒')} <b>API Key</b> ← <code>{pv.get('api_key','')[:20]}...</code>\n"
                   f"📊 <b>الحالة</b> ← {'🟢 نشط' if pv.get('active',True) else '🔴 معطّل'}")
            edit_h(cid, mid, txt, kb); return
        if d.startswith("prov_setname_"):
            pk = d.replace("prov_setname_",""); pv = get_provider(pk)
            if not pv: return
            prov_state[uid] = {'step':'edit_name', 'key':pk, 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="prov_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text=f"‹ : أرسل الاسم الجديد .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, prov_edit_name); return
        if d.startswith("prov_seturl_"):
            pk = d.replace("prov_seturl_",""); pv = get_provider(pk)
            if not pv: return
            prov_state[uid] = {'step':'edit_url', 'key':pk, 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="prov_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text=f"‹ : أرسل الرابط الجديد .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, prov_edit_url); return
        if d.startswith("prov_setapi_"):
            pk = d.replace("prov_setapi_",""); pv = get_provider(pk)
            if not pv: return
            prov_state[uid] = {'step':'edit_api', 'key':pk, 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="prov_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text=f"‹ : أرسل API Key الجديد .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, prov_edit_api); return
        if d.startswith("prov_toggle_"):
            pk = d.replace("prov_toggle_",""); pv = get_provider(pk)
            if not pv: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            pv["active"] = not pv.get("active", True)
            config["providers"][pk] = pv; save_json(CONFIG_FILE, config)
            st = "مفعّل ✅" if pv["active"] else "معطّل ❌"
            golden.answer_callback_query(call.id, f"المزود : {st}", show_alert=True)
            call.data = f"prov_edit_{pk}"; _handle_cb(call); return
        if d.startswith("prov_default_"):
            pk = d.replace("prov_default_","")
            if pk not in config.get("providers", {}):
                golden.answer_callback_query(call.id, "❌", show_alert=True); return
            for pkk in config["providers"]: config["providers"][pkk]["default"] = False
            config["providers"][pk]["default"] = True; save_json(CONFIG_FILE, config)
            golden.answer_callback_query(call.id, "✅", show_alert=True)
            call.data = f"prov_edit_{pk}"; _handle_cb(call); return
        if d.startswith("prov_del_"):
            pk = d.replace("prov_del_",""); pv = get_provider(pk)
            if not pv: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("تأكيد الحذف", callback_data=f"prov_delc_{pk}", emoji=E_YES, style="danger"),
                   btn("إلغاء", callback_data=f"prov_edit_{pk}", emoji=E_NO, style="primary"))
            edit_h(cid, mid, f"{ee(E_BROKEN,'💔')} <b>تأكيد حذف المزود</b> <b>{pv.get('name','')}</b> ؟", kb); return
        if d.startswith("prov_delc_"):
            pk = d.replace("prov_delc_","")
            if pk in config.get("providers", {}):
                name = config["providers"][pk].get("name",pk)
                del config["providers"][pk]; save_json(CONFIG_FILE, config)
                golden.answer_callback_query(call.id, f"✅ {name}", show_alert=True)
            txt, kb = build_providers_menu(); edit_h(cid, mid, txt, kb); return

        if d == "admin_top_services":
            txt, kb = build_top_services_menu(); edit_h(cid, mid, txt, kb); return
        if d == "admin_forced_subs":
            txt, kb = build_forced_subs_menu(); edit_h(cid, mid, txt, kb); return
        if d == "fsub_add":
            fsub_state[uid] = {'step':'name', 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="fsub_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : إضافة قناة إجبارية .\n\n‹ أرسل <b>اسم القناة</b> .",
                chat_id=cid, message_id=mid, reply_markup=kb, parse_mode='HTML')
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, fsub_add_name); return
        if d == "fsub_cancel":
            fsub_state.pop(uid, None); clear_user_state(uid)
            txt, kb = build_forced_subs_menu(); edit_h(cid, mid, txt, kb); return
        if d == "fsub_skip_chatid":
            st = fsub_state.get(uid)
            if st: st['chat_id'] = ''
            fsub_finish_add(uid); return
        if d.startswith("fsub_edit_"):
            try: idx = int(d.replace("fsub_edit_",""))
            except: idx = -1
            forced = config.get("forced_channels", [])
            if idx < 0 or idx >= len(forced): golden.answer_callback_query(call.id, "❌", show_alert=True); return
            ch = forced[idx]
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("تعديل الاسم", callback_data=f"fsub_set_name_{idx}", emoji=E_SEARCH, style="primary"))
            kb.row(btn("تعديل الرابط", callback_data=f"fsub_set_link_{idx}", emoji=E_LINK, style="primary"))
            kb.row(btn("حذف القناة", callback_data=f"fsub_del_{idx}", emoji=E_CROSS, style="danger"))
            kb.row(btn("رجوع", callback_data="admin_forced_subs", emoji=E_NO, style="danger"))
            txt = f"{ee(E_LOCK,'🔒')} <b>تعديل القناة</b>\n📢 {ch.get('name','')}\n🔗 <code>{ch.get('link','')}</code>"
            edit_h(cid, mid, txt, kb); return
        if d.startswith("fsub_set_name_"):
            try: idx = int(d.replace("fsub_set_name_",""))
            except: idx = -1
            forced = config.get("forced_channels", [])
            if idx < 0 or idx >= len(forced): golden.answer_callback_query(call.id, "❌", show_alert=True); return
            fsub_state[uid] = {'step':'edit_name', 'idx':idx, 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="fsub_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : أرسل الاسم الجديد .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, fsub_edit_name); return
        if d.startswith("fsub_set_link_"):
            try: idx = int(d.replace("fsub_set_link_",""))
            except: idx = -1
            forced = config.get("forced_channels", [])
            if idx < 0 or idx >= len(forced): golden.answer_callback_query(call.id, "❌", show_alert=True); return
            fsub_state[uid] = {'step':'edit_link', 'idx':idx, 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="fsub_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : أرسل الرابط الجديد .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, fsub_edit_link); return
        if d.startswith("fsub_del_"):
            try: idx = int(d.replace("fsub_del_",""))
            except: idx = -1
            forced = config.get("forced_channels", [])
            if idx < 0 or idx >= len(forced): golden.answer_callback_query(call.id, "❌", show_alert=True); return
            ch = forced.pop(idx)
            config["forced_channels"] = forced; save_json(CONFIG_FILE, config)
            golden.answer_callback_query(call.id, f"✅ {ch.get('name','')}", show_alert=True)
            txt, kb = build_forced_subs_menu(); edit_h(cid, mid, txt, kb); return

        if d == "admin_points_mgr":
            text, kb = build_points_mgr_menu(0); edit_h(cid, mid, text, kb); return
        if d.startswith("pm_page_"):
            try: page = int(d.replace("pm_page_",""))
            except: page = 0
            text, kb = build_points_mgr_menu(page); edit_h(cid, mid, text, kb); return
        if d == "pm_search":
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_points_mgr", emoji=E_NO, style="danger"))
            try: golden.edit_message_text(text="‹ : أرسل ID المستخدم .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, pm_search_step); return
        if d.startswith("pm_"):
            tuid = d.replace("pm_","")
            if tuid not in Gq: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            pm_show_user(cid, mid, tuid); return
        if d.startswith("pmact_"):
            parts = d.split("_", 2)
            if len(parts) < 3: return
            action, tuid = parts[1], parts[2]
            if tuid not in Gq: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            pm_state[uid] = {'action':action, 'target':tuid}
            prompts = {'add':'أرسل عدد النقاط للإضافة','sub':'أرسل عدد النقاط للخصم','set':'أرسل عدد النقاط للتعيين','charge':'أرسل عدد النقاط للشحن'}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data=f"pm_{tuid}", emoji=E_NO, style="danger"))
            try: golden.edit_message_text(text=f"‹ : {prompts.get(action,'القيمة')}\n‹ نقاطه : {Gq[tuid].get('points',0)}",
                chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, pm_apply_points); return
        if d.startswith("pm_zero_"):
            tuid = d.replace("pm_zero_","")
            if tuid not in Gq: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            Gq[tuid]["points"] = 0; save_json(G1, Gq)
            golden.answer_callback_query(call.id, "✅", show_alert=True)
            pm_show_user(cid, mid, tuid); return

        if d == "admin_services":
            clear_user_state(uid)
            edit_h(cid, mid, f"{ee(E_BOLT,'⚡')} <b>إدارة الخدمات</b>\n━━━━━━━━━━━━━━━", build_services_menu()); return
        if d == "srv_add":
            kb = telebot.types.InlineKeyboardMarkup()
            active = get_active_providers()
            for pk, pv in active.items():
                default_mark = " ⭐" if pv.get('default') else ""
                kb.row(btn(f"مزود: {pv.get('name','?')}{default_mark}", callback_data=f"srvprov_{pk}", emoji=E_ROCKET, style="primary"))
            # ✅ دائماً اعرض خيار النظام الداخلي (للخدمات الخاصة)
            kb.row(btn("مزود: نظام داخلي (بدون API)", callback_data="srvprov_internal", emoji=E_LOCK, style="success"))
            kb.row(btn("إلغاء", callback_data="srv_add_cancel", emoji=E_CROSS, style="danger"))
            edit_h(cid, mid, f"{ee(E_ROCKET,'🚀')} <b>إضافة خدمة</b>\n{ee(E_SPARK,'✨')} اخـتر المزود :", kb); return
        if d.startswith("srvprov_"):
            pk = d.replace("srvprov_","")
            if pk == "internal":
                admin_add_srv[uid] = {'data':{'provider':'internal','id':'internal'},'msgs':[mid]}
                kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="srv_add_cancel", emoji=E_CROSS, style="danger"))
                try: golden.edit_message_text(text=f"‹ : المزود : <b>نظام داخلي</b>\n\n‹ أرسل <b>اسم الخدمة</b> .",
                    chat_id=cid, message_id=mid, reply_markup=kb, parse_mode='HTML')
                except: pass
                golden.register_next_step_handler_by_chat_id(uid, srv_add_name)
                return
            pv = get_provider(pk)
            if not pv: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            admin_add_srv[uid] = {'data':{'provider':pk},'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="srv_add_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text=f"‹ : المزود : <b>{pv.get('name','?')}</b>\n\n‹ أرسل ID الخدمة .",
                chat_id=cid, message_id=mid, reply_markup=kb, parse_mode='HTML')
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, srv_add_id); return
        if d == "srv_add_cancel":
            st = admin_add_srv.pop(uid, None)
            if st: clean_msgs(uid, st)
            try: golden.edit_message_text(text="✅ تم الإلغاء", chat_id=cid, message_id=mid)
            except: pass
            send_h(uid, f"{ee(E_CROWN,'👑')} <b>لوحة الأدمن</b>", markup=build_admin_panel()); return
        if d == "srv_add_skip_desc":
            st = admin_add_srv.get(uid)
            if st:
                try: golden.delete_message(uid, mid)
                except: pass
                ask_qty(uid)
            return
        if d == "srv_edit_list":
            kb = telebot.types.InlineKeyboardMarkup()
            if not SERVICES:
                kb.row(btn("رجوع", callback_data="admin_services", emoji=E_NO, style="danger"))
                edit_h(cid, mid, f"{ee(E_BROKEN,'💔')} لا يوجد خدمات", kb); return
            for k, svc in SERVICES.items():
                emoji, style = get_srv_props(k, svc)
                kb.row(btn(svc.get('name',''), callback_data=f"eS_{k}", emoji=emoji, style=style))
            kb.row(btn("رجوع", callback_data="admin_services", emoji=E_NO, style="danger"))
            edit_h(cid, mid, f"{ee(E_BOLT,'⚡')} <b>اخـتر الخـدمة</b>", kb); return
        if d.startswith("eS_"):
            sk = d.replace("eS_","")
            if sk not in SERVICES: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            svc = SERVICES[sk]
            desc_txt = svc.get('description') or "لا يوجد"
            prov = svc.get('provider','p1')
            if prov == 'internal': prov_name = 'نظام داخلي'
            else: prov_name = get_provider(prov).get('name','?') if get_provider(prov) else '?'
            final_price = svc.get('final_price', svc.get('price', 0))
            pack = svc.get('unit', 100)
            special_mark = " ✅" if svc.get('special') else " ❌"
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("الاسم", callback_data=f"eF_name_{sk}", emoji=E_BOLT, style="primary"),
                   btn("الوصف", callback_data=f"eF_desc_{sk}", emoji=E_SPARK, style="success"))
            kb.row(btn("الوحدة", callback_data=f"eF_unit_{sk}", emoji=E_SEARCH, style="primary"),
                   btn("السعر", callback_data=f"eF_price_{sk}", emoji=E_DIAMOND, style="success"))
            kb.row(btn("السعر النهائي", callback_data=f"eF_final_{sk}", emoji=E_DIAMOND, style="primary"),
                   btn("الكمية", callback_data=f"eF_qty_{sk}", emoji=E_STAR, style="success"))
            # ✅ زر تفعيل/إلغاء خاصية القناة
            kb.row(btn(f"خاصية القناة :{special_mark}", callback_data=f"eF_special_{sk}", emoji=E_LOCK, style="success" if not svc.get('special') else "danger"))
            if svc.get('special'):
                kb.row(btn("تعديل التحذير", callback_data=f"eF_warning_{sk}", emoji=E_SEARCH, style="primary"))
            kb.row(btn("رجوع", callback_data="srv_edit_list", emoji=E_NO, style="danger"))
            txt = (f"{ee(E_BOLT,'⚡')} <b>تعديل الخدمة</b>\n━━━━━━━━━━━━━━━\n"
                   f"📌 الاسم ← {svc.get('name','')}\n📝 الوصف ← {desc_txt}\n"
                   f"{ee(E_SEARCH,'🔍')} الباكج ← {pack}\n"
                   f"{ee(E_DIAMOND,'💎')} السعر النهائي ← {final_price} لكل {pack}\n"
                   f"{ee(E_STAR,'⭐')} الكمية ← {svc.get('min',0)}-{svc.get('max',0)}\n"
                   f"{ee(E_ROCKET,'🚀')} المزود ← {prov_name}\n"
                   f"{ee(E_LOCK,'🔒')} خاصية القناة ← {'مفعّلة ✅' if svc.get('special') else 'معطّلة ❌'}\n"
                   f"🆔 ID ← <code>{svc.get('id','')}</code>")
            edit_h(cid, mid, txt, kb); return
        if d.startswith("eF_special_"):
            sk = d.replace("eF_special_","")
            if sk not in SERVICES: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            svc = SERVICES[sk]
            if svc.get('special'):
                svc.pop('special', None)
                svc.pop('warning_text', None)
                msg = "❌ تم إلغاء خاصية القناة"
            else:
                svc['special'] = 'channel_followers'
                if not svc.get('warning_text'):
                    svc['warning_text'] = DEFAULT_TELE_REAL_WARNING
                msg = "✅ تم تفعيل خاصية القناة"
            if sk in custom_services:
                custom_services[sk] = svc; save_custom_services(custom_services)
            if sk in BASE_SERVICES:
                overrides = load_json(BASE_OVERRIDES_FILE, {}); overrides[sk] = svc; save_json(BASE_OVERRIDES_FILE, overrides)
            SERVICES[sk] = svc
            golden.answer_callback_query(call.id, msg, show_alert=True)
            call.data = f"eS_{sk}"; _handle_cb(call); return
        if d.startswith("eF_"):
            parts = d.split("_", 2)
            if len(parts) < 3: return
            field, sk = parts[1], parts[2]
            if sk not in SERVICES: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            admin_edit_srv[uid] = {'key':sk,'field':field,'msgs':[mid]}
            prompts = {'name':'أرسل الاسم الجديد','desc':'أرسل الوصف (- لحذفه)',
                       'unit':'أرسل الوحدة','price':'أرسل السعر','final':'أرسل السعر النهائي',
                       'qty':'أرسل الكمية (100 أو 100-1000)',
                       'id':'أرسل ID الخدمة عند المزود',
                       'warning':'أرسل نص التحذير (استخدم {bot} لاسم البوت، {final_price} للسعر، {pack} للوحدة، {min} و {max} للكمية)'}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="eF_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text=f"‹ : {prompts.get(field,'القيمة')} .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler_by_chat_id(uid, srv_edit_field); return
        if d == "eF_cancel":
            admin_edit_srv.pop(uid, None); clear_user_state(uid)
            try: golden.edit_message_text(text="✅ تم الإلغاء", chat_id=cid, message_id=mid)
            except: pass
            send_h(uid, f"{ee(E_CROWN,'👑')} <b>لوحة الأدمن</b>", markup=build_admin_panel()); return
        if d == "srv_del_list":
            kb = telebot.types.InlineKeyboardMarkup()
            if not SERVICES:
                kb.row(btn("رجوع", callback_data="admin_services", emoji=E_NO, style="danger"))
                edit_h(cid, mid, f"{ee(E_BROKEN,'💔')} لا يوجد خدمات", kb); return
            for k, svc in SERVICES.items():
                emoji, style = get_srv_props(k, svc)
                kb.row(btn(svc.get('name',''), callback_data=f"dS_{k}", emoji=emoji, style=style))
            kb.row(btn("رجوع", callback_data="admin_services", emoji=E_NO, style="danger"))
            edit_h(cid, mid, f"{ee(E_CROSS,'❌')} <b>اخـتر الخـدمة للحـذف</b>", kb); return
        if d.startswith("dS_"):
            sk = d.replace("dS_","")
            if sk not in SERVICES: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            svc = SERVICES[sk]
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("تأكيد", callback_data=f"dSc_{sk}", emoji=E_YES, style="danger"),
                   btn("إلغاء", callback_data="admin_services", emoji=E_NO, style="primary"))
            edit_h(cid, mid, f"{ee(E_BROKEN,'💔')} <b>حذف</b> <b>{svc.get('name','')}</b> ؟", kb); return
        if d.startswith("dSc_"):
            sk = d.replace("dSc_","")
            # ✅ حذف فعلي من custom_services أيضاً
            if sk in custom_services:
                del custom_services[sk]; save_custom_services(custom_services)
            if sk in SERVICES:
                del SERVICES[sk]
            hidden = config.get('hidden_services', [])
            if sk in hidden: hidden.remove(sk)
            if sk in config.get('service_order', []):
                config['service_order'] = [x for x in config['service_order'] if x != sk]
            config['hidden_services'] = hidden
            save_json(CONFIG_FILE, config)
            golden.answer_callback_query(call.id, "✅ تم الحذف", show_alert=True)
            try: golden.edit_message_text(text="✅ تم الحذف", chat_id=cid, message_id=mid)
            except: pass
            send_h(uid, f"{ee(E_CROWN,'👑')} <b>لوحة الأدمن</b>", markup=build_admin_panel()); return

        if d == "admin_points_prices":
            prices = config.get('points_prices', [])
            txt = f"{ee(E_DIAMOND,'💎')} <b>أسعـار النـقـاط</b>\n━━━━━━━━━━━━━━━\n"
            for p in prices: txt += f"• {p}\n"
            txt += f"\n{ee(E_SPARK,'✨')} أرسل الأسعار الجديدة"
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
            edit_h(cid, mid, txt, kb)
            golden.register_next_step_handler_by_chat_id(uid, admin_set_points_prices); return

        if d == "admin_back":
            admin_add_srv.pop(uid, None); admin_edit_srv.pop(uid, None); fsub_state.pop(uid, None)
            prov_state.pop(uid, None); gift_state.pop(uid, None); charge_state.pop(uid, None)
            chr_state.pop(uid, None)
            clear_user_state(uid)
            try: golden.delete_message(uid, mid)
            except: pass
            send_h(uid, f"{ee(E_CROWN,'👑')} <b>لوحة الأدمن</b>", markup=build_admin_panel()); return
        if d == "admin_broadcast":
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
            try: golden.edit_message_text(text="‹ : ارسل الرسـالة .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler(call.message, do_broadcast); return
        if d == "admin_ban":
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
            try: golden.edit_message_text(text="‹ : ارسـل ID للحـظر .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler(call.message, do_ban); return
        if d == "admin_unban":
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
            try: golden.edit_message_text(text="‹ : ارسـل ID لفك الحظر .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler(call.message, do_unban); return
        if d == "admin_settings":
            clear_user_state(uid)
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn(f"المزودين ({len(get_active_providers())} نشط)", callback_data="admin_providers", emoji=E_ROCKET, style="success"))
            kb.row(btn("اختبار الاتصال", callback_data="admin_test_server", emoji=E_SEARCH, style="success"))
            kb.row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
            provs_txt = ""
            for pk, pv in config.get("providers", {}).items():
                provs_txt += f"• {pv.get('name','?')} ({'🟢' if pv.get('active') else '🔴'})\n"
            if not provs_txt: provs_txt = "لا يوجد مزودين\n"
            try: golden.edit_message_text(text=f"‹ : الإعدادات :\n\n‹ المزودين :\n{provs_txt}",
                chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            return
        if d == "admin_test_server":
            results = []
            for pk, pv in config.get("providers", {}).items():
                if not pv.get("active"): continue
                try:
                    r = requests.post(pv['url'], data={'key':pv['api_key'],'action':'balance'}, timeout=5)
                    results.append(f"{pv.get('name','?')}: ✅ {r.text[:80]}")
                except Exception as e: results.append(f"{pv.get('name','?')}: ❌ {str(e)[:50]}")
            golden.answer_callback_query(call.id, "\n".join(results)[:200] if results else "لا مزودين", show_alert=True); return
        if d == "admin_gift":
            gift_state[uid] = {'step':'points', 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="gift_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : <b>صنع هدية</b>\n\n‹ أرسل <b>عدد النقاط</b> .",
                chat_id=cid, message_id=mid, reply_markup=kb, parse_mode='HTML')
            except: pass
            golden.register_next_step_handler(call.message, do_gift_points); return
        if d == "gift_cancel":
            gift_state.pop(uid, None); clear_user_state(uid)
            send_h(uid, f"{ee(E_CROWN,'👑')} <b>لوحة الأدمن</b>", markup=build_admin_panel())
            try: golden.delete_message(uid, mid)
            except: pass
            return
        if d == "admin_charge":
            charge_state[uid] = {'step':'id', 'msgs':[mid]}
            kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="charge_cancel", emoji=E_CROSS, style="danger"))
            try: golden.edit_message_text(text="‹ : <b>شحن نقاط</b>\n\n‹ أرسل <b>ID المستخدم</b> .",
                chat_id=cid, message_id=mid, reply_markup=kb, parse_mode='HTML')
            except: pass
            golden.register_next_step_handler(call.message, do_charge_id); return
        if d == "charge_cancel":
            charge_state.pop(uid, None); clear_user_state(uid)
            send_h(uid, f"{ee(E_CROWN,'👑')} <b>لوحة الأدمن</b>", markup=build_admin_panel())
            try: golden.delete_message(uid, mid)
            except: pass
            return
        if d == "admin_gift_settings":
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("تغيير النقاط", callback_data="ags_points", emoji=E_GIFT, style="success"))
            kb.row(btn("تغيير المدة", callback_data="ags_cooldown", emoji=E_BOLT, style="primary"))
            kb.row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
            days = config.get("daily_gift_cooldown", 172800)/86400
            try: golden.edit_message_text(text=f"‹ : إعدادات الهدية\n‹ النقاط : {config.get('daily_gift_points')}\n‹ المدة : {days} يوم",
                chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            return
        if d == "ags_points":
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_gift_settings", emoji=E_NO, style="danger"))
            try: golden.edit_message_text(text="‹ : ارسل عدد النقاط .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler(call.message, ags_points_step); return
        if d == "ags_cooldown":
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_gift_settings", emoji=E_NO, style="danger"))
            try: golden.edit_message_text(text="‹ : ارسل المدة بالساعات .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler(call.message, ags_cooldown_step); return
        if d == "admin_ref_settings":
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("تغيير المكافأة", callback_data="ars_reward", emoji=E_LINK, style="success"))
            kb.row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
            try: golden.edit_message_text(text=f"‹ : إعدادات الدعوة\n‹ المكافأة : {config.get('referral_reward')} نقطة",
                chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            return
        if d == "ars_reward":
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_ref_settings", emoji=E_NO, style="danger"))
            try: golden.edit_message_text(text="‹ : ارسل عدد النقاط .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler(call.message, ars_reward_step); return
        if d == "admin_activation_ch":
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("تعيين", callback_data="admin_set_act_ch", emoji=E_LINK, style="success"))
            kb.row(btn("اختبار", callback_data="admin_test_act_ch", emoji=E_TG, style="primary"))
            kb.row(btn("مسح", callback_data="admin_clear_act_ch", emoji=E_CROSS, style="danger"))
            kb.row(btn("رجوع", callback_data="admin_channels", emoji=E_NO, style="danger"))
            cur = config.get("activation_channel") or "غير محددة"
            try: golden.edit_message_text(text=f"‹ : قناة التفعيلات\n‹ {cur}", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            return
        if d == "admin_set_act_ch":
            kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_activation_ch", emoji=E_NO, style="danger"))
            try: golden.edit_message_text(text="‹ : ارسل ID القناة .", chat_id=cid, message_id=mid, reply_markup=kb)
            except: pass
            golden.register_next_step_handler(call.message, set_act_ch); return
        if d == "admin_clear_act_ch":
            config["activation_channel"]=""; save_json(CONFIG_FILE,config)
            golden.answer_callback_query(call.id, "✅", show_alert=True); return
        if d == "admin_test_act_ch":
            ch = config.get("activation_channel","").strip()
            if not ch: golden.answer_callback_query(call.id, "❌", show_alert=True); return
            try:
                golden.send_message(ch, "✅ اختبار")
                golden.answer_callback_query(call.id, "✅ نجح", show_alert=True)
            except Exception as e: golden.answer_callback_query(call.id, f"❌ {str(e)[:150]}", show_alert=True)
            return
        if d == "admin_toggle_login":
            new_state = not config.get("login_notify", True)
            config["login_notify"] = new_state; save_json(CONFIG_FILE, config)
            st = "مفعّل ✅" if new_state else "معطّل ❌"
            try: golden.answer_callback_query(call.id, f"الإشعار : {st}", show_alert=True)
            except: pass
            try:
                golden.edit_message_text(text=f"{ee(E_CROWN,'👑')} <b>لوحة الأدمن</b>\n{ee(E_EYE,'👁')} الإشعار : <b>{st}</b>",
                    chat_id=cid, message_id=mid, reply_markup=build_admin_panel(), parse_mode='HTML')
            except: pass
            return

    if d == "noop":
        try: golden.answer_callback_query(call.id)
        except: pass
        return
    if d == "back_main":
        clear_user_state(uid)
        gift_state.pop(uid, None); charge_state.pop(uid, None)
        edit_h(cid, mid, welcome_text(uid), main_menu(uid, ud)); return
    if d == "gift":
        now = time.time(); cd = int(config.get("daily_gift_cooldown",172800)); gp = int(config.get("daily_gift_points",10))
        if now - ud.get("last_gift",0) >= cd:
            ud["points"] = ud.get("points",0) + gp
            ud["gifts_collected"] = ud.get("gifts_collected",0) + 1
            ud["gift_points"] = ud.get("gift_points",0) + gp
            ud["last_gift"] = now; save_json(G1,Gq)
            txt = f"{ee(E_GIFT,'🎁')} <b>هدية!</b>\n{ee(E_DIAMOND,'💎')} +{gp} نقطة\n{ee(E_DIAMOND,'💎')} نقاطك : {ud.get('points',0)}"
        else:
            h = int((cd-(now-ud.get("last_gift",0)))//3600)+1
            txt = f"{ee(E_LOCK,'🔒')} انتظر {h} ساعة"
        kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
        edit_h(cid, mid, txt, kb); return
    if d == "account":
        txt = (f"{ee(E_EYE,'👁')} <b>حسابك</b>\n━━━━━━━━━━━━━━━\n"
               f"ID : {ud.get('id','')}\n💎 نقاطك : {ud.get('points',0)}\n"
               f"🔗 المدعوين : {ud.get('invited_count',0)}\n⚡ الطلبات : {ud.get('requests',0)}")
        kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
        edit_h(cid, mid, txt, kb); return
    if d == "stats":
        txt = (f"{ee(E_STAR,'⭐')} <b>إحصائيات البوت</b>\n━━━━━━━━━━━━━━━\n"
               f"👥 المستخدمين : {Gr.get('total_users',0)}\n"
               f"⚡ الطلبات : {Gr.get('total_requests',0)}\n"
               f"🔗 الدعوات : {Gr.get('total_invites',0)}")
        kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
        edit_h(cid, mid, txt, kb); return
    if d == "invite":
        link = f"https://t.me/{golden.get_me().username}?start={uid}"
        rw = config.get("referral_reward",25)
        txt = (f"{ee(E_LINK,'🔗')} <b>رابط الدعوة</b>\n<code>{link}</code>\n\n"
               f"🎁 مكافأتك ← {rw} نقطة لكل شخص\n⭐ المدعوين ← {ud.get('invited_count',0)}")
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(telebot.types.InlineKeyboardButton("📋 نسخ رابط الإحالة", switch_inline_query=link))
        kb.row(btn("أفضل المدعين", callback_data="top_referrers", emoji=E_CROWN, style="success"))
        kb.row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
        edit_h(cid, mid, txt, kb); return
    if d == "transfer":
        kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
        try: golden.edit_message_text(text="‹ : ارسـل ID الشخص .", chat_id=cid, message_id=mid, reply_markup=kb)
        except: pass
        golden.register_next_step_handler(call.message, do_transfer_start); return
    if d == "request_info":
        kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
        try: golden.edit_message_text(text="‹ : ارسـل ID الطـلب .", chat_id=cid, message_id=mid, reply_markup=kb)
        except: pass
        golden.register_next_step_handler(call.message, request_info_step); return
    if d == "buy_points":
        prices = config.get('points_prices', [])
        txt = f"{ee(E_DIAMOND,'💎')} <b>أسعـار النـقـاط</b>\n━━━━━━━━━━━━━━━\n"
        for p in prices: txt += f"⭐ {p}\n"
        txt += f"━━━━━━━━━━━━━━━\n📱 للشراء ← @zzmmkj"
        kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
        edit_h(cid, mid, txt, kb); return
    if d.startswith("trf_"):
        parts = d.split("_")
        if len(parts) < 3: return
        target = parts[1]; amt = int(parts[2]); us = str(uid)
        # ✅ فحص الهدف أولاً
        if target not in Gq:
            golden.answer_callback_query(call.id, "❌ المستخدم غير موجود", show_alert=True); return
        if us == target:
            golden.answer_callback_query(call.id, "❌ لا يمكن التحويل لنفسك", show_alert=True); return
        if us not in Gq or Gq[us].get("points",0) < amt:
            golden.answer_callback_query(call.id, "❌ نقاطك غير كافية", show_alert=True); return
        if amt <= 0:
            golden.answer_callback_query(call.id, "❌ قيمة غير صحيحة", show_alert=True); return
        Gq[us]["points"] = Gq[us].get("points",0) - amt
        Gq[us]["transfers"] = Gq[us].get("transfers",0) + 1
        Gq[target]["points"] = Gq[target].get("points",0) + amt
        save_json(G1, Gq)
        golden.answer_callback_query(call.id, f"✅ {amt} نقطة", show_alert=True)
        try: force_send(int(target), f"{ee(E_GIFT,'🎁')} <b>تم استلام {amt} نقطة</b>")
        except: pass
        return

def process_update_link(m):
    try:
        uid = m.from_user.id
        st = edit_link_state.get(uid)
        if not st: return
        oid = st.get('order_id')
        old_ch_id = st.get('old_channel_id')
        new_link = (m.text or "").strip()

        new_ch_id = extract_channel_identifier(new_link)
        if not new_ch_id:
            edit_link_state.pop(uid, None); clear_user_state(uid)
            error_restart(uid, "رابط غير صالح\nأرسل رابط قناة صحيح (مثال: https://t.me/yourchannel)")
            return

        if not verify_bot_admin_in_channel(new_ch_id):
            try: bot_username = golden.get_me().username
            except: bot_username = "Bot"
            edit_link_state.pop(uid, None); clear_user_state(uid)
            error_restart(uid,
                f"البوت ليس أدمن في القناة!\n\n"
                f"أضف @{bot_username} كأدمن في القناة الجديدة ثم أعد المحاولة")
            return

        if str(old_ch_id) == str(new_ch_id):
            edit_link_state.pop(uid, None); clear_user_state(uid)
            error_restart(uid, "هذا نفس الرابط الحالي!")
            return

        for o in Gq.get(str(uid), {}).get("orders", []):
            if isinstance(o, dict) and o.get("is_internal") and o.get("status") == "active":
                if str(o.get("channel_id")) == str(new_ch_id) and str(o.get("order_id")) != str(oid):
                    edit_link_state.pop(uid, None); clear_user_state(uid)
                    error_restart(uid, "لديك طلب آخر على نفس القناة!")
                    return

        if old_ch_id:
            try: remove_buyer_channel_from_rewards(old_ch_id)
            except: pass

        try: add_buyer_channel_to_rewards(uid, new_ch_id, new_link, oid, 0)
        except Exception as e: print(f"add_buyer_channel: {e}")

        u = get_user(uid)
        for o in u.get("orders", []):
            if isinstance(o, dict) and str(o.get("order_id")) == str(oid):
                o["link"] = new_link
                o["channel_id"] = new_ch_id
                o["status"] = "active"
                break
        save_json(G1, Gq)

        try:
            uname = f"@{u.get('username')}" if u.get('username') else "بدون يوزر"
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            act = (f"{ee(E_BOLT,'⚡')} <b>تحديث رابط طلب</b>\n━━━━━━━━━━━━━━━\n"
                   f"{ee(E_WELCOME,'👋')} <b>المستخدم</b> ← {uname}\n"
                   f"{ee(E_EYE,'👁')} <b>ID</b> ← <code>{uid}</code>\n"
                   f"{ee(E_SEARCH,'🔍')} <b>رقم الطلب</b> ← <code>{oid}</code>\n"
                   f"{ee(E_TG,'📢')} <b>القناة القديمة</b> ← <code>{old_ch_id}</code>\n"
                   f"{ee(E_LINK,'🔗')} <b>القناة الجديدة</b> ← <code>{new_ch_id}</code>\n"
                   f"⏰ <b>الوقت</b> ← {now}")
            notify_activation_channel(act)
        except: pass

        edit_link_state.pop(uid, None); clear_user_state(uid)
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(btn("طلباتي", callback_data="my_orders", emoji=E_SEARCH, style="primary"))
        send_h(uid,
            f"{ee(E_YES,'✅')} <b>تم تحديث الرابط بنجاح</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{ee(E_TG,'📢')} <b>القناة الجديدة</b> : <code>{new_ch_id}</code>\n"
            f"{ee(E_SPARK,'✨')} القناة القديمة أُزيلت من قسم النقاط\n"
            f"{ee(E_CROWN,'👑')} قناتك الجديدة تعمل الآن في قسم تجميع النقاط\n"
            f"━━━━━━━━━━━━━━━",
            markup=kb)
    except Exception as e:
        print(f"process_update_link: {e}")
        edit_link_state.pop(m.from_user.id, None); clear_user_state(m.from_user.id)
        error_restart(m.from_user.id, "خطأ غير متوقع")

# ============ باقي الخطوات ============
def buyer_reward_pts_step(m):
    uid = m.from_user.id
    if uid != G8: return
    txt = (m.text or "").strip()
    if not txt.isdigit(): error_restart(uid, "رقم غير صحيح"); return
    config["channel_followers_reward_points"] = int(txt)
    save_json(CONFIG_FILE, config)
    clear_user_state(uid)
    send_h(uid, f"✅ تم تحديث نقاط قناة المشتري إلى <b>{txt}</b>")

def chr_add_name(m):
    uid = m.from_user.id; st = chr_state.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if not txt: error_restart(uid, "اسم غير صالح"); return
    st['data']['name'] = txt
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="chr_cancel", emoji=E_CROSS, style="danger"))
    try: golden.send_message(uid, f"‹ : الاسم : {txt}\n\n‹ أرسل <b>رابط القناة</b> .", reply_markup=kb, parse_mode='HTML')
    except: pass
    golden.register_next_step_handler_by_chat_id(uid, chr_add_link)

def chr_add_link(m):
    uid = m.from_user.id; st = chr_state.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); link = (m.text or "").strip()
    if link.startswith('@'): link = f"https://t.me/{link[1:]}"
    elif not link.startswith('http'): error_restart(uid, "رابط غير صالح"); return
    st['data']['link'] = link
    auto_chat_id = ""
    if "t.me/" in link and "t.me/+" not in link:
        uname = link.split("t.me/")[-1].strip("/").split("?")[0]
        if uname and not uname.startswith("+"): auto_chat_id = "@" + uname
    st['data']['chat_id'] = auto_chat_id
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="chr_cancel", emoji=E_CROSS, style="danger"))
    try: golden.send_message(uid, f"‹ : الرابط : {link}\n\n‹ أرسل <b>عدد النقاط</b> للمشتركين .", reply_markup=kb, parse_mode='HTML')
    except: pass
    golden.register_next_step_handler_by_chat_id(uid, chr_add_points)

def chr_add_points(m):
    uid = m.from_user.id; st = chr_state.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if not txt.isdigit(): error_restart(uid, "رقم غير صحيح"); return
    data = st['data']
    data['points'] = int(txt)
    rewards = config.get("channel_rewards", [])
    new_id = f"ch_{int(time.time())}_{random.randint(100,999)}"
    emoji = random.choice([E_TG, E_LINK, E_STAR, E_HEART, E_GIFT, E_FIRE])
    style = random.choice(["primary", "success"])
    rewards.append({"id": new_id, "name": data['name'], "link": data['link'],
                    "chat_id": data['chat_id'], "points": data['points'],
                    "emoji": emoji, "style": style})
    config["channel_rewards"] = rewards; save_json(CONFIG_FILE, config)
    chr_state.pop(uid, None); clear_user_state(uid)
    send_h(uid, f"{ee(E_YES,'✅')} <b>تـم إضافة القناة</b>\n📢 {data['name']}\n💎 {data['points']} نقطة")
    txt2, kb = build_channel_rewards_admin(); send_h(uid, txt2, markup=kb)

def chr_edit_name(m):
    uid = m.from_user.id; st = chr_state.get(uid)
    if not st: return
    idx = st.get('idx', -1); txt = (m.text or "").strip()
    rewards = config.get("channel_rewards", [])
    if idx < 0 or idx >= len(rewards) or not txt: error_restart(uid, "خطأ"); return
    rewards[idx]["name"] = txt; config["channel_rewards"] = rewards; save_json(CONFIG_FILE, config)
    chr_state.pop(uid, None); clear_user_state(uid)
    send_h(uid, "✅ تم تحديث الاسم")
    txt2, kb = build_channel_rewards_admin(); send_h(uid, txt2, markup=kb)

def chr_edit_link(m):
    uid = m.from_user.id; st = chr_state.get(uid)
    if not st: return
    idx = st.get('idx', -1); link = (m.text or "").strip()
    if link.startswith('@'): link = f"https://t.me/{link[1:]}"
    rewards = config.get("channel_rewards", [])
    if idx < 0 or idx >= len(rewards) or not link.startswith('http'): error_restart(uid, "خطأ"); return
    rewards[idx]["link"] = link
    if "t.me/" in link and "t.me/+" not in link:
        uname = link.split("t.me/")[-1].strip("/").split("?")[0]
        if uname and not uname.startswith("+"): rewards[idx]["chat_id"] = "@" + uname
    config["channel_rewards"] = rewards; save_json(CONFIG_FILE, config)
    chr_state.pop(uid, None); clear_user_state(uid)
    send_h(uid, "✅ تم تحديث الرابط")
    txt2, kb = build_channel_rewards_admin(); send_h(uid, txt2, markup=kb)

def chr_edit_chatid(m):
    uid = m.from_user.id; st = chr_state.get(uid)
    if not st: return
    idx = st.get('idx', -1); txt = (m.text or "").strip()
    rewards = config.get("channel_rewards", [])
    if idx < 0 or idx >= len(rewards): error_restart(uid, "خطأ"); return
    rewards[idx]["chat_id"] = txt; config["channel_rewards"] = rewards; save_json(CONFIG_FILE, config)
    chr_state.pop(uid, None); clear_user_state(uid)
    send_h(uid, "✅ تم تحديث chat_id")
    txt2, kb = build_channel_rewards_admin(); send_h(uid, txt2, markup=kb)

def chr_edit_points(m):
    uid = m.from_user.id; st = chr_state.get(uid)
    if not st: return
    idx = st.get('idx', -1); txt = (m.text or "").strip()
    if not txt.isdigit(): error_restart(uid, "رقم غير صحيح"); return
    rewards = config.get("channel_rewards", [])
    if idx < 0 or idx >= len(rewards): error_restart(uid, "خطأ"); return
    rewards[idx]["points"] = int(txt); config["channel_rewards"] = rewards; save_json(CONFIG_FILE, config)
    chr_state.pop(uid, None); clear_user_state(uid)
    send_h(uid, "✅ تم تحديث النقاط")
    txt2, kb = build_channel_rewards_admin(); send_h(uid, txt2, markup=kb)

def prov_add_name(m):
    uid = m.from_user.id; st = prov_state.get(uid)
    if not st: return
    txt = (m.text or "").strip()
    if not txt: error_restart(uid, "اسم غير صالح"); return
    st['name'] = txt
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="prov_cancel", emoji=E_CROSS, style="danger"))
    try: golden.send_message(uid, f"‹ : الاسم : {txt}\n\n‹ أرسل <b>رابط المزود</b>", reply_markup=kb, parse_mode='HTML')
    except: pass
    golden.register_next_step_handler_by_chat_id(uid, prov_add_url)

def prov_add_url(m):
    uid = m.from_user.id; st = prov_state.get(uid)
    if not st: return
    txt = (m.text or "").strip()
    if not txt.startswith("http"): error_restart(uid, "رابط غير صالح"); return
    st['url'] = txt
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="prov_cancel", emoji=E_CROSS, style="danger"))
    try: golden.send_message(uid, f"‹ : الرابط : {txt}\n\n‹ أرسل <b>API Key</b>", reply_markup=kb, parse_mode='HTML')
    except: pass
    golden.register_next_step_handler_by_chat_id(uid, prov_add_api)

def prov_add_api(m):
    uid = m.from_user.id; st = prov_state.get(uid)
    if not st: return
    txt = (m.text or "").strip()
    if not txt: error_restart(uid, "API Key غير صالح"); return
    name = st.get('name','مزود'); url = st.get('url',''); api_key = txt
    provs = config.get("providers", {})
    new_pk = f"p{len(provs)+1}"
    while new_pk in provs: new_pk = f"p{random.randint(1000,9999)}"
    provs[new_pk] = {"name": name,"url": url,"api_key": api_key,"active": True,"default": False}
    config["providers"] = provs; save_json(CONFIG_FILE, config)
    prov_state.pop(uid, None); clear_user_state(uid)
    send_h(uid, f"{ee(E_YES,'✅')} <b>تـم إضافة المزود</b>\n📌 {name}")
    txt2, kb = build_providers_menu(); send_h(uid, txt2, markup=kb)

def prov_edit_name(m):
    uid = m.from_user.id; st = prov_state.get(uid)
    if not st: return
    pk = st.get('key'); txt = (m.text or "").strip()
    if not txt: error_restart(uid, "اسم غير صالح"); return
    if pk in config.get("providers", {}):
        config["providers"][pk]["name"] = txt; save_json(CONFIG_FILE, config)
        prov_state.pop(uid, None); clear_user_state(uid)
        send_h(uid, "✅ تم تحديث الاسم")
        txt2, kb = build_providers_menu(); send_h(uid, txt2, markup=kb)

def prov_edit_url(m):
    uid = m.from_user.id; st = prov_state.get(uid)
    if not st: return
    pk = st.get('key'); txt = (m.text or "").strip()
    if not txt.startswith("http"): error_restart(uid, "رابط غير صالح"); return
    if pk in config.get("providers", {}):
        config["providers"][pk]["url"] = txt; save_json(CONFIG_FILE, config)
        prov_state.pop(uid, None); clear_user_state(uid)
        send_h(uid, "✅ تم تحديث الرابط")
        txt2, kb = build_providers_menu(); send_h(uid, txt2, markup=kb)

def prov_edit_api(m):
    uid = m.from_user.id; st = prov_state.get(uid)
    if not st: return
    pk = st.get('key'); txt = (m.text or "").strip()
    if not txt: error_restart(uid, "API Key غير صالح"); return
    if pk in config.get("providers", {}):
        config["providers"][pk]["api_key"] = txt; save_json(CONFIG_FILE, config)
        prov_state.pop(uid, None); clear_user_state(uid)
        send_h(uid, "✅ تم تحديث API Key")
        txt2, kb = build_providers_menu(); send_h(uid, txt2, markup=kb)

def fsub_add_name(m):
    uid = m.from_user.id; st = fsub_state.get(uid)
    if not st: return
    txt = (m.text or "").strip()
    if not txt: error_restart(uid, "اسم غير صالح"); return
    st['name'] = txt
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="fsub_cancel", emoji=E_CROSS, style="danger"))
    try: golden.send_message(uid, f"‹ : الاسم : {txt}\n\n‹ أرسل <b>رابط القناة</b>", reply_markup=kb, parse_mode='HTML')
    except: pass
    golden.register_next_step_handler_by_chat_id(uid, fsub_add_link)

def fsub_add_link(m):
    uid = m.from_user.id; st = fsub_state.get(uid)
    if not st: return
    link = (m.text or "").strip()
    if link.startswith('@'): link = f"https://t.me/{link[1:]}"
    elif not link.startswith('http'): error_restart(uid, "رابط غير صالح"); return
    st['link'] = link
    auto_chat_id = ""
    if "t.me/+" in link or "joinchat" in link:
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(btn("تخطي", callback_data="fsub_skip_chatid", emoji=E_ROCKET, style="primary"))
        kb.row(btn("إلغاء", callback_data="fsub_cancel", emoji=E_CROSS, style="danger"))
        try: golden.send_message(uid, "⚠️ قناة خاصة - أرسل chat_id أو تخطي", reply_markup=kb)
        except: pass
        golden.register_next_step_handler_by_chat_id(uid, fsub_add_chatid); return
    else:
        if "t.me/" in link:
            uname = link.split("t.me/")[-1].strip("/").split("?")[0]
            if uname and not uname.startswith("+"): auto_chat_id = "@" + uname
        st['chat_id'] = auto_chat_id
    fsub_finish_add(uid)

def fsub_add_chatid(m):
    uid = m.from_user.id; st = fsub_state.get(uid)
    if not st: return
    txt = (m.text or "").strip()
    if txt.startswith('@') or txt.startswith('-') or txt.isdigit() or (txt.startswith('-') and txt[1:].isdigit()):
        st['chat_id'] = txt
    else: error_restart(uid, "chat_id غير صالح"); return
    fsub_finish_add(uid)

def fsub_finish_add(uid):
    st = fsub_state.pop(uid, None)
    if not st: return
    name = st.get('name', 'قناة'); link = st.get('link', ''); chat_id = st.get('chat_id', '')
    forced = config.get("forced_channels", [])
    emoji = random.choice([E_TG, E_LINK, E_STAR, E_HEART, E_GIFT, E_FIRE])
    style = random.choice(["primary", "success"])
    forced.append({"name": name, "link": link, "chat_id": chat_id, "emoji": emoji, "style": style})
    config["forced_channels"] = forced; save_json(CONFIG_FILE, config)
    clear_user_state(uid)
    txt = f"{ee(E_YES,'✅')} <b>تـم إضافة القناة</b>\n📢 {name}"
    t2, kb = build_forced_subs_menu()
    send_h(uid, txt); send_h(uid, t2, markup=kb)

def fsub_edit_name(m):
    uid = m.from_user.id; st = fsub_state.get(uid)
    if not st: return
    idx = st.get('idx', -1); txt = (m.text or "").strip()
    forced = config.get("forced_channels", [])
    if idx < 0 or idx >= len(forced) or not txt: error_restart(uid, "خطأ"); return
    forced[idx]["name"] = txt; config["forced_channels"] = forced; save_json(CONFIG_FILE, config)
    fsub_state.pop(uid, None); clear_user_state(uid)
    send_h(uid, "✅ تم التحديث")
    t2, kb = build_forced_subs_menu(); send_h(uid, t2, markup=kb)

def fsub_edit_link(m):
    uid = m.from_user.id; st = fsub_state.get(uid)
    if not st: return
    idx = st.get('idx', -1); link = (m.text or "").strip()
    if link.startswith('@'): link = f"https://t.me/{link[1:]}"
    forced = config.get("forced_channels", [])
    if idx < 0 or idx >= len(forced) or not link.startswith('http'): error_restart(uid, "خطأ"); return
    forced[idx]["link"] = link
    if "t.me/" in link and "t.me/+" not in link:
        uname = link.split("t.me/")[-1].strip("/").split("?")[0]
        if uname and not uname.startswith("+"): forced[idx]["chat_id"] = "@" + uname
    config["forced_channels"] = forced; save_json(CONFIG_FILE, config)
    fsub_state.pop(uid, None); clear_user_state(uid)
    send_h(uid, "✅ تم التحديث")
    t2, kb = build_forced_subs_menu(); send_h(uid, t2, markup=kb)

def pm_show_user(cid, mid, tuid):
    try:
        u = Gq.get(tuid, {})
        uname = u.get('username','بدون')
        text = (f"{ee(E_EYE,'👁')} <b>المستخدم</b>\n━━━━━━━━━━━━━━━\n"
                f"ID : <code>{tuid}</code>\n@{uname}\n💎 {u.get('points',0)}\n"
                f"⚡ {u.get('requests',0)}\n🔗 {u.get('invited_count',0)}")
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(btn("إضافة", callback_data=f"pmact_add_{tuid}", emoji=E_SPARK, style="success"),
               btn("خصم", callback_data=f"pmact_sub_{tuid}", emoji=E_CROSS, style="danger"))
        kb.row(btn("شحن", callback_data=f"pmact_charge_{tuid}", emoji=E_GIFT, style="success"),
               btn("تعيين", callback_data=f"pmact_set_{tuid}", emoji=E_BOLT, style="primary"))
        kb.row(btn("تصفير", callback_data=f"pm_zero_{tuid}", emoji=E_BROKEN, style="danger"))
        kb.row(btn("رجوع", callback_data="admin_points_mgr", emoji=E_NO, style="danger"))
        edit_h(cid, mid, text, kb)
    except: pass

def show_my_orders(uid, message, view="active"):
    try:
        u = get_user(uid)
        kb = telebot.types.InlineKeyboardMarkup()
        all_orders = [o for o in u.get("orders", []) if isinstance(o, dict)]
        active_orders = [o for o in all_orders if o.get("status") not in ("completed", "ended")]
        completed_orders = [o for o in all_orders if o.get("status") == "completed"]
        if view == "completed":
            txt = f"{ee(E_YES,'✅')} <b>الطلبات المكتملة</b>\n━━━━━━━━━━━━━━━\n\n"
            if not completed_orders: txt += f"{ee(E_BROKEN,'💔')} <i>لا يوجد</i>"
            else:
                for o in reversed(completed_orders[-5:]):
                    oid = o.get("order_id"); svc_name = str(o.get("service","خدمة"))
                    txt += f"{ee(E_STAR,'⭐')} {svc_name}\n⚡ {o.get('qty',0)} | ✅ مكتمل\n"
                    if oid: txt += f"🔍 <code>{oid}</code>\n\n"
            kb.row(btn("النشطة", callback_data="my_orders_all", emoji=E_BOLT, style="primary"))
        else:
            txt = f"{ee(E_SEARCH,'🔍')} <b>طـلـبـاتـي</b>\n━━━━━━━━━━━━━━━\n\n"
            has = False
            if active_orders:
                has = True
                for o in list(reversed(active_orders[-5:])):
                    oid = o.get("order_id"); svc_name = str(o.get("service","خدمة"))
                    sname = svc_name[:20]
                    is_internal = o.get("is_internal", False)
                    if is_internal:
                        ch_id = o.get("channel_id", "")
                        order_qty = o.get("qty", 0)
                        verified = 0
                        for r in config.get("channel_rewards", []):
                            if str(r.get("chat_id")) == str(ch_id) and r.get("from_service"):
                                verified = r.get("verified_count", 0)
                                if r.get("order_qty"): order_qty = r.get("order_qty")
                                break
                        remaining = max(0, order_qty - verified)
                        progress = int((verified / order_qty * 100)) if order_qty > 0 else 0
                        txt += (f"{ee(E_CROWN,'👑')} <b>{svc_name}</b> 🏠\n"
                                f"━━━━━━━━━━━━━━━\n"
                                f"{ee(E_TG,'📢')} القناة : <code>{ch_id}</code>\n"
                                f"{ee(E_STAR,'⭐')} المطلوب : <b>{order_qty}</b>\n"
                                f"{ee(E_YES,'✅')} تم التحقق : <b>{verified}</b>\n"
                                f"{ee(E_BOLT,'⚡')} المتبقي : <b>{remaining}</b>\n"
                                f"{ee(E_FIRE,'🔥')} الإنجاز : <b>{progress}%</b>\n"
                                f"{ee(E_SEARCH,'🔍')} <code>{oid}</code>\n\n")
                        kb.row(btn(f"🔄 {sname}", callback_data=f"refresh_order_{oid}", emoji=E_ROCKET, style="success"))
                    else:
                        txt += f"{ee(E_STAR,'⭐')} {svc_name}\n⚡ {o.get('qty',0)}\n"
                        if oid:
                            txt += f"🔍 <code>{oid}</code>\n\n"
                            kb.row(btn(f"تحديث {sname}", callback_data=f"refresh_order_{oid}", emoji=E_ROCKET, style="success"))
                        else: txt += "\n"
            if not has: txt += f"{ee(E_BROKEN,'💔')} <i>لا يوجد لديك طلبات</i>"
            kb.row(btn("🔄 تحديث جميع الطلبات", callback_data="user_update_all_orders", emoji=E_SEARCH, style="success"))
            kb.row(btn(f"مكتمل ({len(completed_orders)})", callback_data="my_orders_completed", emoji=E_YES, style="primary"))
        kb.row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
        try:
            golden.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=txt, reply_markup=kb, parse_mode='HTML'); return
        except: pass
        try: golden.send_message(uid, txt, reply_markup=kb, parse_mode='HTML'); return
        except: pass
        try: golden.send_message(uid, strip_all_html(txt), reply_markup=kb); return
        except: pass
    except Exception as e: print(f"show_my_orders: {e}")

def handle_qty_step(m, sk):
    try:
        uid = m.from_user.id
        if sk not in SERVICES: error_restart(uid, "خدمة غير متوفرة"); return
        ud = get_user(uid); svc = SERVICES[sk]
        txt = (m.text or "").strip()
        if not txt.isdigit(): error_restart(uid, "عدد غير صالح"); return
        qty = int(txt)
        if qty < svc.get('min',1): error_restart(uid, f"الحد الأدنى {svc.get('min',1)}"); return
        if qty > svc.get('max',999999): error_restart(uid, f"الحد الأقصى {svc.get('max',999999)}"); return
        cost = calc_cost(qty, svc)
        if ud.get("points",0) < cost:
            send_h(uid, f"❌ <b>نقاطك غير كافية</b>\nالتكلفة : {cost}\nنقاطك : {ud.get('points',0)}", markup=restart_kb()); return
        is_special = svc.get('special') == 'channel_followers'
        if is_special:
            try: bot_username = golden.get_me().username
            except: bot_username = "Bot"
            send_h(uid,
                f"✅ <b>تم استلام الكمية</b> {qty}\n"
                f"💎 التكلفة ← {cost} نقطة\n"
                f"━━━━━━━━━━━━━━━\n"
                f"{ee(E_LOCK,'🔒')} <b>الخطوة الأخيرة :</b>\n"
                f"أرسل رابط قناتك الآن\n\n"
                f"⚠️ تأكد أنك أضفت البوت <b>@{bot_username}</b> كأدمن أولاً\n"
                f"❌ لن يتم إنشاء الطلب إذا لم يكن البوت أدمن\n"
                f"⚠️ لا يمكن تكرار نفس الرابط إذا كان لديك طلب نشط عليه")
        else:
            send_h(uid, f"✅ <b>تم استلام الكمية</b> {qty}\n💎 التكلفة ← {cost} نقطة\n🔗 الآن ارسل الرابط")
        golden.register_next_step_handler(m, handle_link_step, sk, qty, cost)
    except: pass

def handle_link_step(m, sk, qty, cost):
    try:
        uid = m.from_user.id
        if sk not in SERVICES: error_restart(uid, "خدمة غير متوفرة"); return
        ud = get_user(uid); svc = SERVICES[sk]
        link = (m.text or "").strip()
        is_special = svc.get('special') == 'channel_followers'
        if is_special:
            ch_id = extract_channel_identifier(link)
            if not ch_id:
                error_restart(uid, "أرسل رابط قناة صحيح (مثال: https://t.me/yourchannel أو @yourchannel)"); return

            for o in ud.get("orders", []):
                if isinstance(o, dict) and o.get("is_internal") and o.get("status") == "active":
                    if str(o.get("channel_id")) == str(ch_id):
                        error_restart(uid, "⚠️ لديك طلب نشط على نفس القناة بالفعل\n💡 يمكنك تغيير الرابط من قسم طلباتي")
                        return

            if not verify_bot_admin_in_channel(ch_id):
                try: bot_username = golden.get_me().username
                except: bot_username = "Bot"
                error_restart(uid,
                    f"البوت ليس أدمن في القناة!\n\n"
                    f"أضف @{bot_username} كأدمن في قناتك ثم أعد المحاولة"); return
            if ud.get("points",0) < cost: error_restart(uid, "نقاطك غير كافية"); return
            pending_orders[uid] = {'sk':sk,'qty':qty,'cost':cost,'link':link,'special':True,'channel_id':ch_id}
            txt = (f"{ee(E_SEARCH,'🔍')} <b>تأكيـد الاشـتـراك</b>\n━━━━━━━━━━━━━━━\n"
                   f"⭐ {svc.get('name','')}\n⚡ {qty}\n💎 {cost} نقطة\n"
                   f"📢 القناة : {ch_id}\n"
                   f"━━━━━━━━━━━━━━━\n"
                   f"{ee(E_LOCK,'🔒')} <b>تنبيه:</b> سيتم مراقبة البوت في القناة كل دقيقة\n"
                   f"⚠️ إذا أزلت البوت سينتهي الاشتراك فوراً\n"
                   f"{ee(E_CROSS,'❌')} <b>لا يوجد استرجاع للنقاط بعد الموافقة</b>\n"
                   f"━━━━━━━━━━━━━━━\n"
                   f"{ee(E_SPARK,'✨')} هل تريد التأكيد ؟")
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(btn("تأكيد ✅", callback_data="oc_yes", emoji=E_YES, style="success"),
                   btn("إلغاء ❌", callback_data="oc_no", emoji=E_CROSS, style="danger"))
            send_h(uid, txt, markup=kb, silent_fail=False)
            return
        if not validate_url(link, svc.get('type','instagram')): error_restart(uid, "رابط غير صالح"); return
        if ud.get("points",0) < cost: error_restart(uid, "نقاطك غير كافية"); return
        pending_orders[uid] = {'sk':sk,'qty':qty,'cost':cost,'link':link}
        txt = (f"{ee(E_SEARCH,'🔍')} <b>تأكيـد الـطـلـب</b>\n━━━━━━━━━━━━━━━\n"
               f"⭐ {svc.get('name','')}\n⚡ {qty}\n💎 {cost} نقطة\n🔗 <a href=\"{link}\">الرابط</a>\n"
               f"━━━━━━━━━━━━━━━\n{ee(E_SPARK,'✨')} هل تريد تأكيد الطلب ؟")
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(btn("تأكيد", callback_data="oc_yes", emoji=E_YES, style="success"),
               btn("إلغاء", callback_data="oc_no", emoji=E_CROSS, style="danger"))
        send_h(uid, txt, markup=kb, silent_fail=False)
    except: pass

def request_info_step(m):
    try:
        uid = m.from_user.id; oid = (m.text or "").strip()
        if not oid.isdigit() and not oid.startswith("INT_"): error_restart(uid, "أرسل رقم صحيح"); return
        u = get_user(uid); prov_key = None; is_internal = False; target_order = None
        for o in u.get("orders", []):
            if isinstance(o, dict) and str(o.get("order_id"))==str(oid):
                prov_key = o.get("provider")
                is_internal = o.get("is_internal", False)
                target_order = o
                break
        if is_internal and target_order:
            ch_id = target_order.get("channel_id", "")
            order_qty = target_order.get("qty", 0); verified = 0
            for r in config.get("channel_rewards", []):
                if str(r.get("chat_id")) == str(ch_id) and r.get("from_service"):
                    verified = r.get("verified_count", 0)
                    if r.get("order_qty"): order_qty = r.get("order_qty")
                    break
            remaining = max(0, order_qty - verified)
            progress = int((verified / order_qty * 100)) if order_qty > 0 else 0
            send_h(uid, f"{ee(E_CROWN,'👑')} <b>إحصائيات طلبك</b>\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"{ee(E_SEARCH,'🔍')} <b>رقم الطلب</b> : <code>{oid}</code>\n"
                       f"{ee(E_TG,'📢')} <b>القناة</b> : <code>{ch_id}</code>\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"{ee(E_STAR,'⭐')} <b>المطلوب</b> : <b>{order_qty}</b>\n"
                       f"{ee(E_YES,'✅')} <b>تم التحقق</b> : <b>{verified}</b>\n"
                       f"{ee(E_BOLT,'⚡')} <b>المتبقي</b> : <b>{remaining}</b>\n"
                       f"{ee(E_FIRE,'🔥')} <b>نسبة الإنجاز</b> : <b>{progress}%</b>\n"
                       f"━━━━━━━━━━━━━━━")
            return
        st = get_order_status(oid, prov_key)
        if not st: error_restart(uid, "تعذر جلب الحالة"); return
        if 'error' in st: error_restart(uid, f"خطأ ← {st['error']}"); return
        status = st.get('status','غير معروف')
        sa = {'Pending':'⏳ انتظار','In progress':'🚀 تنفيذ','Completed':'✅ مكتمل',
              'Partial':'⚠️ جزئي','Canceled':'❌ ملغي'}.get(status,status)
        if status in ['Completed', 'Partial']: mark_order_completed(uid, oid)
        txt = f"🔍 <b>معلومات الطلب</b>\nرقم : <code>{oid}</code>\nالحالة : {sa}\nالبداية : {st.get('start_count','0')}\nالمتبقي : {st.get('remains','0')}"
        kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="back_main", emoji=E_NO, style="danger"))
        send_h(uid, txt, markup=kb)
    except: pass

def do_transfer_start(m):
    try:
        target = (m.text or "").strip(); uid = str(m.from_user.id)
        if not target.isdigit() or target == uid or target not in Gq:
            error_restart(m.from_user.id, "مستخدم غير موجود"); return
        kb = telebot.types.InlineKeyboardMarkup()
        kb.row(btn("10", callback_data=f"trf_{target}_10", emoji=E_DIAMOND, style="primary"),
               btn("25", callback_data=f"trf_{target}_25", emoji=E_DIAMOND, style="primary"),
               btn("50", callback_data=f"trf_{target}_50", emoji=E_DIAMOND, style="success"))
        golden.send_message(m.from_user.id, f"‹ : اختر الكمية للتحويل لـ {target} .", reply_markup=kb)
    except: pass

def pm_search_step(m):
    try:
        tuid = (m.text or "").strip()
        if tuid not in Gq: error_restart(G8, "غير موجود"); return
        msg = golden.send_message(G8, "⏳ ...")
        pm_show_user(G8, msg.message_id, tuid)
    except: pass

def pm_apply_points(m):
    try:
        uid = m.from_user.id
        if uid not in pm_state: return
        st = pm_state.pop(uid); action = st.get('action'); tuid = st.get('target')
        txt = (m.text or "").strip()
        if not txt.isdigit(): error_restart(uid, "رقم غير صحيح"); return
        val = int(txt)
        if tuid not in Gq: error_restart(uid, "غير موجود"); return
        if action == "add": Gq[tuid]["points"] = Gq[tuid].get("points",0) + val; msg = f"+{val}"
        elif action == "sub": Gq[tuid]["points"] = max(0, Gq[tuid].get("points",0) - val); msg = f"-{val}"
        elif action == "set": Gq[tuid]["points"] = val; msg = f"={val}"
        elif action == "charge": Gq[tuid]["points"] = Gq[tuid].get("points",0) + val; msg = f"+{val}"
        else: return
        save_json(G1, Gq)
        send_h(uid, f"✅ {msg}\nنقاطه الآن ← {Gq[tuid].get('points',0)}")
        try: force_send(int(tuid), f"💎 <b>تم تحديث نقاطك</b>\nنقاطك : {Gq[tuid].get('points',0)}")
        except: pass
        clear_user_state(uid)
        msg2 = golden.send_message(uid, "⏳ ...")
        pm_show_user(uid, msg2.message_id, tuid)
    except: pass

def srv_add_id(m):
    uid = m.from_user.id; st = admin_add_srv.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if not txt.isdigit():
        clean_msgs(uid, admin_add_srv.pop(uid,None)); error_restart(uid, "ID غير صحيح")
        send_h(uid, "👑 لوحة الأدمن", markup=build_admin_panel()); return
    st['data']['id'] = txt
    pk = st['data'].get('provider','p1')
    if pk == 'internal': pv_name = 'نظام داخلي'
    else:
        pv = get_provider(pk); pv_name = pv.get('name','?') if pv else '?'
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="srv_add_cancel", emoji=E_CROSS, style="danger"))
    msg = golden.send_message(uid, f"‹ : المزود : {pv_name}\n‹ ID : {txt}\n\n‹ أرسل اسم الخدمة .", reply_markup=kb, parse_mode='HTML')
    st['msgs'].append(msg.message_id)
    clear_user_state(uid)
    golden.register_next_step_handler_by_chat_id(uid, srv_add_name)

def srv_add_name(m):
    uid = m.from_user.id; st = admin_add_srv.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if len(txt) < 2:
        clean_msgs(uid, admin_add_srv.pop(uid,None)); error_restart(uid, "اسم غير صحيح")
        send_h(uid, "👑 لوحة الأدمن", markup=build_admin_panel()); return
    st['data']['name'] = txt
    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(btn("تخطي", callback_data="srv_add_skip_desc", emoji=E_NO, style="primary"),
           btn("إلغاء", callback_data="srv_add_cancel", emoji=E_CROSS, style="danger"))
    msg = golden.send_message(uid, f"‹ : الاسم : {txt}\n\n‹ أرسل وصف الخدمة (اختياري)\n‹ أو اضغط تخطي .", reply_markup=kb, parse_mode='HTML')
    st['msgs'].append(msg.message_id)
    clear_user_state(uid)
    golden.register_next_step_handler_by_chat_id(uid, srv_add_desc)

def srv_add_desc(m):
    uid = m.from_user.id; st = admin_add_srv.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if txt and txt != "-": st['data']['description'] = txt
    ask_qty(uid)

def ask_qty(uid):
    st = admin_add_srv.get(uid)
    if not st: return
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="srv_add_cancel", emoji=E_CROSS, style="danger"))
    try:
        msg = golden.send_message(uid, "‹ : أرسل الكمية (100 أو 100-1000)", reply_markup=kb, parse_mode='HTML')
        st['msgs'].append(msg.message_id)
    except: pass
    clear_user_state(uid)
    golden.register_next_step_handler_by_chat_id(uid, srv_add_qty)

def srv_add_qty(m):
    uid = m.from_user.id; st = admin_add_srv.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if '-' in txt and not txt.startswith('-'):
        parts = txt.split('-')
        try:
            mn = int(parts[0].strip()); mx = int(parts[1].strip())
            if mn > mx: mn, mx = mx, mn
        except:
            clean_msgs(uid, admin_add_srv.pop(uid,None)); error_restart(uid, "كمية غير صحيحة")
            send_h(uid, "👑 لوحة الأدمن", markup=build_admin_panel()); return
    elif txt.isdigit(): mn = mx = int(txt)
    else:
        clean_msgs(uid, admin_add_srv.pop(uid,None)); error_restart(uid, "كمية غير صحيحة")
        send_h(uid, "👑 لوحة الأدمن", markup=build_admin_panel()); return
    st['data']['min'] = mn; st['data']['max'] = mx
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="srv_add_cancel", emoji=E_CROSS, style="danger"))
    msg = golden.send_message(uid, f"‹ : الكمية : {mn}-{mx}\n\n‹ أرسل الوحدة (مثلاً 1000)", reply_markup=kb, parse_mode='HTML')
    st['msgs'].append(msg.message_id)
    clear_user_state(uid)
    golden.register_next_step_handler_by_chat_id(uid, srv_add_unit)

def srv_add_unit(m):
    uid = m.from_user.id; st = admin_add_srv.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if not txt.isdigit() or int(txt) <= 0:
        clean_msgs(uid, admin_add_srv.pop(uid,None)); error_restart(uid, "الوحدة غير صحيحة")
        send_h(uid, "👑 لوحة الأدمن", markup=build_admin_panel()); return
    st['data']['unit'] = int(txt)
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="srv_add_cancel", emoji=E_CROSS, style="danger"))
    msg = golden.send_message(uid, f"‹ : الوحدة : {txt}\n\n‹ أرسل السعر النهائي", reply_markup=kb, parse_mode='HTML')
    st['msgs'].append(msg.message_id)
    clear_user_state(uid)
    golden.register_next_step_handler_by_chat_id(uid, srv_add_price)

def srv_add_price(m):
    uid = m.from_user.id; st = admin_add_srv.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if not txt.isdigit():
        clean_msgs(uid, admin_add_srv.pop(uid,None)); error_restart(uid, "سعر غير صحيح")
        send_h(uid, "👑 لوحة الأدمن", markup=build_admin_panel()); return
    price = int(txt); data = st['data']; name = data.get('name','')
    srv_type = 'instagram'; n = name.lower()
    if 'تليجرام' in name or 'telegram' in n: srv_type='telegram'
    elif 'تيك توك' in name or 'tiktok' in n: srv_type='tiktok'
    key = f"custom_{data.get('id','')}"; base = key; i = 1
    while key in SERVICES: key = f"{base}_{i}"; i += 1
    new_svc = {'id':data.get('id',''),'name':name,'min':data.get('min',1),'max':data.get('max',1),
               'price':price,'final_price':price,'unit':data.get('unit',100),'type':srv_type,
               'emoji':random.choice(RANDOM_EMOJIS),'style':random.choice(RANDOM_STYLES),
               'provider':data.get('provider','p1')}
    if data.get('description'): new_svc['description'] = data['description']
    custom_services[key] = new_svc; save_custom_services(custom_services); SERVICES[key] = new_svc
    clean_msgs(uid, admin_add_srv.pop(uid,None))
    kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
    if data.get('provider') == 'internal': prov_name = 'نظام داخلي'
    else: prov_name = get_provider(data.get('provider','p1')).get('name','?') if get_provider(data.get('provider','p1')) else '?'
    send_h(uid, f"✅ <b>تم إضافة الخدمة</b>\n📌 {name}\n⚡ {data.get('id','')}\n🔍 وحدة {data.get('unit',100)}\n💎 {price}\n⭐ {data.get('min',0)}-{data.get('max',0)}\n🚀 {prov_name}\n\n💡 لتفعيل خصائص القناة : إدارة الخدمات ← تعديل الخدمة ← خاصية القناة", markup=kb)

def srv_edit_field(m):
    uid = m.from_user.id; st = admin_edit_srv.get(uid)
    if not st: return
    txt = (m.text or "").strip(); sk = st.get('key'); field = st.get('field')
    if sk not in SERVICES: admin_edit_srv.pop(uid, None); return
    svc = SERVICES[sk]
    if field == 'name':
        if len(txt) < 2: error_restart(uid, "اسم غير صحيح"); return
        svc['name'] = txt
    elif field == 'desc':
        if txt == "-": svc.pop('description', None)
        else: svc['description'] = txt
    elif field == 'unit':
        if not txt.isdigit() or int(txt) <= 0: error_restart(uid, "وحدة غير صحيحة"); return
        svc['unit'] = int(txt)
    elif field == 'price':
        if not txt.isdigit(): error_restart(uid, "رقم غير صحيح"); return
        svc['price'] = int(txt)
    elif field == 'final':
        if not txt.isdigit(): error_restart(uid, "رقم غير صحيح"); return
        svc['final_price'] = int(txt)
    elif field == 'qty':
        if '-' in txt and not txt.startswith('-'):
            parts = txt.split('-')
            try:
                mn = int(parts[0].strip()); mx = int(parts[1].strip())
                if mn > mx: mn, mx = mx, mn
                svc['min'] = mn; svc['max'] = mx
            except: error_restart(uid, "صيغة غير صحيحة"); return
        elif txt.isdigit(): svc['min'] = int(txt); svc['max'] = int(txt)
        else: error_restart(uid, "رقم غير صحيح"); return
    elif field == 'id':
        if txt.lower() == 'internal':
            svc['id'] = 'internal'
            svc['provider'] = 'internal'
        elif not txt.isdigit(): error_restart(uid, "ID غير صحيح"); return
        else: svc['id'] = txt
    elif field == 'warning':
        svc['warning_text'] = txt
    admin_edit_srv.pop(uid, None); clear_user_state(uid)
    if sk in custom_services: custom_services[sk] = svc; save_custom_services(custom_services)
    if sk in BASE_SERVICES:
        overrides = load_json(BASE_OVERRIDES_FILE, {}); overrides[sk] = svc; save_json(BASE_OVERRIDES_FILE, overrides)
    SERVICES[sk] = svc
    kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
    send_h(uid, "✅ تم التحديث", markup=kb)

def admin_set_points_prices(m):
    uid = m.from_user.id
    if uid != G8: return
    lines = [l.strip() for l in (m.text or "").split('\n') if l.strip()]
    if not lines: error_restart(uid, "أرسل نص صحيح"); return
    config['points_prices'] = lines; save_json(CONFIG_FILE, config)
    clear_user_state(uid)
    kb = telebot.types.InlineKeyboardMarkup().row(btn("رجوع", callback_data="admin_back", emoji=E_NO, style="danger"))
    send_h(uid, "✅ تم تحديث الأسعار", markup=kb)

def do_gift_points(m):
    uid = m.from_user.id; st = gift_state.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if not txt.isdigit():
        gift_state.pop(uid, None); clear_user_state(uid); error_restart(uid, "رقم غير صحيح")
        send_h(uid, "👑 لوحة الأدمن", markup=build_admin_panel()); return
    st['points'] = int(txt)
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="gift_cancel", emoji=E_CROSS, style="danger"))
    try: golden.send_message(uid, f"‹ : النقاط : {txt}\n\n‹ أرسل <b>عدد المستخدمين</b> .", reply_markup=kb, parse_mode='HTML')
    except: pass
    golden.register_next_step_handler_by_chat_id(uid, do_gift_maxusers)

def do_gift_maxusers(m):
    uid = m.from_user.id; st = gift_state.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if not txt.isdigit() or int(txt) < 1:
        gift_state.pop(uid, None); clear_user_state(uid); error_restart(uid, "رقم غير صحيح"); return
    max_users = int(txt); pts = st['points']
    code = 'Xbot_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    Gt[code] = {"points":pts,"max_users":max_users,"used_count":0,"used_by":[]}
    save_json(G6, Gt)
    gift_state.pop(uid, None); clear_user_state(uid)
    link = f"https://t.me/{golden.get_me().username}?start={code}"
    send_h(uid, f"🎁 <b>تم إنشاء الهدية</b>\n💎 {pts} نقطة\n⭐ {max_users} مستخدم\n🔗 <code>{link}</code>")

def do_charge_id(m):
    uid = m.from_user.id; st = charge_state.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if not txt.isdigit():
        charge_state.pop(uid, None); clear_user_state(uid); error_restart(uid, "ID غير صحيح"); return
    if txt not in Gq:
        charge_state.pop(uid, None); clear_user_state(uid); error_restart(uid, "غير موجود"); return
    st['target'] = txt
    kb = telebot.types.InlineKeyboardMarkup().row(btn("إلغاء", callback_data="charge_cancel", emoji=E_CROSS, style="danger"))
    try: golden.send_message(uid, f"‹ : ID : {txt}\n‹ نقاطه : {Gq[txt].get('points',0)}\n\n‹ أرسل عدد النقاط .", reply_markup=kb, parse_mode='HTML')
    except: pass
    golden.register_next_step_handler_by_chat_id(uid, do_charge_amount)

def do_charge_amount(m):
    uid = m.from_user.id; st = charge_state.get(uid)
    if not st: return
    st['msgs'].append(m.message_id); txt = (m.text or "").strip()
    if not txt.isdigit() or int(txt) <= 0:
        charge_state.pop(uid, None); clear_user_state(uid); error_restart(uid, "رقم غير صحيح"); return
    val = int(txt); target = st['target']
    if target in Gq:
        Gq[target]["points"] = Gq[target].get("points",0) + val
        save_json(G1, Gq)
        send_h(uid, f"✅ شحن {val} نقطة\nنقاطه الآن : {Gq[target].get('points',0)}")
        try: force_send(int(target), f"🎁 <b>تم شحن {val} نقطة</b>")
        except: pass
    charge_state.pop(uid, None); clear_user_state(uid)

def do_broadcast(m):
    if not m.text: return
    c = 0
    for u in list(Gq.keys()):
        try: golden.send_message(int(u), m.text); c += 1; time.sleep(0.05)
        except: pass
    send_h(G8, f"✅ تم الإرسال لـ {c}")

def do_ban(m):
    txt = (m.text or "").strip()
    if not txt.isdigit(): error_restart(G8, "ID غير صحيح"); return
    if txt not in Gu: Gu.append(txt); save_black(Gu)
    send_h(G8, f"✅ تم حظر {txt}")

def do_unban(m):
    txt = (m.text or "").strip()
    if not txt.isdigit(): error_restart(G8, "ID غير صحيح"); return
    if txt in Gu: Gu.remove(txt); save_black(Gu)
    send_h(G8, f"✅ تم فك الحظر")

def ags_points_step(m):
    txt = (m.text or "").strip()
    if not txt.isdigit(): error_restart(G8, "رقم غير صحيح"); return
    config["daily_gift_points"] = int(txt); save_json(CONFIG_FILE, config)
    send_h(G8, "✅")

def ags_cooldown_step(m):
    txt = (m.text or "").strip()
    if not txt.isdigit(): error_restart(G8, "رقم غير صحيح"); return
    config["daily_gift_cooldown"] = int(txt) * 3600; save_json(CONFIG_FILE, config)
    send_h(G8, "✅")

def ars_reward_step(m):
    txt = (m.text or "").strip()
    if not txt.isdigit(): error_restart(G8, "رقم غير صحيح"); return
    config["referral_reward"] = int(txt); save_json(CONFIG_FILE, config)
    send_h(G8, "✅")

def set_act_ch(m):
    ch = (m.text or "").strip()
    if not ch: error_restart(G8, "أرسل ID"); return
    config["activation_channel"] = ch; save_json(CONFIG_FILE, config)
    try:
        golden.send_message(ch, "✅ اختبار")
        send_h(G8, f"✅ {ch}")
    except Exception as e: send_h(G8, f"⚠️ {str(e)[:150]}")

threading.Thread(target=monitor_channel_orders, daemon=True).start()

print("=" * 50)
print("✅ البوت شغال...")
print(f"👥 المستخدمين: {Gr.get('total_users',0)}")
print(f"⚡ الطلبات: {Gr.get('total_requests',0)}")
print(f"📦 الخدمات: {len(SERVICES)}")
print(f"📢 قنوات النقاط: {len(config.get('channel_rewards',[]))}")
print(f"🚀 المزودين: {len(config.get('providers',{}))}")
print(f"🔑 الأدمن: {G8}")
print(f"👁 مراقبة القنوات: ✅ كل دقيقة")
print("=" * 50)

while True:
    try:
        golden.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"Polling: {e}"); time.sleep(5)