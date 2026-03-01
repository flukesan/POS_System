@echo off
chcp 65001 > nul
title AgriPOS Desktop

echo ========================================
echo   AgriPOS - ระบบจัดการร้านค้าเกษตร
echo ========================================
echo.

:: Check Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] ไม่พบ Python กรุณาติดตั้ง Python 3.11+ ก่อน
    pause
    exit /b 1
)

:: Create venv if not exists
if not exist "venv\" (
    echo [SETUP] กำลังสร้าง virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install dependencies
echo [SETUP] ตรวจสอบ dependencies...
pip install -r requirements.txt -q --disable-pip-version-check

:: Copy .env if not exists
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env > nul
        echo [INFO] สร้างไฟล์ .env แล้ว กรุณาตั้งค่า API URL ในไฟล์ .env
    )
)

:: Check if backend is running
echo [INFO] ตรวจสอบการเชื่อมต่อกับ Server...
for /f "tokens=*" %%a in ('type .env ^| findstr "API_URL"') do set %%a
if "%API_URL%"=="" set API_URL=http://localhost:8000

curl -s -o nul -w "%%{http_code}" %API_URL%/health > nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] ไม่สามารถเชื่อมต่อกับ Server ที่ %API_URL%
    echo          กรุณาตรวจสอบว่า Docker backend กำลังรันอยู่
    echo.
    choice /c YN /m "ต้องการเปิดโปรแกรมต่อไปหรือไม่?"
    if errorlevel 2 exit /b 0
)

echo [START] กำลังเปิด AgriPOS...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] โปรแกรมปิดตัวผิดปกติ กรุณาตรวจสอบ log ด้านบน
    pause
)
