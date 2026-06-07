import telebot
import requests
import threading
import time
import os
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- ⚠️ إعدادات البوت والـ API والتحكم (ضع بياناتك هنا) ---
BOT_TOKEN = "ضع_توكن_البوت_هنا"      # 8079896033:AAGC8LigHHqLLK1uc8mJDVyRAw8_7eosLzk BotFather
USER_NAME = "Abdelhadisayed"    # اسم حسابك الفعلي في موقع Durian
API_TOKEN = "YXRjMHFVSlVtR09RSytaeUNDMTZrQT09"   # الـ API Key بتاعك
PROJECT_ID = "0257"                 # كود مشروع التليجرام الصحيح 🎯
ADMIN_ID = 7087179945                # الـ ID بتاع حسابك أنت في التليجرام
SUPPORT_URL = "t.me/abdelhadisayed" 

# 💰 إعدادات فودافون كاش التلقائي
USD_TO_EGP_RATE = 50.0              # سعر الدولار مقابل الجنيه جوه البوت (عدله براحتك)
VODAFONE_NUMBER = "01028520360"       # رقم فودافون كاش بتاعك اللي الزباين هتحول عليه
# ---------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

user_hunting_targets = {}  
hunting_active = False
USER_BALANCES = {} 
admin_state = {} 

BALANCES_FILE = "balances.txt"

def load_balances():
    global USER_BALANCES
    if os.path.exists(BALANCES_FILE):
        try:
            with open(BALANCES_FILE, "r") as f:
                for line in f:
                    if ":" in line:
                        u_id, bal = line.strip().split(":")
                        USER_BALANCES[int(u_id)] = float(bal)
        except: pass

def save_balances():
    try:
        with open(BALANCES_FILE, "w") as f:
            for u_id, bal in USER_BALANCES.items():
                f.write(f"{u_id}:{bal}\n")
    except: pass

load_balances()

ALL_COUNTRIES = {
    "الأرجنتين": {"code": "ar", "price": 0.25, "flag": "🇦🇷"},
    "تونس": {"code": "tn", "price": 0.25, "flag": "🇹🇳"},
    "مصر": {"code": "eg", "price": 0.25, "flag": "🇪🇬"},
    "روسيا": {"code": "ru", "price": 0.25, "flag": "🇷🇺"},
    "أمريكا": {"code": "us", "price": 0.25, "flag": "🇺🇸"},
    "تايلاند": {"code": "th", "price": 0.25, "flag": "🇹🇭"},
    "الإمارات": {"code": "ae", "price": 0.25, "flag": "🇦🇪"},
    "سوريا": {"code": "sy", "price": 0.25, "flag": "🇸🇾"},
    "فرنسا": {"code": "fr", "price": 0.25, "flag": "🇫🇷"},
    "بورتوريكو": {"code": "pr", "price": 0.25, "flag": "🇵🇷"},
    "فيجي": {"code": "fj", "price": 0.25, "flag": "🇫🇯"},
    "أفغانستان": {"code": "af", "price": 0.25, "flag": "🇦🇫"},
    "الأردن": {"code": "jo", "price": 0.25, "flag": "🇯🇴"}
}

active_hunted_numbers = {} 

def get_user_balance(user_id):
    if user_id not in USER_BALANCES: 
        USER_BALANCES[user_id] = 0.00
        save_balances()
    return USER_BALANCES[user_id]

def get_country_info_by_code(code):
    for name, info in ALL_COUNTRIES.items():
        if info["code"] == code: return name, info["price"], info["flag"]
    return f"دولة ({code})", 0.25, "🌍"

def get_admin_dashboard_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("💰 شحن رصيد لزبون", callback_data="admin_add_balance"), InlineKeyboardButton("➖ سحب رصيد من زبون", callback_data="admin_sub_balance"))
    markup.add(InlineKeyboardButton("🔄 تصفير محفظة مستخدم", callback_data="admin_clear_balance"), InlineKeyboardButton("📢 إذاعة رسالة (برودكاست)", callback_data="admin_broadcast"))
    markup.add(InlineKeyboardButton("🔄 تحديث الإحصائيات", callback_data="admin_refresh_stats"))
    return markup

def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🛒 شراء حساب", callback_data="buy_account"))
    markup.add(InlineKeyboardButton("💰 إيداع / شحن", callback_data="deposit"), InlineKeyboardButton("👨‍💻 التواصل مع الدعم", url=SUPPORT_URL))
    markup.add(InlineKeyboardButton("🎯 تفعيل الصيد التلقائي", callback_data="manage_hunting"))
    return markup

