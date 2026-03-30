"""
database.py — SQLite database layer for MedScan AI
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "medscan.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                upload_time TEXT NOT NULL,
                file_path TEXT,
                extracted_text TEXT,
                analysis_result TEXT,
                risk_summary TEXT,
                status TEXT DEFAULT 'uploaded'
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_report(filename: str, file_path: str) -> int:
    """Insert a new report record and return its ID."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO reports (filename, upload_time, file_path, status) VALUES (?, ?, ?, ?)",
            (filename, datetime.utcnow().isoformat(), file_path, "uploaded")
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_analysis(
    report_id: int,
    extracted_text: str,
    analysis_result: Dict[str, Any],
    risk_summary: Dict[str, Any]
):
    """Store OCR text and analysis results."""
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE reports
               SET extracted_text = ?,
                   analysis_result = ?,
                   risk_summary = ?,
                   status = ?
               WHERE id = ?""",
            (
                extracted_text,
                json.dumps(analysis_result),
                json.dumps(risk_summary),
                "analyzed",
                report_id,
            )
        )
        conn.commit()
    finally:
        conn.close()


def get_report(report_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a report by ID."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM reports WHERE id = ?", (report_id,)
        ).fetchone()
        if row is None:
            return None
        data = dict(row)
        if data.get("analysis_result"):
            data["analysis_result"] = json.loads(data["analysis_result"])
        if data.get("risk_summary"):
            data["risk_summary"] = json.loads(data["risk_summary"])
        return data
    finally:
        conn.close()


def list_reports(limit: int = 20) -> list:
    """List recent reports."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, filename, upload_time, status FROM reports ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
