@echo off
echo Starting AI Resume Assistant...
echo.
echo Starting backend server in new window...
start "Backend Server" cmd /k "python app.py"
timeout /t 3 /nobreak >nul
echo.
echo Starting frontend server in new window...
start "Frontend Server" cmd /k "cd frontend && npm install && npm run dev"
echo.
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
pause

