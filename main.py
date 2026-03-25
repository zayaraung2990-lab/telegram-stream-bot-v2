import os
import asyncio
import uvicorn
from quart import Quart, Response
from telethon import TelegramClient, events

app = Quart(__name__)

# Environment Variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")

client = TelegramClient('bot_session', API_ID, API_HASH)

# --- BOT SECTION: Link ထုတ်ပေးမည့်အပိုင်း ---
@client.on(events.NewMessage)
async def link_handler(event):
    if event.message.file:
        msg_id = event.message.id
        # Direct Link တည်ဆောက်ခြင်း
        stream_link = f"https://{RENDER_HOST}/stream/{msg_id}"
        await event.reply(f"🎬 **သင့်ဗီဒီယိုအတွက် Direct Link:**\n\n`{stream_link}`")
    elif event.raw_text == "/start":
        await event.reply("Welcome! ဗီဒီယိုဖိုင်တစ်ခု ပို့ပေးပါ၊ ကျွန်တော် Direct Link ထုတ်ပေးပါ့မယ်။")

# --- SERVER SECTION: ဗီဒီယိုပြသမည့်အပိုင်း ---
@app.route('/')
async def index():
    return "Bot is Running Live!"

@app.route('/stream/<int:msg_id>')
async def stream(msg_id):
    channel_id = int(os.getenv("CHANNEL_ID"))
    try:
        if not client.is_connected():
            await client.connect()
        
        msg = await client.get_messages(channel_id, ids=msg_id)
        if not msg or not msg.file:
            return "File not found", 404

        async def gen():
            async for chunk in client.iter_download(msg.media, chunk_size=1024*512):
                yield chunk

        return Response(gen(), headers={
            'Content-Type': msg.file.mime_type,
            'Content-Length': str(msg.file.size),
            'Accept-Ranges': 'bytes',
        })
    except Exception as e:
        return str(e), 500

async def main():
    await client.start(bot_token=BOT_TOKEN)
    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