def get_countries_keyboard(user_id, page=0):
    markup = InlineKeyboardMarkup(row_width=2)
    user_targets = user_hunting_targets.get(user_id, [])
    items = list(ALL_COUNTRIES.items())
    per_page = 14  
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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        admin_text = f"👑 <b>مرحباً بك يا مدير في لوحة التحكم الإدارية</b>\n\n📊 <b>إحصائيات حية:</b>\n• الزبائن: <code>{len(USER_BALANCES)}</code>\n• الأرصدة: <code>{sum(USER_BALANCES.values()):.2f} $</code>"
        bot.send_message(message.chat.id, admin_text, reply_markup=get_admin_dashboard_keyboard(), parse_mode="HTML")
    else:
        welcome_text = f"• <u><b>Pulse-SMS - Auto Hunting Bot</b></u> •\n\n💰 <b>رصيدك الحالي:</b> {get_user_balance(user_id):.2f} $\n\nاختر من الأسفل 👇"
        bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    
    if user_id == ADMIN_ID:
        if call.data == "admin_add_balance":
            msg = bot.send_message(user_id, "✍️ أرسل **ID حساب الزبون** للشحن:")
            bot.register_next_step_handler(msg, process_admin_target_id, "add")
            return
        elif call.data == "admin_sub_balance":
            msg = bot.send_message(user_id, "✍️ أرسل **ID حساب الزبون** للخصم:")
            bot.register_next_step_handler(msg, process_admin_target_id, "sub")
            return
        elif call.data == "admin_clear_balance":
            msg = bot.send_message(user_id, "✍️ أرسل **ID الزبون** لتصفير محفظته:")
            bot.register_next_step_handler(msg, process_admin_clear_id)
            return
        elif call.data == "admin_broadcast":
            msg = bot.send_message(user_id, "📢 اكتب رسالة البرودكاست لإذاعتها:")
            bot.register_next_step_handler(msg, process_admin_broadcast)
            return
        elif call.data == "admin_refresh_stats":
            bot.answer_callback_query(call.id, "🔄 تم التحديث")
            admin_text = f"👑 <b>لوحة التحكم المحدثة</b>\n\n📊 <b>إحصائيات حية:</b>\n• الزبائن: <code>{len(USER_BALANCES)}</code>\n• الأرصدة: <code>{sum(USER_BALANCES.values()):.2f} $</code>"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=admin_text, reply_markup=get_admin_dashboard_keyboard(), parse_mode="HTML")
            return

    if call.data == "deposit":
        bot.answer_callback_query(call.id)
        deposit_text = (
            f"💳 <b>قسم الشحن التلقائي (فودافون كاش)</b>\n\n"
            f"يرجى تحويل المبلغ المراد شحنه إلى الرقم التالي:\n"
            f"📱 رقم الكاش: <code>{VODAFONE_NUMBER}</code>\n\n"
            f"⚠️ <b>طريقة تفعيل الرصيد:</b>\n"
            f"بعد إتمام التحويل بنجاح، قم بعمل <b>نسخ لرسالة شركة فودافون</b> التي تصلك على هاتفك (تم تحويل مبلغ... إلخ) "
            f"وقم بـ <b>إرسال الرسالة نصياً هنا في شات البوت مباشرة</b>.\n\n"
            f"💵 سعر تحويل الدولار داخل البوت: 1$ = {USD_TO_EGP_RATE} جنيه."
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=deposit_text, reply_markup=markup, parse_mode="HTML")
        return

    if call.data == "manage_hunting" or call.data == "buy_account":
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
        
        if code not in user_hunting_targets[user_id] and get_user_balance(user_id) < price:
            bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ لتفعيل هذه الدولة!", show_alert=True)
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
        welcome_text = f"• <u><b>Pulse-SMS - Auto Hunting Bot</b></u> •\n\n💰 <b>رصيدك الحالي:</b> {get_user_balance(user_id):.2f} $\n\nاختر من الأسفل 👇"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")
    
    elif call.data.startswith("claim_"):
        phone = call.data.split("_")[1]
        if phone in active_hunted_numbers:
            target_info = active_hunted_numbers[phone]
            price = float(target_info['price'])
            
            if get_user_balance(user_id) >= price:
                del active_hunted_numbers[phone]
                
                bot.answer_callback_query(call.id, "✅ تم حجز الرقم مبدئياً! جاري سحب الـ SMS...")
                bot.edit_message_text(
                    chat_id=call.message.chat.id, 
                    message_id=call.message.id, 
                    text=f"🎰 <b>الدولة متاحة الآن</b> 🥳\n\n{target_info['flag']} {target_info['country']}\n📱 الرقم المحجوز: <code>{phone}</code>\n\n🔄 جاري انتظار كود الـ SMS من السيرفر الصيني...\n⚠️ <b>تنبيه:</b> لن يتم خصم الـ {price:.2f}$ من محفظتك إلا بعد وصول الكود بنجاح! 👍",
                    parse_mode="HTML"
                )
                threading.Thread(target=wait_for_sms, args=(user_id, phone, price)).start()
            else:
                bot.answer_callback_query(call.id, "❌ رصيدك غير كافٍ لإتمام عملية الحجز!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ الرقم تم بيعه أو انتهت صلاحيته الحجز!", show_alert=True)

