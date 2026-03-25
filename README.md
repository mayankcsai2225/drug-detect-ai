---
title: NCB DrugNet Intelligence Platform
emoji: 🛡️
colorFrom: green
colorTo: gray
sdk: docker
pinned: false
---

# 🛡️ NCB DrugNet Intelligence Platform

> **Law Enforcement AI System for India's Narcotics Control Bureau (NCB)**  
> Automated OSINT surveillance, NLP classification, and evidence management across Telegram, Instagram, and WhatsApp public channels.

---

## 🚀 Quick Start

```powershell
# 1. Install dependencies (Python 3.12 required)
py -3.12 -m pip install -r requirements.txt

# 2. Configure environment
copy .env.example .env
# Fill in your SUPABASE_URL, SUPABASE_KEY, etc.

# 3. Run the platform
py -3.12 -m uvicorn app.main:app --host 127.0.0.1 --port 7860

# 4. Open in browser
# → http://127.0.0.1:7860 (Use this instead of 0.0.0.0 on Windows)
```

---

## 📸 Platform Features

| Tab | Features |
|---|---|
| 🟥 **Live Dashboard** | Real-time intelligence feed, KPI cards, risk leaderboard |
| 🎯 **Target Management** | Add/track Telegram & Instagram targets, set scan frequency |
| 🔬 **Evidence Explorer** | Filter posts by platform/drug/confidence, image gallery, AI heatmap |
| 🕸️ **OSINT Identity Map** | Network graph of phone/crypto connections, manual investigation probe |
| 🎮 **Scan Control Center** | Trigger manual scans, live log terminal, keyword watchlist |
| 📄 **Reports & Export** | One-click PDF evidence bundles with SHA-256 integrity hashes |

---

## 🎬 Demo Mode (60-Second Setup)

1. Start the server (see Quick Start above)
2. Open **[http://127.0.0.1:7860](http://127.0.0.1:7860)**
3. Expand **🛠️ DEMO CONTROLS** at the top
4. Click **"Load Quick Demo"** — dashboard instantly populates with 5 synthetic high-risk targets

**Demo highlights:**
- **OSINT Map** → Select `@darkmarket_mumbai` → "Run Demo Investigation" → See network graph
- **Scan Control** → Select any target → "▶ Scan Selected Now" → Watch live log output
- **Reports** → Enter officer name → "Generate PDF" → Download court-ready evidence bundle

---

## ⚙️ Environment Setup

Create a `.env` file in the project root:
```env
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGci...  # anon/public key
SUPABASE_SERVICE_KEY=eyJhbGci...  # service_role key (needed for demo inserts)
HUGGINGFACE_API_TOKEN=hf_...
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890
```

### Getting Supabase Credentials
1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **Settings → API** to find your URL and keys
3. Run the SQL schema in **SQL Editor** (see `supabase_schema.sql`)

### Getting Telegram API Keys
1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in → **API Development Tools** → Create App
3. Copy `App api_id` and `App api_hash`

---

## 🗄️ Database Setup (Supabase SQL)

Run this in your Supabase SQL Editor:

```sql
-- Required tables
CREATE TABLE targets (id UUID DEFAULT gen_random_uuid() PRIMARY KEY, handle TEXT, platform TEXT, status TEXT, risk_score FLOAT, subscriber_count INT, last_scanned TIMESTAMPTZ, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE posts (id UUID DEFAULT gen_random_uuid() PRIMARY KEY, target_id UUID REFERENCES targets(id), platform TEXT, raw_text TEXT, ocr_text TEXT, confidence_score FLOAT, has_image BOOL, image_path TEXT, geo_address TEXT, detected_drugs TEXT[], captured_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE alerts (id UUID DEFAULT gen_random_uuid() PRIMARY KEY, message TEXT, alert_type TEXT, severity TEXT, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE identity_leads (id UUID DEFAULT gen_random_uuid() PRIMARY KEY, target_id UUID, lead_type TEXT, value TEXT, source TEXT, geo_country TEXT, isp TEXT, confidence FLOAT, verified BOOL DEFAULT FALSE, created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE scan_jobs (id UUID DEFAULT gen_random_uuid() PRIMARY KEY, job_type TEXT, status TEXT, started_at TIMESTAMPTZ, completed_at TIMESTAMPTZ, error_log TEXT, created_at TIMESTAMPTZ DEFAULT NOW());

-- Disable RLS for local development
ALTER TABLE targets DISABLE ROW LEVEL SECURITY;
ALTER TABLE posts DISABLE ROW LEVEL SECURITY;
ALTER TABLE alerts DISABLE ROW LEVEL SECURITY;
ALTER TABLE identity_leads DISABLE ROW LEVEL SECURITY;
ALTER TABLE scan_jobs DISABLE ROW LEVEL SECURITY;
```

---

## 🏗️ Architecture

```
app/
├── main.py              # FastAPI app + Gradio UI composition
├── config.py            # Pydantic settings from .env
├── database.py          # Supabase client
├── scheduler.py         # APScheduler job definitions
├── scheduler_logic.py   # Core scan/classify pipeline
├── nlp/
│   ├── keyword_filter.py    # Stage 1: NDPS keyword matching
│   ├── nlp_classifier.py    # Stage 2: DistilBERT zero-shot
│   ├── ocr_processor.py     # Pytesseract OCR
│   └── vision_detector.py   # YOLOv8 substance detection
├── osint/
│   └── osint_engine.py      # Phone/crypto/IP/location extraction
├── scrapers/
│   ├── telegram_scraper.py  # Telethon public channel reader
│   └── instagram_scraper.py # Instaloader public profile reader
├── export/
│   └── pdf_generator.py     # ReportLab PDF + SHA-256 hashing
└── ui/
    ├── dashboard.py     # Live Dashboard tab
    ├── targets.py       # Target Management tab
    ├── evidence.py      # Evidence Explorer tab
    ├── osint_map.py     # OSINT Identity Map tab
    ├── scan_control.py  # Scan Control Center tab
    ├── reports.py       # Reports & Export tab
    └── theme.py         # NCB dark theme CSS
```

---

## 🧪 Running Tests

```powershell
py -3.12 -m pip install -r requirements-test.txt
py -3.12 -m pytest test_drugnet.py --cov=app -v
```

---

## 🐳 Docker & Deployment

### Local Docker
```bash
docker build -t ncb-drugnet .
docker run -p 7860:7860 --env-file .env ncb-drugnet
```

### 🚀 Hugging Face Spaces
This project is pre-configured for **Hugging Face Spaces** (Docker SDK):
- **Rootless Security**: `Dockerfile` is optimized to run as a non-root user (UID 1000).
- **Auto-cached Models**: YOLOv8 and DistilBERT are baked into the image.
- **Secret Management**: Compatible with HF Space Secrets for API keys.

For a detailed walkthrough, see [HF_DEPLOYMENT_PLAN.md](./HF_DEPLOYMENT_PLAN.md).

---

## ⚖️ Legal & Ethical Notice

> This platform is designed **exclusively for lawful OSINT operations** by authorized NCB personnel under the provisions of the **Narcotic Drugs and Psychotropic Substances (NDPS) Act, 1985**.  
> - ✅ Only public channel data is accessed  
> - ✅ No private messages or accounts are intercepted  
> - ✅ All evidence is SHA-256 hashed for court admissibility  
> - ❌ Unauthorized use is strictly prohibited
