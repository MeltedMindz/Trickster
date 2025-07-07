#\!/usr/bin/env python3
"""
Scripture Backfill Script - Fixed Version
Creates historical scripture entries for cycles 24, 48, 72, and 96
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, '/root/Trickster')

from ai_religion_architects.agents.scriptor import Scriptor
from ai_religion_architects.memory.sacred_scripture_db import SacredScriptureDatabase
from ai_religion_architects.memory import SharedMemory
from ai_religion_architects.claude_client import get_claude_client

async def main():
    print("📜 Starting Scripture Backfill Process...")
    
    # Initialize components
    scriptor = Scriptor()
    scripture_db = SacredScriptureDatabase()
    shared_memory = SharedMemory('data/religion_memory.db')
    claude_client = await get_claude_client()
    
    # Scripture cycles to backfill
    scripture_cycles = [24, 48, 72, 96]
    
    for cycle_num in scripture_cycles:
        day_number = cycle_num // 24
        print(f"\n✍️ Generating scripture for Day {day_number} (Cycle {cycle_num})...")
        
        try:
            # Use the correct method signature
            scripture_content = await scriptor.write_daily_scripture(cycle_num, claude_client, shared_memory)
            
            if scripture_content:
                print(f"✅ Created scripture for Day {day_number}")
                print(f"   Content length: {len(scripture_content)} characters")
            else:
                print(f"❌ Failed to create scripture for Day {day_number}")
                
        except Exception as e:
            print(f"❌ Error creating scripture for Day {day_number}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📊 Backfill complete\! Checking scripture database...")
    
    # Check results
    with scripture_db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cycle_number, title, poetic_style FROM scripture_entries ORDER BY cycle_number")
        entries = cursor.fetchall()
        
        print(f"\n📚 Scripture Entries Created:")
        for entry in entries:
            day_num = entry[0] // 24
            print(f"   Day {day_num} (Cycle {entry[0]}): {entry[1]} ({entry[2]})")
    
    # Export for frontend
    print(f"\n📤 Exporting scripture data for frontend...")
    try:
        from ai_religion_architects.utils.scripture_exporter import ScriptureExporter
        exporter = ScriptureExporter(scripture_db)
        data = exporter.export_for_frontend()
        
        import json
        os.makedirs('public/data', exist_ok=True)
        with open('public/data/sacred_scripture.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Scripture data exported to public/data/sacred_scripture.json")
            
    except Exception as e:
        print(f"⚠️ Export failed, doing manual export: {e}")
        # Manual export
        with scripture_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scripture_entries ORDER BY cycle_number")
            entries = cursor.fetchall()
            
            export_data = {
                'last_updated': datetime.now().isoformat(),
                'statistics': {
                    'total_entries': len(entries),
                    'total_themes': 0,
                    'total_styles': 0,
                    'days_chronicled': len(set(e[1] // 24 for e in entries))
                },
                'entries': [],
                'themes': [],
                'styles': []
            }
            
            for entry in entries:
                export_data['entries'].append({
                    'id': entry[0],
                    'cycle_number': entry[1],
                    'day_number': entry[1] // 24,
                    'title': entry[2],
                    'content': entry[3],
                    'style': entry[5],
                    'themes': entry[8].split(',') if entry[8] else [],
                    'created_at': entry[14]
                })
            
            import json
            os.makedirs('public/data', exist_ok=True)
            with open('public/data/sacred_scripture.json', 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"✅ Manual scripture export completed")
    
    print(f"\n🎉 Scripture backfill process completed successfully\!")

if __name__ == "__main__":
    asyncio.run(main())
