#!/bin/bash
set -e

echo "🕊️ Starting AI Religion Architects with Claude API..."

# Validate required environment variables
if [ -z "$CLAUDE_API_KEY" ]; then
    echo "❌ ERROR: CLAUDE_API_KEY environment variable is required"
    echo "Please set your Claude API key in the .env file"
    exit 1
fi

echo "✅ Claude API key configured"
echo "📊 Configuration:"
echo "   Model: ${CLAUDE_MODEL:-claude-3-sonnet-20240229}"
echo "   Cycle Interval: ${CYCLE_INTERVAL_HOURS:-1} hour(s)"
echo "   Max Tokens: ${CLAUDE_MAX_TOKENS:-2000}"

# Start the WebSocket server in the background
echo "🔌 Starting WebSocket server..."
cd /app/backend
uvicorn websocket_server:app --host 0.0.0.0 --port 8000 --workers 1 &
WEBSOCKET_PID=$!

# Wait for WebSocket server to be ready
echo "⏳ Waiting for WebSocket server to be ready..."
sleep 5

# Test WebSocket server
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ WebSocket server is running"
else
    echo "⚠️  WebSocket server may not be responding"
fi

# Start the Claude-powered orchestrator
echo "🚀 Starting Claude orchestrator with APScheduler..."
cd /app
python run_claude_system.py --no-websocket

# If orchestrator exits, kill WebSocket server
echo "🛑 Orchestrator stopped, cleaning up..."
kill $WEBSOCKET_PID 2>/dev/null || true

echo "✨ AI Religion Architects stopped."