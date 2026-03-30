"""
ocr.py — OCR engine using Tesseract + OpenCV preprocessing
"""

import os
import sys
import logging
import numpy as np
from pathlib import Path
from typing import List

import cv2

try:
    import pytesseract
    # Common Windows path for Tesseract
    if sys.platform == "win32":
        tess_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(tess_path):
            pytesseract.pytesseract.tesseract_cmd = tess_path
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not installed; OCR will be skipped.")

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


# ---------------------------------------------------------------------------
# Image preprocessing
# ---------------------------------------------------------------------------

def preprocess_image(img: np.ndarray) -> np.ndarray:
    """Apply a series of CV2 transformations to maximise OCR accuracy."""
    # Convert to grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Adaptive thresholding (handles uneven lighting)
    thresh = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 10
    )

    # Deskew
    deskewed = _deskew(thresh)

    # Sharpen
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(deskewed, -1, kernel)

    return sharpened


def _deskew(image: np.ndarray) -> np.ndarray:
    """Correct skew of a binary image."""
    try:
        coords = np.column_stack(np.where(image < 128))
        if len(coords) < 10:
            return image
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        if abs(angle) < 0.5:
            return image
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated
    except Exception:
        return image


# ---------------------------------------------------------------------------
# OCR execution
# ---------------------------------------------------------------------------

def _run_tesseract(image: np.ndarray) -> str:
    """Run Tesseract on a preprocessed image array."""
    if not TESSERACT_AVAILABLE:
        return ""
    config = "--oem 3 --psm 6"
    text = pytesseract.image_to_string(image, config=config)
    return text


def _extract_from_image_file(path: str) -> str:
    """Load an image file, preprocess, and OCR it."""
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Cannot read image: {path}")
    processed = preprocess_image(img)
    return _run_tesseract(processed)


def _extract_from_pdf(path: str) -> str:
    """Extract text from a PDF using pdf2image+pytesseract or pdfplumber."""
    texts: List[str] = []

    # Try pdfplumber first (no poppler needed, works for text PDFs)
    if PDFPLUMBER_AVAILABLE:
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        texts.append(t)
            if texts:
                return "\n".join(texts)
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")

    # Fallback: render with pdf2image and OCR each page
    if PDF2IMAGE_AVAILABLE and TESSERACT_AVAILABLE:
        try:
            pages = convert_from_path(path, dpi=200)
            for page_img in pages:
                img_array = np.array(page_img)
                processed = preprocess_image(img_array)
                texts.append(_run_tesseract(processed))
            return "\n".join(texts)
        except Exception as e:
            logger.warning(f"pdf2image failed: {e}")

    # Last resort: try reading bytes as image
    raise RuntimeError(
        "Could not extract text from PDF. "
        "Install pdfplumber or pdf2image+poppler."
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_text(file_path: str) -> str:
    """
    Extract text from a medical report file.

    Parameters
    ----------
    file_path : str
        Absolute path to the uploaded file.

    Returns
    -------
    str
        Extracted raw text.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        raw = _extract_from_pdf(file_path)
    elif ext in {".jpg", ".jpeg", ".png"}:
        raw = _extract_from_image_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Normalise whitespace
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    return "\n".join(lines)
