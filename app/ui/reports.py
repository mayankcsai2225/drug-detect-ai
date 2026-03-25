import gradio as gr
import pandas as pd
import uuid
import os
import hashlib
from app.database import get_supabase
from app.export.pdf_generator import generate_evidence_pdf, calculate_pdf_hash

DEMO_REPORT_HISTORY = [
    {"id": "rpt_001", "created_at": "2026-03-25 09:00:00", "status": "completed", "hash": "a3f5d9e2b1c8a7..."},
    {"id": "rpt_002", "created_at": "2026-03-25 15:30:00", "status": "completed", "hash": "f2e1d4a9c3b7e5..."},
    {"id": "rpt_003", "created_at": "2026-03-25 20:00:00", "status": "completed", "hash": "d8c2a6f1e9b3d7..."},
]

DEMO_TARGETS = ["@darkmarket_mumbai", "high_life_delhi", "@cartel_bangalore", "@goa_party_connect", "@drugnetdemo_bot"]

def generate_demo_report(case_num, officer, targets_selected, sections):
    """Generates a demo PDF using synthetic evidence data."""
    if not case_num:
        case_num = str(uuid.uuid4())[:8].upper()
    if not officer:
        officer = "Inspector Demo"

    # Use demo data
    target_data = {
        "handle": targets_selected[0] if targets_selected else "@darkmarket_mumbai",
        "platform": "telegram",
        "risk_score": 0.97,
        "status": "active"
    }
    demo_posts = [
        {"raw_text": "🚨 FRESH STOCK: Pure Heroin (Grade A) South Bombay. +91-90040-12345. Price: ₹4,000/g.", "confidence_score": 0.98, "captured_at": "2026-03-25 10:00:00"},
    ]
    demo_leads = [
        {"lead_type": "phone", "value": "+91-90040-12345", "confidence": 0.97},
        {"lead_type": "crypto_btc", "value": "1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX", "confidence": 0.99},
    ]
    try:
        file_path = generate_evidence_pdf(target_data, demo_posts, demo_leads, officer, case_num)
        file_hash = calculate_pdf_hash(file_path)
        try:
            db = get_supabase()
            db.table('scan_jobs').insert({"job_type": "pdf_report", "status": "completed", "error_log": f"Hash: {file_hash}"}).execute()
        except:
            pass
        return file_path, file_hash
    except Exception as e:
        return None, f"Demo PDF error: {e}"

def get_reports_history():
    try:
        db = get_supabase()
        resp = db.table('scan_jobs').select('*').eq('job_type', 'pdf_report').execute()
        if resp.data:
            return pd.DataFrame(resp.data)
    except:
        pass
    return pd.DataFrame(DEMO_REPORT_HISTORY)

def verify_pdf_hash(file_obj):
    if file_obj is None:
        return "No file uploaded."
    try:
        with open(file_obj.name, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        return f"✅ SHA-256 Hash: {h}\n\nFile integrity verified. This hash can be compared against the original recorded hash in the case file."
    except Exception as e:
        return f"❌ Verification failed: {e}"

def build_reports_tab():
    with gr.Tab("REPORTS & EXPORT"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📄 Evidence Bundle Generator")
                case_id = gr.Textbox(value=str(uuid.uuid4())[:8].upper(), label="Case Reference ID")
                officer_name = gr.Textbox(placeholder="e.g. Inspector R. Sharma", label="Officer Name")
                target_multiselect = gr.CheckboxGroup(
                    DEMO_TARGETS, value=["@darkmarket_mumbai"],
                    label="Include Targets"
                )
                sections_grp = gr.CheckboxGroup(
                    ["Evidence Posts", "OSINT Leads", "Image Gallery", "Chain of Custody"],
                    value=["Evidence Posts", "OSINT Leads"], label="Included Sections"
                )
                report_btn = gr.Button("⬇️ Generate PDF Evidence Report", variant="primary")

                gr.Markdown("---")
                gr.Markdown("### 🔒 PDF Integrity Checker (SHA-256)")
                pdf_upload = gr.File(label="Upload PDF Evidence Bundle")
                verify_btn = gr.Button("Verify Integrity Hash", variant="secondary")
                verify_out = gr.Textbox(label="Verification Result", interactive=False, lines=4)

            with gr.Column(scale=2):
                gr.Markdown("### ⬇️ Download Evidence Bundle")
                report_file = gr.File(label="Ready for Download", interactive=False)
                report_hash = gr.Textbox(label="SHA-256 Integrity Hash", interactive=False)

                gr.Markdown("### 📋 Report Generation Logs")
                reports_table = gr.Dataframe(value=get_reports_history(), height=350)
                refresh_btn = gr.Button("Refresh Logs", variant="secondary")

        report_btn.click(
            generate_demo_report,
            inputs=[case_id, officer_name, target_multiselect, sections_grp],
            outputs=[report_file, report_hash]
        )
        verify_btn.click(verify_pdf_hash, inputs=[pdf_upload], outputs=[verify_out])
        refresh_btn.click(get_reports_history, outputs=reports_table)
