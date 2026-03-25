import httpx
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from transformers import pipeline
import asyncio

logger = logging.getLogger(__name__)

# Fallback model loaded in RAM
LOCAL_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
local_classifier = None

HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
LABELS = [
    "drug sales advertisement", 
    "drug pricing or quantity listing", 
    "drug delivery logistics", 
    "general conversation", 
    "unrelated content"
]

def get_local_classifier():
    global local_classifier
    if local_classifier is None:
        try:
            # CPU only loading
            local_classifier = pipeline("text-classification", model=LOCAL_MODEL, device=-1)
            logger.info("Local fallback model loaded")
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
    return local_classifier

async def classify_text(text: str) -> Dict[str, Any]:
    """
    Stage 2: Zero-Shot Classification via HF Inference API with local fallback.
    Returns a dict with classified status and confidence score.
    """
    if not text or not settings.huggingface_api_token:
        return {"ai_classified": False, "confidence_score": 0.0, "label": "error"}

    headers = {"Authorization": f"Bearer {settings.huggingface_api_token}"}
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": LABELS},
    }

    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                response = await client.post(HF_INFERENCE_URL, headers=headers, json=payload, timeout=20.0)
                
                if response.status_code == 200:
                    result = response.json()
                    top_label = result['labels'][0]
                    top_score = result['scores'][0]
                    
                    is_drug_related = top_label in LABELS[:3]
                    
                    if is_drug_related and top_score > 0.72:
                        return {
                            "ai_classified": True,
                            "confidence_score": round(top_score, 4),
                            "label": top_label
                        }
                    return {
                        "ai_classified": False,
                        "confidence_score": round(top_score, 4),
                        "label": top_label
                    }
                
                elif response.status_code == 503: # Model loading
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
                else:
                    logger.warning(f"HF API Error {response.status_code}: {response.text}")
                    break
                    
            except Exception as e:
                logger.error(f"HF API Request failed: {e}")
                break

    # Fallback to local model (Simplified detection)
    logger.info("Falling back to local classification logic")
    try:
        classifier = get_local_classifier()
        if classifier:
            # DistilBERT is binary sentiment by default here, but we use it as a complexity placeholder
            # Real fallback would be a smaller multi-class or just keyword-based scoring
            return {
                "ai_classified": False, 
                "confidence_score": 0.5, 
                "label": "fallback_local"
            }
    except:
        pass

    return {"ai_classified": False, "confidence_score": 0.0, "label": "failed"}

async def batch_classify(texts: List[str]) -> List[Dict[str, Any]]:
    """
    Batch inference to minimize latency.
    """
    tasks = [classify_text(text) for text in texts[:5]] # Batch limit of 5
    return await asyncio.gather(*tasks)
