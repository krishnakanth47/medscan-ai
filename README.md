# 🩺 MedScan AI — Intelligent Medical Report Analyzer

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org/)
[![Tesseract](https://img.shields.io/badge/OCR-Tesseract-5C5C5C)](https://tesseract-ocr.github.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)

> **MedScan AI** is a production-ready AI healthcare web application that analyzes medical reports using OCR and machine learning to detect abnormal health parameters and generate actionable health insights.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Multi-format Upload** | Supports PDF, JPG, JPEG, PNG (up to 10 MB) |
| 🔍 **OCR Extraction** | Tesseract + OpenCV preprocessing (denoise, deskew, threshold) |
| 📊 **9 Biomarkers** | Hemoglobin, Glucose, Cholesterol, BP, Platelets, WBC, RBC, Creatinine, Urea |
| 🚨 **Risk Detection** | Rule-based engine — Anemia, Diabetes, Heart Disease, Hypertension, and more |
| 📈 **Visual Dashboard** | Radar chart, parameter cards, color-coded status badges |
| 📥 **PDF Export** | Branded, professional ReportLab-generated health report |
| 🐳 **Docker Ready** | One-command deployment with `docker-compose up` |

---

## 🏗️ Architecture

```
MedScan AI
├── backend/          # Python FastAPI
│   ├── main.py           # API routes & app entry
│   ├── ocr.py            # Tesseract + OpenCV pipeline
│   ├── analyzer.py       # Regex extraction + risk engine
│   ├── report_generator.py # ReportLab PDF builder
│   ├── database.py       # SQLite CRUD layer
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
│       ├── test_analyzer.py
│       └── test_api.py
├── frontend/         # React + Tailwind CSS (Vite)
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── UploadForm.jsx
│           ├── Dashboard.jsx
│           └── ResultCard.jsx
├── data/
│   └── sample_reports/sample_abnormal.txt
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start

### Option A — Docker (Recommended)

> Requires Docker Desktop installed and running.

```bash
cd C:\Users\HP\OneDrive\Desktop\health
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### Option B — Local Development

#### 1. Backend

```powershell
# Install Tesseract OCR (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR\

cd C:\Users\HP\OneDrive\Desktop\health\backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 2. Frontend

```powershell
cd C:\Users\HP\OneDrive\Desktop\health\frontend
npm install        # already done if scaffolded
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | System health check |
| `POST` | `/upload` | Upload report file |
| `POST` | `/analyze/{id}` | Run OCR + analysis |
| `GET`  | `/report/{id}` | Retrieve report data |
| `GET`  | `/reports` | List recent reports |
| `GET`  | `/download/{id}` | Download PDF report |

Interactive docs: **http://localhost:8000/docs**

---

## 🧪 Running Tests

```powershell
cd C:\Users\HP\OneDrive\Desktop\health\backend
pip install pytest httpx
pytest tests/ -v
```

---

## 📋 Detected Biomarkers & Risk Rules

| Parameter | Unit | Normal Range | Risk If Abnormal |
|-----------|------|-------------|-----------------|
| Hemoglobin | g/dL | M: 13.5–17.5 / F: 12–15.5 | Anemia (< 12) |
| Glucose | mg/dL | 70–99 | Diabetes (> 126), Pre-Diabetes (100–126) |
| Cholesterol | mg/dL | < 200 | Heart Disease Risk (> 240) |
| Blood Pressure | mmHg | 120/80 | Hypertension (> 140/90) |
| Platelets | ×10³/µL | 150–400 | Thrombocytopenia / Thrombocytosis |
| WBC | ×10³/µL | 4.0–11.0 | Leukocytosis / Leukopenia |
| RBC | ×10⁶/µL | 4.2–6.1 | Polycythemia / Anaemia |
| Creatinine | mg/dL | 0.74–1.35 | Kidney Dysfunction |
| Urea (BUN) | mg/dL | 7–25 | Kidney Dysfunction |

---

## 🛡️ Security Notes

- File type and size validated server-side
- Uploaded files are renamed with UUID to prevent path traversal
- CORS restricted (configure `allow_origins` for production)
- No authentication by default — add OAuth2/JWT for production

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | Python 3.11 · FastAPI |
| OCR | Tesseract · pytesseract |
| Image Processing | OpenCV |
| PDF Parsing | pdfplumber · pdf2image |
| PDF Generation | ReportLab |
| Database | SQLite |
| Frontend | React 18 · Vite |
| Styling | Tailwind CSS v4 |
| Charts | Recharts |
| Deployment | Docker · docker-compose |

---

## 📝 License

MIT — for educational/demonstration use. **Not intended for clinical diagnosis.**
