@echo off
echo ========================================
echo Honeybee-MCP Installation Script
echo ========================================
echo.

echo Step 1: Installing all dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

echo Step 2: Reinstalling fastMCP to resolve Pydantic conflicts...
pip install --no-deps --force-reinstall fastmcp
if %errorlevel% neq 0 (
    echo ERROR: Failed to reinstall fastMCP
    exit /b 1
)
echo [OK] fastMCP reinstalled successfully
echo.

echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo You can now run the Honeybee-MCP server:
echo   python server.py
echo.