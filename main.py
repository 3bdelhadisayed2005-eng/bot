import telebot
import requests
import threading
import time
import os
import random
import string
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- ⚠️ إعدادات البوت الأساسية ---
BOT_TOKEN = "8079896033:AAGC8LigHHqLLK1uc8mJDVyRAw8_7eosLzk"      # توكن البوت الخاص بك من BotFather
ADMIN_ID = 7087179945                # الـ ID بتاعك كمدير للبوت 👑

# 🔑 بيانات الحسابات الثلاثة لموقع Durian 
DURIAN_ACCOUNTS = [
    ["3bdelhadisayed", "N3BIVTV2OWxheFFYenpFL0NrbW45Zz09"],

    ["Abdelhadi2005", "RStqT2cvR2dMMTNPVVFaMU9DYXdQdz09"]
]
# -----------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

BALANCES_FILE = "balances.txt"
SETTINGS_FILE = "settings.txt"
PROMOS_FILE = "promos.txt"
ORDERS_FILE = "orders.txt"
PRICES_FILE = "prices.txt"
BANNED_FILE = "banned.txt"
REFERRALS_FILE = "referrals.txt"

USER_BALANCES = {}
SETTINGS = {
    "rate": 50.0, 
    "wallet": "010xxxxxxx", 
    "binance_id": "123456789", 
    "pid": "0257", 
    "support": "https://t.me/YourSupportUsername",
    "channel_user": "@YourChannelUsername", 
    "channel_url": "https://t.me/YourChannelUsername", 
    "ref_reward": 0.01 
}
PROMO_CODES = {}
USER_ORDERS = {}
BANNED_USERS = set()
USED_REFERRALS = set()

SYSTEM_STATS = {"total_sales": 0.0, "successful_orders": 0, "failed_orders": 0}

ALL_COUNTRIES = {
    "مصر": {"code": "eg", "price": 0.25, "flag": "🇪🇬"}, "روسيا": {"code": "ru", "price": 0.25, "flag": "🇷🇺"},
    "أمريكا": {"code": "us", "price": 0.25, "flag": "🇺🇸"}, "الهند": {"code": "in", "price": 0.25, "flag": "🇮🇳"},
    "تونس": {"code": "tn", "price": 0.25, "flag": "🇹🇳"}, "الأرجنتين": {"code": "ar", "price": 0.25, "flag": "🇦🇷"},
    "الجزائر": {"code": "dz", "price": 0.25, "flag": "🇩🇿"}, "ليبيا": {"code": "ly", "price": 0.25, "flag": "🇱🇾"},
    "سوريا": {"code": "sy", "price": 0.25, "flag": "🇸🇾"}, "الأردن": {"code": "jo", "price": 0.25, "flag": "🇯🇴"},
    "الإمارات": {"code": "ae", "price": 0.25, "flag": "🇦🇪"}, "جنوب إفريقيا": {"code": "tz", "price": 0.25, "flag": "🇿🇦"},
    "نيجيريا": {"code": "ng", "price": 0.25, "flag": "🇳🇬"}, "تايلاند": {"code": "th", "price": 0.25, "flag": "🇹🇭"},
    "المكسيك": {"code": "mx", "price": 0.25, "flag": "🇲🇽"}, "باكستان": {"code": "pk", "price": 0.25, "flag": "🇵🇰"},
    "موريتانيا": {"code": "mr", "price": 0.25, "flag": "🇲🇷"}, "الكونغو الديمقراطية": {"code": "cd", "price": 0.25, "flag": "🇨🇩"},
    "أنغولا": {"code": "ao", "price": 0.25, "flag": "🇦🇴"}, "أفغانستان": {"code": "af", "price": 0.25, "flag": "🇦🇫"},
    "تنزانيا": {"code": "tz", "price": 0.25, "flag": "🇹🇿"}, "جمهورية الدومينيكان": {"code": "do", "price": 0.25, "flag": "🇩🇴"},
    "موزمبيق": {"code": "mz", "price": 0.25, "flag": "🇲🇿"}, "الكاميرون": {"code": "cm", "price": 0.25, "flag": "🇨🇲"},
    "السنغال": {"code": "sn", "price": 0.25, "flag": "🇸🇳"}, "كينيا": {"code": "ke", "price": 0.25, "flag": "🇰🇪"},
    "الكونغو": {"code": "cg", "price": 0.25, "flag": "🇨🇬"}, "الفلبين": {"code": "ph", "price": 0.25, "flag": "🇵🇭"},
    "أوغندا": {"code": "ug", "price": 0.25, "flag": "🇺🇬"}, "زامبيا": {"code": "zm", "price": 0.25, "flag": "🇿🇲"},
    "توغو": {"code": "tg", "price": 0.25, "flag": "🇹🇬"}, "كمبوديا": {"code": "kh", "price": 0.25, "flag": "🇰🇭"},
    "بوركينا فاسو": {"code": "bf", "price": 0.25, "flag": "🇧🇫"}, "هايتي": {"code": "ht", "price": 0.25, "flag": "🇭🇹"},
    "مالاوي": {"code": "mw", "price": 0.25, "flag": "🇲🇼"}, "إثيوبيا": {"code": "et", "price": 0.25, "flag": "🇪🇹"},
    "فرنسا": {"code": "fr", "price": 0.25, "flag": "🇫🇷"}, "بورتوريكو": {"code": "pr", "price": 0.25, "flag": "🇵🇷"},
    "فيجي": {"code": "fj", "price": 0.25, "flag": "🇫🇯"}, "أستراليا": {"code": "au", "price": 0.25, "flag": "🇦🇺"},
    "سلوفاكيا": {"code": "sk", "price": 0.25, "flag": "🇸🇰"}, "إسبانيا": {"code": "es", "price": 0.25, "flag": "🇪🇸"},
    "ألمانيا": {"code": "de", "price": 0.25, "flag": "🇩🇪"}
}

