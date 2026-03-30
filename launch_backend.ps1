$BACKEND = "C:\Users\HP\OneDrive\Desktop\health\backend"

Write-Host "=== MedScan AI Backend ===" -ForegroundColor Cyan
Write-Host ""

# The .venv is bare - use system Python instead
Write-Host "[1/2] Installing requirements with system Python..." -ForegroundColor Yellow
python -m pip install -r "$BACKEND\requirements.txt"

if ($LASTEXITCODE -ne 0) {
    Write-Host "FAILED. Make sure Python is installed and in PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/2] Starting backend on http://localhost:8000 ..." -ForegroundColor Green
Write-Host "      Keep this window open while using the app." -ForegroundColor DarkGray
Write-Host ""
Set-Location $BACKEND
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