# 📲 نظام فك شفرة رسائل فودافون كاش والشحن التلقائي الفوري 💳
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # التحقق من أن الرسالة هي رسالة فودافون كاش الرسمية للتحويل
    if "تم تحويل" in text and "بنجاح" in text:
        try:
            # استخراج المبلغ المالي من الرسالة بالـ Regex الذكي
            amount_match = re.search(r"مبلغ\s+([\d\.]+)\s+جنيه", text)
            if amount_match:
                egp_amount = float(amount_match.group(1))
                
                # حساب القيمة بالدولار بناءً على السعر المحدد فوق
                usd_gained = round(egp_amount / USD_TO_EGP_RATE, 2)
                
                if usd_gained > 0:
                    # إضافة الرصيد لحساب المستخدم فوراً وحفظ التغيير
                    if user_id not in USER_BALANCES: USER_BALANCES[user_id] = 0.00
                    USER_BALANCES[user_id] += usd_gained
                    save_balances()
                    
                    # إرسال تأكيد للزبون
                    bot.reply_to(
                        message, 
                        f"✅ <b>تم استلام وتأكيد تحويلك بنجاح!</b>\n"
                        f"💰 المبلغ المستلم: <code>{egp_amount} جنيه</code>\n"
                        f"💵 الرصيد المضاف: <code>+{usd_gained}$</code>\n"
                        f"💳 محفظتك الحالية الآن: <b>{USER_BALANCES[user_id]:.2f}$</b>\n\n"
                        f"استمتع بالصيد والشراء الفوري! 🎉", 
                        parse_mode="HTML"
                    )
                    
                    # إشعار للأدمن في نفس اللحظة لمراقبة العمليات
                    try:
                        bot.send_message(
                            ADMIN_ID, 
                            f"🔔 <b>عملية شحن تلقائي جديدة!</b>\n"
                            f"👤 الزبون الـ ID: <code>{user_id}</code>\n"
                            f"📱 اسم المستخدم: @{message.from_user.username or 'بلا اسم'}\n"
                            f"💰 شحن بمبلغ: <code>{egp_amount} جنيه</code> 👈 عادلت: <code>{usd_gained}$</code>", 
                            parse_mode="HTML"
                        )
                    except: pass
                    return
        except Exception as e:
            print(f"Error parsing VF Cash message: {e}")
            
        bot.reply_to(message, "❌ <b>عذراً، لم نتمكن من التحقق من صحة الرسالة!</b> تأكد من نسخها كاملة كما وصلت من الشركة، أو تواصل مع الدعم الفني.", parse_mode="HTML")
    else:
        # لو رسالة عادية لا تطابق الفودافون كاش
        if user_id != ADMIN_ID:
            bot.reply_to(message, "❓ خيار غير معروف. يرجى استخدام أزرار التحكم بالأسفل.", reply_markup=get_main_keyboard())

def release_bad_number(phone_number):
    try:
        url = f"https://api.durianrcs.com/out/ext_api/cancelMobile?name={USER_NAME}&ApiKey={API_TOKEN}&pn={phone_number}&pid={PROJECT_ID}&serial=2"
        requests.get(url, timeout=5)
    except: pass

def is_number_banned_on_telegram(phone_number):
    try:
        check_url = f"https://api.durianrcs.com/out/ext_api/getMsg?name={USER_NAME}&ApiKey={API_TOKEN}&pn={phone_number}&pid={PROJECT_ID}&serial=2"
        res = requests.get(check_url, timeout=4).json()
        if res.get("code") == 905 or "block" in str(res).lower() or "ban" in str(res).lower():
            return True
    except: pass
    return False

