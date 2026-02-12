import asyncio
from nostr_sdk import (
    Client, Filter, Kind, KindStandard,
    EventBuilder,
    HandleNotification,
    LogLevel,
    init_logger,
    NostrSigner,
    RelayUrl
)
from nostr_bot.config import get_keys, RELAYS
from nostr_bot.ots_utils import stamp_event_id
from nostr_bot.database import init_db, save_timestamp
from nostr_bot.upgrade_task import run_upgrade_task

class BotNotificationHandler(HandleNotification):
    def __init__(self, client, bot_keys):
        self.client = client
        self.bot_keys = bot_keys

    async def handle(self, relay_url, subscription_id, event):
        # Kind 1 is Short Text Note
        if event.kind().as_std() == KindStandard.TEXT_NOTE:
            # Check if bot is mentioned
            bot_pubkey = self.bot_keys.public_key()
            is_mentioned = False
            for tag in event.tags():
                t_list = tag.as_vec()
                if len(t_list) >= 2 and t_list[0] == "p" and t_list[1] == bot_pubkey.to_hex():
                    is_mentioned = True
                    break

            if is_mentioned:
                print(f"Bot mentioned in event {event.id().to_hex()}")
                await self.process_mention(event)

    async def process_mention(self, event):
        event_id_hex = event.id().to_hex()

        try:
            print(f"Timestamping event {event_id_hex}...")
            ots_hex = stamp_event_id(event_id_hex)

            reply_content = f"Timestamp created for this event ID ({event_id_hex}).\n\nOpenTimestamps proof (hex):\n{ots_hex}"

            # Create reply event using text_note_reply (handles NIP-10)
            builder = EventBuilder.text_note_reply(reply_content, event)
            reply_event = builder.sign_with_keys(self.bot_keys)

            await self.client.send_event(reply_event)

            # Save to DB for future upgrading
            save_timestamp(event_id_hex, reply_event.id().to_hex(), ots_hex)
            print(f"Reply sent: {reply_event.id().to_hex()}")

        except Exception as e:
            print(f"Error processing mention: {e}")
            import traceback
            traceback.print_exc()

    async def handle_msg(self, relay_url, msg):
        pass

async def main():
    init_logger(LogLevel.INFO)
    keys = get_keys()
    signer = NostrSigner.keys(keys)
    init_db()

    client = Client(signer)
    for relay in RELAYS:
        await client.add_relay(RelayUrl.parse(relay))

    await client.connect()

    # Subscribe to mentions
    bot_pubkey = keys.public_key()
    mention_filter = Filter().pubkey(bot_pubkey).kind(Kind.from_std(KindStandard.TEXT_NOTE))
    await client.subscribe(mention_filter)

    print(f"Bot started. Public key: {bot_pubkey.to_bech32()}")

    # Start the upgrade task in the background
    asyncio.create_task(run_upgrade_task(client, keys))

    handler = BotNotificationHandler(client, keys)
    await client.handle_notifications(handler)

if __name__ == "__main__":
    asyncio.run(main())
