"""
analyzer.py — Medical parameter extraction, health analysis, and risk detection
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Reference ranges  {name: {unit, ranges_male, ranges_female, ranges_general}}
# ---------------------------------------------------------------------------

PARAMETERS: Dict[str, Dict] = {
    "Hemoglobin": {
        "unit": "g/dL",
        "patterns": [
            r"hemo?globin[^\d]*(\d+\.?\d*)",
            r"hb[^\d]*(\d+\.?\d*)",
            r"haemo?globin[^\d]*(\d+\.?\d*)",
        ],
        "male":   (13.5, 17.5),
        "female": (12.0, 15.5),
        "general": (12.0, 17.5),
    },
    "Glucose": {
        "unit": "mg/dL",
        "patterns": [
            r"(?:fasting\s*)?(?:blood\s*)?glucose[^\d]*(\d+\.?\d*)",
            r"(?:fasting\s*)?blood\s*sugar[^\d]*(\d+\.?\d*)",
            r"fbg[^\d]*(\d+\.?\d*)",
        ],
        "general": (70, 99),
        "critical_high": 400,
        "critical_low": 40,
    },
    "Cholesterol": {
        "unit": "mg/dL",
        "patterns": [
            r"(?:total\s*)?cholesterol[^\d]*(\d+\.?\d*)",
            r"tc[^\d]*(\d+\.?\d*)",
        ],
        "general": (0, 200),
        "high_threshold": 240,
    },
    "BloodPressureSystolic": {
        "unit": "mmHg",
        "patterns": [
            r"(?:systolic|bps|sbp)[^\d]*(\d+\.?\d*)",
            r"blood\s*pressure[^\d]*(\d+)[\s/]+\d+",
            r"bp[^\d]*(\d+)[\s/]+\d+",
        ],
        "general": (90, 120),
    },
    "BloodPressureDiastolic": {
        "unit": "mmHg",
        "patterns": [
            r"(?:diastolic|bpd|dbp)[^\d]*(\d+\.?\d*)",
            r"blood\s*pressure[^\d]*\d+[\s/]+(\d+)",
            r"bp[^\d]*\d+[\s/]+(\d+)",
        ],
        "general": (60, 80),
    },
    "Platelets": {
        "unit": "×10³/µL",
        "patterns": [
            r"platelet[^\d]*(\d+\.?\d*)",
            r"plt[^\d]*(\d+\.?\d*)",
        ],
        "general": (150, 400),
    },
    "WBC": {
        "unit": "×10³/µL",
        "patterns": [
            r"(?:total\s*)?(?:white\s*blood\s*cells?|wbc|leukocytes?)[^\d]*(\d+\.?\d*)",
            r"tlc[^\d]*(\d+\.?\d*)",
        ],
        "general": (4.0, 11.0),
    },
    "RBC": {
        "unit": "×10⁶/µL",
        "patterns": [
            r"(?:red\s*blood\s*cells?|rbc)[^\d]*(\d+\.?\d*)",
        ],
        "male":   (4.7, 6.1),
        "female": (4.2, 5.4),
        "general": (4.2, 6.1),
    },
    "Creatinine": {
        "unit": "mg/dL",
        "patterns": [
            r"creatinine[^\d]*(\d+\.?\d*)",
            r"cr[^\d]*(\d+\.?\d*)",
        ],
        "male":   (0.74, 1.35),
        "female": (0.59, 1.04),
        "general": (0.59, 1.35),
    },
    "Urea": {
        "unit": "mg/dL",
        "patterns": [
            r"(?:blood\s*)?urea[^\d]*(\d+\.?\d*)",
            r"bun[^\d]*(\d+\.?\d*)",
        ],
        "general": (7, 25),
    },
}

# Risk rule definitions
RISK_RULES = [
    {
        "id": "anemia",
        "name": "Anemia",
        "condition": lambda p: _val(p, "Hemoglobin") is not None and _val(p, "Hemoglobin") < 12,
        "severity": "Moderate",
        "recommendation": "Consult a hematologist. Increase iron-rich foods and consider iron supplementation.",
    },
    {
        "id": "severe_anemia",
        "name": "Severe Anemia",
        "condition": lambda p: _val(p, "Hemoglobin") is not None and _val(p, "Hemoglobin") < 8,
        "severity": "Critical",
        "recommendation": "Seek immediate medical attention. Blood transfusion may be required.",
    },
    {
        "id": "polycythemia",
        "name": "Polycythemia",
        "condition": lambda p: _val(p, "Hemoglobin") is not None and _val(p, "Hemoglobin") > 18,
        "severity": "High",
        "recommendation": "Consult a hematologist. Monitor for clotting risk.",
    },
    {
        "id": "diabetes",
        "name": "Diabetes (Suspected)",
        "condition": lambda p: _val(p, "Glucose") is not None and _val(p, "Glucose") > 126,
        "severity": "High",
        "recommendation": "Consult an endocrinologist. Monitor blood sugar regularly and adopt a low-glycaemic diet.",
    },
    {
        "id": "prediabetes",
        "name": "Pre-Diabetes",
        "condition": lambda p: _val(p, "Glucose") is not None and 100 < _val(p, "Glucose") <= 126,
        "severity": "Moderate",
        "recommendation": "Adopt a balanced diet, increase physical activity, and schedule follow-up glucose tests.",
    },
    {
        "id": "hypoglycemia",
        "name": "Hypoglycemia",
        "condition": lambda p: _val(p, "Glucose") is not None and _val(p, "Glucose") < 70,
        "severity": "High",
        "recommendation": "Immediate glucose intake. Investigate underlying cause with a physician.",
    },
    {
        "id": "high_cholesterol",
        "name": "Hypercholesterolemia (Heart Disease Risk)",
        "condition": lambda p: _val(p, "Cholesterol") is not None and _val(p, "Cholesterol") > 240,
        "severity": "High",
        "recommendation": "Consult a cardiologist. Adopt a low-fat diet, exercise regularly, consider statins.",
    },
    {
        "id": "borderline_cholesterol",
        "name": "Borderline High Cholesterol",
        "condition": lambda p: _val(p, "Cholesterol") is not None and 200 < _val(p, "Cholesterol") <= 240,
        "severity": "Moderate",
        "recommendation": "Reduce saturated fat intake. Increase physical activity and schedule a lipid panel recheck.",
    },
    {
        "id": "hypertension",
        "name": "Hypertension",
        "condition": lambda p: (
            _val(p, "BloodPressureSystolic") is not None and _val(p, "BloodPressureSystolic") > 140
        ) or (
            _val(p, "BloodPressureDiastolic") is not None and _val(p, "BloodPressureDiastolic") > 90
        ),
        "severity": "High",
        "recommendation": "Consult a cardiologist. Reduce sodium intake, manage stress, and consider antihypertensive therapy.",
    },
    {
        "id": "thrombocytopenia",
        "name": "Thrombocytopenia (Low Platelets)",
        "condition": lambda p: _val(p, "Platelets") is not None and _val(p, "Platelets") < 150,
        "severity": "Moderate",
        "recommendation": "Consult a hematologist. Investigate cause (dengue, ITP, medications).",
    },
    {
        "id": "thrombocytosis",
        "name": "Thrombocytosis (High Platelets)",
        "condition": lambda p: _val(p, "Platelets") is not None and _val(p, "Platelets") > 400,
        "severity": "Moderate",
        "recommendation": "Consult a physician. Rule out infection, inflammation, or myeloproliferative disorder.",
    },
    {
        "id": "leukocytosis",
        "name": "Leukocytosis (High WBC — Infection Risk)",
        "condition": lambda p: _val(p, "WBC") is not None and _val(p, "WBC") > 11,
        "severity": "Moderate",
        "recommendation": "Consult a physician. May indicate infection, inflammation, or blood disorder.",
    },
    {
        "id": "leukopenia",
        "name": "Leukopenia (Low WBC — Immune Risk)",
        "condition": lambda p: _val(p, "WBC") is not None and _val(p, "WBC") < 4,
        "severity": "Moderate",
        "recommendation": "Consult a physician. Investigate bone marrow function and immune health.",
    },
    {
        "id": "kidney_disease",
        "name": "Possible Kidney Dysfunction",
        "condition": lambda p: (
            _val(p, "Creatinine") is not None and _val(p, "Creatinine") > 1.35
        ) or (
            _val(p, "Urea") is not None and _val(p, "Urea") > 50
        ),
        "severity": "High",
        "recommendation": "Consult a nephrologist. Stay well-hydrated and avoid nephrotoxic drugs.",
    },
]


def _val(params: Dict[str, Any], key: str) -> Optional[float]:
    """Safely extract numeric value from a parameter dict."""
    p = params.get(key)
    if p is None:
        return None
    return p.get("value")


# ---------------------------------------------------------------------------
# Parameter extraction
# ---------------------------------------------------------------------------

def _extract_value(text: str, patterns: List[str]) -> Optional[float]:
    """Try each regex pattern; return first valid float match."""
    text_lower = text.lower()
    for pat in patterns:
        try:
            m = re.search(pat, text_lower)
            if m:
                return float(m.group(1))
        except (ValueError, IndexError):
            continue
    return None


def _determine_status(
    name: str,
    value: float,
    gender: str = "general",
) -> Tuple[str, Tuple[float, float]]:
    """
    Return (status_label, (low, high)) tuple.
    status_label ∈ {Normal, Low, High, Critical}
    """
    info = PARAMETERS[name]
    if gender in ("male", "female") and gender in info:
        low, high = info[gender]
    else:
        low, high = info["general"]

    # Check critical thresholds first
    crit_high = info.get("critical_high")
    crit_low = info.get("critical_low")
    if crit_high is not None and value > crit_high:
        return "Critical", (low, high)
    if crit_low is not None and value < crit_low:
        return "Critical", (low, high)

    if value < low:
        status = "Low"
    elif value > high:
        status = "High"
    else:
        status = "Normal"

    # Escalate "High" cholesterol beyond hard threshold to Critical
    ht = info.get("high_threshold")
    if ht is not None and value > ht:
        status = "Critical"

    return status, (low, high)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_parameters(text: str, gender: str = "general") -> Dict[str, Any]:
    """
    Extract all detectable medical parameters from OCR text.

    Returns
    -------
    dict mapping parameter name → {value, unit, status, range_low, range_high}
    """
    results: Dict[str, Any] = {}
    for name, info in PARAMETERS.items():
        value = _extract_value(text, info["patterns"])
        if value is None:
            continue
        status, (range_low, range_high) = _determine_status(name, value, gender)
        results[name] = {
            "value": value,
            "unit": info["unit"],
            "status": status,
            "range_low": range_low,
            "range_high": range_high,
        }
    return results


def detect_risks(parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply rule-based risk detection on extracted parameters.

    Returns
    -------
    list of risk dicts: {id, name, severity, recommendation}
    """
    risks = []
    for rule in RISK_RULES:
        try:
            if rule["condition"](parameters):
                risks.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "recommendation": rule["recommendation"],
                })
        except Exception as e:
            logger.warning(f"Risk rule {rule['id']} error: {e}")
    return risks


def analyze(text: str, gender: str = "general") -> Dict[str, Any]:
    """
    Full analysis pipeline: extract parameters → detect risks → summarise.

    Returns
    -------
    {
        "parameters": {...},
        "risks": [...],
        "summary": {
            "total_detected": int,
            "abnormal_count": int,
            "risk_count": int,
            "overall_status": str,
        }
    }
    """
    parameters = extract_parameters(text, gender)
    risks = detect_risks(parameters)

    abnormal = [
        k for k, v in parameters.items() if v["status"] != "Normal"
    ]
    critical_params = [
        k for k, v in parameters.items() if v["status"] == "Critical"
    ]
    critical_risks = [r for r in risks if r["severity"] == "Critical"]

    if critical_params or critical_risks:
        overall = "Critical"
    elif abnormal or risks:
        overall = "Needs Attention"
    elif parameters:
        overall = "Healthy"
    else:
        overall = "Insufficient Data"

    summary = {
        "total_detected": len(parameters),
        "abnormal_count": len(abnormal),
        "risk_count": len(risks),
        "overall_status": overall,
        "abnormal_parameters": abnormal,
    }

    return {
        "parameters": parameters,
        "risks": risks,
        "summary": summary,
    }
