#!/bin/bash
echo "🧪 Testing router setup..."

# Start dev server in background
npm run dev &
DEV_PID=$!

# Wait for server to start
sleep 5

# Test if routes respond
echo "Testing routes:"
curl -s http://localhost:5173/ >/dev/null && echo "✅ / (home)" || echo "❌ / (home)"
curl -s http://localhost:5173/phylo >/dev/null && echo "✅ /phylo" || echo "❌ /phylo"

# Kill the background process
kill $DEV_PID 2>/dev/null

echo "🚀 Manual test: Open http://localhost:5173 and check navigation"
