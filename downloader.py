import os
import tempfile
import yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from languages import LANGUAGES
from utils import get_lang, save_user

def platform_selector_handler(update, context):
    query = update.callback_query
    lang = get_lang(query.from_user.id)
    query.edit_message_text(LANGUAGES[lang]['send_link'])

def download_video_handler(update, context):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    save_user(user_id)

    if update.message:
        url = update.message.text.strip()
        context.user_data['video_url'] = url
        update.message.reply_text(LANGUAGES[lang]['downloading'])

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                    'noplaylist': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    formats = info.get("formats", [])
                    keyboard = []

                    for fmt in formats:
                        if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none' and fmt.get('filesize'):
                            size_mb = round(fmt['filesize'] / (1024 * 1024), 1)
                            text = f"{fmt['format_note']} - {size_mb}MB"
                            callback_data = f"quality_{fmt['format_id']}"
                            keyboard.append([InlineKeyboardButton(text, callback_data=callback_data)])

                    reply_markup = InlineKeyboardMarkup(keyboard)
                    update.message.reply_text(LANGUAGES[lang]['quality_select'], reply_markup=reply_markup)
                    context.user_data['video_info'] = info

        except Exception as e:
            update.message.reply_text("❌ Xatolik yoki video topilmadi.")

    elif update.callback_query:
        query = update.callback_query
        fmt_id = query.data.split("_")[1]
        info = context.user_data.get("video_info")
        url = context.user_data.get("video_url")

        if not info or not url:
            query.edit_message_text("❌ Video topilmadi.")
            return

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {
                    'format': fmt_id,
                    'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                    'noplaylist': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    for fname in os.listdir(tmpdir):
                        file_path = os.path.join(tmpdir, fname)
                        with open(file_path, 'rb') as f:
                            query.message.reply_video(video=f)
        except Exception:
            query.message.reply_text("❌ Yuklab olishda xatolik.")