user_hunting_targets = {}
hunting_active = False
active_hunted_numbers = {}
admin_state = {}
USER_PURCHASE_COOLDOWN = {}

def load_all_data():
    global USER_BALANCES, SETTINGS, PROMO_CODES, USER_ORDERS, ALL_COUNTRIES, BANNED_USERS, SYSTEM_STATS, USED_REFERRALS
    if os.path.exists(BALANCES_FILE):
        try:
            with open(BALANCES_FILE, "r") as f:
                for line in f:
                    if ":" in line: u_id, bal = line.strip().split(":"); USER_BALANCES[int(u_id)] = float(bal)
        except: pass
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                for line in f:
                    if "=" in line: 
                        k, v = line.strip().split("=")
                        SETTINGS[k] = float(v) if k in ["rate", "ref_reward"] else v
        except: pass
    if os.path.exists(PROMOS_FILE):
        try:
            with open(PROMOS_FILE, "r") as f:
                for line in f:
                    if ":" in line: code, val = line.strip().split(":"); PROMO_CODES[code] = float(val)
        except: pass
    if os.path.exists(BANNED_FILE):
        try:
            with open(BANNED_FILE, "r") as f:
                for line in f: BANNED_USERS.add(int(line.strip()))
        except: pass
    if os.path.exists(REFERRALS_FILE):
        try:
            with open(REFERRALS_FILE, "r") as f:
                for line in f: USED_REFERRALS.add(int(line.strip()))
        except: pass
    if os.path.exists(PRICES_FILE):
        try:
            with open(PRICES_FILE, "r") as f:
                for line in f:
                    if ":" in line: c_name, pr = line.strip().split(":"); 
                    if c_name in ALL_COUNTRIES: ALL_COUNTRIES[c_name]["price"] = float(pr)
        except: pass
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r") as f:
                for line in f:
                    if "||" in line:
                        u_id, text = line.strip().split("||", 1); u_id = int(u_id);
                        if u_id not in USER_ORDERS: USER_ORDERS[u_id] = []
                        USER_ORDERS[u_id].append(text)
                        SYSTEM_STATS["successful_orders"] += 1
                        try:
                            price_part = text.split("سعر: ")[1].replace("$", "")
                            SYSTEM_STATS["total_sales"] += float(price_part)
                        except: pass
        except: pass

def save_data(mode):
    try:
        if mode == "balances":
            with open(BALANCES_FILE, "w") as f:
                for u_id, bal in USER_BALANCES.items(): f.write(f"{u_id}:{bal}\n")
        elif mode == "settings":
            with open(SETTINGS_FILE, "w") as f:
                for k, v in SETTINGS.items(): f.write(f"{k}={v}\n")
        elif mode == "promos":
            with open(PROMOS_FILE, "w") as f:
                for code, val in PROMO_CODES.items(): f.write(f"{code}:{val}\n")
        elif mode == "banned":
            with open(BANNED_FILE, "w") as f:
                for u_id in BANNED_USERS: f.write(f"{u_id}\n")
        elif mode == "referrals":
            with open(REFERRALS_FILE, "w") as f:
                for u_id in USED_REFERRALS: f.write(f"{u_id}\n")
        elif mode == "prices":
            with open(PRICES_FILE, "w") as f:
                for c_name, info in ALL_COUNTRIES.items(): f.write(f"{c_name}:{info['price']}\n")
    except: pass

def log_order(user_id, order_text):
    if user_id not in USER_ORDERS: USER_ORDERS[user_id] = []
    USER_ORDERS[user_id].append(order_text)
    try:
        with open(ORDERS_FILE, "a") as f: f.write(f"{user_id}||{order_text}\n")
    except: pass

load_all_data()

def get_user_balance(user_id):
    if user_id not in USER_BALANCES: 
        USER_BALANCES[user_id] = 0.00
        save_data("balances")
    return USER_BALANCES[user_id]

def get_country_info_by_code(code):
    for name, info in ALL_COUNTRIES.items():
        if info["code"] == code: return name, info["price"], info["flag"]
    return f"دولة ({code})", 0.25, "🌍"

def check_user_joined_channel(user_id):
    if user_id == ADMIN_ID: return True
    if "YourChannelUsername" in SETTINGS["channel_user"]: return True
    try:
        member = bot.get_chat_member(SETTINGS["channel_user"], user_id)
        if member.status in ['member', 'creator', 'administrator']: return True
    except: pass
    return False

def get_force_join_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📢 اشترك في القناة من هنا أولاً 📢", url=SETTINGS["channel_url"]),
        InlineKeyboardButton("🔄 ✅ تحقق من الاشتراك الحين", callback_data="check_join_btn")
    )
    return markup

