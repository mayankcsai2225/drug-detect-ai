import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from app.database import get_supabase

# ─── DEMO DATA ────────────────────────────────────────────────────────────────
DEMO_LEADS = [
    {"lead_type": "phone", "value": "+91-90040-12345", "source": "@darkmarket_mumbai", "geo_country": "India", "isp": "Jio", "confidence": 0.97, "verified": True},
    {"lead_type": "crypto_btc", "value": "1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX", "source": "@darkmarket_mumbai", "geo_country": "India", "isp": "", "confidence": 0.99, "verified": False},
    {"lead_type": "email", "value": "supply_chain@protonmail.com", "source": "@cartel_bangalore", "geo_country": "India", "isp": "ProtonMail", "confidence": 0.85, "verified": False},
    {"lead_type": "phone", "value": "+91-80808-80808", "source": "@cartel_bangalore", "geo_country": "India", "isp": "Airtel", "confidence": 0.91, "verified": True},
    {"lead_type": "crypto_eth", "value": "0x2bE4dBf7cda9890987", "source": "high_life_delhi", "geo_country": "India", "isp": "", "confidence": 0.89, "verified": False},
    {"lead_type": "ip_address", "value": "103.211.54.22", "source": "@goa_party_connect", "geo_country": "India", "isp": "BSNL", "confidence": 0.72, "verified": False},
    {"lead_type": "phone", "value": "+91-70200-00000", "source": "@goa_party_connect", "geo_country": "India", "isp": "Vi", "confidence": 0.88, "verified": True},
    {"lead_type": "email", "value": "drops_north@gmail.com", "source": "@drugnetdemo_bot", "geo_country": "India", "isp": "Google", "confidence": 0.76, "verified": False},
]

def get_leads_df():
    try:
        db = get_supabase()
        resp = db.table('identity_leads').select('lead_type, value, source, geo_country, isp, confidence, verified').execute()
        if resp.data:
            return pd.DataFrame(resp.data)
    except:
        pass
    return pd.DataFrame(DEMO_LEADS)

def run_osint_demo(target_name):
    """Returns prebuilt OSINT results for demo targets."""
    demo_results = {
        "@darkmarket_mumbai": [
            {"lead_type": "phone", "value": "+91-90040-12345", "confidence": 0.97},
            {"lead_type": "crypto_btc", "value": "1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX", "confidence": 0.99},
        ],
        "high_life_delhi": [
            {"lead_type": "crypto_eth", "value": "0x2bE4dBf7cda9890987", "confidence": 0.89},
        ],
        "@cartel_bangalore": [
            {"lead_type": "phone", "value": "+91-80808-80808", "confidence": 0.91},
            {"lead_type": "email", "value": "supply_chain@protonmail.com", "confidence": 0.85},
        ],
    }
    results = demo_results.get(target_name, [{"lead_type": "—", "value": "No leads found in demo data", "confidence": 0.0}])
    links_md = f"### 🔗 Cross-Platform Links for `{target_name}`\n- Telegram: `t.me/{target_name.strip('@')}`\n- Instagram: `instagram.com/{target_name.strip('@')}`"
    return pd.DataFrame(results), links_md

def build_demo_network_graph():
    """Create a Plotly network graph of identity connections."""
    # Node positions
    nodes = {
        "@darkmarket_mumbai": (0, 0), "+91-90040-12345": (-1.5, 1.5), "1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX": (1.5, 1.5),
        "@cartel_bangalore": (3, 0), "+91-80808-80808": (4.5, 1.5), "supply_chain@protonmail.com": (4.5, -1.5),
        "high_life_delhi": (0, -3), "0x2bE4dBf7cda9890987": (1.5, -4.5),
    }
    colors = {
        "@darkmarket_mumbai": "#FF4B4B", "+91-90040-12345": "#FFA500", "1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX": "#FFD700",
        "@cartel_bangalore": "#FF4B4B", "+91-80808-80808": "#FFA500", "supply_chain@protonmail.com": "#00BFFF",
        "high_life_delhi": "#FF4B4B", "0x2bE4dBf7cda9890987": "#FFD700",
    }
    edges = [
        ("@darkmarket_mumbai", "+91-90040-12345"), ("@darkmarket_mumbai", "1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX"),
        ("@cartel_bangalore", "+91-80808-80808"), ("@cartel_bangalore", "supply_chain@protonmail.com"),
        ("high_life_delhi", "0x2bE4dBf7cda9890987"),
    ]
    edge_x, edge_y = [], []
    for src, dst in edges:
        x0, y0 = nodes[src]; x1, y1 = nodes[dst]
        edge_x += [x0, x1, None]; edge_y += [y0, y1, None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(color='#444', width=1.5), hoverinfo='none'))
    names = list(nodes.keys())
    xs = [v[0] for v in nodes.values()]; ys = [v[1] for v in nodes.values()]
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode='markers+text', text=names,
        textposition="top center", hoverinfo='text',
        marker=dict(size=18, color=[colors[n] for n in names], line=dict(width=2, color='white')),
        textfont=dict(color='white', size=9)
    ))
    fig.update_layout(
        paper_bgcolor='#0D1117', plot_bgcolor='#0D1117',
        showlegend=False, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=20, b=20), height=500,
        title=dict(text="🕸️ Identity Connection Map — Demo Data", font=dict(color='white', size=14))
    )
    return fig

def build_osint_map_tab():
    with gr.Tab("OSINT IDENTITY MAP"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🔍 Manual Investigation Probe")
                probe_input = gr.Textbox(placeholder="Enter phone/email/IP/username...", label="Investigation Target")
                probe_btn = gr.Button("Investigate", variant="primary")
                
                gr.Markdown("#### 🎯 Quick Demo Investigations")
                demo_target = gr.Dropdown(
                    ["@darkmarket_mumbai", "high_life_delhi", "@cartel_bangalore"],
                    label="Load Demo Target"
                )
                demo_probe_btn = gr.Button("Run Demo Investigation", variant="secondary")
                probe_links = gr.Markdown("")
                probe_results = gr.Dataframe(label="Extraction Results", height=250)

            with gr.Column(scale=2):
                gr.Markdown("### 🗄️ Identity Leads Database")
                leads_table = gr.Dataframe(value=get_leads_df(), height=300)
                refresh_btn = gr.Button("Refresh Database", variant="secondary")

        with gr.Row():
            gr.Markdown("### 🕸️ Identity Connection Map")
            network_plot = gr.Plot(value=build_demo_network_graph())

        # Interactions
        probe_btn.click(run_osint_demo, inputs=probe_input, outputs=[probe_results, probe_links])
        demo_probe_btn.click(run_osint_demo, inputs=demo_target, outputs=[probe_results, probe_links])
        refresh_btn.click(get_leads_df, outputs=leads_table)
