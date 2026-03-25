from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import get_supabase
from app.scheduler_logic import run_scan_for_target
import logging

logger = logging.getLogger(__name__)

async def scan_all_active_targets():
    """
    Job 1: Fetches all active targets and runs scrapers/pipeline.
    """
    logger.info("Starting scheduled scan for all active targets")
    db = get_supabase()
    resp = db.table('targets').select('*').eq('status', 'active').execute()
    
    if resp.data:
        # Create scan_jobs record
        job_resp = db.table('scan_jobs').insert({
            "job_type": "full_scan",
            "status": "running",
            "started_at": "now()"
        }).execute()
        job_id = job_resp.data[0]['id'] if job_resp.data else None
        
        for target in resp.data:
            try:
                await run_scan_for_target(target)
            except Exception as e:
                logger.error(f"Error scanning target {target['handle']}: {e}")
                
        # Update job status
        if job_id:
            db.table('scan_jobs').update({
                "status": "completed",
                "completed_at": "now()"
            }).eq('id', job_id).execute()
    
    logger.info("Finished scheduled scan")

async def run_discovery_crawl():
    """
    Job 2: Crawl discovered links from recent posts.
    """
    logger.info("Starting discovery crawl")
    # TBD logic (scans for new t.me links and adds to queue)
    pass

async def alert_check_realtime():
    """
    Job 3: Checks for high confidence threats.
    """
    # Logic in scheduler_logic handles immediate alert on insert, 
    # but this can verify periodically.
    pass

def setup_scheduler():
    """
    Initializes APScheduler with AsyncIOScheduler.
    """
    scheduler = AsyncIOScheduler()
    
    # 30-minute full scan
    scheduler.add_job(scan_all_active_targets, 'interval', minutes=30, id='full_scan')
    
    # 6-hour discovery crawl
    scheduler.add_job(run_discovery_crawl, 'interval', hours=6, id='discovery_crawl')
    
    # 5-minute alert check
    scheduler.add_job(alert_check_realtime, 'interval', minutes=5, id='alert_check')
    
    return scheduler
