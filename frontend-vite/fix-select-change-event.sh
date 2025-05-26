#!/bin/bash
echo "🔧 Fixing SelectChangeEvent imports in both files..."

# Files to fix
files=("src/components/pages/VisualizationPage.tsx" "src/components/pages/AnalysisPage.tsx")

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "Fixing $file"
    
    # Create a backup
    cp "$file" "$file.backup"
    
    # Use node to fix the imports properly
    node -e "
    const fs = require('fs');
    let content = fs.readFileSync('$file', 'utf8');
    
    // Remove SelectChangeEvent from the main MUI import
    content = content.replace(
      /(import\s*{\s*[^}]*),\s*SelectChangeEvent\s*([^}]*}\s*from\s*['\"]\@mui\/material['\"]\s*;)/,
      '\$1\$2'
    );
    
    content = content.replace(
      /(import\s*{\s*)SelectChangeEvent\s*,\s*([^}]*}\s*from\s*['\"]\@mui\/material['\"]\s*;)/,
      '\$1\$2'
    );
    
    // Add the correct import after the MUI import line
    if (!content.includes('from \"@mui/material/Select\"')) {
      content = content.replace(
        /(import\s*{[^}]*}\s*from\s*['\"]\@mui\/material['\"]\s*;)/,
        '\$1\nimport type { SelectChangeEvent } from \"@mui/material/Select\";'
      );
    }
    
    fs.writeFileSync('$file', content);
    console.log('✅ Fixed $file');
    "
  fi
done

echo "✅ All SelectChangeEvent imports fixed!"
