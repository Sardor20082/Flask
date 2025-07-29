from flask import Flask, request
import config
import handlers

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot ishlayapti!'

@app.route(f"/{config.BOT_TOKEN}", methods=['POST'])
def webhook():
    if request.method == "POST":
        update = request.get_json()
        handlers.handle_update(update)
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
