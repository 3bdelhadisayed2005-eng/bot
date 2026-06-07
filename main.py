import telebot
import requests
import threading
import time
import os
import random
import string
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- ⚠️ إعدادات البوت الأساسية (ضع التوكن والـ ID الخاص بك فقط) ---
BOT_TOKEN = "8079896033:AAGC8LigHHqLLK1uc8mJDVyRAw8_7eosLzk"      # توكن البوت الخاص بك من BotFather
ADMIN_ID = 7087179945                # الـ ID بتاع حسابك أنت في التليجرام (أرقام فقط)

# 🔑 بيانات الحسابات الثلاثة لموقع Durian (غير الكلام العربي فقط وسيب الأقواس والترتيب)
DURIAN_ACCOUNTS = [
    ["Abdelhadisayed", "YXRjMHFVSlVtR09RSytaeUNDMTZrQT09"],
    ["3bdelhadisayed", "N3BIVTV2OWxheFFYenpFL0NrbW45Zz09"],
    ["Abdelhadi2005", "RStqT2cvR2dMMTNPVVFaMU9DYXdQdz09"]
]
# -----------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

# 💾 ملفات حفظ البيانات لمنع ضياعها عند إعادة تشغيل السيرفر
BALANCES_FILE = "balances.txt"
SETTINGS_FILE = "settings.txt"
PROMOS_FILE = "promos.txt"
ORDERS_FILE = "orders.txt"
PRICES_FILE = "prices.txt"

USER_BALANCES = {}
SETTINGS = {"rate": 50.0, "wallet": "010xxxxxxx", "pid": "0257", "support": "https://t.me/YourSupportUsername"}
PROMO_CODES = {}
USER_ORDERS = {}

# 🌍 الـ 41 دولة الأساسية للبوت
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

# --- 💾 دالات الحفظ والقراءة التلقائية للبيانات ---
def load_all_data():
    global USER_BALANCES, SETTINGS, PROMO_CODES, USER_ORDERS, ALL_COUNTRIES
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
                    if "=" in line: k, v = line.strip().split("="); SETTINGS[k] = float(v) if k == "rate" else v
        except: pass
    if os.path.exists(PROMOS_FILE):
        try:
            with open(PROMOS_FILE, "r") as f:
                for line in f:
                    if ":" in line: code, val = line.strip().split(":"); PROMO_CODES[code] = float(val)
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

# --- 👑 لوحات أزرار التحكم الكاملة للإدارة ---
def get_admin_dashboard_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("💰 شحن رصيد لزبون", callback_data="admin_add_balance"), InlineKeyboardButton("➖ سحب رصيد", callback_data="admin_sub_balance"))
    markup.add(InlineKeyboardButton("⚙️ تعديل الكاش والسعر", callback_data="admin_set_vars"), InlineKeyboardButton("🎫 توليد كود شحن", callback_data="admin_gen_promo"))
    markup.add(InlineKeyboardButton("🌍 تعديل سعر دولة", callback_data="admin_set_country_price"), InlineKeyboardButton("📢 إذاعة رسالة", callback_data="admin_broadcast"))
    markup.add(InlineKeyboardButton("🔄 تحديث الإحصائيات", callback_data="admin_refresh_stats"))
    return markup

def get_admin_vars_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"📱 رقم الكاش الحالي ({SETTINGS['wallet']})", callback_data="edit_wallet"),
        InlineKeyboardButton(f"💵 سعر الدولار الحالي ({SETTINGS['rate']} ج.م)", callback_data="edit_rate"),
        InlineKeyboardButton(f"🎯 كود المشروع الحالى ({SETTINGS['pid']})", callback_data="edit_pid"),
        InlineKeyboardButton(f"👨‍💻 يوزر الدعم الحالي", callback_data="edit_support"),
        InlineKeyboardButton("🔙 عودة للوحة الإدارة", callback_data="admin_back_main")
    )
    return markup

