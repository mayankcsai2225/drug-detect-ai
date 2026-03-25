import logging
import asyncio
from typing import List, Dict, Any
from app.database import get_supabase
from app.nlp.keyword_filter import check_keywords
from app.nlp.nlp_classifier import classify_text
from app.nlp.ocr_processor import extract_text_from_image
from app.nlp.vision_detector import detect_substances
from app.osint.osint_engine import extract_all_leads, calculate_post_hash, get_gps_data
from app.scrapers.telegram_scraper import scrape_public_channel
from app.scrapers.instagram_scraper import InstagramScraper
from datetime import datetime

logger = logging.getLogger(__name__)

async def process_post(post_data: Dict[str, Any], target_id: str):
    """
    Full pipeline to process a single post: OCR -> Keyword -> AI -> OSINT -> Hash -> DB
    """
    raw_text = post_data.get('raw_text', '')
    image_path = post_data.get('image_path')
    
    # 1. OCR Process
    ocr_text = ""
    if image_path:
        ocr_text = await extract_text_from_image(image_path)
    
    combined_text = f"{raw_text} {ocr_text}"
    
    # 2. Stage 1: Keyword Filter
    keyword_matched = check_keywords(combined_text)
    
    ai_status = {"ai_classified": False, "confidence_score": 0.0}
    # 3. Stage 2: NLP Classification (only if keyword matched)
    if keyword_matched:
        ai_status = await classify_text(combined_text)
    
    # 4. Vision Detection
    has_substances = False
    if image_path:
        detections = await detect_substances(image_path)
        has_substances = len(detections) > 0
    
    # 5. OSINT Extraction
    leads = await extract_all_leads(combined_text, source=post_data.get('handle', ''))
    
    # 6. Integrity Hash
    post_hash = calculate_post_hash(combined_text)
    
    # 7. GPS if available
    gps_data = {}
    if image_path:
        gps_info = await get_gps_data(image_path)
        if gps_info:
            gps_data = gps_info
            
    # 8. Database Insert
    db = get_supabase()
    
    post_insert = {
        "target_id": target_id,
        "platform": post_data.get('platform'),
        "post_url": post_data.get('post_url'),
        "raw_text": raw_text,
        "ocr_text": ocr_text,
        "keyword_matched": keyword_matched,
        "ai_classified": ai_status.get('ai_classified', False),
        "confidence_score": ai_status.get('confidence_score', 0.0),
        "has_image": post_data.get('has_image', False),
        "image_path": image_path,
        "sha256_hash": post_hash,
        **gps_data
    }
    
    try:
        # Avoid duplicate posts via hash
        resp = db.table('posts').upsert(post_insert, on_conflict='sha256_hash').execute()
        if resp.data:
            post_id = resp.data[0]['id']
            # Insert leads
            for lead in leads:
                lead['target_id'] = target_id
                db.table('identity_leads').insert(lead).execute()
            
            # Check for high severity alerts
            if ai_status.get('confidence_score', 0) > 0.85:
                alert = {
                    "post_id": post_id,
                    "target_id": target_id,
                    "alert_type": "HIGH_THREAT_DETECTION",
                    "severity": "critical",
                    "message": f"Critical threat detected on {post_data.get('platform')}: {post_data.get('handle')}"
                }
                db.table('alerts').insert(alert).execute()
    except Exception as e:
        logger.error(f"Error saving post to DB: {e}")

async def run_scan_for_target(target: Dict[str, Any]):
    """
    Executes a scan for a specific target based on platform.
    """
    platform = target.get('platform')
    handle = target.get('handle')
    target_id = target.get('id')
    
    posts = []
    if platform == 'telegram':
        posts = await scrape_public_channel(f"https://t.me/{handle}")
    elif platform == 'instagram':
        ig_scraper = InstagramScraper()
        posts = await ig_scraper.scrape_public_profile(handle)
        
    for post in posts:
        await process_post(post, target_id)
        
    # Update last_scanned
    get_supabase().table('targets').update({"last_scanned": datetime.now().isoformat()}).eq('id', target_id).execute()
