"""
main.py — FastAPI application for MedScan AI
"""

import os
import io
import logging
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from database import create_db, get_report, list_reports, save_report, update_analysis
from ocr import extract_text, SUPPORTED_EXTENSIONS
from analyzer import analyze
from report_generator import generate_pdf

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="MedScan AI",
    description="Intelligent Medical Report Analyzer API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    create_db()
    logger.info("Database initialised.")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"])
async def health_check():
    """System health check."""
    return {"status": "ok", "service": "MedScan AI", "version": "1.0.0"}


@app.post("/upload", tags=["Reports"])
async def upload_report(file: UploadFile = File(...)):
    """
    Upload a medical report (PDF / JPG / PNG).

    Returns: { report_id, filename, message }
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Accepted: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    # Read and check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit.")

    # Save to disk with unique name
    safe_name = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOADS_DIR / safe_name
    with open(save_path, "wb") as f:
        f.write(content)

    report_id = save_report(file.filename, str(save_path))
    logger.info(f"Uploaded report #{report_id}: {file.filename}")

    return {
        "report_id": report_id,
        "filename": file.filename,
        "message": "File uploaded successfully. Call POST /analyze/{report_id} to process.",
    }


@app.post("/analyze/{report_id}", tags=["Reports"])
async def analyze_report(report_id: int, gender: Optional[str] = "general"):
    """
    Run OCR + health analysis on an uploaded report.

    Query param: gender = male | female | general (default)
    Returns: full analysis JSON
    """
    report = get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report #{report_id} not found.")

    file_path = report.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Original file not found on server.")

    # --- OCR ---
    try:
        logger.info(f"Starting OCR for report #{report_id}")
        raw_text = extract_text(file_path)
    except Exception as e:
        logger.error(f"OCR failed for report #{report_id}: {e}")
        raise HTTPException(status_code=422, detail=f"OCR extraction failed: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text could be extracted from the file."
        )

    # --- Analysis ---
    try:
        result = analyze(raw_text, gender=gender)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis engine error: {str(e)}")

    # --- Persist ---
    update_analysis(
        report_id,
        extracted_text=raw_text,
        analysis_result=result,
        risk_summary=result.get("summary", {}),
    )

    logger.info(
        f"Report #{report_id} analysed — "
        f"{result['summary']['total_detected']} parameters, "
        f"{result['summary']['risk_count']} risks."
    )

    return {
        "report_id": report_id,
        "filename": report["filename"],
        "upload_time": report["upload_time"],
        **result,
    }


@app.get("/report/{report_id}", tags=["Reports"])
async def get_report_endpoint(report_id: int):
    """Retrieve a previously analysed report by ID."""
    report = get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report #{report_id} not found.")
    return report


@app.get("/reports", tags=["Reports"])
async def list_reports_endpoint(limit: int = 20):
    """List recent reports (id, filename, upload_time, status)."""
    return list_reports(limit)


@app.get("/download/{report_id}", tags=["Reports"])
async def download_pdf(report_id: int):
    """Generate and stream a PDF health report."""
    report = get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"Report #{report_id} not found.")

    if report.get("status") != "analyzed":
        raise HTTPException(
            status_code=400,
            detail="Report has not been analysed yet. Call POST /analyze/{id} first."
        )

    analysis_result = report.get("analysis_result") or {}
    risk_summary = report.get("risk_summary") or {}

    try:
        pdf_bytes = generate_pdf(
            report_id=report_id,
            filename=report["filename"],
            upload_time=report["upload_time"],
            analysis_result=analysis_result,
            risk_summary=risk_summary,
            extracted_text=report.get("extracted_text"),
        )
    except Exception as e:
        logger.error(f"PDF generation failed for report #{report_id}: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="medscan_report_{report_id}.pdf"'
        },
    )


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again."},
    )
