# OpenTimestamps Telegram Bot

A standalone Telegram bot that timestamps files using OpenTimestamps.

## Features

- **File Timestamping**: Send any file (document, photo, video, audio) to the bot, and it will reply with a `.ots` proof file.

## Installation

```bash
pip install python-telegram-bot python-dotenv opentimestamps opentimestamps-client
```

## Configuration

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

## Running the Bot

```bash
python3 -m telegram_bot.bot
```
