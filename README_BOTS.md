# OpenTimestamps Bots

This project provides bots for Nostr and Telegram that allow users to timestamp data using the OpenTimestamps protocol.

## Features

- **Nostr Bot**:
  - **Automatic Timestamping**: When the bot is mentioned in a note, it timestamps the event ID and replies with the initial `.ots` proof (hex encoded).
  - **Periodic Upgrades**: Every hour, the bot checks for pending timestamps and attempts to upgrade them to include Bitcoin block attestations.
  - **Persistent State**: Uses SQLite to track pending upgrades.
- **Telegram Bot**:
  - **File Timestamping**: Send any file (document, photo, video, audio) to the bot, and it will reply with a `.ots` proof file.

## Installation

Ensure you have the dependencies installed:

```bash
pip install nostr-sdk python-dotenv opentimestamps opentimestamps-client python-telegram-bot
```

## Configuration

Create a `.env` file in the root directory:

```env
# Nostr Configuration
NOSTR_PRIVATE_KEY=nsec1... # Optional, will be generated if missing

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

## Running the Bots

### Nostr Bot
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 nostr_bot/bot.py
```

### Telegram Bot
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 telegram_bot/bot.py
```

## Project Structure

- `nostr_bot/`: Nostr-specific logic.
- `telegram_bot/`: Telegram-specific logic.
- `nostr_bot/ots_utils.py`: Shared OpenTimestamps integration logic.
- `nostr_bot/database.py`: Shared SQLite database layer.
