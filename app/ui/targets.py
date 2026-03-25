import gradio as gr
import pandas as pd
from app.database import get_supabase
from app.scheduler_logic import run_scan_for_target

def add_target(handle, platform):
    """
    Inserts a new target into Supabase and triggers an immediate scan.
    """
    db = get_supabase()
    target_data = {
        "handle": handle,
        "platform": platform,
        "status": "active",
        "created_at": "now()",
        "risk_score": 0.0
    }
    
    try:
        resp = db.table('targets').upsert(target_data, on_conflict='handle').execute()
        if resp.data:
            new_target = resp.data[0]
            # Off-loop scan (Simplified for Gradio UI)
            import asyncio
            asyncio.run(run_scan_for_target(new_target))
            return gr.Info(f"Target {handle} added and scan initiated."), get_targets_df()
        return gr.Error("Failed to add target."), get_targets_df()
    except Exception as e:
        return gr.Error(f"Database error: {e}"), get_targets_df()

def bulk_import(bulk_text, platform):
    """
    Handles multi-line target import.
    """
    handles = [h.strip() for h in bulk_text.split('\n') if h.strip()]
    for h in handles:
        add_target(h, platform)
    return gr.Info(f"Bulk import of {len(handles)} targets complete."), get_targets_df()

def get_targets_df():
    """
    Retrieves all targets for the management table.
    """
    db = get_supabase()
    resp = db.table('targets').select('id, handle, platform, subscriber_count, risk_score, status, last_scanned').execute()
    if resp.data:
        return pd.DataFrame(resp.data)
    return pd.DataFrame(columns=["id", "handle", "platform", "subscriber_count", "risk_score", "status", "last_scanned"])

def build_targets_tab():
    with gr.Tab("TARGET MANAGEMENT"):
        with gr.Row():
            # Left Panel: Add Target
            with gr.Column(scale=1):
                gr.Markdown("### Add New Target")
                with gr.Group():
                    handle_input = gr.Textbox(placeholder="Channel URL or @handle", label="Target Handle")
                    platform_input = gr.Dropdown(["telegram", "instagram"], label="Platform")
                    add_btn = gr.Button("Add Target & Scan Now", variant="primary")
                
                gr.Markdown("### Bulk Import")
                bulk_input = gr.Textbox(placeholder="one_handle\nanother_handle", lines=5, label="Handle List")
                bulk_btn = gr.Button("Import Bulk Targets")
                
            # Right Panel: Manage Targets
            with gr.Column(scale=2):
                gr.Markdown("### Active Targets")
                target_table = gr.Dataframe(value=get_targets_df(), interactive=False, height=500)
                refresh_btn = gr.Button("Refresh Table", variant="secondary")
                
        # Link callbacks
        add_btn.click(add_target, inputs=[handle_input, platform_input], outputs=[gr.State(None), target_table])
        bulk_btn.click(bulk_import, inputs=[bulk_input, platform_input], outputs=[gr.State(None), target_table])
        refresh_btn.click(get_targets_df, outputs=target_table)