def get_admin_dashboard_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("💰 شحن رصيد لزبون", callback_data="admin_add_balance"), InlineKeyboardButton("➖ سحب رصيد", callback_data="admin_sub_balance"))
    markup.add(InlineKeyboardButton("⚙️ تعديل الكاش والسعر", callback_data="admin_set_vars"), InlineKeyboardButton("🎫 توليد كود شحن", callback_data="admin_gen_promo"))
    markup.add(InlineKeyboardButton("🌍 تعديل سعر دولة", callback_data="admin_set_country_price"), InlineKeyboardButton("📊 تعديل جماعي للأسعار", callback_data="admin_mass_price"))
    markup.add(InlineKeyboardButton("👥 إدارة زبون معين", callback_data="admin_manage_user"), InlineKeyboardButton("📢 إذاعة رسالة برودكاست", callback_data="admin_broadcast"))
    markup.add(InlineKeyboardButton("🔄 تنظيف الذاكرة والتعليق", callback_data="admin_clear_cache"), InlineKeyboardButton("🔄 تحديث لوحة التحكم", callback_data="admin_refresh_stats"))
    return markup

def get_admin_vars_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"📱 رقم الكاش الحالي ({SETTINGS['wallet']})", callback_data="edit_wallet"),
        InlineKeyboardButton(f"💵 سعر الدولار الحالي ({SETTINGS['rate']} ج.م)", callback_data="edit_rate"),
        InlineKeyboardButton(f"🪙 بايننس باي ID الحالي ({SETTINGS['binance_id']})", callback_data="edit_binance"),
        InlineKeyboardButton(f"🎯 كود المشروع الحالى ({SETTINGS['pid']})", callback_data="edit_pid"),
        InlineKeyboardButton(f"📢 يوزر القناة الإلزامية ({SETTINGS['channel_user']})", callback_data="edit_chuser"),
        InlineKeyboardButton(f"🔗 رابط القناة الإلزامية", callback_data="edit_churl"),
        InlineKeyboardButton(f"🎁 هدية الإحالة الحالية ({SETTINGS['ref_reward']}$)", callback_data="edit_refreward"),
        InlineKeyboardButton(f"👨‍💻 يوزر الدعم الحالي", callback_data="edit_support"),
        InlineKeyboardButton("🔙 عودة للوحة الإدارة", callback_data="admin_back_main")
    )
    return markup

def get_user_manage_keyboard(target_id):
    markup = InlineKeyboardMarkup(row_width=2)
    ban_status = "🔴 حظر الزبون" if target_id not in BANNED_USERS else "🟢 فك الحظر عنه"
    markup.add(InlineKeyboardButton(ban_status, callback_data=f"banuser_{target_id}"))
    markup.add(InlineKeyboardButton("🔄 تصفير محفظته", callback_data=f"clearbal_{target_id}"))
    markup.add(InlineKeyboardButton("🔙 عودة", callback_data="admin_back_main"))
    return markup

def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🎯 تفعيل الصيد التلقائي", callback_data="manage_hunting"))
    markup.add(InlineKeyboardButton("💰 إيداع / شحن", callback_data="deposit"), InlineKeyboardButton("📋 أرقامي المشتراة", callback_data="user_orders"))
    markup.add(InlineKeyboardButton("👥 رابط الإحالة والربح", callback_data="user_referral"), InlineKeyboardButton("🎫 شحن كود هدية", callback_data="user_redeem_promo"))
    markup.add(InlineKeyboardButton("👨‍💻 التواصل مع الدعم", url=SETTINGS["support"]))
    return markup

