import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from admin import admin_panel_handler, broadcast_handler, stats_handler, set_channel_handler, handle_text_admin
from downloader import download_video_handler, platform_selector_handler
from utils import check_channel_subscription, choose_language_handler, get_lang, lang_callback_handler
from languages import LANGUAGES

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=4)

logging.basicConfig(level=logging.INFO)

dispatcher.add_handler(CommandHandler("start", choose_language_handler))
dispatcher.add_handler(CallbackQueryHandler(lang_callback_handler, pattern="^lang_"))
dispatcher.add_handler(CallbackQueryHandler(platform_selector_handler, pattern="^platform_"))
dispatcher.add_handler(CallbackQueryHandler(download_video_handler, pattern="^quality_"))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video_handler))

dispatcher.add_handler(CommandHandler("admin", admin_panel_handler))
dispatcher.add_handler(CallbackQueryHandler(stats_handler, pattern="^stats$"))
dispatcher.add_handler(CallbackQueryHandler(broadcast_handler, pattern="^broadcast$"))
dispatcher.add_handler(CallbackQueryHandler(set_channel_handler, pattern="^set_channel$"))
dispatcher.add_handler(MessageHandler(Filters.text & Filters.user(user_id=int(os.getenv("ADMIN_ID", "123456"))), handle_text_admin))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    if check_channel_subscription(update):
        dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot ishlayapti!"

if __name__ == "__main__":
    bot.delete_webhook()
    bot.set_webhook(url=os.getenv("WEBHOOK_URL") + f"/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
