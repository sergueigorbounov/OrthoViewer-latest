#!/bin/bash
echo "🔍 Checking for missing dependencies in your components..."

# Find all import statements and see what packages are being imported
echo "📦 External packages being imported:"
grep -r "from ['\"]" src/ --include="*.tsx" --include="*.ts" | \
  sed "s/.*from ['\"]//g" | \
  sed "s/['\"].*//g" | \
  grep -v "^\./" | \
  grep -v "^\.\./" | \
  sort | uniq | \
  while read package; do
    if [[ ! -z "$package" ]]; then
      # Check if package exists in node_modules
      if [[ -d "node_modules/$package" ]]; then
        echo "✅ $package"
      else
        echo "❌ $package (MISSING)"
      fi
    fi
  done

echo ""
echo "📋 Suggested install command for missing packages:"
echo "npm install recharts @mui/x-data-grid @mui/x-charts lodash moment date-fns"
