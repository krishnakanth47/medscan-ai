"""
tests/test_analyzer.py — Unit tests for the health analysis engine
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from analyzer import extract_parameters, detect_risks, analyze


SAMPLE_TEXT = """
PATIENT MEDICAL REPORT
Hemoglobin: 10.2 g/dL
Glucose (Fasting): 135 mg/dL
Total Cholesterol: 255 mg/dL
Blood Pressure: 145/95 mmHg
Platelet Count: 220 x10^3/uL
WBC: 9.2 x10^3/uL
RBC: 4.5 x10^6/uL
Creatinine: 1.0 mg/dL
Urea: 18 mg/dL
"""

NORMAL_TEXT = """
Hemoglobin: 14.2 g/dL
Glucose: 88 mg/dL
Total Cholesterol: 185 mg/dL
Blood Pressure: 118/76 mmHg
Platelet Count: 280 x10^3/uL
WBC: 7.0
RBC: 5.0
Creatinine: 0.9
Urea: 15
"""


class TestExtractParameters:
    def test_hemoglobin_extracted(self):
        params = extract_parameters(SAMPLE_TEXT)
        assert "Hemoglobin" in params
        assert params["Hemoglobin"]["value"] == 10.2

    def test_glucose_extracted(self):
        params = extract_parameters(SAMPLE_TEXT)
        assert "Glucose" in params
        assert params["Glucose"]["value"] == 135.0

    def test_cholesterol_extracted(self):
        params = extract_parameters(SAMPLE_TEXT)
        assert "Cholesterol" in params
        assert params["Cholesterol"]["value"] == 255.0

    def test_status_low_hemoglobin(self):
        params = extract_parameters(SAMPLE_TEXT)
        assert params["Hemoglobin"]["status"] == "Low"

    def test_status_high_glucose(self):
        params = extract_parameters(SAMPLE_TEXT)
        assert params["Glucose"]["status"] == "High"

    def test_status_critical_cholesterol(self):
        params = extract_parameters(SAMPLE_TEXT)
        assert params["Cholesterol"]["status"] == "Critical"

    def test_normal_values(self):
        params = extract_parameters(NORMAL_TEXT)
        for name, data in params.items():
            assert data["status"] == "Normal", f"{name} should be Normal"


class TestDetectRisks:
    def test_anemia_detected(self):
        params = extract_parameters(SAMPLE_TEXT)
        risks = detect_risks(params)
        ids = [r["id"] for r in risks]
        assert "anemia" in ids

    def test_diabetes_detected(self):
        params = extract_parameters(SAMPLE_TEXT)
        risks = detect_risks(params)
        ids = [r["id"] for r in risks]
        assert "diabetes" in ids

    def test_high_cholesterol_risk(self):
        params = extract_parameters(SAMPLE_TEXT)
        risks = detect_risks(params)
        ids = [r["id"] for r in risks]
        assert "high_cholesterol" in ids

    def test_hypertension_detected(self):
        params = extract_parameters(SAMPLE_TEXT)
        risks = detect_risks(params)
        ids = [r["id"] for r in risks]
        assert "hypertension" in ids

    def test_no_risks_for_normal(self):
        params = extract_parameters(NORMAL_TEXT)
        risks = detect_risks(params)
        assert len(risks) == 0


class TestAnalyze:
    def test_returns_all_keys(self):
        result = analyze(SAMPLE_TEXT)
        assert "parameters" in result
        assert "risks" in result
        assert "summary" in result

    def test_overall_status_needs_attention(self):
        result = analyze(SAMPLE_TEXT)
        assert result["summary"]["overall_status"] in ("Needs Attention", "Critical")

    def test_overall_status_healthy(self):
        result = analyze(NORMAL_TEXT)
        assert result["summary"]["overall_status"] == "Healthy"

    def test_empty_text(self):
        result = analyze("")
        assert result["summary"]["overall_status"] == "Insufficient Data"
        assert result["summary"]["total_detected"] == 0
