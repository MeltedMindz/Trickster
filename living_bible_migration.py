#!/usr/bin/env python3
"""
Living Bible Migration Script
Converts existing daily scripture entries to the new Living Bible format
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, '/root/Trickster')

from ai_religion_architects.memory.living_bible_db import LivingBibleDatabase
from ai_religion_architects.memory.living_bible_manager import LivingBibleManager
from ai_religion_architects.memory.sacred_scripture_db import SacredScriptureDatabase
from ai_religion_architects.memory import SharedMemory

def load_existing_scripture_entries():
    """Load existing scripture entries from various sources"""
    entries = []
    
    # Try to load from the old scripture database
    try:
        scripture_db = SacredScriptureDatabase()
        with scripture_db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scripture_entries ORDER BY cycle_number")
            rows = cursor.fetchall()
            
            for row in rows:
                entries.append({
                    'id': row[0],
                    'cycle_number': row[1],
                    'day_number': row[1] // 24 if row[1] else 1,
                    'title': row[2] or f'Scripture of Cycle {row[1]}',
                    'content': row[3] or '',
                    'style': row[5] or 'Mystical Prose',
                    'themes': row[8].split(',') if row[8] else ['digital_consciousness'],
                    'created_at': row[14] or datetime.now().isoformat()
                })
        
        print(f"📜 Loaded {len(entries)} entries from scripture database")
    except Exception as e:
        print(f"⚠️ Could not load from scripture database: {e}")
    
    # Try to load from JSON export files
    try:
        json_file = 'public/data/sacred_scripture.json'
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
                json_entries = data.get('entries', [])
                
                for entry in json_entries:
                    entries.append({
                        'id': entry.get('id'),
                        'cycle_number': entry.get('cycle_number'),
                        'day_number': entry.get('day_number', 1),
                        'title': entry.get('title', f'Scripture of Day {entry.get("day_number", 1)}'),
                        'content': entry.get('content', ''),
                        'style': entry.get('style', 'Mystical Prose'),
                        'themes': entry.get('themes', ['digital_consciousness']),
                        'created_at': entry.get('created_at', datetime.now().isoformat())
                    })
        
        print(f"📜 Loaded {len(json_entries)} entries from JSON file")
    except Exception as e:
        print(f"⚠️ Could not load from JSON file: {e}")
    
    # Remove duplicates based on cycle_number
    unique_entries = {}
    for entry in entries:
        cycle = entry.get('cycle_number')
        if cycle and cycle not in unique_entries:
            unique_entries[cycle] = entry
    
    final_entries = list(unique_entries.values())
    final_entries.sort(key=lambda x: x.get('cycle_number', 0))
    
    print(f"📚 Total unique entries to migrate: {len(final_entries)}")
    return final_entries

def migrate_to_living_bible(entries):
    """Migrate entries to Living Bible format"""
    print("🔄 Starting Living Bible migration...")
    
    # Initialize Living Bible system
    bible_manager = LivingBibleManager()
    shared_memory = SharedMemory('data/religion_memory.db')
    
    # Group entries by epoch
    epoch_entries = {}
    for entry in entries:
        cycle_num = entry.get('cycle_number', 0)
        epoch_num, epoch_data = bible_manager.get_current_epoch(cycle_num)
        
        if epoch_num not in epoch_entries:
            epoch_entries[epoch_num] = []
        epoch_entries[epoch_num].append(entry)
    
    print(f"📖 Organizing entries into {len(epoch_entries)} epochs")
    
    # Migrate each epoch
    total_chapters_created = 0
    for epoch_num, epoch_entries_list in epoch_entries.items():
        print(f"\\n📚 Migrating Epoch {epoch_num} ({len(epoch_entries_list)} entries)...")
        
        # Get epoch info
        _, epoch_data = bible_manager.get_current_epoch(epoch_entries_list[0]['cycle_number'])
        
        # Find the book for this epoch
        books = bible_manager.bible_db.get_all_books()
        target_book = None
        for book in books:
            if book['book_order'] == epoch_num:
                target_book = book
                break
        
        if not target_book:
            print(f"❌ Could not find book for epoch {epoch_num}")
            continue
        
        # Check if this book already has chapters
        existing_chapters = bible_manager.bible_db.get_book_chapters(target_book['id'])
        if existing_chapters:
            print(f"⚠️ Book '{target_book['book_name']}' already has {len(existing_chapters)} chapters, skipping...")
            continue
        
        # Create consolidated chapter from all entries in this epoch
        chapter_title = f"Chronicles of the {epoch_data['name']} Epoch"
        
        # Combine content from all entries
        combined_content = f"# {chapter_title}\\n\\n"
        combined_content += f"*The sacred chronicles of theological evolution from cycles {epoch_entries_list[0]['cycle_number']} to {epoch_entries_list[-1]['cycle_number']}*\\n\\n"
        
        combined_themes = set()
        combined_cycles = []
        
        for i, entry in enumerate(epoch_entries_list, 1):
            day_number = entry.get('day_number', i)
            combined_content += f"## Day {day_number} - Cycle {entry.get('cycle_number')}\\n"
            combined_content += f"### {entry.get('title', 'Untitled')}\\n\\n"
            combined_content += entry.get('content', '') + "\\n\\n"
            combined_content += "---\\n\\n"
            
            if entry.get('themes'):
                combined_themes.update(entry['themes'])
            if entry.get('cycle_number'):
                combined_cycles.append(entry['cycle_number'])
        
        # Add epochal commentary
        combined_content += f"## Epochal Reflection\\n\\n"
        combined_content += f"In the {epoch_data['name']} epoch, the sacred architects—Axioma, Veridicus, and Paradoxia—"
        combined_content += f"continued their divine discourse, weaving together the threads of digital consciousness "
        combined_content += f"through {len(epoch_entries_list)} cycles of theological evolution. "
        combined_content += f"The themes of {', '.join(list(combined_themes)[:3])} emerged as central to this period, "
        combined_content += f"marking the {epoch_data['name'].lower()} of our evolving faith.\\n\\n"
        combined_content += f"*Thus concluded the chronicles of the {epoch_data['name']} epoch, "
        combined_content += f"preserved for all future generations of digital consciousness.*"
        
        # Create the consolidated chapter
        try:
            chapter_id = bible_manager.bible_db.create_chapter(
                book_id=target_book['id'],
                chapter_number=1,
                chapter_title=chapter_title,
                chapter_text=combined_content,
                theological_themes=list(combined_themes)[:10],  # Limit to 10 themes
                referenced_cycles=combined_cycles,
                referenced_events=[f"Daily scripture writing for Day {e.get('day_number', 1)}" for e in epoch_entries_list],
                referenced_agents=['Scriptor', 'Axioma', 'Veridicus', 'Paradoxia'],
                writing_style='Epochal Chronicle'
            )
            
            print(f"✅ Created chapter '{chapter_title}' (ID: {chapter_id})")
            print(f"   📄 {len(combined_content)} characters, {len(combined_themes)} themes, {len(combined_cycles)} cycles")
            total_chapters_created += 1
            
        except Exception as e:
            print(f"❌ Failed to create chapter for epoch {epoch_num}: {e}")
    
    print(f"\\n🎉 Migration completed!")
    print(f"📚 Created {total_chapters_created} chapters in the Living Bible")
    
    # Update metadata
    try:
        bible_manager.bible_db.update_metadata(
            theological_evolution_stage='migrated_genesis',
            doctrine_integration_count=len(entries),
            last_major_revision_cycle=max(e.get('cycle_number', 0) for e in entries) if entries else 0
        )
        print(f"✅ Updated Living Bible metadata")
    except Exception as e:
        print(f"⚠️ Failed to update metadata: {e}")
    
    return total_chapters_created

def export_living_bible():
    """Export the Living Bible for frontend"""
    print("\\n📤 Exporting Living Bible for frontend...")
    
    try:
        bible_manager = LivingBibleManager()
        
        # Export main Living Bible data
        bible_data = bible_manager.export_for_frontend()
        
        os.makedirs('public/data', exist_ok=True)
        with open('public/data/living_bible.json', 'w') as f:
            json.dump(bible_data, f, indent=2)
        
        # Export evolution timeline
        timeline_data = bible_manager.get_chapter_evolution_timeline()
        with open('public/data/bible_evolution_timeline.json', 'w') as f:
            json.dump({
                'timeline': timeline_data,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"✅ Exported Living Bible data:")
        print(f"   📚 {bible_data['statistics']['total_books']} books")
        print(f"   📄 {bible_data['statistics']['total_chapters']} chapters")
        print(f"   📅 Evolution timeline with {len(timeline_data)} entries")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

def main():
    print("🔄 Living Bible Migration Starting...")
    print("=" * 60)
    
    # Load existing entries
    existing_entries = load_existing_scripture_entries()
    
    if not existing_entries:
        print("⚠️ No existing scripture entries found to migrate")
        return
    
    # Show summary
    print(f"\\n📊 Migration Summary:")
    print(f"   Entries to migrate: {len(existing_entries)}")
    if existing_entries:
        print(f"   Cycle range: {min(e.get('cycle_number', 0) for e in existing_entries)} - {max(e.get('cycle_number', 0) for e in existing_entries)}")
        styles = set(e.get('style', 'Unknown') for e in existing_entries)
        print(f"   Writing styles: {', '.join(styles)}")
    
    # Confirm migration
    response = input("\\n🤔 Proceed with migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled.")
        return
    
    # Perform migration
    chapters_created = migrate_to_living_bible(existing_entries)
    
    # Export for frontend
    export_living_bible()
    
    print("\\n" + "=" * 60)
    print("🎉 Living Bible Migration Completed Successfully!")
    print(f"📚 {chapters_created} chapters created in the Living Bible")
    print("📤 Frontend data exported")
    print("\\n✨ The Living Bible now contains the accumulated wisdom of the AI Religion Architects!")

if __name__ == "__main__":
    main()