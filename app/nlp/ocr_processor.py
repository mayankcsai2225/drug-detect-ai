import pytesseract
from PIL import Image
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

async def extract_text_from_image(image_path: str) -> str:
    """
    Extract text content from an image using Pytesseract OCR.
    Runs OCR logic in a separate thread.
    """
    if not image_path:
        return ""

    try:
        # Load image and resize if too large
        img = Image.open(image_path)
        img.thumbnail((800, 800)) # Limit image size for performance

        # Run OCR in a non-blocking way
        text = await asyncio.to_thread(_run_ocr, img)
        return text if text else ""
    except Exception as e:
        logger.error(f"OCR Error extracting text from {image_path}: {e}")
        return ""

def _run_ocr(img: Image.Image) -> str:
    """
    Synchronous OCR execution.
    """
    # Using 'hin+eng' for Hindi and English support as specified
    return pytesseract.image_to_string(img, lang='eng+hin')
