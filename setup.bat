@echo off
echo ============================================
echo   AI Research Skills MCP - Setup
echo   91 skills - 22 categories - 8 tools
echo ============================================
echo.

REM Create venv
echo Creating Python virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Python not found. Install from python.org
    echo Make sure "Add Python to PATH" is checked during install.
    pause
    exit /b 1
)

REM Activate and install deps
echo Installing dependencies...
call venv\Scripts\activate
pip install mcp pyyaml google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
if errorlevel 1 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Setup complete!
echo ============================================
echo.
echo Next steps:
echo   1. Press Win+R, type: %%APPDATA%%\Claude
echo   2. Open claude_desktop_config.json in Notepad
echo   3. Add this to your mcpServers section:
echo.
echo      "ai-research-skills": {
echo        "command": "%CD%\venv\Scripts\python.exe",
echo        "args": ["%CD%\servers\server.py"]
echo      }
echo.
echo   4. Save the file and restart Claude Desktop
echo.
pause
