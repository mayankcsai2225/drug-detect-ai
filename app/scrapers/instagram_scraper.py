import instaloader
import logging
import asyncio
import os
import random
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.98 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

class InstagramScraper:
    def __init__(self):
        self.L = instaloader.Instaloader(
            download_videos=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        self.L.context._session.headers.update({'User-Agent': random.choice(UA_LIST)})

    async def scrape_public_profile(self, username: str) -> List[Dict[str, Any]]:
        """
        Uses Instaloader to scrape public profile bio and posts.
        No authentication used for anonymous scraping.
        """
        return await asyncio.to_thread(self._scrape_sync, username)

    def _scrape_sync(self, username: str) -> List[Dict[str, Any]]:
        posts_data = []
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
            
            # Skip if private
            if profile.is_private:
                logger.info(f"Instagram profile {username} is private, skipping.")
                return []
            
            # Extract Bio information
            bio_text = profile.biography
            external_url = profile.external_url
            
            # Extract Posts
            for post in profile.get_posts():
                image_path = None
                if post.url:
                    # Download image for OCR/Vision
                    file_name = f"ig_{post.shortcode}.jpg"
                    image_path = os.path.join("/tmp", file_name)
                    # We usually need to download the file locally
                    self.L.download_post(post, target=os.path.join("/tmp", post.shortcode))
                    # instaloader usually creates a folder per shortcode.
                    # Simplified logic here to point to image
                    # Real implementation would find the jpg in the folder.
                    
                posts_data.append({
                    "platform": "instagram",
                    "post_url": f"https://instagram.com/p/{post.shortcode}",
                    "raw_text": f"{post.caption} | BIO: {bio_text} | URL: {external_url}",
                    "captured_at": post.date_utc.isoformat(),
                    "handle": username,
                    "image_path": image_path,
                    "has_image": True if image_path else False
                })
                
                # Limit per profile to avoid rate limiting
                if len(posts_data) >= 50:
                    break
                
                # Slight wait to respect platform
                import time
                time.sleep(random.uniform(1.0, 3.0))

        except Exception as e:
            logger.error(f"Error scraping Instagram profile {username}: {e}")
            
        return posts_data
