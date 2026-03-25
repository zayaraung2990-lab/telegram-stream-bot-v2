import os
from quart import Quart, Response
from telethon import TelegramClient

app = Quart(__name__)

# Environment Variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@app.route('/')
async def index():
    return "Bot is Running Live!"

@app.route('/stream/<int:msg_id>')
async def stream(msg_id):
    channel_id = int(os.getenv("CHANNEL_ID"))
    try:
        # Client connect ဖြစ်မဖြစ် အရင်စစ်မယ်
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
            'Content-Disposition': f'attachment; filename="{msg.file.name}"'
        })
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
