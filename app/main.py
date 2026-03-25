import os
import logging
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr
from app.config import settings
from app.database import init_db, get_supabase
from app.scheduler import setup_scheduler
from app.ui.theme import get_ncb_theme, NCB_THEME_CSS
from app.ui.dashboard import build_dashboard_tab
from app.ui.targets import build_targets_tab
from app.ui.evidence import build_evidence_tab
from app.ui.osint_map import build_osint_map_tab
from app.ui.scan_control import build_scan_control_tab
from app.ui.reports import build_reports_tab
from contextlib import asynccontextmanager

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# --- FastAPI State & Lifecycle ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    """
    logger.info("Initializing NCB DrugNet Intelligence Platform...")
    
    # 1. Initialize DB
    init_db()
    
    # 2. Setup Scheduler
    app.state.scheduler = setup_scheduler()
    app.state.scheduler.start()
    logger.info("APScheduler started successfully")
    
    # 3. Model Warming
    # Ensuring models are loaded into CPU RAM on startup
    from app.nlp.nlp_classifier import get_local_classifier
    from app.nlp.vision_detector import get_yolo_model
    get_local_classifier()
    get_yolo_model()
    
    yield
    
    # Shutdown logic
    app.state.scheduler.shutdown()
    logger.info("Application shutting down...")

app = FastAPI(title="NCB DrugNet Intelligence Platform", version="1.0.0", lifespan=lifespan)

# CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---
@app.post("/demo/load")
async def load_demo_data():
    """
    Inserts synthetic intel data for demo/hackathon purposes.
    Uses SUPABASE_SERVICE_KEY to bypass RLS if available.
    """
    import json
    from supabase import create_client
    try:
        with open("demo_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Prefer service_role key to bypass RLS, fall back to anon key
        service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
        if service_key:
            db = create_client(settings.supabase_url, service_key)
            logger.info("Demo using service_role key (bypasses RLS)")
        else:
            db = get_supabase()
            logger.warning("Demo using anon key — RLS may block inserts. Set SUPABASE_SERVICE_KEY to fix.")

        # Clean current demo data
        try:
            db.table('alerts').delete().neq('message', '___EMPTY___').execute()
            db.table('targets').delete().neq('handle', '___EMPTY___').execute()
        except Exception as del_err:
            logger.warning(f"Cleanup skipped (may be RLS): {del_err}")

        # Insert demo targets
        unique_handles = list(set([item['handle'] for item in data]))
        for handle in unique_handles:
            risk = next(i['risk_score'] for i in data if i['handle'] == handle)
            db.table('targets').insert({"handle": handle, "risk_score": risk, "platform": "telegram", "status": "active"}).execute()

        # Insert demo alerts
        for item in data:
            db.table('alerts').insert({
                "message": item['raw_text'][:500],
                "alert_type": item['classification'],
                "severity": "critical" if item['risk_score'] > 0.85 else "high"
            }).execute()

        return {"status": "success", "entries": len(data)}
    except Exception as e:
        logger.error(f"Demo load failed: {e}")
        return {"status": "error", "message": f"{e}"}

# --- Gradio UI Composition ---
# The UI is stitched from individual tab modules.
with gr.Blocks(theme=get_ncb_theme(), css=NCB_THEME_CSS, title="NCB DrugNet Intelligence") as drugnet_ui:
    gr.Markdown("# 🛡️ NCB DrugNet Intelligence Platform")
    gr.Markdown("#### Law Enforcement Agency (NCB India) — Official Intelligence Dashboard")
    
    with gr.Accordion("🛠️ DEMO CONTROLS", open=False):
        with gr.Row():
            demo_toggle = gr.Checkbox(label="ENABLE DEMO MODE", value=False)
            demo_load_btn = gr.Button("Load Quick Demo (60-sec Setup)", variant="primary")
            demo_status = gr.Markdown("*Use demo mode for presentations (Synthetic Data only)*")
        
        async def run_demo():
            try:
                result = await load_demo_data()
                if result.get("status") == "success":
                    return f"✅ **Demo Loaded Successfully!** ({result.get('entries')} records inserted)"
                else:
                    return f"❌ **Demo Load Failed**: {result.get('message')}"
            except Exception as e:
                return f"❌ **Error**: {e}"
        
        demo_load_btn.click(run_demo, outputs=[demo_status])
    
    # Stitch Tabs
    build_dashboard_tab()
    build_targets_tab()
    build_evidence_tab()
    build_osint_map_tab()
    build_scan_control_tab()
    build_reports_tab()

# Mount Gradio into FastAPI
app = gr.mount_gradio_app(app, drugnet_ui, path="/")

# --- API Endpoints ---
@app.get("/health")
def health_check():
    """
    Service health and scheduler status endpoint.
    """
    return {
        "status": "operational",
        "system": "NCB DrugNet v1.0",
        "scheduler_active": app.state.scheduler.running,
        "supabase_connected": True if get_supabase() else False
    }

@app.post("/api/scan/all")
async def trigger_full_scan(background_tasks: BackgroundTasks):
    """
    Trigger a manual full scan in the background.
    """
    from app.scheduler import scan_all_active_targets
    background_tasks.add_task(scan_all_active_targets)
    return {"message": "Full scan initiated in background"}

@app.get("/api/targets")
def list_targets():
    """
    API access for targets (External/CLI tools).
    """
    db = get_supabase()
    return db.table('targets').select('*').execute().data

# --- Entry Point ---
if __name__ == "__main__":
    import uvicorn
    # Default port for HF Spaces is 7860
    uvicorn.run("app.main:app", host="0.0.0.0", port=7860, reload=True)
