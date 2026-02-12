# OpenTimestamps Nostr Bot

A Nostr bot that timestamps events using OpenTimestamps.

## Features

- **Automatic Timestamping**: When the bot is mentioned in a note, it timestamps the event ID and replies with the initial `.ots` proof (hex encoded).
- **Periodic Upgrades**: Every 6 hours, the bot checks for pending timestamps and attempts to upgrade them to include Bitcoin block attestations.
- **Persistent State**: Uses SQLite to track pending upgrades.
- **Easy Identity Management**: Generates a Nostr key pair on first run if not provided in `.env`.

## Installation

Ensure you have the dependencies installed:

```bash
pip install nostr-sdk python-dotenv opentimestamps opentimestamps-client
```

## Running the Bot

1. Set your Nostr private key in a `.env` file (optional):
   ```
   NOSTR_PRIVATE_KEY=nsec1...
   ```
2. Run the bot:
   ```bash
   python3 -m nostr_bot.bot
   ```

## Files

- `bot.py`: Main entry point, handles Nostr connection and mentions.
- `ots_utils.py`: OpenTimestamps integration logic.
- `database.py`: SQLite database layer for persistence.
- `upgrade_task.py`: Periodic task for upgrading timestamps.
- `config.py`: Configuration and identity management.
