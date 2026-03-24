@app.route('/stream/<int:msg_id>')
async def stream(msg_id):
    channel_id = int(os.getenv("CHANNEL_ID"))
    try:
        # client က login ဝင်ထားခြင်း ရှိမရှိ အရင်စစ်မယ်
        if not client.is_connected():
            await client.connect()
            
        msg = await client.get_messages(channel_id, ids=msg_id)
        
        if not msg or not msg.file:
            print(f"Error: Message {msg_id} not found in channel {channel_id}")
            return "File not found", 404

        async def gen():
            async for chunk in client.iter_download(msg.media, chunk_size=1024*512): # chunk size ကို နည်းနည်းလျှော့လိုက်တယ်
                yield chunk

        return Response(gen(), headers={
            'Content-Type': msg.file.mime_type,
            'Content-Length': str(msg.file.size),
            'Accept-Ranges': 'bytes',
            'Content-Disposition': f'attachment; filename="{msg.file.name}"'
        })
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}") # ဒီစာသားက Logs ထဲမှာ အဖြေပေးပါလိမ့်မယ်
        return f"Error: {str(e)}", 500