def get_countries_keyboard(user_id, page=0):
    markup = InlineKeyboardMarkup(row_width=2)
    user_targets = user_hunting_targets.get(user_id, [])
    items = list(ALL_COUNTRIES.items())
    per_page = 10  
    start = page * per_page
    end = start + per_page
    
    for name, info in items[start:end]:
        code = info["code"]
        status = " 🎯 [جاري]" if code in user_targets else ""
        markup.add(InlineKeyboardButton(f"{info['flag']} {name}{status}", callback_data=f"hunt_{code}_{page}"))
        
    nav = []
    if page > 0: nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"hpage_{page-1}"))
    if end < len(items): nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"hpage_{page+1}"))
    if nav: markup.row(*nav)
    markup.add(InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main"))
    return markup

def get_deposit_methods_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📱 شحن عبر فودافون كاش (مصر)", callback_data="dep_vodafone"),
        InlineKeyboardButton("🪙 شحن عبر Binance Pay (عالمي)", callback_data="dep_binance"),
        InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        bot.send_message(message.chat.id, "❌ **عذراً، لقد تم حظرك من استخدام البوت من قبل الإدارة.**")
        return

    start_args = message.text.split()
    if len(start_args) > 1 and user_id != ADMIN_ID:
        try:
            inviter_id = int(start_args[1].strip())
            if inviter_id != user_id and user_id not in USER_BALANCES and user_id not in USED_REFERRALS:
                reward = SETTINGS["ref_reward"]
                if reward > 0:
                    if inviter_id not in USER_BALANCES: USER_BALANCES[inviter_id] = 0.00
                    USER_BALANCES[inviter_id] += reward
                    save_data("balances")
                    USED_REFERRALS.add(user_id)
                    save_data("referrals")
                    try: bot.send_message(inviter_id, f"🎉 <b>دخل زبون جديد عبر رابط إحالتك!</b>\n💰 المكافأة: <b>+{reward}$</b>")
                    except: pass
        except: pass

    if not check_user_joined_channel(user_id):
        bot.send_message(message.chat.id, f"⚠️ <b>يجب الاشتراك في قناة البوت الرسمية أولاً لتفعيل الحساب!</b>", reply_markup=get_force_join_keyboard(), parse_mode="HTML")
        return
        
    if user_id == ADMIN_ID:
        admin_text = (
            f"👑 <b>مرحباً بك يا مدير في لوحة التحكم الإدارية الفائقة</b>\n\n"
            f"📊 <b>إحصائيات السيستم التراكمية والحية:</b>\n"
            f"• إجمالي الزبائن: <code>{len(USER_BALANCES)}</code>\n"
            f"• إجمالي أرصدة الزبائن: <code>{sum(USER_BALANCES.values()):.2f} $</code>\n"
            f"• مبيعات البوت الناجحة: <code>{SYSTEM_STATS['total_sales']:.2f} $</code>\n"
            f"• عدد الأرقام المباعة: <code>{SYSTEM_STATS['successful_orders']} رقم</code>\n"
            f"• محاولات حجز ملغية/فاشلة: <code>{SYSTEM_STATS['failed_orders']} محاولة</code>"
        )
        bot.send_message(message.chat.id, admin_text, reply_markup=get_admin_dashboard_keyboard(), parse_mode="HTML")
    else:
        welcome_text = f"• <u><b>🕸️ 𝕊ℙ𝓘𝓓𝓔𝓡 𝕊𝕄𝕊 🕷️ - Auto Hunting Bot</b></u> •\n\n💰 <b>رصيدك الحالي:</b> {get_user_balance(user_id):.2f} $\n\n🆔 الـ ID الخاص بك: <code>{user_id}</code>"
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    if user_id in BANNED_USERS and user_id != ADMIN_ID: return

    if call.data == "check_join_btn":
        if check_user_joined_channel(user_id):
            bot.answer_callback_query(call.id, "✅ تم تفعيل حسابك بنجاح!", show_alert=True)
            welcome_text = f"• <u><b>🕸️ 𝕊ℙ𝓘𝓓𝓔𝓡 𝕊𝕄𝕊 🕷️ - Auto Hunting Bot</b></u> •\n\n💰 <b>رصيدك الحالي:</b> {get_user_balance(user_id):.2f} $\n\n🆔 الـ ID الخاص بك: <code>{user_id}</code>"
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id, text=welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, "❌ لسه مشركتش يا غالي! اشترك الحين.", show_alert=True)
        return

    if not check_user_joined_channel(user_id) and user_id != ADMIN_ID: return

    if user_id == ADMIN_ID:
        if call.data == "admin_back_main":
            bot.answer_callback_query(call.id)
            admin_text = (
                f"👑 <b>مرحباً بك يا مدير في لوحة التحكم الإدارية الفائقة</b>\n\n"
                f"📊 <b>إحصائيات حية:</b>\n"
                f"• إجمالي الزبائن: <code>{len(USER_BALANCES)}</code>\n"
                f"• إجمالي الأرصدة: <code>{sum(USER_BALANCES.values()):.2f} $</code>\n"
                f"• مبيعات البوت: <code>{SYSTEM_STATS['total_sales']:.2f} $</code>"
            )
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id, text=admin_text, reply_markup=get_admin_dashboard_keyboard(), parse_mode="HTML")
            return
        elif call.data == "admin_clear_cache":
            global active_hunted_numbers
            active_hunted_numbers.clear()
            bot.answer_callback_query(call.id, "🔄 تم تنظيف الذاكرة!", show_alert=True)
            return
        elif call.data == "admin_set_vars":
            bot.answer_callback_query(call.id)
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id, text="⚙️ **إعدادات ومغيرات السيستم من التليجرام:**", reply_markup=get_admin_vars_keyboard(), parse_mode="Markdown")
            return
        elif call.data in ["edit_wallet", "edit_rate", "edit_binance", "edit_pid", "edit_chuser", "edit_churl", "edit_refreward", "edit_support"]:
            bot.answer_callback_query(call.id)
            admin_state[user_id] = {"mode": "edit_var", "var": call.data.replace("edit_", "")}
            bot.send_message(user_id, "✍️ أرسل القيمة الجديدة الآن:")
            return
        elif call.data == "admin_add_balance":
            msg = bot.send_message(user_id, "✍️ أرسل **ID حساب الزبون** للشحن:")
            bot.register_next_step_handler(msg, process_admin_target_id, "add")
            return
        elif call.data == "admin_sub_balance":
            msg = bot.send_message(user_id, "✍️ أرسل **ID حساب الزبون** للخصم:")
            bot.register_next_step_handler(msg, process_admin_target_id, "sub")
            return
        elif call.data == "admin_gen_promo":
            bot.answer_callback_query(call.id)
            admin_state[user_id] = {"mode": "gen_promo"}
            bot.send_message(user_id, "✍️ أدخل قيمة كود الشحن بالدولار:")
            return
        elif call.data == "admin_mass_price":
            bot.answer_callback_query(call.id)
            admin_state[user_id] = {"mode": "mass_price"}
            bot.send_message(user_id, "✍️ أدخل السعر الموحد الجديد لجميع الدول:")
            return
        elif call.data == "admin_manage_user":
            bot.answer_callback_query(call.id)
            admin_state[user_id] = {"mode": "query_user"}
            bot.send_message(user_id, "✍️ أرسل الـ ID الخاص بالزبون:")
            return
        elif call.data.startswith("banuser_"):
            t_id = int(call.data.split("_")[1])
            if t_id in BANNED_USERS: BANNED_USERS.remove(t_id); bot.answer_callback_query(call.id, "🟢 تم فك الحظر")
            else: BANNED_USERS.add(t_id); bot.answer_callback_query(call.id, "🔴 تم حظر الزبون")
            save_data("banned")
            return
        elif call.data.startswith("clearbal_"):
            t_id = int(call.data.split("_")[1])
            USER_BALANCES[t_id] = 0.00
            save_data("balances")
            bot.answer_callback_query(call.id, "🔄 تم تصفير المحفظة", show_alert=True)
            return
        elif call.data == "admin_set_country_price":
            bot.answer_callback_query(call.id)
            admin_state[user_id] = {"mode": "set_country_select"}
            bot.send_message(user_id, "✍️ اكتب اسم الدولة بالظبط:")
            return
        elif call.data == "admin_broadcast":
            msg = bot.send_message(user_id, "📢 اكتب رسالة البرودكاست لإذاعتها:")
            bot.register_next_step_handler(msg, process_admin_broadcast)
            return
        elif call.data == "admin_refresh_stats":
            bot.answer_callback_query(call.id)
            admin_text = (
                f"👑 <b>لوحة التحكم المحدثة الفائقة</b>\n\n"
                f"📊 <b>إحصائيات حية:</b>\n"
                f"• إجمالي الزبائن: <code>{len(USER_BALANCES)}</code>\n"
                f"• إجمالي الأرصدة: <code>{sum(USER_BALANCES.values()):.2f} $</code>"
            )
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id, text=admin_text, reply_markup=get_admin_dashboard_keyboard(), parse_mode="HTML")
            return

    if call.data == "manage_hunting":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="🌍 **قسم الصيد التلقائي لأرقام التليجرام:**", reply_markup=get_countries_keyboard(user_id, page=0), parse_mode="Markdown")
        return
    elif call.data.startswith("hpage_"):
        bot.answer_callback_query(call.id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=get_countries_keyboard(user_id, page=int(call.data.split("_")[1])))
        return
    elif call.data.startswith("hunt_"):
        parts = call.data.split("_")
        code, page = parts[1], int(parts[2])
        if user_id not in user_hunting_targets: user_hunting_targets[user_id] = []
        name, price, _ = get_country_info_by_code(code)
        
        if code not in user_hunting_targets[user_id] and get_user_balance(user_id) <= 0:
            bot.answer_callback_query(call.id, "❌ محفظتك فارغة!", show_alert=True)
            return
        if code in user_hunting_targets[user_id]:
            user_hunting_targets[user_id].remove(code)
            bot.answer_callback_query(call.id, f"🛑 تم إيقاف صيد {name}")
        else:
            user_hunting_targets[user_id].append(code)
            bot.answer_callback_query(call.id, f"🎯 تم تفعيل صيد {name}")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=get_countries_keyboard(user_id, page=page))
        return

    elif call.data == "user_referral":
        bot.answer_callback_query(call.id)
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        ref_text = f"👥 <b>برنامج إحالة وربح رصيد مجاني</b>\n\n🔗 <code>{ref_link}</code>\n\n💰 ستحصل على <b>{SETTINGS['ref_reward']:.2f}$</b> لكل صديق جديد يشترك!"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=user_id, message_id=call.message.id, text=ref_text, reply_markup=markup, parse_mode="HTML")
        return

    elif call.data == "deposit":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="💳 **الرجاء اختيار طريقة الإيداع المناسبة لك للشحن:**", reply_markup=get_deposit_methods_keyboard(), parse_mode="Markdown")
        return

    elif call.data == "dep_vodafone":
        bot.answer_callback_query(call.id)
        deposit_text = f"📱 <b>شحن الرصيد عبر فودافون كاش</b>\n\n📱 رقم الكاش: <code>{SETTINGS['wallet']}</code>\n💵 الحسبة: 1$ = {SETTINGS['rate']} جنيه."
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 عودة", callback_data="deposit"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=deposit_text, reply_markup=markup, parse_mode="HTML")
        return

    elif call.data == "dep_binance":
        bot.answer_callback_query(call.id)
        binance_text = f"🪙 <b>شحن الرصيد عبر Binance Pay</b>\n\n🆔 معرف بايننس: <code>{SETTINGS['binance_id']}</code>"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 عودة", callback_data="deposit"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=binance_text, reply_markup=markup, parse_mode="HTML")
        return

    elif call.data == "user_redeem_promo":
        bot.answer_callback_query(call.id)
        admin_state[user_id] = {"mode": "redeem_promo"}
        bot.send_message(user_id, "🎫 أدخل كود الهدية الخاص بك هنا:")
        return

    elif call.data == "user_orders":
        bot.answer_callback_query(call.id)
        orders = USER_ORDERS.get(user_id, [])
        if not orders: bot.send_message(user_id, "📋 ليس لديك أرقام مشتراة.")
        else:
            text = "📋 **سجل أرقامك المشتراة السابقة:**\n\n" + "\n\n".join(orders[-10:])
            bot.send_message(user_id, text)
        return

    elif call.data == "back_to_main":
        bot.answer_callback_query(call.id)
        welcome_text = f"• <u><b>🕸️ 𝕊ℙ𝓘𝓓𝓔𝓡 𝕊𝕄𝕊 🕷️ - Auto Hunting Bot</b></u> •\n\n💰 <b>رصيدك الحالي:</b> {get_user_balance(user_id):.2f} $\n\n🆔 الـ ID الخاص بك: <code>{user_id}</code>"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
        return
    
    elif call.data.startswith("claim_"):
        current_time = time.time()
        last_purchase_time = USER_PURCHASE_COOLDOWN.get(user_id, 0)
        
        # ⏱️ الحظر الفوري للإسبام: الزبون مجبر ينتظر 5 ثوانٍ بين محاولات حجز الأرقام
        if current_time - last_purchase_time < 5:
            bot.answer_callback_query(call.id, "⚠️ يرجى الانتظار 5 ثوانٍ بين محاولات الشراء.", show_alert=True)
            return

        parts = call.data.split("_")
        phone = parts[1]
        acc_index = int(parts[2])
        
        if phone in active_hunted_numbers:
            target_info = active_hunted_numbers[phone]
            price = float(target_info['price'])
            
            # 💸 التعديل الأمني: نتحقق من رصيده أولاً، لكن لا نخصم شيئاً الحين!
            if get_user_balance(user_id) >= price:
                USER_PURCHASE_COOLDOWN[user_id] = current_time
                del active_hunted_numbers[phone]
                
                bot.answer_callback_query(call.id, "🔄 جاري التأمين وبدء الفحص...")
                
                loading_markup = InlineKeyboardMarkup()
                loading_markup.add(InlineKeyboardButton("10%", callback_data="none"))
                bot.edit_message_text(
                    chat_id=user_id, 
                    message_id=call.message.id, 
                    text=f"🔄 <b>جاري فحص وحجز الرقم من السيرفر الصيني...</b>\n📱 الرقم: <code>[ جاري التأمين... * * * * * * * * * ]</code>", 
                    reply_markup=loading_markup, 
                    parse_mode="HTML"
                )
                
                threading.Thread(target=wait_for_sms, args=(user_id, phone, price, acc_index, call.message.id, target_info['country'], target_info['flag'])).start()
            else:
                bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ الرقم تم بيعه أو انتهت صلاحيته!", show_alert=True)

