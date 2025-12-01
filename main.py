from json import JSONDecodeError
import json
import telebot # type: ignore
# from Telebot.util import user_link # type: ignore
from telebot import types # type: ignore



TOKEN = "8446867334:AAHRFFTZ6lC7TX8tl1hfVq0xDt_IobULEoQ" 
bot = telebot.TeleBot(TOKEN)

# ===================== ADMIN SYSTEM =====================
ADMINS = [5916640487] 
def is_admin(user_id):
    return user_id in ADMINS

# ===================== LOAD JSON =====================
with open("library.json", "r", encoding="utf-8") as f:
    LIBRARY = json.load(f)

def save_json():
    with open("library.json", "w", encoding="utf-8") as f:
        json.dump(LIBRARY, f, ensure_ascii=False, indent=2)

# ===================== MENUS =====================
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📘 المحتوى الأكاديمي", "🛩 نبذة عن جمعية هندسة الطيران")
    kb.add("👨‍💻 نبذة عن البوت والمطورين")
    return kb

def academic_menu():
    Kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    Kb.add("📚 المقررات", "📝المراجع")
    Kb.add("🔙 الرجوع")
    return Kb

def semester_menu():
    Kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for sem in LIBRARY.keys():
        Kb.add(sem)
    Kb.add("🔙 الرجوع")
    return Kb

def subject_sections():
    Kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    Kb.add("📖 محاضرات", "📄 شيتات")
    Kb.add("🧪 متابعات", "📝 امتحانات")
    Kb.add("🔙 الرجوع")
    return Kb

def review_menu():
    Kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    Kb.add("🔬 مراجع علمية", "📚 مراجع عامة")
    Kb.add("🔙 الرجوع")
    return Kb

# ===================== STATE TRACKERS =====================
CURRENT_SEMESTER = {}
CURRENT_SUBJECT = {}
CURRENT_SECTION = {}

# ===================== BOT LOGIC =====================
@bot.message_handler(commands=['start'])
def start(msg):
    if is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "مرحبًا أيها الأدمن 👑", reply_markup=main_menu())
    else:
        bot.send_message(msg.chat.id, "مرحبًا بك في مكتبة هندسة الطيران 🎓✈️", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def main_handler(msg):
    Text = msg.text
    Chat_id = msg.chat.id

    if Text == "📘 المحتوى الأكاديمي":
        bot.send_message(Chat_id, "اختر نوع المحتوى", reply_markup=academic_menu())

    elif Text == "📚 المقررات":
        bot.send_message(Chat_id, "اختر السمستر:", reply_markup=semester_menu())

    elif Text in LIBRARY.keys():
        CURRENT_SEMESTER[Chat_id] = Text
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for sub in LIBRARY[Text].keys():
            kb.add(sub)
        kb.add("🔙 الرجوع")
        bot.send_message(Chat_id, f"مواد {Text}:", reply_markup=kb)

    elif Chat_id in CURRENT_SEMESTER and Text in LIBRARY[CURRENT_SEMESTER[Chat_id]].keys():
        CURRENT_SUBJECT[Chat_id] = Text
        bot.send_message(Chat_id, f"اختر التقسيم لمادة: {Text}", reply_markup=subject_sections())

    elif Text in ["📖 محاضرات", "📄 شيتات", "🧪 متابعات", "📝 امتحانات"]:
        if not is_admin(msg.from_user.id):
            bot.send_message(Chat_id, "❌ هذه الخاصية متاحة للادمن فقط")
            return
        CURRENT_SECTION[Chat_id] = Text.lower()
        bot.send_message(Chat_id, f"الآن أرسل الملف ليتم حفظ file_id تلقائيًا في {Text}")

    elif Text == "📝 المراجع":
        bot.send_message(Chat_id, "اختر نوع المراجع:", reply_markup=review_menu())

    elif Text in ["🔬 مراجع علمية", "📚 مراجع عامة"]:
        if not is_admin(msg.from_user.id):
            bot.send_message(Chat_id, "❌ هذه الخاصية متاحة للادمن فقط")
            return
        CURRENT_SECTION[Chat_id] = Text.lower()
        bot.send_message(Chat_id, f"الآن أرسل الملف ليتم حفظ file_id تلقائيًا في {Text}")

    elif Text == "🛩 نبذة عن جمعية هندسة الطيران":
        bot.send_message(Chat_id, "هنا يمكنك إضافة نبذة عن الجمعية")

    elif Text == "👨‍💻 نبذة عن البوت والمطورين":
        bot.send_message(Chat_id, "هنا يمكنك إضافة نبذة عن البوت والمطورين")

    elif Text == "🔙 الرجوع":
        bot.send_message(Chat_id, "رجوع للقائمة الرئيسية", reply_markup=main_menu())

# ===================== RECEIVE FILES =====================
@bot.message_handler(content_types=['document', 'photo'])
def receive_file(msg):
    if not is_admin(msg.from_user.id):
        bot.send_message(msg.chat.id, "❌ هذه الخاصية متاحة للادمن فقط")
        return

    Chat_id = msg.chat.id
    Section = CURRENT_SECTION.get(Chat_id)
    Semester = CURRENT_SEMESTER.get(Chat_id)
    Subject = CURRENT_SUBJECT.get(Chat_id)

    if not Section or not Semester or not Subject:
        bot.send_message(Chat_id, "❌ الرجاء اختيار السمستر والمادة أولًا")
        return

    if msg.content_type == 'document':
        File_id = msg.document.file_id
    elif msg.content_type == 'photo':
        File_id = msg.photo[-1].file_id
    else:
        bot.send_message(Chat_id, "نوع الملف غير مدعوم")
        return

    # حفظ file_id تلقائيًا في JSON
    LIBRARY[Semester][Subject][Section] = File_id
    save_json()
    bot.send_message(Chat_id, f"✅ تم حفظ الملف بنجاح في {Section}")

# ===================== RUN BOT =====================
bot.infinity_polling()
