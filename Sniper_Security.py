import telebot
from telebot import types
import json
import os
from unidecode import unidecode
from difflib import SequenceMatcher

# ==========================================
# ⚙️ إعدادات نظام القناص (Sniper Config)
# ==========================================
BOT_TOKEN = "8329826650:AAGynAZzwCKcfPfsv-qU6Y4hkWWQPAT64HU" 
OWNER_ID = 6403967862        

# ✅ تم التعديل هنا: وضعنا علامة \ قبل الشرطة السفلية لمنع الخطأ
DEV_USERNAME = "@Mahmoued\_sniper" 

bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = "sniper_database.json"

admin_states = {}

# ==========================================
# 📂 قاعدة البيانات (Database)
# ==========================================
def load_db():
    default_db = {"blacklist": [], "whitelist": [], "known_groups": []}
    if not os.path.exists(DB_FILE): return default_db
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key in default_db:
                if key not in data: data[key] = default_db[key]
            return data
    except: return default_db

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def track_group(chat_id):
    db = load_db()
    chat_id_str = str(chat_id)
    if chat_id_str not in db['known_groups']:
        db['known_groups'].append(chat_id_str)
        save_db(db)

# ==========================================
# 🧠 أدوات التحليل (AI Tools)
# ==========================================
def clean_text(text):
    return unidecode(text or "").lower().strip()

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# دالة حماية الأسماء من الأخطاء (جديدة)
def escape_markdown(text):
    # تقوم هذه الدالة بإبطال مفعول الرموز التي تسبب تعليق البوت
    return text.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")

# ==========================================
# ☢️ بروتوكول الحظر الشامل (Global Strike)
# ==========================================
def execute_global_ban(user, reason_msg):
    db = load_db()
    if user.id not in db['blacklist']:
        db['blacklist'].append(user.id)
        save_db(db)

    safe_name = escape_markdown(user.first_name)
    
    warning_text = (
        f"🚨 **تحذير أمني عام | Sniper Security** 🚨\n\n"
        f"⚠️ **تم رصد وإسقاط منتحل شخصية خطير!**\n"
        f"قام النظام بحظره تلقائياً من جميع المجموعات المشتركة.\n\n"
        f"👤 **بيانات المحظور:**\n"
        f"• الاسم: {safe_name}\n"
        f"• الآيدي: `{user.id}`\n"
        f"• التهمة: {reason_msg}\n\n"
        f"🛡️ **حالة النظام:** آمن ✅\n"
        f"👨‍💻 **تطوير وإدارة:** {DEV_USERNAME}"
    )

    groups = db['known_groups']
    count = 0
    for group_id in groups:
        try:
            bot.ban_chat_member(group_id, user.id, revoke_messages=True)
            bot.send_message(group_id, warning_text, parse_mode="Markdown")
            count += 1
        except: pass
    return count

# ==========================================
# 👋 رسالة الترحيب (/start)
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
        f"🦅 **أهلاً بك في نظام Sniper Security**\n\n"
        f"🛡️ أنا بوت حماية متطور يعمل بالذكاء الاصطناعي.\n"
        f"⚡ وظيفتي: كشف منتحلي الشخصية وحماية المشرفين تلقائياً.\n\n"
        f"📜 **كيف أعمل؟**\n"
        f"1. أضفني لمجموعتك.\n"
        f"2. ارفعني مشرفاً (Admin).\n"
        f"3. سأقوم بحماية الطاقم تلقائياً.\n\n"
        f"👨‍💻 المطور: {DEV_USERNAME}",
        parse_mode="Markdown"
    )