def global_auto_buyer():
    global hunting_active
    hunting_active = True
    while hunting_active:
        for name, info in list(ALL_COUNTRIES.items()):
            country_code = info["code"]
            try:
                url = f"https://api.durianrcs.com/out/ext_api/getMobile?name={USER_NAME}&ApiKey={API_TOKEN}&cuy={country_code}&pid={PROJECT_ID}&num=1&noblack=1&serial=2"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    res_json = response.json()
                    if res_json.get("code") == 200:
                        phone_number = res_json.get("data")
                        
                        if is_number_banned_on_telegram(phone_number):
                            release_bad_number(phone_number)
                            continue
                            
                        c_name, price, flag = get_country_info_by_code(country_code)
                        active_hunted_numbers[phone_number] = {"country": c_name, "flag": flag, "price": price}
                        
                        for u_id, targets in list(user_hunting_targets.items()):
                            if country_code in targets:
                                markup = InlineKeyboardMarkup()
                                markup.add(InlineKeyboardButton("🛒 شراء الآن", callback_data=f"claim_{phone_number}"))
                                formatted_msg = f"🥳 🎰 **الدولة متاحة الآن**\n\n{flag} {c_name}\n✅ رقم جاهز تماماً وفريش!\n💰 سعر الشراء: **${price:.2f}**\n\n🛒 اضغط شراء الآن لحجزه فوراً"
                                bot.send_message(u_id, formatted_msg, reply_markup=markup, parse_mode="Markdown")
                                user_hunting_targets[u_id].remove(country_code)
            except Exception as e:
                print(f"⚠️ عطل شبكة مؤقت في دالة الصيد، جاري التخطي: {e}")
            time.sleep(2.5)
        time.sleep(2)

def wait_for_sms(user_id, phone_number, price):
    sms_url = f"https://api.durianrcs.com/out/ext_api/getMsg?name={USER_NAME}&ApiKey={API_TOKEN}&pn={phone_number}&pid={PROJECT_ID}&serial=2"
    for _ in range(20): 
        try:
            time.sleep(15)
            res = requests.get(sms_url, timeout=5).json()
            if res.get("code") == 200:
                sms_code = res.get("data")
                
                if USER_BALANCES[user_id] >= price:
                    USER_BALANCES[user_id] -= price
                    save_balances()
                
                bot.send_message(
                    user_id, 
                    f"✅ **تم استلام الكود بنجاح!**\n• الرقم: `{phone_number}`\n\n🔑 كود تفعيل التليجرام: <code>{sms_code}</code>\n\n💰 تم خصم **${price:.2f}** من محفظتك الحين.\n💵 رصيدك المتبقي الحالي: **${USER_BALANCES[user_id]:.2f}**", 
                    parse_mode="HTML"
                )
                return
        except: pass
    bot.send_message(user_id, f"⚠️ انتهى وقت انتظار الـ SMS للرقم `{phone_number}`.\n❌ **تم إلغاء الطلب تلقائياً ولم يتم خصم أي سنت من رصيدك.**")

def process_admin_target_id(message, action):
    try:
        target_id = int(message.text.strip())
        admin_state[message.from_user.id] = {"action": action, "target_user": target_id}
        msg = bot.send_message(message.chat.id, "💰 أدخل القيمة الآن:")
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
                save_balances()
                bot.send_message(admin_id, "✅ تم الشحن بنجاح!")
                try: bot.send_message(target_id, f"💰 **تم شحن محفظتك بـ +{amount:.2f}$ بنجاح!**")
                except: pass
            else:
                USER_BALANCES[target_id] = max(0.00, USER_BALANCES[target_id] - amount)
                save_balances()
                bot.send_message(admin_id, "✅ تم الخصم بنجاح!")
            del admin_state[admin_id]
        except: bot.send_message(message.chat.id, "❌ خطأ في المبلغ.")

def process_admin_clear_id(message):
    try:
        target_id = int(message.text.strip())
        USER_BALANCES[target_id] = 0.00
        save_balances()
        bot.send_message(ADMIN_ID, "🔄 تم تصفير المحفظة بنجاح.")
    except: bot.send_message(ADMIN_ID, "❌ خطأ.")

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
    print("🤖 جاري تشغيل البوت المحدث بدعم الشحن التلقائي فودافون كاش...")
    threading.Thread(target=global_auto_buyer, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"🚨 عطل شبكة مؤقت: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_bot_safe()