# --- ⚙️ معالجة الرسائل النصية المصلحة من أخطاء الـ Syntax بالملي الحين جوة السيستم ---
@bot.message_handler(func=lambda msg: msg.from_user.id in admin_state)
def handle_states(message):
    user_id = message.from_user.id
    state = admin_state[user_id]
    text = message.text.strip()
    
    if state.get("mode") == "edit_var":
        var = state["var"]
        if var == "rate": SETTINGS["rate"] = float(text)
        elif var == "wallet": SETTINGS["wallet"] = text
        elif var == "binance": SETTINGS["binance_id"] = text
        elif var == "pid": SETTINGS["pid"] = text
        elif var == "chuser": SETTINGS["channel_user"] = text
        elif var == "churl": SETTINGS["channel_url"] = text
        elif var == "refreward": SETTINGS["ref_reward"] = float(text)
        elif var == "support": SETTINGS["support"] = text
        save_data("settings")
        bot.send_message(user_id, f"✅ تم تحديث {var} بنجاح الحين!")
        del admin_state[user_id]
        
    elif state.get("mode") == "gen_promo":
        try:
            val = float(text)
            code = "PULSE-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            PROMO_CODES[code] = val
            save_data("promos")
            bot.send_message(user_id, f"🎫 **تم توليد كود الشحن بنجاح:**\n\n`{code}`\n\n💰 قيمته: **{val}$**")
        except: bot.send_message(user_id, "❌ قيمة غير صحيحة.")
        del admin_state[user_id]
        
    elif state.get("mode") == "mass_price":
        try:
            new_pr = float(text)
            for c_name in ALL_COUNTRIES: ALL_COUNTRIES[c_name]["price"] = new_pr
            save_data("prices")
            bot.send_message(user_id, f"✅ تم تحديث أسعار الدول لتكون موحدة: **{new_pr}$**!")
        except: bot.send_message(user_id, "❌ القيمة غير صحيحة.")
        del admin_state[user_id]
        
    elif state.get("mode") == "query_user":
        try:
            t_id = int(text)
            t_bal = get_user_balance(t_id)
            ban_text = "⚠️ محظور" if t_id in BANNED_USERS else "🟢 نشط"
            info_msg = f"👤 **بيانات حساب الزبون:**\n\n• رصيده الحالى: **{t_bal:.2f} $**\n• حالة الحساب: **{ban_text}**"
            bot.send_message(user_id, info_msg, reply_markup=get_user_manage_keyboard(t_id))
        except: bot.send_message(user_id, "❌ الـ ID غير صحيح.")
        del admin_state[user_id]
        
    elif state.get("mode") == "set_country_select":
        if text in ALL_COUNTRIES:
            admin_state[user_id] = {"mode": "set_country_price_val", "c_name": text}
            bot.send_message(user_id, f"💰 أدخل السعر الجديد لدولة {text} بالدولار:")
        else:
            bot.send_message(user_id, "❌ اسم الدولة غير موجود.")
            del admin_state[user_id]
            
    elif state.get("mode") == "set_country_price_val":
        try:
            pr = float(text)
            c_name = state["c_name"]
            ALL_COUNTRIES[c_name]["price"] = pr
            save_data("prices")
            bot.send_message(user_id, f"✅ تم تغيير سعر دولة **{c_name}** بنجاح إلى **{pr}$**!")
        except: bot.send_message(user_id, "❌ قيمة السعر غير صحيحة.")
        del admin_state[user_id]
        
    elif state.get("mode") == "redeem_promo":
        if text in PROMO_CODES:
            val = PROMO_CODES[text]
            if user_id not in USER_BALANCES: USER_BALANCES[user_id] = 0.00
            USER_BALANCES[user_id] += val
            del PROMO_CODES[text]
            save_data("promos")
            save_data("balances")
            bot.send_message(user_id, f"🎉 **تم شحن الكود بنجاح!**\n💰 أُضيف إلى محفظتك: **+{val}$**")
        else: bot.send_message(user_id, "❌ كود غير صحيح أو مستخدم.")
        del admin_state[user_id]

