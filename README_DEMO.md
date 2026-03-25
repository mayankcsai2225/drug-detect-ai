# 💎 NCB DrugNet: Quick-Demo Hub

This guide provides everything you need to perform an "Instant Impact" demonstration for recruiters or hackathon panels in under 60 seconds without needing live Telegram/Instagram scraping.

---

## 🚀 1. The Instant Demo (UI-Based)

1.  **Launch the System**: 
    ```powershell
    py -3.12 -m uvicorn app.main:app --host 0.0.0.0 --port 7860
    ```
2.  **Access Dashbord**: Open [http://127.0.0.1:7860](http://127.0.0.1:7860).
3.  **Trigger Demo Mode**:
    - Click the **🛠️ DEMO CONTROLS** accordion at the top.
    - Click the **"Load Quick Demo"** button.
    - The dashboard will instantly populate with 5 high-risk synthetic targets and real-time alerts.

---

## 🧪 2. Run the Testing Suite

Verify the integrity of the NLP pipelines, entity extraction, and OCR systems:

1.  **Install Test Dependencies**:
    ```powershell
    pip install -r requirements-test.txt
    ```
2.  **Run All Tests**:
    ```powershell
    pytest test_drugnet.py --cov=app -v
    ```
    *All tests (NLP, OCR, OSINT, PDF Gen) should pass in < 20s.*

---

## 🏗️ 3. Deliverables for Submission

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Test Suite** | `test_drugnet.py` | Pytest suite with 80%+ code coverage. |
| **Demo Endpoint** | `/demo/load` | Fast API endpoint for instant data population. |
| **Synthetic Data** | `demo_data.json` | 30+ records of drug-related synthetic posts. |
| **CI Support** | `docker-compose.test.yml` | Containerized test environment. |

---

## 📜 4. Key Performance Highlights for Demo
- **Automatic Alert Highlighting**: Synthetic alerts in Mumbai/Delhi/Goa are color-coded by severity.
- **Identity Graph**: Go to "OSINT MAP" and select `@darkmarket_mumbai` to see the connection map.
- **Evidence Bundle**: In the "EVIDENCE Explorer", paste any sample text from `demo_data.json` and click "Export" to show the SHA-256 protected PDF.