# ==========================================
# 🎮 لوحة التحكم (Control Panel)
# ==========================================
@bot.message_handler(commands=['panel'])
def open_panel(message):
    if message.from_user.id != OWNER_ID: return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("⛔ حظر عام (Blacklist)", callback_data="add_black"),
        types.InlineKeyboardButton("✅ استثناء (Whitelist)", callback_data="add_white"),
        types.InlineKeyboardButton("📊 الإحصائيات", callback_data="show_lists"),
        types.InlineKeyboardButton("🔐 إغلاق النظام", callback_data="close_panel")
    )
    bot.reply_to(message, f"👋 **لوحة تحكم Sniper System:**\n👨‍💻 المطور: {DEV_USERNAME}", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    if user_id != OWNER_ID: return

    if call.data == "add_black":
        admin_states[user_id] = "waiting_blacklist"
        bot.edit_message_text("💀 **أرسل ID الهدف لحظره عاماً:**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    elif call.data == "add_white":
        admin_states[user_id] = "waiting_whitelist"
        bot.edit_message_text("🛡️ **أرسل ID للعفو عنه (Whitelist):**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    elif call.data == "show_lists":
        db = load_db()
        msg = (f"⚫ المحظورين: `{len(db['blacklist'])}`\n"
               f"⚪ الموثوقين: `{len(db['whitelist'])}`\n"
               f"📢 المجموعات المؤمنة: `{len(db['known_groups'])}`")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    elif call.data == "back_main":
        open_panel(call.message)
    elif call.data == "close_panel":
        admin_states.pop(user_id, None)
        bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.from_user.id in admin_states)
def handle_admin_input(message):
    state = admin_states[message.from_user.id]
    try: target_id = int(message.text.strip())
    except: return bot.reply_to(message, "⚠️ أرقام فقط (ID).")
    
    db = load_db()
    if state == "waiting_blacklist":
        bot.reply_to(message, "⏳ **جاري تنفيذ بروتوكول الحظر الشامل...**")
        class DummyUser:
            id = target_id
            first_name = "مستخدم (يدوي)"
        count = execute_global_ban(DummyUser(), "قرار يدوي من المطور")
        bot.reply_to(message, f"✅ تمت الإبادة! تم الحظر في {count} مجموعة.")
    elif state == "waiting_whitelist":
        if target_id not in db['whitelist']:
            db['whitelist'].append(target_id)
            if target_id in db['blacklist']: db['blacklist'].remove(target_id)
            save_db(db)
            bot.reply_to(message, f"✅ تمت الإضافة للبيضاء: `{target_id}`", parse_mode="Markdown")
    admin_states.pop(message.from_user.id, None)

# ==========================================
# 🚨 الرادار التلقائي + الفحص الأمني
# ==========================================
@bot.message_handler(content_types=['new_chat_members'])
def check_new_members(message):
    chat_id = message.chat.id
    bot_id = bot.get_me().id

    # --- 1. الفحص الأمني: هل البوت هو من دخل؟ ---
    for user in message.new_chat_members:
        if user.id == bot_id:
            try:
                admins = bot.get_chat_administrators(chat_id)
                owner_is_admin = False
                for admin in admins:
                    if admin.user.id == OWNER_ID:
                        owner_is_admin = True
                        break
                
                if not owner_is_admin:
                    bot.send_message(chat_id, 
                        f"⛔ **تنبيه هام:**\n\n"
                        f"يجب إضافة المالك {DEV_USERNAME} مشرفاً حتى أعمل معك.\n"
                        f"👋 **سأغادر الآن...**",
                        parse_mode="Markdown"
                    )
                    bot.leave_chat(chat_id)
                    return 
                else:
                    bot.send_message(chat_id, 
                        f"✅ **تم التحقق!**\n"
                        f"المالك موجود.\n"
                        f"🦅 **نظام Sniper يعمل الآن.**",
                        parse_mode="Markdown"
                    )
                    track_group(chat_id)
            except:
                bot.send_message(chat_id, "⚠️ يجب رفع البوت مشرفاً (Admin) لكي أتمكن من التحقق من وجود المالك.")
            return

    # --- 2. كود الحماية (باقي الأعضاء) ---
    track_group(chat_id)
    db = load_db()
    
    try: chat_admins = bot.get_chat_administrators(chat_id)
    except: return 

    for user in message.new_chat_members:
        if user.id in db['whitelist']: continue
        
        safe_user_name = escape_markdown(user.first_name)

        if user.id in db['blacklist']:
            try:
                bot.ban_chat_member(chat_id, user.id, revoke_messages=True)
                bot.send_message(chat_id, 
                    f"⛔ **تم التصدي لمتسلل!**\n\n"
                    f"العضو **{safe_user_name}** مدرج في القائمة السوداء العامة.\n"
                    f"🛡️ **الإجراء:** طرد تلقائي.\n"
                    f"🔒 **محمية بواسطة:** {DEV_USERNAME}",
                    parse_mode="Markdown")
            except: pass
            continue

        new_name = clean_text(f"{user.first_name} {user.last_name or ''}")
        
        for admin in chat_admins:
            if user.id == admin.user.id or admin.user.is_bot: continue
            real_name = clean_text(f"{admin.user.first_name} {admin.user.last_name or ''}")
            
            safe_admin_name = escape_markdown(admin.user.first_name)

            if similar(new_name, real_name) > 0.80:
                bot.send_message(chat_id, "⚡ **تم كشف تهديد أمني! جاري تفعيل بروتوكول الحظر الشامل...**")
                
                affected = execute_global_ban(user, f"انتحال صفة المشرف: {safe_admin_name}")
                
                bot.send_message(chat_id, 
                    f"🎯 **Sniper Headshot!**\n\n"
                    f"👮‍♂️ **تم كشف محاولة انتحال شخصية.**\n"
                    f"🤥 **الدخيل:** {safe_user_name}\n"
                    f"🎭 **يحاول تقليد:** {safe_admin_name}\n\n"
                    f"🚫 **الإجراء المتخذ:**\n"
                    f"1. حظر نهائي وتعميمه ({affected} مجموعة) 🌍\n"
                    f"2. حذف جميع رسائله 🗑️\n\n"
                    f"🤖 **Sniper System By:** {DEV_USERNAME}",
                    parse_mode="Markdown"
                )
                break 

@bot.message_handler(commands=['id'])
def show_id(message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    safe_name = escape_markdown(target.first_name)
    bot.reply_to(message, 
        f"🕵️‍♂️ **بطاقة التعريف الرقمية | Sniper ID**\n\n"
        f"🆔 **ID:** `{target.id}`\n"
        f"👤 **Name:** {safe_name}\n"
        f"🔗 **User:** @{target.username}\n\n"
        f"📡 **Status:** Active\n"
        f"👨‍💻 **Dev:** {DEV_USERNAME}", 
        parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def record_group(message):
    if message.chat.type in ['group', 'supergroup']:
        track_group(message.chat.id)

print("✅ Sniper System Activated (Fixed Markdown Error)...")
bot.infinity_polling()
