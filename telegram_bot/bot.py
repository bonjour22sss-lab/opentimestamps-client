import logging
import os
import io
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler
from telegram_bot.config import get_telegram_token
from telegram_bot.ots_utils import stamp_data

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Try to get the best file representation
    message = update.message
    if not message:
        return

    document = message.document
    photo = message.photo
    video = message.video
    audio = message.audio

    file_to_download = None
    file_name = "file"

    if document:
        file_to_download = document
        file_name = document.file_name
    elif photo:
        file_to_download = photo[-1] # Get largest photo
        file_name = f"photo_{message.message_id}.jpg"
    elif video:
        file_to_download = video
        file_name = video.file_name or f"video_{message.message_id}.mp4"
    elif audio:
        file_to_download = audio
        file_name = audio.file_name or f"audio_{message.message_id}.mp3"

    if not file_to_download:
        return

    await message.reply_text(f"Timestamping {file_name}...")

    try:
        file = await file_to_download.get_file()
        file_bytes = await file.download_as_bytearray()

        ots_data = stamp_data(bytes(file_bytes))

        ots_file = io.BytesIO(ots_data)
        ots_file.name = f"{file_name}.ots"

        await message.reply_document(
            document=ots_file,
            filename=f"{file_name}.ots",
            caption="Here is your OpenTimestamps proof!"
        )
    except Exception as e:
        logging.error(f"Error timestamping: {e}")
        await message.reply_text(f"Error timestamping file: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me any file and I will timestamp it using OpenTimestamps.")

if __name__ == '__main__':
    token = get_telegram_token()
    if not token:
        print("TELEGRAM_BOT_TOKEN not found in .env. Please set it to run the Telegram bot.")
        # We don't exit here if we are just importing it or something, but since this is __main__...
        exit(1)

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, handle_file))

    print("Telegram bot started...")
    application.run_polling()
