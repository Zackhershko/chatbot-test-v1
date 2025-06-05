@echo off
REM Start Python FastAPI server
start cmd /k "python main.py"

REM Start local web server for index.html on port 5500
start cmd /k "python -m http.server 5500"

echo Servers started:
echo FastAPI server running on http://localhost:8000
echo Web server running on http://localhost:5500
