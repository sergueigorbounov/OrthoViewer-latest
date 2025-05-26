#!/bin/bash
echo "🔧 Cleaning duplicate SelectChangeEvent imports..."

# Fix VisualizationPage.tsx
echo "Fixing VisualizationPage.tsx..."
# Remove all SelectChangeEvent imports first
sed -i '/import.*SelectChangeEvent.*from.*@mui\/material\/Select/d' src/components/pages/VisualizationPage.tsx

# Add one correct import after the MUI import
sed -i '/} from .*@mui\/material/a import type { SelectChangeEvent } from "@mui/material/Select";' src/components/pages/VisualizationPage.tsx

# Fix AnalysisPage.tsx  
echo "Fixing AnalysisPage.tsx..."
# Remove all SelectChangeEvent imports first
sed -i '/import.*SelectChangeEvent.*from.*@mui\/material\/Select/d' src/components/pages/AnalysisPage.tsx

# Add one correct import after the MUI import
sed -i '/} from .*@mui\/material/a import type { SelectChangeEvent } from "@mui/material/Select";' src/components/pages/AnalysisPage.tsx

echo "✅ Cleaned up duplicate imports!"
