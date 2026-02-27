@echo off
echo ========================================
echo   AgriPOS - Windows Local Setup
echo ========================================

REM ── Step 1: Create PostgreSQL user and database ──────────
echo.
echo [Step 1] Setting up PostgreSQL database...
echo   Enter your PostgreSQL superuser (postgres) password when prompted.
echo.

REM Create posuser
psql -U postgres -c "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='posuser') THEN CREATE ROLE posuser WITH LOGIN PASSWORD 'pospassword'; END IF; END $$;"

REM Create posdb
psql -U postgres -c "SELECT 'CREATE DATABASE posdb OWNER posuser' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='posdb')" | psql -U postgres

REM Fallback create
psql -U postgres -c "CREATE DATABASE posdb OWNER posuser;" 2>nul

REM Grant privileges
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE posdb TO posuser;"

REM ── Step 2: Run Schema ───────────────────────────────────
echo.
echo [Step 2] Creating database schema...
set PGPASSWORD=pospassword
psql -U posuser -d posdb -h localhost -f "%~dp0..\database\01_schema.sql"

REM ── Step 3: Seed Data ────────────────────────────────────
echo.
echo [Step 3] Inserting seed data...
python "%~dp0setup_db_seed.py"

REM ── Step 4: Create .env ──────────────────────────────────
echo.
echo [Step 4] Creating backend\.env ...
if not exist "%~dp0..\backend\.env" (
    copy "%~dp0..\backend\.env.local" "%~dp0..\backend\.env"
    echo   Created backend\.env
) else (
    echo   backend\.env already exists, skipping.
)

echo.
echo ========================================
echo   Setup complete!
echo   Login: admin / admin1234
echo ========================================
echo.
echo Next steps:
echo   cd backend
echo   pip install -r requirements.txt
echo   uvicorn app.main:app --reload --port 8000
pause
