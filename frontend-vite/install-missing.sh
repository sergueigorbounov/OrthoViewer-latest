#!/bin/bash
echo "📦 Installing the specific missing packages..."

# MUI Icons (for Biotech icon and others)
npm install @mui/icons-material

# Web Vitals (for performance monitoring)
npm install web-vitals

# Make sure react-dom is correct version
npm install react-dom@latest

# Also install some other common MUI components you might need
npm install @mui/lab @mui/x-data-grid

echo "✅ Missing packages installed!"
echo "🚀 Try starting: npm run dev"
