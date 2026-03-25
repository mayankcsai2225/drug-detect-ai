from telethon import TelegramClient, errors, functions
import logging
import asyncio
from typing import List, Dict, Any, Optional
from app.config import settings
import os

logger = logging.getLogger(__name__)

SESSION_NAME = "ncb_drugnet_telegram"

async def get_telegram_client() -> Optional[TelegramClient]:
    """
    Initializes and returns an authenticated Telegram client.
    """
    if not settings.telegram_api_id or not settings.telegram_api_hash:
        logger.error("Telegram API credentials missing")
        return None
        
    client = TelegramClient(SESSION_NAME, int(settings.telegram_api_id), settings.telegram_api_hash)
    await client.start()
    return client

async def scrape_public_channel(channel_url: str, limit: int = 500) -> List[Dict[str, Any]]:
    """
    Fetches the last 500 messages from a public Telegram channel.
    Only operates on public data.
    """
    client = await get_telegram_client()
    if not client:
        return []

    messages_data = []
    
    try:
        # Resolve the channel entity
        entity = await client.get_entity(channel_url)
        
        # We only scrape if it's public (handled by get_entity for public URLs)
        # Fetch messages
        async for message in client.iter_messages(entity, limit=limit):
            msg_id = message.id
            text = message.text or ""
            date = message.date.isoformat()
            sender = await message.get_sender()
            sender_handle = sender.username if sender and hasattr(sender, 'username') else "anonymous"
            
            image_path = None
            if message.photo:
                # Save to /tmp
                file_name = f"tg_{msg_id}.jpg"
                image_path = os.path.join("/tmp", file_name)
                # Keep download off primary event loop
                await client.download_media(message.photo, file_path=image_path)
            
            messages_data.append({
                "platform": "telegram",
                "post_url": f"{channel_url}/{msg_id}",
                "raw_text": text,
                "captured_at": date,
                "handle": channel_url.split('/')[-1],
                "sender_username": sender_handle,
                "image_path": image_path,
                "has_image": bool(image_path)
            })
            
    except errors.FloodWaitError as e:
        logger.warning(f"Flood wait error: waiting for {e.seconds}s")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        logger.error(f"Error scraping telegram channel {channel_url}: {e}")
    finally:
        await client.disconnect()
        
    return messages_data

def discover_new_channels(text: str) -> List[str]:
    """
    Scans message text for related t.me links for potential new targets.
    """
    import re
    links = re.findall(r't\.me\/([a-zA-Z0-9_]+)', text)
    return [f"https://t.me/{link}" for link in links]
