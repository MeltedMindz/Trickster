#\!/usr/bin/env python3
"""
Scripture Backfill Script
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
            # Create context for this historical cycle
            context = {
                'cycle_number': cycle_num,
                'day_number': day_number,
                'shared_memory': shared_memory,
                'scripture_db': scripture_db,
                'is_backfill': True
            }
            
            # Generate scripture entry
            scripture_entry = await scriptor.write_daily_scripture(context, claude_client)
            
            if scripture_entry:
                print(f"✅ Created scripture for Day {day_number}: {scripture_entry.get('title', 'Untitled')}")
                print(f"   Themes: {', '.join(scripture_entry.get('themes', [])[:3])}")
                print(f"   Style: {scripture_entry.get('style', 'Unknown')}")
            else:
                print(f"❌ Failed to create scripture for Day {day_number}")
                
        except Exception as e:
            print(f"❌ Error creating scripture for Day {day_number}: {e}")
    
    print(f"\n📊 Backfill complete\! Checking scripture database...")
    
    # Check results
    with scripture_db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT day_number, title, style FROM scripture_entries ORDER BY day_number")
        entries = cursor.fetchall()
        
        print(f"\n📚 Scripture Entries Created:")
        for entry in entries:
            print(f"   Day {entry[0]}: {entry[1]} ({entry[2]})")
    
    print(f"\n🎉 Scripture backfill process completed successfully\!")

if __name__ == "__main__":
    asyncio.run(main())
