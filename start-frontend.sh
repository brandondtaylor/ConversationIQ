#!/bin/bash

echo "🎨 Starting ConversationIQ Frontend..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Start Vite dev server
echo "Starting Vite dev server on http://localhost:5173"
npm run dev
