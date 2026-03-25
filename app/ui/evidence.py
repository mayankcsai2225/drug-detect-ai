import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from app.database import get_supabase
from typing import List

# ─── DEMO POSTS ───────────────────────────────────────────────────────────────
DEMO_POSTS = [
    {"platform": "telegram", "handle": "@darkmarket_mumbai", "raw_text": "🚨 FRESH STOCK: Pure Heroin (Grade A) South Bombay. +91-90040-12345. Price: ₹4,000/g. Crypto OK.", "ocr_text": "Fresh stock Heroin Grade A", "confidence_score": 0.98, "has_image": True, "geo_address": "Mumbai, India", "captured_at": "2026-03-25 10:00"},
    {"platform": "instagram", "handle": "high_life_delhi", "raw_text": "Crystal Meth (Blue) 💎 drop in Dwarka Delhi. DM for details. ETH: 0x2bE4dBf7...", "ocr_text": "Crystal Meth Blue Dwarka Delhi", "confidence_score": 0.95, "has_image": True, "geo_address": "New Delhi, India", "captured_at": "2026-03-25 12:00"},
    {"platform": "telegram", "handle": "@cartel_bangalore", "raw_text": "Shipment arriving at Bangalore airport. Need 5 delivery riders. +91 80808 80808", "ocr_text": "Shipment Bangalore delivery", "confidence_score": 0.82, "has_image": False, "geo_address": "Bangalore, India", "captured_at": "2026-03-25 14:30"},
    {"platform": "telegram", "handle": "@goa_party_connect", "raw_text": "LSD tabs for tonight Vagator beach party 🏖️ Search near sunset point. +9170200-XXXXX", "ocr_text": "LSD tabs beach party Vagator", "confidence_score": 0.90, "has_image": True, "geo_address": "Goa, India", "captured_at": "2026-03-25 18:00"},
    {"platform": "telegram", "handle": "@drugnetdemo_bot", "raw_text": "Looking for ketamine suppliers in Punjab region. Large scale only. DM secure.", "ocr_text": "Ketamine suppliers Punjab", "confidence_score": 0.70, "has_image": False, "geo_address": "Punjab, India", "captured_at": "2026-03-25 08:15"},
]

def get_filtered_posts(platform_filter: List[str], drug_filter: str, confidence_min: float, has_image_only: bool):
    try:
        db = get_supabase()
        query = db.table('posts').select('*')
        if platform_filter:
            query = query.in_('platform', platform_filter)
        if drug_filter and drug_filter != "All":
            query = query.contains('detected_drugs', [drug_filter])
        if has_image_only:
            query = query.eq('has_image', True)
        if confidence_min > 0.5:
            query = query.gte('confidence_score', confidence_min)
        resp = query.order('captured_at', desc=True).limit(100).execute()
        if resp.data:
            return pd.DataFrame(resp.data)
    except:
        pass
    # Fall back to demo data
    df = pd.DataFrame(DEMO_POSTS)
    if platform_filter:
        df = df[df['platform'].isin(platform_filter)]
    if has_image_only:
        df = df[df['has_image'] == True]
    df = df[df['confidence_score'] >= confidence_min]
    return df

def build_confidence_chart():
    """Bar chart of confidence scores for demo posts."""
    df = pd.DataFrame(DEMO_POSTS)
    fig = go.Figure(go.Bar(
        x=df['handle'], y=df['confidence_score'],
        marker_color=['#FF4B4B' if s > 0.85 else '#FFA500' if s > 0.70 else '#4CAF50' for s in df['confidence_score']],
        text=[f"{s:.0%}" for s in df['confidence_score']], textposition='auto'
    ))
    fig.update_layout(
        paper_bgcolor='#0D1117', plot_bgcolor='#0D1117',
        font=dict(color='white'), xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(gridcolor='#21262d', range=[0, 1.0]),
        title=dict(text="🎯 AI Confidence by Target Handle", font=dict(color='white', size=13)),
        margin=dict(l=20, r=20, t=40, b=20), height=300
    )
    return fig

def build_evidence_tab():
    with gr.Tab("EVIDENCE EXPLORER"):
        with gr.Row():
            p_filter = gr.CheckboxGroup(["telegram", "instagram"], label="Platform", value=["telegram", "instagram"])
            d_filter = gr.Dropdown(["All", "MDMA", "LSD", "Cocaine", "Ganja", "Meth", "Heroin", "Ketamine"], label="Drug Type", value="All")
            c_filter = gr.Slider(0.5, 1.0, value=0.5, label="Min Confidence")
            i_filter = gr.Checkbox(label="Has Image Only", value=False)
            filter_btn = gr.Button("Apply Filters", variant="primary")
            demo_fill_btn = gr.Button("🎯 Load Demo Posts", variant="secondary")

        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 📋 Evidence Records")
                posts_table = gr.Dataframe(value=get_filtered_posts([], "All", 0.5, False), height=400)

            with gr.Column(scale=1):
                gr.Markdown("### 📊 AI Confidence Heatmap")
                conf_chart = gr.Plot(value=build_confidence_chart())

        with gr.Row():
            gr.Markdown("### 🖼️ Image Evidence Gallery (Demo Captions)")
            gallery = gr.Gallery(
                value=[
                    ("https://via.placeholder.com/300x200/FF4B4B/FFFFFF?text=Heroin+Packet", "@darkmarket_mumbai · Risk: 0.98"),
                    ("https://via.placeholder.com/300x200/FF8C00/FFFFFF?text=Crystal+Meth", "high_life_delhi · Risk: 0.95"),
                    ("https://via.placeholder.com/300x200/006400/FFFFFF?text=LSD+Tabs", "@goa_party_connect · Risk: 0.90"),
                ],
                columns=[3], rows=[1], object_fit="contain", height=250
            )

        def load_demo_posts():
            return pd.DataFrame(DEMO_POSTS)

        filter_btn.click(get_filtered_posts, inputs=[p_filter, d_filter, c_filter, i_filter], outputs=posts_table)
        demo_fill_btn.click(load_demo_posts, outputs=posts_table)
