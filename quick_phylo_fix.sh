#!/bin/bash

echo "=== Quick Fix for phylo.py Indentation Error ==="

PHYLO_FILE="backend/app/models/phylo.py"

# Navigate to project directory
cd ~/Documents/orthoviewer2-clean

if [ ! -f "$PHYLO_FILE" ]; then
    echo "Error: $PHYLO_FILE not found"
    exit 1
fi

# Restore from backup if it exists
if [ -f "$PHYLO_FILE.backup" ]; then
    echo "Restoring from backup..."
    cp "$PHYLO_FILE.backup" "$PHYLO_FILE"
fi

# Create a temporary Python script to fix the file
cat > temp_fix.py << 'EOF'
import re

# Read the file
with open('backend/app/models/phylo.py', 'r') as f:
    content = f.read()

# Find and replace the problematic line with proper indentation
# Look for the line and capture its indentation
pattern = r'^(\s*)PhyloNodeData\.model_rebuild\(\).*$'
replacement = r'''\1# Pydantic v1 compatibility fix
\1if hasattr(PhyloNodeData, "model_rebuild"):
\1    PhyloNodeData.model_rebuild()
\1else:
\1    PhyloNodeData.update_forward_refs()'''

content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Write back the fixed content
with open('backend/app/models/phylo.py', 'w') as f:
    f.write(content)

print("✓ Fixed phylo.py indentation")
EOF

# Run the fix
python3 temp_fix.py

# Clean up
rm temp_fix.py

echo "✓ phylo.py has been fixed"
echo "Now try running ./tdd.sh again!"