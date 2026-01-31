@echo off
echo Starting Wedding Photo Gallery...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run Streamlit app
streamlit run app.py

pause
