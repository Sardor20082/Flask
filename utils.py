import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ChatMember

def get_lang(user_id):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, lang TEXT, added DATE DEFAULT CURRENT_DATE)")
    cur.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else "uz"

def save_user(user_id, lang="uz"):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, lang) VALUES (?, ?)", (user_id, lang))
    conn.commit()
    conn.close()

def choose_language_handler(update, context):
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Tilni tanlang:", reply_markup=reply_markup)

def lang_callback_handler(update, context):
    query = update.callback_query
    lang = query.data.split("_")[1]
    save_user(query.from_user.id, lang)

    from languages import LANGUAGES
    keyboard = [
        [InlineKeyboardButton("YouTube", callback_data="platform_youtube")],
        [InlineKeyboardButton("TikTok", callback_data="platform_tiktok")],
        [InlineKeyboardButton("Instagram", callback_data="platform_instagram")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(LANGUAGES[lang]['choose_platform'], reply_markup=reply_markup)

def check_channel_subscription(update):
    try:
        with open("channel.txt", "r") as f:
            channel = f.read().strip()
    except:
        return True  # kanal yo‘q bo‘lsa, tekshirmaymiz

    user = update.effective_user
    bot = update.get_bot()
    try:
        member = bot.get_chat_member(chat_id=channel, user_id=user.id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except:
        return False
