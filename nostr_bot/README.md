# OpenTimestamps Nostr Bot

A standalone Nostr bot that timestamps events using OpenTimestamps.

## Features

- **Automatic Timestamping**: When the bot is mentioned in a note, it timestamps the event ID and replies with the initial `.ots` proof (hex encoded).
- **Periodic Upgrades**: Every hour, the bot checks for pending timestamps and attempts to upgrade them to include Bitcoin block attestations.
- **Persistent State**: Uses SQLite to track pending upgrades.
- **Easy Identity Management**: Generates a Nostr key pair on first run if not provided in `.env`.

## Installation

```bash
pip install nostr-sdk python-dotenv opentimestamps opentimestamps-client
```

## Configuration

Create a `.env` file in the project root:

```env
NOSTR_PRIVATE_KEY=nsec1... # Optional, will be generated if missing
```

## Running the Bot

```bash
python3 -m nostr_bot.bot
```