# --- 👤 لوحات أزرار المستخدم بتصميمه المتناسق والنظيف ---
def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🎯 تفعيل الصيد التلقائي", callback_data="manage_hunting"))
    markup.add(InlineKeyboardButton("💰 إيداع / شحن", callback_data="deposit"), InlineKeyboardButton("📋 أرقامي المشتراة", callback_data="user_orders"))
    markup.add(InlineKeyboardButton("🎫 شحن كود هدية", callback_data="user_redeem_promo"), InlineKeyboardButton("👨‍💻 التواصل مع الدعم", url=SETTINGS["support"]))
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
        markup.add(InlineKeyboardButton(f"{info['flag']} {name} (${info['price']}){status}", callback_data=f"hunt_{code}_{page}"))
        
    nav = []
    if page > 0: nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"hpage_{page-1}"))
    if end < len(items): nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"hpage_{page+1}"))
    if nav: markup.row(*nav)
    markup.add(InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        admin_text = f"👑 <b>مرحباً بك يا مدير في لوحة التحكم الإدارية</b>\n\n📊 <b>إحصائيات حية:</b>\n• الزبائن: <code>{len(USER_BALANCES)}</code>\n• الأرصدة: <code>{sum(USER_BALANCES.values()):.2f} $</code>\n• الأكواد النشطة: <code>{len(PROMO_CODES)} كود</code>"
        bot.send_message(message.chat.id, admin_text, reply_markup=get_admin_dashboard_keyboard(), parse_mode="HTML")
    else:
        welcome_text = f"• <u><b>Pulse-SMS - Auto Hunting Bot</b></u> •\n\n💰 <b>رصيدك الحالي:</b> {get_user_balance(user_id):.2f} $\n\n🆔 الـ ID الخاص بك: <code>{user_id}</code>\n\nاختر من الأسفل 👇"
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    
    if user_id == ADMIN_ID:
        if call.data == "admin_back_main":
            bot.answer_callback_query(call.id)
            admin_text = f"👑 <b>مرحباً بك يا مدير في لوحة التحكم الإدارية</b>\n\n📊 <b>إحصائيات حية:</b>\n• الزبائن: <code>{len(USER_BALANCES)}</code>\n• الأرصدة: <code>{sum(USER_BALANCES.values()):.2f} $</code>"
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id, text=admin_text, reply_markup=get_admin_dashboard_keyboard(), parse_mode="HTML")
            return
        elif call.data == "admin_set_vars":
            bot.answer_callback_query(call.id)
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id, text="⚙️ **إعدادات ومغيرات السيستم من التليجرام:**", reply_markup=get_admin_vars_keyboard(), parse_mode="Markdown")
            return
        elif call.data in ["edit_wallet", "edit_rate", "edit_pid", "edit_support"]:
            bot.answer_callback_query(call.id)
            admin_state[user_id] = {"mode": "edit_var", "var": call.data.split("_")[1]}
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
            bot.send_message(user_id, "✍️ أدخل قيمة كود الشحن بالدولار (مثال: 5):")
            return
        elif call.data == "admin_set_country_price":
            bot.answer_callback_query(call.id)
            admin_state[user_id] = {"mode": "set_country_select"}
            bot.send_message(user_id, "✍️ اكتب اسم الدولة بالظبط المراد تغيير سعرها (مثال: مصر):")
            return
        elif call.data == "admin_broadcast":
            msg = bot.send_message(user_id, "📢 اكتب رسالة البرودكاست لإذاعتها:")
            bot.register_next_step_handler(msg, process_admin_broadcast)
            return
        elif call.data == "admin_refresh_stats":
            bot.answer_callback_query(call.id, "🔄 تم التحديث")
            admin_text = f"👑 <b>لوحة التحكم المحدثة</b>\n\n📊 <b>إحصائيات حية:</b>\n• الزبائن: <code>{len(USER_BALANCES)}</code>\n• الأرصدة: <code>{sum(USER_BALANCES.values()):.2f} $</code>"
            bot.edit_message_text(chat_id=user_id, message_id=call.message.id, text=admin_text, reply_markup=get_admin_dashboard_keyboard(), parse_mode="HTML")
            return

    if call.data == "deposit":
        bot.answer_callback_query(call.id)
        deposit_text = (
            f"💳 <b>شحن الرصيد عن طريق المشرف</b>\n\n"
            f"يرجى تحويل المبلغ المراد شحنه إلى رقم فودافون كاش التالي:\n"
            f"📱 رقم الكاش: <code>{SETTINGS['wallet']}</code>\n\n"
            f"💵 حسبة تحويل الدولار داخل البوت: 1$ = {SETTINGS['rate']} جنيه.\n\n"
            f"📥 <b>خطوات تفعيل الرصيد:</b>\n"
            f"1️⃣ قم بتحويل المبلغ على الرقم أعلاه.\n"
            f"2️⃣ خذ لقطة شاشة للتحويل.\n"
            f"3️⃣ أرسل السكرين مع الـ ID الخاص بك لكي يشحن محفظتك فوراً.\n\n"
            f"🆔 الـ ID الخاص بك: <code>{user_id}</code>"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=deposit_text, reply_markup=markup, parse_mode="HTML")
        return

    elif call.data == "user_redeem_promo":
        bot.answer_callback_query(call.id)
        admin_state[user_id] = {"mode": "redeem_promo"}
        bot.send_message(user_id, "🎫 أدخل كود الهدية / كود الشحن الخاص بك هنا:")
        return

    elif call.data == "user_orders":
        bot.answer_callback_query(call.id)
        orders = USER_ORDERS.get(user_id, [])
        if not orders:
            bot.send_message(user_id, "📋 ليس لديك أرقام مشتراة سابقة حتى الآن.")
        else:
            text = "📋 **سجل أرقامك المشتراة السابقة وسحوبات الـ SMS:**\n\n" + "\n\n".join(orders[-10:])
            bot.send_message(user_id, text)
        return

    elif call.data == "manage_hunting":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="🌍 **قسم الصيد التلقائي لأرقام التليجرام:**", reply_markup=get_countries_keyboard(user_id, page=0), parse_mode="Markdown")
    elif call.data.startswith("hpage_"):
        bot.answer_callback_query(call.id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=get_countries_keyboard(user_id, page=int(call.data.split("_")[1])))
    elif call.data.startswith("hunt_"):
        parts = call.data.split("_")
        code, page = parts[1], int(parts[2])
        if user_id not in user_hunting_targets: user_hunting_targets[user_id] = []
        name, price, _ = get_country_info_by_code(code)
        
        if code not in user_hunting_targets[user_id] and get_user_balance(user_id) <= 0:
            bot.answer_callback_query(call.id, "❌ محفظتك فارغة! يرجى الشحن لتفعيل الصيد.", show_alert=True)
            return
        if code in user_hunting_targets[user_id]:
            user_hunting_targets[user_id].remove(code)
            bot.answer_callback_query(call.id, f"🛑 تم إيقاف صيد {name}")
        else:
            user_hunting_targets[user_id].append(code)
            bot.answer_callback_query(call.id, f"🎯 تم تفعيل صيد {name}")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=get_countries_keyboard(user_id, page=page))
    elif call.data == "back_to_main":
        bot.answer_callback_query(call.id)
        welcome_text = f"• <u><b>Pulse-SMS - Auto Hunting Bot</b></u> •\n\n💰 <b>رصيدك الحالي:</b> {get_user_balance(user_id):.2f} $\n\n🆔 الـ ID الخاص بك: <code>{user_id}</code>\n\nاختر من الأسفل 👇"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    
    elif call.data.startswith("claim_"):
        parts = call.data.split("_")
        phone = parts[1]
        acc_index = int(parts[2])
        
        if phone in active_hunted_numbers:
            target_info = active_hunted_numbers[phone]
            price = float(target_info['price'])
            
            if get_user_balance(user_id) >= price:
                del active_hunted_numbers[phone]
                
                bot.send_message(user_id, "✅ تم حجز الرقم مبدئياً! جاري سحب الـ SMS...")
                threading.Thread(target=wait_for_sms, args=(user_id, phone, price, acc_index)).start()
            else:
                bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ لإتمام عملية الحجز!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ الرقم تم بيعه أو انتهت صلاحيته الحجز!", show_alert=True)

