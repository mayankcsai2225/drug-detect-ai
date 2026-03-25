import logging
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)

supabase: Client = None

def get_supabase() -> Client:
    global supabase
    if supabase is None:
        if settings.supabase_url and settings.supabase_key:
            try:
                supabase = create_client(settings.supabase_url, settings.supabase_key)
                logger.info("Supabase client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                # We return a dummy client or raise error depending on needs
                raise e
        else:
            logger.warning("Supabase URL or Key not set, database operations will fail.")
    return supabase

def init_db():
    get_supabase()
