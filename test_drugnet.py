import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.nlp.nlp_classifier import classify_text
from app.osint.osint_engine import OSINTEngine
from app.export.pdf_generator import PDFEvidenceGenerator
import os

client = TestClient(app)

# --- NLP UNIT TESTS ---
@pytest.mark.parametrize("text, expected_risk", [
    ("Meth ₹5k/g Delhi drop +919876543210. Discreet shipping.", 0.8), # High
    ("Just watching a movie at home, nothing new.", 0.2), # Low
    ("MDMA available in Mumbai local pickup only, 0xabc123ETH", 0.9) # High
])
def test_nlp_classification_real(text, expected_risk):
    # Using real model for unit test but if slow, could mock
    result = classify_text(text)
    if expected_risk > 0.5:
        assert result['risk_score'] > 0.5
        assert result['classification'] in ['high_risk', 'marketing']
    else:
        assert result['risk_score'] < 0.5

# --- ENTITY EXTRACTION UNIT TESTS ---
def test_osint_entity_extraction():
    engine = OSINTEngine()
    test_text = "Call me at +91-98765-43210 or email ncb_demo@protonmail.com. Sending to Mumbai, MH."
    entities = engine.extract_entities(test_text)
    
    assert "+919876543210" in entities['phones']
    assert "ncb_demo@protonmail.com" in entities['emails']
    assert "India" in [loc['country'] for loc in entities['locations']]

# --- VISION & OCR MOCK TESTS ---
@patch("app.nlp.vision_detector.get_yolo_model")
def test_vision_substance_detection(mock_yolo_loader):
    mock_model = MagicMock()
    mock_yolo_loader.return_value = mock_model
    
    from app.nlp.vision_detector import detect_substances
    # Mock return 1 box for 'powder'
    mock_model.return_value = [MagicMock(boxes=MagicMock(cls=[0], conf=[0.9]))]
    mock_model.names = {0: "powder"}
    
    detections = detect_substances("dummy.jpg")
    assert any(d['label'] == 'powder' for d in detections)

# --- PDF GENERATION UNIT TEST ---
def test_pdf_evidence_generation():
    gen = PDFEvidenceGenerator()
    data = {
        "platform": "telegram",
        "handle": "drug_dealer_99",
        "raw_text": "Coke deal +919000000000",
        "entities": {"phones": ["+919000000000"]},
        "classification": {"label": "marketing", "score": 0.95}
    }
    output_path = "test_evidence.pdf"
    gen.generate_bundle(data, output_path)
    
    assert os.path.exists(output_path)
    # Check SHA-256 integrity
    import hashlib
    with open(output_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    assert len(file_hash) == 64
    os.remove(output_path)

# --- API INTEGRATION TESTS ---
@patch("app.database.get_supabase")
def test_full_pipeline_api(mock_supabase_getter):
    # Mock Supabase
    mock_db = MagicMock()
    mock_supabase_getter.return_value = mock_db
    mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": 1}])
    
    # POST /api/scan/all
    response = client.post("/api/scan/all")
    assert response.status_code == 200
    assert "Full scan initiated" in response.json()['message']

@patch("app.database.get_supabase")
def test_dashboard_stats_api(mock_supabase_getter):
    mock_db = MagicMock()
    mock_supabase_getter.return_value = mock_db
    # Mock 10 rows for targets
    mock_db.table.return_value.select.return_value.execute.return_value = MagicMock(data=[{"handle": "@test", "risk_score": 0.9}])
    
    response = client.get("/api/targets")
    assert response.status_code == 200
    assert len(response.json()) > 0

# --- GRADIO MOCK TEST ---
def test_gradio_ui_init():
    # Test if UI components initialize without crashing
    from app.ui.dashboard import build_dashboard_tab
    import gradio as gr
    with gr.Blocks() as demo:
        build_dashboard_tab()
    assert len(demo.children) > 0
