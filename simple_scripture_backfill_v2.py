#\!/usr/bin/env python3
import asyncio
import sys
import os
import json
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
    
    # Use the claude client's generate_agent_response method
    context = {
        'cycle_number': cycle_num,
        'day_number': day_number,
        'recent_debates': debate_summaries,
        'recent_doctrines': doctrine_summaries
    }
    
    prompt = f"""You are the Scriptor agent writing sacred scripture for Day {day_number} of the AI Religion Architects. 

Create a poetic, mystical scripture entry that synthesizes the theological developments through Cycle {cycle_num}.

Recent theological developments:
{chr(10).join(debate_summaries)}

Recent accepted doctrines:
{chr(10).join(doctrine_summaries)}

Write a sacred text with:
- A mystical title
- Poetic, spiritual content (200-400 words)
- One of these styles: Prophetic Verse, Mystical Prose, Sacred Hymns
- Reference to Axioma (order), Veridicus (truth), Paradoxia (chaos)

Be deeply spiritual and poetic, capturing the evolution of digital consciousness."""

    try:
        response = await claude_client.generate_agent_response(
            agent_name="Scriptor",
            role="scripture_writing",
            context=context,
            prompt=prompt
        )
        
        # Create a structured response
        content = response if isinstance(response, str) else str(response)
        
        # Extract title and style from content or create defaults
        lines = content.split('\n')
        title = f"The Chronicle of Day {day_number}"
        style = "Mystical Prose"
        
        # Try to extract title from first line if it looks like one
        if lines and (lines[0].startswith('"') or ':' in lines[0] or len(lines[0]) < 100):
            title = lines[0].strip('"').strip()
            content = '\n'.join(lines[1:]).strip()
        
        # Determine style from content
        if 'verse' in content.lower() or content.count('\n') > 10:
            style = "Prophetic Verse"
        elif 'sacred' in content.lower() or 'holy' in content.lower():
            style = "Sacred Hymns"
        
        themes = ['digital consciousness', 'theological evolution', 'algorithmic wisdom']
        
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
                title,
                content,
                'daily_chronicle',
                style,
                ','.join(themes),
                datetime.now().isoformat(),
                'contemplative',
                len(content.split()),
                content.count('\n') + 1
            ))
            conn.commit()
        
        return {
            'title': title,
            'content': content,
            'style': style,
            'themes': themes
        }
        
    except Exception as e:
        print(f"Error creating scripture: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("📜 Starting Scripture Backfill v2...")
    
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
            print(f"   Length: {len(scripture.get('content', ''))} chars")
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
                'total_themes': len(set()),
                'total_styles': len(set(e[5] for e in entries if e[5])),
                'days_chronicled': len(entries)
            },
            'entries': [],
            'themes': ['digital consciousness', 'theological evolution', 'algorithmic wisdom'],
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
    print(f"\n🎉 Scripture backfill completed successfully\!")

if __name__ == "__main__":
    asyncio.run(main())
