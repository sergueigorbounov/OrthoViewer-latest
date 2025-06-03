#!/usr/bin/env python3
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import os

def extract_chat_history():
    """Extract chat history from Cursor workspace storage."""
    
    # Path to your current workspace
    workspace_path = Path.home() / ".config/Cursor/User/workspaceStorage/f694ae7dac0fd0e0f9aee715b5d76f48/state.vscdb"
    
    if not workspace_path.exists():
        print(f"❌ Database not found at: {workspace_path}")
        return
    
    print(f"📂 Reading from: {workspace_path}")
    
    try:
        conn = sqlite3.connect(str(workspace_path))
        cursor = conn.cursor()
        
        # Query for chat-related data
        cursor.execute("""
            SELECT key, value 
            FROM ItemTable 
            WHERE key IN ('aiService.prompts', 'composer.composerData') 
               OR key LIKE '%chat%' 
               OR key LIKE '%composer%'
        """)
        
        results = cursor.fetchall()
        
        print(f"\n🔍 Found {len(results)} chat-related entries:")
        print("=" * 60)
        
        for key, value in results:
            print(f"\n📋 Key: {key}")
            print("-" * 40)
            
            if key == 'aiService.prompts':
                try:
                    prompts = json.loads(value)
                    print(f"💬 Found {len(prompts)} prompts:")
                    
                    for i, prompt in enumerate(prompts[-10:], 1):  # Show last 10
                        if isinstance(prompt, dict) and 'text' in prompt:
                            text = prompt['text'][:200] + "..." if len(prompt['text']) > 200 else prompt['text']
                            print(f"  {i}. {text}")
                        
                except json.JSONDecodeError:
                    print(f"  📝 Raw data (first 200 chars): {value[:200]}...")
            
            elif key == 'composer.composerData':
                try:
                    composer_data = json.loads(value)
                    print(f"🎼 Composer data: {json.dumps(composer_data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"  📝 Raw data: {value}")
            
            else:
                if len(value) > 200:
                    print(f"  📄 Data length: {len(value)} characters")
                    print(f"  📝 Preview: {value[:200]}...")
                else:
                    print(f"  📝 Data: {value}")
        
        # Save full prompts to file
        cursor.execute("SELECT value FROM ItemTable WHERE key = 'aiService.prompts'")
        prompts_data = cursor.fetchone()
        
        if prompts_data:
            with open('cursor_chat_history.json', 'w', encoding='utf-8') as f:
                json.dump(json.loads(prompts_data[0]), f, indent=2, ensure_ascii=False)
            print(f"\n💾 Full chat history saved to: cursor_chat_history.json")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    extract_chat_history() 