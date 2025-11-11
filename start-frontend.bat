@echo off
echo Starting ConversationIQ Frontend...

cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install
)

REM Start Vite dev server
echo Starting Vite dev server on http://localhost:5173
call npm run dev