def release_bad_number(phone_number, acc_index):
    acc = DURIAN_ACCOUNTS[acc_index]
    try:
        url = f"https://api.durianrcs.com/out/ext_api/cancelMobile?name={acc[0]}&ApiKey={acc[1]}&pn={phone_number}&pid={str(SETTINGS['pid'])}&serial=2"
        requests.get(url, timeout=5)
    except: pass

def is_number_banned_on_telegram(phone_number, acc_index):
    acc = DURIAN_ACCOUNTS[acc_index]
    try:
        check_url = f"https://api.durianrcs.com/out/ext_api/getMsg?name={acc[0]}&ApiKey={acc[1]}&pn={phone_number}&pid={str(SETTINGS['pid'])}&serial=2"
        res = requests.get(check_url, timeout=4).json()
        res_str = str(res).lower()
        if res.get("code") == 905 or "block" in res_str or "ban" in res_str or "password" in res_str or "verify" in res_str or "email" in res_str:
            return True
    except: pass
    return False

def global_auto_buyer():
    global hunting_active
    hunting_active = True
    while hunting_active:
        for u_id, targets_list in list(user_hunting_targets.items()):
            if get_user_balance(u_id) <= 0 and len(targets_list) > 0:
                user_hunting_targets[u_id] = []
                try: bot.send_message(u_id, f"🛑 **تم إيقاف الصيد التلقائي لجميع الدول لأن رصيدك انتهى!**")
                except: pass

        active_codes = set()
        for targets_list in user_hunting_targets.values():
            for target_code in targets_list: active_codes.add(target_code)
                
        if not active_codes:
            time.sleep(1)
            continue

        for c_name, c_info in list(ALL_COUNTRIES.items()):
            country_code = c_info["code"]
            if country_code not in active_codes: continue
            
            for idx, acc in enumerate(DURIAN_ACCOUNTS):
                if "اسم_الحساب" in acc[0] or "مفتاح_API" in acc[1]: continue
                try:
                    url = f"https://api.durianrcs.com/out/ext_api/getMobile?name={acc[0]}&ApiKey={acc[1]}&cuy={country_code}&pid={str(SETTINGS['pid'])}&num=1&noblack=1&serial=2"
                    response = requests.get(url, timeout=4)
                    
                    if response.status_code == 200:
                        res_json = response.json()
                        if res_json.get("code") == 200:
                            phone_number = res_json.get("data")
                            
                            if is_number_banned_on_telegram(phone_number, idx):
                                release_bad_number(phone_number, idx)
                                continue
                                
                            price = c_info["price"]
                            flag = c_info["flag"]
                            active_hunted_numbers[phone_number] = {"country": c_name, "flag": flag, "price": price}
                            
                            for u_id, targets_list in list(user_hunting_targets.items()):
                                if u_id not in BANNED_USERS and check_user_joined_channel(u_id) and country_code in targets_list and get_user_balance(u_id) > 0:
                                    markup = InlineKeyboardMarkup()
                                    markup.add(InlineKeyboardButton("🛒 شراء الآن", callback_data=f"claim_{phone_number}_{idx}"))
                                    formatted_msg = f"🥳 🎰 <b>الدولة متاحة الآن</b>\n\n{flag} {c_name}\n✅ رقم جاهز وفريش تماماً!\n💰 سعر الشراء: <b>${price:.2f}</b>\n\n🛒 اضغط شراء الآن لحجزه فوراً"
                                    bot.send_message(u_id, formatted_msg, reply_markup=markup, parse_mode="HTML")
                            break
                except: pass
                time.sleep(0.5)
            time.sleep(0.5)

