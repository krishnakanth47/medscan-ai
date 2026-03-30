"""
tests/test_api.py — Integration tests for FastAPI endpoints
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import io
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Ensure DB tables exist before each test."""
    from database import create_db
    create_db()


class TestHealthEndpoint:
    def test_health_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestUploadEndpoint:
    def test_upload_txt_rejected(self):
        resp = client.post(
            "/upload",
            files={"file": ("test.txt", b"some text", "text/plain")},
        )
        assert resp.status_code == 400

    def test_upload_png_accepted(self):
        # 1x1 white PNG
        png_bytes = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
            b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
            b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        resp = client.post(
            "/upload",
            files={"file": ("report.png", png_bytes, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "report_id" in data
        assert data["report_id"] > 0


class TestReportEndpoint:
    def test_get_nonexistent_report(self):
        resp = client.get("/report/99999")
        assert resp.status_code == 404

    def test_analyze_nonexistent_report(self):
        resp = client.post("/analyze/99999")
        assert resp.status_code == 404

    def test_download_unanalyzed_report(self):
        # Upload first
        png_bytes = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
            b'\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18'
            b'\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        upload_resp = client.post(
            "/upload",
            files={"file": ("report.png", png_bytes, "image/png")},
        )
        report_id = upload_resp.json()["report_id"]
        dl_resp = client.get(f"/download/{report_id}")
        # Should return 400 because not yet analysed
        assert dl_resp.status_code == 400


class TestListReports:
    def test_list_returns_array(self):
        resp = client.get("/reports")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
