import gradio as gr
import pandas as pd
from app.database import get_supabase
import plotly.express as px

def get_stats():
    """
    Fetches live stats from Supabase for dashboard KPIs.
    """
    db = get_supabase()
    
    # Total targets
    t_count = db.table('targets').select('id', count='exact').execute().count or 0
    # Today's posts
    from datetime import date
    p_count = db.table('posts').select('id', count='exact').gte('captured_at', date.today().isoformat()).execute().count or 0
    # Critical alerts
    a_count = db.table('alerts').select('id', count='exact').eq('severity', 'critical').execute().count or 0
    # OSINT Leads
    l_count = db.table('identity_leads').select('id', count='exact').execute().count or 0
    
    return [
        f"<h2>{t_count}</h2><p>Total Targets</p>",
        f"<h2>{p_count}</h2><p>Posts Captured Today</p>",
        f"<h2 style='color: #FF7B72'>{a_count}</h2><p>Critical Threats Active</p>",
        f"<h2>{l_count}</h2><p>OSINT Identity Leads</p>"
    ]

def get_alerts_df():
    """
    Fetches real-time alert feed.
    """
    db = get_supabase()
    resp = db.table('alerts').select('created_at, alert_type, severity, message').order('created_at', desc=True).limit(20).execute()
    if resp.data:
        return pd.DataFrame(resp.data)
    return pd.DataFrame(columns=["created_at", "alert_type", "severity", "message"])

def get_risk_leaderboard():
    """
    Generates Plotly horizontal bar chart for top risk targets.
    """
    db = get_supabase()
    resp = db.table('targets').select('handle, risk_score').order('risk_score', desc=True).limit(10).execute()
    if resp.data:
        df = pd.DataFrame(resp.data)
        fig = px.bar(df, x='risk_score', y='handle', orientation='h', color='risk_score', 
                     color_continuous_scale='Reds', template='plotly_dark')
        fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    return None

def build_dashboard_tab():
    with gr.Tab("LIVE DASHBOARD"):
        with gr.Row():
            t_count = gr.HTML("", elem_classes=["kpi-card"])
            p_count = gr.HTML("", elem_classes=["kpi-card"])
            a_count = gr.HTML("", elem_classes=["kpi-card"])
            l_count = gr.HTML("", elem_classes=["kpi-card"])
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### Real-time Intelligence Feed")
                alert_feed = gr.Dataframe(value=get_alerts_df(), height=400, interactive=False)
            
            with gr.Column(scale=1):
                gr.Markdown("### High Risk Leaderboard")
                risk_chart = gr.Plot(value=get_risk_leaderboard())
        
        # Dashboard Auto-Refresh Logic
        # Update components periodically
        dashboard_timer = gr.Timer(10) # 10s refresh
        dashboard_timer.tick(get_stats, outputs=[t_count, p_count, a_count, l_count])
        dashboard_timer.tick(get_alerts_df, outputs=[alert_feed])
        dashboard_timer.tick(get_risk_leaderboard, outputs=[risk_chart])
        
        # Initial load
        # gr.on creates a combined trigger
        # But for compatibility, let's just trigger on tab select
        # In Gradio 4, Tab has a select event
        # Alternatively, use the main blocks.load
