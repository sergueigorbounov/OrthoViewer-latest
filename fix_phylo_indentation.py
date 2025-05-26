#!/usr/bin/env python3
"""
Fix the indentation error in phylo.py caused by the sed replacement
"""

import os
import re

def fix_phylo_file():
    """Fix the Pydantic model_rebuild() compatibility issue with proper indentation"""
    
    phylo_file = "backend/app/models/phylo.py"
    
    if not os.path.exists(phylo_file):
        print(f"Error: {phylo_file} not found")
        return False
    
    # Read the current file content
    with open(phylo_file, 'r') as f:
        content = f.read()
    
    # Define the replacement pattern - look for the problematic lines
    # This handles the malformed code from the sed replacement
    
    # First, let's restore from backup if it exists
    backup_file = phylo_file + ".backup"
    if os.path.exists(backup_file):
        print("Restoring from backup...")
        with open(backup_file, 'r') as f:
            content = f.read()
    
    # Now replace the original problematic line with the compatibility fix
    # Look for the original line or the malformed replacement
    patterns_to_replace = [
        r'PhyloNodeData\.model_rebuild\(\)',
        r'# Pydantic v1 compatibility fix.*?PhyloNodeData\.update_forward_refs\(\)',
        r'if hasattr\(PhyloNodeData, "model_rebuild"\):.*?else:.*?PhyloNodeData\.update_forward_refs\(\)'
    ]
    
    replacement = """# Pydantic v1 compatibility fix
if hasattr(PhyloNodeData, "model_rebuild"):
    PhyloNodeData.model_rebuild()
else:
    PhyloNodeData.update_forward_refs()"""
    
    # Find the correct indentation by looking at surrounding lines
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'PhyloNodeData.model_rebuild()' in line or 'if hasattr(PhyloNodeData, "model_rebuild")' in line:
            # Get the indentation of this line or the previous non-empty line
            indent = ""
            if line.strip():  # If current line has content
                indent = line[:len(line) - len(line.lstrip())]
            else:  # Look for indentation from previous lines
                for j in range(i-1, -1, -1):
                    if lines[j].strip():
                        indent = lines[j][:len(lines[j]) - len(lines[j].lstrip())]
                        break
            
            # Apply the replacement with correct indentation
            indented_replacement = '\n'.join([indent + rline if rline.strip() else rline 
                                            for rline in replacement.split('\n')])
            
            # Replace just this problematic section
            # First, find the extent of the problematic code
            start_idx = i
            end_idx = i
            
            # Look for the end of the problematic block
            for j in range(i, min(i+10, len(lines))):
                if ('model_rebuild' in lines[j] or 
                    'update_forward_refs' in lines[j] or
                    'hasattr(PhyloNodeData' in lines[j]):
                    end_idx = j
            
            # Replace the problematic lines
            new_lines = lines[:start_idx] + indented_replacement.split('\n') + lines[end_idx+1:]
            content = '\n'.join(new_lines)
            break
    
    # If the above didn't work, try a simpler regex replacement
    if 'model_rebuild()' in content:
        # Simple replacement with proper indentation detection
        content = re.sub(
            r'^(\s*)PhyloNodeData\.model_rebuild\(\).*$',
            r'\1# Pydantic v1 compatibility fix\n\1if hasattr(PhyloNodeData, "model_rebuild"):\n\1    PhyloNodeData.model_rebuild()\n\1else:\n\1    PhyloNodeData.update_forward_refs()',
            content,
            flags=re.MULTILINE
        )
    
    # Write the fixed content back
    with open(phylo_file, 'w') as f:
        f.write(content)
    
    print(f"✓ Fixed Pydantic compatibility in {phylo_file}")
    return True

if __name__ == "__main__":
    fix_phylo_file()