import os
from quart import Quart, Response
from telethon import TelegramClient

app = Quart(__name__)

# Telegram ကရတဲ့ API ID နဲ့ HASH ကို ဒီမှာထည့်ပါ (သို့မဟုတ် Environment Variable သုံးပါ)
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

@app.route('/stream/<int:msg_id>')
async def stream(msg_id):
    # သင်ရေးထားတဲ့ အောက်က code တွေ ဒီမှာ ဆက်လာပါမယ်...
    # channel_id = ... စတာတွေပေါ့