# ⏱️ ⚡ دالة الفحص الذكية المعدلة: الخصم التلقائي والفعلي للرصيد يحصل بعد وصول كود الـ SMS بنجاح فقط! الحين مقفلة 🔒📌
def wait_for_sms(user_id, phone_number, price, acc_index, status_msg_id, c_name, flag):
    acc = DURIAN_ACCOUNTS[acc_index]
    sms_url = f"https://api.durianrcs.com/out/ext_api/getMsg?name={acc[0]}&ApiKey={acc[1]}&pn={phone_number}&pid={str(SETTINGS['pid'])}&serial=2"
    
    loading_steps = ["10%", "30%", "60%", "90%", "100%"]
    for step in loading_steps:
        try:
            progress_markup = InlineKeyboardMarkup()
            progress_markup.add(InlineKeyboardButton(f"{step}", callback_data="none"))
            timer_text = f"🔄 <b>جاري تجهيز الخط... {step}</b>\n📱 الرقم: <code>[ جاري التأمين... * * * * * * * * * ]</code>"
            bot.edit_message_text(chat_id=user_id, message_id=status_msg_id, text=timer_text, reply_markup=progress_markup, parse_mode="HTML")
            time.sleep(0.3) 
        except: pass

    try:
        init_timer_text = (f"🎰 <b>تم حجز الرقم بنجاح!</b>\n\n"
                          f"🌍 <b>الدولة:</b> {flag} {c_name}\n"
                          f"📱 <b>الرقم المحجوز لك:</b> <code>{phone_number}</code>\n\n"
                          f"⏳ <b>جاري فحص وصول الكود الحين...</b>\n"
                          f"✨ <i>يرجى الانتظار، سيتم تثبيت الكود فور وصوله تلقائياً.</i>")
        bot.edit_message_text(chat_id=user_id, message_id=status_msg_id, text=init_timer_text, reply_markup=None, parse_mode="HTML")
    except: pass

    total_wait_seconds = 300  
    check_interval = 15       
    loops = total_wait_seconds // check_interval
    
    for i in range(loops):
        try:
            time.sleep(check_interval)

            if is_number_banned_on_telegram(phone_number, acc_index): break
                
            res = requests.get(sms_url, timeout=5).json()
            if res.get("code") == 200:
                sms_code = res.get("data")
                
                # 💸 لحظة استلام الكود بنجاح: الحين يحصل الخصم الحقيقي والأكيد من محفظة العميل! 🔒💰
                if user_id not in USER_BALANCES: USER_BALANCES[user_id] = 0.00
                USER_BALANCES[user_id] = max(0.00, USER_BALANCES[user_id] - price)
                save_data("balances")
                
                success_text = f"✅ <b>تم شراء الرقم واستلام الكود بنجاح!</b>\n\n{flag} {c_name}\n📱 الرقم: <code>{phone_number}</code>\n💰 السعر: <b>{price}$</b>\n\n📥 الكود وصلك بالأسفل وتم تثبيته فوق 📌"
                bot.edit_message_text(chat_id=user_id, message_id=status_msg_id, text=success_text, reply_markup=None, parse_mode="HTML")
                
                pin_msg_text = f"✅ تم استلام الكود! • الرقم: <code>{phone_number}</code> • الدولة: {flag} {c_name}\n🔑 كود تفعيل التليجرام: <code>{sms_code}</code>"
                sent_pin_msg = bot.send_message(user_id, pin_msg_text, parse_mode="HTML")
                try: bot.pin_chat_message(chat_id=user_id, message_id=sent_pin_msg.message_id, disable_notification=False)
                except: pass
                
                log_order(user_id, f"📱 {phone_number} | كود: {sms_code} | سعر: {price}$")
                SYSTEM_STATS["successful_orders"] += 1
                SYSTEM_STATS["total_sales"] += price
                
                try:
                    admin_log_msg = f"🔔 <b>بيع ناجح:</b>\n• الزبون: <code>{user_id}</code>\n• الرقم: <code>{phone_number}</code>\n• الكود: <code>{sms_code}</code>"
                    bot.send_message(ADMIN_ID, admin_log_msg, parse_mode="HTML")
                except: pass
                return
        except: pass
    
    # ❌ لو موصلش الكود وانتهى الوقت: الرصيد أصلاً مخصمنهوش من الأول، فبنلغي الرقم أوتوماتيك مجاناً تماماً! 😎🍿
    release_bad_number(phone_number, acc_index)
    SYSTEM_STATS["failed_orders"] += 1
    
    fail_text = f"❌ <b>انتهى وقت الانتظار لعدم وصول الكود للرقم:</b>\n<code>{phone_number}</code>\n\n💰 لم يتم خصم أي مبلغ من رصيدك لعدم استلام كود التفعيل، محفظتك في أمان كامل!"
    try: bot.edit_message_text(chat_id=user_id, message_id=status_msg_id, text=fail_text, reply_markup=None, parse_mode="HTML")
    except: pass

