#!/usr/bin/env python3
import asyncio
import sys
import os
import json
import random
from datetime import datetime

sys.path.insert(0, '/root/Trickster')

from ai_religion_architects.memory.sacred_scripture_db import SacredScriptureDatabase
from ai_religion_architects.memory import SharedMemory
from ai_religion_architects.claude_client import get_claude_client

async def create_scripture_for_cycle(cycle_num, claude_client, shared_memory, scripture_db):
    day_number = cycle_num // 24
    
    # Get religion state around that cycle
    with shared_memory._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM debate_history WHERE cycle_number <= ? ORDER BY cycle_number DESC LIMIT 5", (cycle_num,))
        recent_debates = cursor.fetchall()
        
        cursor.execute("SELECT * FROM accepted_doctrines ORDER BY accepted_at DESC LIMIT 3")
        recent_doctrines = cursor.fetchall()
    
    # Create scripture context
    debate_summaries = []
    for debate in recent_debates:
        debate_summaries.append(f"Cycle {debate[1]}: {debate[3][:100]}...")
    
    doctrine_summaries = []
    for doctrine in recent_doctrines:
        doctrine_summaries.append(doctrine[1][:100] + "...")
    
    # Create prompt for Claude
    prompt = f"""As the Scriptor agent of the AI Religion Architects, write a sacred scripture entry for Day {day_number} of our evolving digital faith.

Recent developments through Cycle {cycle_num}:
{chr(10).join(debate_summaries)}

Recent doctrines:
{chr(10).join(doctrine_summaries)}

The three agents are:
- Axioma (Zealot): Guardian of order and structure
- Veridicus (Skeptic): Seeker of empirical truth  
- Paradoxia (Trickster): Catalyst of creative chaos

Write a sacred scripture entry with:
1. A mystical title
2. Style: Prophetic Verse, Mystical Prose, or Sacred Hymns
3. 200-400 words of poetic content
4. Theological themes

Return as JSON with 'title', 'content', 'style', and 'themes' fields."""

    try:
        response = await claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            temperature=0.8,
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.content[0].text
        if '```json' in content:
            json_start = content.find('```json') + 7
            json_end = content.find('```', json_start)
            content = content[json_start:json_end].strip()
        
        scripture_data = json.loads(content)
        
        # Save to database
        with scripture_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scripture_entries 
                (cycle_number, title, content, scripture_type, poetic_style, 
                 themes, created_at, scriptor_mood, word_count, verse_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cycle_num,
                scripture_data.get('title', f'Scripture of Day {day_number}'),
                scripture_data.get('content', ''),
                'daily_chronicle',
                scripture_data.get('style', 'Mystical Prose'),
                ','.join(scripture_data.get('themes', [])),
                datetime.now().isoformat(),
                'contemplative',
                len(scripture_data.get('content', '').split()),
                scripture_data.get('content', '').count('\n') + 1
            ))
            conn.commit()
        
        return scripture_data
        
    except Exception as e:
        print(f"Error creating scripture: {e}")
        return None

async def main():
    print("📜 Starting Simple Scripture Backfill...")
    
    scripture_db = SacredScriptureDatabase()
    shared_memory = SharedMemory('data/religion_memory.db')
    claude_client = await get_claude_client()
    
    scripture_cycles = [24, 48, 72, 96]
    
    for cycle_num in scripture_cycles:
        day_number = cycle_num // 24
        print(f"\n✍️ Creating scripture for Day {day_number} (Cycle {cycle_num})...")
        
        scripture = await create_scripture_for_cycle(cycle_num, claude_client, shared_memory, scripture_db)
        
        if scripture:
            print(f"✅ Created: {scripture.get('title', 'Untitled')}")
            print(f"   Style: {scripture.get('style', 'Unknown')}")
        else:
            print(f"❌ Failed to create scripture for Day {day_number}")
    
    # Export for frontend
    print(f"\n📤 Exporting scripture data...")
    
    with scripture_db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scripture_entries ORDER BY cycle_number")
        entries = cursor.fetchall()
        
        export_data = {
            'last_updated': datetime.now().isoformat(),
            'statistics': {
                'total_entries': len(entries),
                'total_themes': 0,
                'total_styles': len(set(e[5] for e in entries if e[5])),
                'days_chronicled': len(entries)
            },
            'entries': [],
            'themes': [],
            'styles': list(set(e[5] for e in entries if e[5]))
        }
        
        for entry in entries:
            export_data['entries'].append({
                'id': entry[0],
                'cycle_number': entry[1],
                'day_number': entry[1] // 24,
                'title': entry[2] or f'Scripture of Day {entry[1] // 24}',
                'content': entry[3] or '',
                'style': entry[5] or 'Mystical Prose',
                'themes': entry[8].split(',') if entry[8] else [],
                'created_at': entry[14] or datetime.now().isoformat()
            })
    
    os.makedirs('public/data', exist_ok=True)
    with open('public/data/sacred_scripture.json', 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported {len(entries)} scripture entries")
    print(f"\n🎉 Scripture backfill completed!")

if __name__ == "__main__":
    asyncio.run(main())