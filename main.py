import os
from telethon import TelegramClient, events
from quart import Quart, Response
import asyncio

# Environment Variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Quart(__name__)
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@app.route('/')
async def index():
    return "2GB+ Streaming Server is Active!"

@app.route('/stream/<int:msg_id>')
async def stream(msg_id):
    channel_id = int(os.getenv("CHANNEL_ID"))
    try:
        msg = await client.get_messages(channel_id, ids=msg_id)
        if not msg or not msg.file:
            return "File not found", 404

        async def gen():
            async for chunk in client.iter_download(msg.media, chunk_size=1024*1024):
                yield chunk

        return Response(gen(), headers={
            'Content-Type': msg.file.mime_type,
            'Content-Length': str(msg.file.size),
            'Accept-Ranges': 'bytes',
            'Content-Disposition': f'attachment; filename="{msg.file.name}"'
        })
    except Exception as e:
        return f"Error: {str(e)}", 500

@client.on(events.NewMessage)
async def handler(event):
    if event.video:
        # Render ကပေးတဲ့ URL ကို သုံးမှာဖြစ်လို့ Environment variable ထဲမှာ RENDER_EXTERNAL_HOSTNAME ပါရပါမယ်
        host = os.getenv('RENDER_EXTERNAL_HOSTNAME', 'your-app.onrender.com')
        link = f"https://{host}/stream/{event.message.id}"
        await event.reply(f"✅ Direct Link (2GB Support):\n\n{link}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    client.loop.run_until_complete(uvicorn.run(app, host="0.0.0.0", port=port))