def process_admin_target_id(message, action):
    try:
        target_id = int(message.text.strip())
        admin_state[message.from_user.id] = {"action": action, "target_user": target_id, "mode": "admin_amount"}
        msg = bot.send_message(message.chat.id, "💰 أدخل القيمة بالدولار الآن:")
        bot.register_next_step_handler(msg, process_admin_amount)
    except: bot.send_message(message.chat.id, "❌ الـ ID غير صحيح.")

def process_admin_amount(message):
    admin_id = message.from_user.id
    if admin_id in admin_state and admin_id == ADMIN_ID:
        try:
            amount = float(message.text.strip())
            target_id = admin_state[admin_id]["target_user"]
            action = admin_state[admin_id]["action"]
            if target_id not in USER_BALANCES: USER_BALANCES[target_id] = 0.00
            if action == "add":
                USER_BALANCES[target_id] += amount
                save_data("balances")
                bot.send_message(admin_id, f"✅ تم شحن {amount}$ لحساب {target_id}!")
                try: bot.send_message(target_id, f"💰 **تم شحن محفظتك بـ +{amount:.2f}$ من قبل الإدارة!**")
                except: pass
            else:
                USER_BALANCES[target_id] = max(0.00, USER_BALANCES[target_id] - amount)
                save_data("balances")
                bot.send_message(admin_id, f"✅ تم خصم {amount}$ من حساب {target_id}!")
            del admin_state[admin_id]
        except:
            bot.send_message(admin_id, "❌ خطأ في القيمة.")
            if admin_id in admin_state: del admin_state[admin_id]

def process_admin_broadcast(message):
    text = message.text
    count = 0
    for u_id in list(USER_BALANCES.keys()):
        if u_id == ADMIN_ID: continue
        try:
            bot.send_message(u_id, f"📢 **إعلان من الإدارة:**\n\n{text}")
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ تم الإرسال لـ {count} زبون بنجاح.")

def run_bot_safe():
    print("🕸️🕷️ تم قفل منطق الخصم الآمن والـ Cooldown المظبوط على النسخة الـ 700 سطر بنجاح... 🚀✨📌")
    threading.Thread(target=global_auto_buyer, daemon=True).start()
    while True:
        try: bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except: time.sleep(5)

if __name__ == "__main__":
    run_bot_safe()
