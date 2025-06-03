#!/usr/bin/env python3
import json
from datetime import datetime

def create_readable_history():
    """Convert JSON chat history to readable markdown format."""
    
    try:
        with open('cursor_chat_history.json', 'r', encoding='utf-8') as f:
            prompts = json.load(f)
        
        with open('cursor_chat_readable.md', 'w', encoding='utf-8') as f:
            f.write("# Cursor Chat History\n\n")
            f.write(f"Total prompts: {len(prompts)}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for i, prompt in enumerate(prompts, 1):
                if isinstance(prompt, dict) and 'text' in prompt:
                    f.write(f"## Prompt {i}\n\n")
                    f.write(f"**Text:** {prompt['text']}\n\n")
                    if 'commandType' in prompt:
                        f.write(f"**Command Type:** {prompt['commandType']}\n\n")
                    f.write("---\n\n")
        
        print(f"✅ Readable history created: cursor_chat_readable.md")
        print(f"📊 Total prompts: {len(prompts)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_readable_history() 