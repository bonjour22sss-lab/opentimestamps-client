import os
from dotenv import load_dotenv
from nostr_sdk import Keys, SecretKey

load_dotenv()

def get_keys():
    nsec = os.getenv("NOSTR_PRIVATE_KEY")
    if nsec:
        try:
            return Keys.parse(nsec)
        except Exception as e:
            print(f"Error loading NOSTR_PRIVATE_KEY from .env: {e}")
            print("Generating a new one...")

    # Generate new keys
    keys = Keys.generate()
    nsec_str = keys.secret_key().to_bech32()

    # Save to .env if it doesn't exist or is invalid
    with open(".env", "a") as f:
        f.write(f"\nNOSTR_PRIVATE_KEY={nsec_str}\n")

    print(f"Generated new key: {keys.public_key().to_bech32()}")
    print("Saved to .env")
    return keys

RELAYS = [
    "wss://nos.lol",
    "wss://relay.damus.io",
    "wss://relay.snort.social",
    "wss://relay.primal.net",
    "wss://offchain.pub"
]

DB_PATH = "nostr_bot/bot_data.db"
UPGRADE_INTERVAL_HOURS = 6
