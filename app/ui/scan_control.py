import gradio as gr
import pandas as pd
import time
from app.database import get_supabase

DEMO_JOBS = [
    {"id": "job_001", "job_type": "telegram_scan", "status": "completed", "started_at": "2026-03-25 08:00:00", "completed_at": "2026-03-25 08:00:45", "error_log": "OK – 3 posts classified"},
    {"id": "job_002", "job_type": "instagram_scan", "status": "completed", "started_at": "2026-03-25 10:00:00", "completed_at": "2026-03-25 10:01:10", "error_log": "OK – 1 post classified"},
    {"id": "job_003", "job_type": "discovery_crawl", "status": "completed", "started_at": "2026-03-25 12:00:00", "completed_at": "2026-03-25 12:00:20", "error_log": "OK – 2 new targets found"},
    {"id": "job_004", "job_type": "telegram_scan", "status": "failed", "started_at": "2026-03-25 14:00:00", "completed_at": "2026-03-25 14:00:05", "error_log": "Rate limited by Telegram"},
    {"id": "job_005", "job_type": "telegram_scan", "status": "completed", "started_at": "2026-03-25 16:00:00", "completed_at": "2026-03-25 16:01:30", "error_log": "OK – 1 critical alert raised"},
]

DEMO_KEYWORDS = ["mdma", "molly", "lsd", "acid", "charas", "chaabi", "maal", "smack", "crystal", "ice", "white powder", "ganja", "weed", "cocaine", "coke", "heroin", "brown sugar", "ketamine", "xtc"]

DEMO_LOG_LINES = [
    "[08:00:00] 🟢 Scheduler Started – 3 targets active",
    "[08:00:01] 🔍 Scanning @darkmarket_mumbai (Telegram)...",
    "[08:00:12] ⚠️  Keyword HIT: 'Heroin', 'Grade A' – Stage 1 Pass",
    "[08:00:15] 🤖 AI Classify: 'drug_marketing' (confidence=0.98)",
    "[08:00:18] 📞 OSINT: Phone +91-90040-12345 extracted",
    "[08:00:22] 🏦 OSINT: BTC Wallet 1F1tAaz5x... extracted",
    "[08:00:30] 📄 Evidence hash: SHA-256 calculated",
    "[08:00:45] ✅ Job complete – 3 posts ingested, 1 critical alert raised",
    "[10:00:00] 🔍 Scanning high_life_delhi (Instagram)...",
    "[10:00:45] ⚠️  Keyword HIT: 'Crystal Meth', 'Blue' – Stage 1 Pass",
    "[10:00:55] 🤖 AI Classify: 'high_risk_marketing' (confidence=0.95)",
    "[10:01:10] ✅ Job complete – 1 post, 1 alert raised",
]

def get_job_history():
    try:
        db = get_supabase()
        resp = db.table('scan_jobs').select('*').order('created_at', desc=True).limit(20).execute()
        if resp.data:
            return pd.DataFrame(resp.data)
    except:
        pass
    return pd.DataFrame(DEMO_JOBS)

def get_active_targets():
    try:
        db = get_supabase()
        resp = db.table('targets').select('handle').eq('status', 'active').execute()
        if resp.data:
            return [r['handle'] for r in resp.data]
    except:
        pass
    return ["@darkmarket_mumbai", "high_life_delhi", "@cartel_bangalore", "@goa_party_connect", "@drugnetdemo_bot"]

def run_demo_scan(target):
    """Simulates a scan run with a progress log."""
    lines = [
        f"[{time.strftime('%H:%M:%S')}] 🟢 Initiating manual scan for {target}...",
        f"[{time.strftime('%H:%M:%S')}] 🔍 Connecting to Telegram API (mock)...",
        f"[{time.strftime('%H:%M:%S')}] 📥 Fetching last 50 messages...",
        f"[{time.strftime('%H:%M:%S')}] ⚠️  Keyword HIT detected – drug-related terms found",
        f"[{time.strftime('%H:%M:%S')}] 🤖 AI Classification: high_risk (score=0.93)",
        f"[{time.strftime('%H:%M:%S')}] 📞 OSINT extraction complete – 1 phone found",
        f"[{time.strftime('%H:%M:%S')}] ✅ Scan complete – 1 alert raised to dashboard",
    ]
    return "\n".join(lines), get_job_history()

def build_scan_control_tab():
    with gr.Tab("SCAN CONTROL CENTER"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🎮 Manual Scan Control")
                target_selector = gr.Dropdown(get_active_targets(), label="Select Target", value="@darkmarket_mumbai")
                target_btn = gr.Button("▶ Scan Selected Now (Demo)", variant="primary")
                full_scan_btn = gr.Button("▶▶ Scan ALL Targets (Demo)", variant="secondary")
                
                gr.Markdown("---")
                gr.Markdown("### 🖥️ Scan Log Terminal")
                log_box = gr.Textbox(
                    value="\n".join(DEMO_LOG_LINES),
                    lines=14, interactive=False, label="Live Log Output"
                )

            with gr.Column(scale=2):
                gr.Markdown("### 📊 Scan Job History & Status")
                job_table = gr.Dataframe(value=get_job_history(), height=350)
                refresh_btn = gr.Button("Refresh History", variant="secondary")

                gr.Markdown("### 🔑 AI Keywords Watchlist")
                gr.Dataframe(
                    value=pd.DataFrame({"Keyword": DEMO_KEYWORDS}),
                    label="Core NDPS Keyword Set", height=200
                )

        target_btn.click(run_demo_scan, inputs=[target_selector], outputs=[log_box, job_table])
        full_scan_btn.click(
            lambda: ("\n".join(DEMO_LOG_LINES + [f"\n[{time.strftime('%H:%M:%S')}] 🟢 ALL 5 TARGETS SCANNED SUCCESSFULLY"]), get_job_history()),
            outputs=[log_box, job_table]
        )
        refresh_btn.click(get_job_history, outputs=job_table)