# --- ⚙️ معالجة الرسائل النصية وحالات الإدخال المتعددة الحين ---
@bot.message_handler(func=lambda msg: msg.from_user.id in admin_state)
def handle_states(message):
    user_id = message.from_user.id
    state = admin_state[user_id]
    text = message.text.strip()
    
    if state.get("mode") == "edit_var":
        var = state["var"]
        if var == "rate": SETTINGS["rate"] = float(text)
        elif var == "wallet": SETTINGS["wallet"] = text
        elif var == "pid": SETTINGS["pid"] = text
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
        
    elif state.get("mode") == "set_country_select":
        if text in ALL_COUNTRIES:
            admin_state[user_id] = {"mode": "set_country_price_val", "c_name": text}
            bot.send_message(user_id, f"💰 أدخل السعر الجديد لدولة {text} بالدولار:")
        else:
            bot.send_message(user_id, "❌ اسم الدولة غير موجود بقائمة الدول.")
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
        else:
            bot.send_message(user_id, "❌ كود غير صحيح أو مستخدم سابقاً.")
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
        if res.get("code") == 905 or "block" in str(res).lower() or "ban" in str(res).lower():
            return True
    except: pass
    return False

def global_auto_buyer():
    global hunting_active
    hunting_active = True
    while hunting_active:
        for u_id, targets in list(user_hunting_targets.items()):
            if get_user_balance(u_id) <= 0:
                for target_code in list(targets): user_hunting_targets[u_id].remove(target_code)
                try: bot.send_message(u_id, f"🛑 **تم إيقاف الصيد التلقائي لأن رصيدك انتهى تماماً!**")
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
                                if country_code in targets_list and get_user_balance(u_id) > 0:
                                    markup = InlineKeyboardMarkup()
                                    markup.add(InlineKeyboardButton("🛒 شراء الآن", callback_data=f"claim_{phone_number}_{idx}"))
                                    formatted_msg = f"🥳 🎰 **الدولة متاحة الآن**\n\n{flag} {c_name}\n✅ رقم جاهز وفريش تماماً!\n💰 سعر الشراء: **${price:.2f}**\n\n🛒 اضغط شراء الآن لحجزه فوراً"
                                    bot.send_message(u_id, formatted_msg, reply_markup=markup, parse_mode="Markdown")
                            break
                except: pass
                time.sleep(0.5)
            time.sleep(0.5)

