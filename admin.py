import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from languages import LANGUAGES
from utils import get_lang

ADMIN_ID = int(os.getenv("ADMIN_ID", "123456"))

def admin_panel_handler(update, context):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if user_id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton(LANGUAGES[lang]['stats'], callback_data="stats")],
        [InlineKeyboardButton(LANGUAGES[lang]['broadcast'], callback_data="broadcast")],
        [InlineKeyboardButton(LANGUAGES[lang]['set_channel'], callback_data="set_channel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(LANGUAGES[lang]['admin_panel'], reply_markup=reply_markup)

def stats_handler(update, context):
    query = update.callback_query
    lang = get_lang(query.from_user.id)

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE DATE(added)=DATE('now')")
    today = cur.fetchone()[0]
    conn.close()

    text = LANGUAGES[lang]['total_users'].format(total) + "\n" + LANGUAGES[lang]['new_today'].format(today)
    query.edit_message_text(text)

def broadcast_handler(update, context):
    query = update.callback_query
    lang = get_lang(query.from_user.id)
    context.user_data['broadcast'] = True
    query.edit_message_text(LANGUAGES[lang]['send_broadcast'])

def set_channel_handler(update, context):
    query = update.callback_query
    lang = get_lang(query.from_user.id)
    context.user_data['set_channel'] = True
    query.edit_message_text("✏️ Yangi kanal username yoki ID ni kiriting:")

def handle_text_admin(update, context):
    user_id = update.effective_user.id
    lang = get_lang(user_id)

    if context.user_data.get('broadcast'):
        context.user_data['broadcast'] = False
        text = update.message.text

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users")
        users = cur.fetchall()
        conn.close()

        for (uid,) in users:
            try:
                context.bot.send_message(chat_id=uid, text=text)
            except:
                pass

        update.message.reply_text(LANGUAGES[lang]['message_sent'])

    elif context.user_data.get('set_channel'):
        context.user_data['set_channel'] = False
        new_channel = update.message.text.strip()
        with open("channel.txt", "w") as f:
            f.write(new_channel)
        update.message.reply_text(LANGUAGES[lang]['channel_updated'])
