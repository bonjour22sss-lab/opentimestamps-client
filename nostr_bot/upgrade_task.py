import asyncio
import time
from nostr_sdk import (
    Client, Keys, EventBuilder, Tag, NostrSigner
)
from nostr_bot.config import get_keys, RELAYS, UPGRADE_INTERVAL_HOURS
from nostr_bot.database import get_pending_upgrades, mark_as_upgraded, update_last_attempt
from nostr_bot.ots_utils import upgrade_ots_data

async def run_upgrade_task(client, keys):
    while True:
        print("Checking for timestamps to upgrade...")
        pending = get_pending_upgrades()

        for event_id, initial_reply_id, ots_data in pending:
            try:
                print(f"Attempting to upgrade timestamp for event {event_id}...")
                new_ots_hex, is_complete = upgrade_ots_data(ots_data)

                if new_ots_hex:
                    print(f"Successfully upgraded timestamp for event {event_id}!")

                    # Send a reply to the initial reply
                    reply_content = f"Timestamp upgraded for event {event_id}.\n\nIt is now confirmed in the Bitcoin blockchain!\n\nUpgraded OpenTimestamps proof (hex):\n{new_ots_hex}"

                    tags = [
                        Tag.parse(["e", initial_reply_id, "", "reply"]),
                        Tag.parse(["e", event_id, "", "root"]), # Keep track of the root event
                    ]

                    reply_event = EventBuilder.text_note(reply_content).tags(tags).sign_with_keys(keys)
                    await client.send_event(reply_event)

                    mark_as_upgraded(event_id, new_ots_hex)
                    print(f"Upgrade notification sent: {reply_event.id().to_hex()}")
                else:
                    print(f"No upgrade available yet for event {event_id}.")
                    update_last_attempt(event_id)

            except Exception as e:
                print(f"Error upgrading timestamp for event {event_id}: {e}")

        print(f"Upgrade task finished. Sleeping for {UPGRADE_INTERVAL_HOURS} hours...")
        await asyncio.sleep(UPGRADE_INTERVAL_HOURS * 3600)

if __name__ == "__main__":
    # For standalone testing if needed
    async def main():
        keys = get_keys()
        signer = NostrSigner.keys(keys)
        client = Client(signer)
        for relay in RELAYS:
            await client.add_relay(relay)
        await client.connect()
        await run_upgrade_task(client, keys)

    asyncio.run(main())
