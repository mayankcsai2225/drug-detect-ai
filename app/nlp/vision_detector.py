from ultralytics import YOLO
import cv2
import logging
import asyncio
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# YOLO Model Initialization
# Loading the nano model for CPU inference
MODEL_PATH = "yolov8n.pt"
yolo_model = None

def get_yolo_model():
    global yolo_model
    if yolo_model is None:
        try:
            yolo_model = YOLO(MODEL_PATH)
            logger.info(f"YOLOv8n model {MODEL_PATH} loaded")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
    return yolo_model

async def detect_substances(image_path: str) -> List[Dict[str, Any]]:
    """
    Detect suspicious substances in images using YOLOv8n CPU.
    Returns a list of detections with labels and confidence.
    """
    if not image_path:
        return []

    model = get_yolo_model()
    if not model:
        return []

    try:
        # Run detection in a non-blocking thread
        results = await asyncio.to_thread(model, image_path, imgsz=320, conf=0.6, verbose=False)
        
        detections = []
        # Suspicious drug-related classes (Placeholder map based on COCO classes)
        # Note: COCO classes for drugs aren't standard, but we look for common objects
        # or custom class IDs if fine-tuned. For pre-trained, we log labels found.
        
        for r in results:
            for box in r.boxes:
                label = model.names[int(box.cls[0])]
                conf = float(box.conf[0])
                
                # Highlighted suspicious labels for drug narcotics context (approximate)
                suspicious_labels = ['pill', 'powder', 'syringe', 'cannabis', 'bottle', 'plastic bag']
                
                if label in suspicious_labels:
                    detections.append({
                        "label": label,
                        "confidence": round(conf, 4),
                        "box": [float(x) for x in box.xyxy[0]]
                    })
        
        return detections
    except Exception as e:
        logger.error(f"YOLO Error detecting substances in {image_path}: {e}")
        return []
