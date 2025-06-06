@echo off
set FRONTEND_URL=https://chatbot-test-v1-1.onrender.com/ping
set PING_INTERVAL=300

echo Starting ping to %FRONTEND_URL% every 5 minutes...

:loop
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%

curl -s -o nul -w "%%{http_code}" "%FRONTEND_URL%" > temp.txt
set /p STATUS=<temp.txt
del temp.txt

echo [%TIMESTAMP%] Pinged %FRONTEND_URL% - Status: %STATUS%
timeout /t %PING_INTERVAL% /nobreak > nul
goto loop