def wait_for_sms(user_id, phone_number, price, acc_index):
    acc = DURIAN_ACCOUNTS[acc_index]
    sms_url = f"https://api.durianrcs.com/out/ext_api/getMsg?name={acc[0]}&ApiKey={acc[1]}&pn={phone_number}&pid={str(SETTINGS['pid'])}&serial=2"
    for _ in range(20): 
        try:
            time.sleep(15)
            res = requests.get(sms_url, timeout=5).json()
            if res.get("code") == 200:
                sms_code = res.get("data")
                if USER_BALANCES[user_id] >= price:
                    USER_BALANCES[user_id] -= price
                    save_data("balances")
                success_text = f"✅ **تم استلام الكود بنجاح!**\n• الرقم: `{phone_number}`\n🔑 كود تفعيل التليجرام: <code>{sms_code}</code>\n💰 تم خصم **${price:.2f}**"
                bot.send_message(user_id, success_text, parse_mode="HTML")
                log_order(user_id, f"📱 {phone_number} | كود: {sms_code} | سعر: {price}$")
                return
        except: pass
    bot.send_message(user_id, f"⚠️ انتهى وقت انتظار الـ SMS للرقم `{phone_number}`.")

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
            else:
                USER_BALANCES[target_id] = max(0.00, USER_BALANCES[target_id] - amount)
                save_data("balances")
                bot.send_message(admin_id, f"✅ تم خصم {amount}$ من حساب {target_id}!")
            del admin_state[admin_id]
        except: bot.send_message(message.chat.id, "❌ خطأ في القيمة.")

def process_admin_broadcast(message):
    text = message.text
    count = 0
    for u_id in list(USER_BALANCES.keys()):
        try:
            bot.send_message(u_id, f"📢 **إعلان من الإدارة:**\n\n{text}")
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ تم الإرسال لـ {count} زبون.")

def run_bot_safe():
    print("🤖 تشغيل النسخة الخارقة والنظيفة بالكامل...")
    threading.Thread(target=global_auto_buyer, daemon=True).start()
    while True:
        try: bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except: time.sleep(5)

if __name__ == "__main__":
    run_bot_safe()
