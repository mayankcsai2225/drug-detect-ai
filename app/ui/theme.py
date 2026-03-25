import gradio as gr

# NCB-themed dark palette (GitHub dark style)
# Colors based on spec: background #0D1117, surface #161B22, primary #238636
NCB_THEME_CSS = """
:root {
  --background-fill-primary: #0D1117;
  --background-fill-secondary: #010409;
  --border-color-primary: #30363D;
  --color-accent: #238636;
  --text-color-primary: #E6EDF3;
  --text-color-secondary: #8B949E;
  --input-background-fill: #161B22;
}

body {
  background-color: #0D1117 !important;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Dataframe header styling */
.gradio-container .gradio-dataframe table thead th {
    background-color: #161B22 !important;
    color: #E6EDF3 !important;
    border-bottom: 2px solid #30363D !important;
}

/* KPI Card styling */
.kpi-card {
  background-color: #161B22;
  border: 1px solid #30363D;
  border-radius: 6px;
  padding: 16px;
  text-align: center;
  transition: transform 0.2s;
}
.kpi-card:hover {
  transform: translateY(-2px);
  border-color: #238636;
}
.kpi-value {
  font-size: 24px;
  font-weight: bold;
  color: #238636;
}
.kpi-label {
  font-size: 14px;
  color: #8B949E;
}

/* Red KPIs for critical counts */
.kpi-critical {
    color: #DA3633 !important;
}

/* Severity Badges (pill shape) */
.badge-pill {
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    text-transform: uppercase;
    font-weight: bold;
}
.badge-critical { background-color: #DA3633; color: white; }
.badge-high { background-color: #D29922; color: white; }
.badge-medium { background-color: #1F6FEB; color: white; }
.badge-low { background-color: #484F58; color: white; }

/* Sticky headers for large dataframes */
.gr-box { overflow: auto; max-height: 500px; }

/* D3.js Graph Container */
#osint-graph {
    width: 100%;
    height: 600px;
    background-color: #010409;
    border: 1px solid #30363D;
}
"""

def get_ncb_theme():
    # Gradio theme override
    theme = gr.themes.Default(
        primary_hue="green",
        secondary_hue="slate",
        neutral_hue="gray",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"]
    ).set(
        body_background_fill="#0D1117",
        body_text_color="#E6EDF3",
        background_fill_primary="#0D1117",
        background_fill_secondary="#161B22",
        block_background_fill="#161B22",
        block_label_background_fill="#21262D",
        block_title_text_color="#E6EDF3",
        input_background_fill="#0D1117",
        input_border_color="#30363D",
        button_primary_background_fill="#238636",
        button_primary_background_fill_hover="#2EA043",
        button_primary_text_color="#FFFFFF"
    )
    return theme
