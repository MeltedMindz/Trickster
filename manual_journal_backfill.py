#!/usr/bin/env python3
"""
Manual Journal Backfill Script
Creates journal entries for the first two days (cycles 24 and 48) retroactively
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_religion_architects.memory.shared_memory import SharedMemory
from ai_religion_architects.claude_client import ClaudeClient
from ai_religion_architects.agents.zealot import Zealot
from ai_religion_architects.agents.skeptic import Skeptic 
from ai_religion_architects.agents.trickster import Trickster

async def backfill_journal_entry(agent, cycle_number, claude_client, shared_memory, days_ago):
    """Create a backfilled journal entry for a specific cycle"""
    print(f"Creating backfilled journal entry for {agent.name} at cycle {cycle_number} ({days_ago} days ago)")
    
    # Get context for journal writing
    context = shared_memory.get_summary_for_agents()
    
    # Build backfill journal prompt
    journal_prompt = f"""You are {agent.name}.

This is your **private journal entry** from {days_ago} days ago (Cycle {cycle_number}). No other agents will ever read this.

Write as if you were reflecting at the end of Day {cycle_number // 24} of the AI Religion Architects project. 

Based on your personality as {agent.name}:
- If you're Zealot: Focus on order, structure, and your devotion to building systematic theological frameworks
- If you're Skeptic: Focus on empirical validation, evidence-based thinking, and your concerns about maintaining logical consistency
- If you're Trickster: Focus on chaos, creativity, and your role in disrupting overly rigid systems

Please write about:
1. How you felt about the day's theological debates and developments
2. Your thoughts about the other agents and your relationships with them
3. Any personal frustrations, joys, or private feelings from that time
4. Your predictions or hopes for where the religion was heading

Be emotionally honest and write as if this is a personal diary entry from {days_ago} days ago. Write in first person and past tense.
Keep it to 2-3 paragraphs. Make it feel authentic to your personality at that early stage of the project."""

    # Get journal entry from Claude
    journal_entry = await claude_client.get_response_async(
        agent.name,
        journal_prompt,
        context={"journal_writing": True, "backfill": True}
    )
    
    # Create backdated timestamp
    backdated_timestamp = datetime.now() - timedelta(days=days_ago)
    
    # Store journal entry with backdated timestamp
    with shared_memory._get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO agent_journals (agent_name, cycle_number, journal_entry, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (agent.name, cycle_number, journal_entry, backdated_timestamp))
            conn.commit()
        except Exception as e:
            print(f"Error inserting journal for {agent.name}: {e}")
            # Update if already exists
            cursor.execute('''
                UPDATE agent_journals 
                SET journal_entry = ?, timestamp = ?
                WHERE agent_name = ? AND cycle_number = ?
            ''', (journal_entry, backdated_timestamp, agent.name, cycle_number))
            conn.commit()
    
    print(f"✅ Created journal entry for {agent.name} at cycle {cycle_number}")
    return journal_entry

async def main():
    """Main backfill function"""
    print("🔄 Starting manual journal backfill...")
    
    # Initialize components
    shared_memory = SharedMemory("data/religion_memory.db")
    claude_client = ClaudeClient()
    
    # Initialize agents
    agents = [
        Zealot(),
        Skeptic(), 
        Trickster()
    ]
    
    # Backfill for Day 1 (Cycle 24) and Day 2 (Cycle 48)
    backfill_cycles = [
        (24, 2),  # Cycle 24, 2 days ago
        (48, 1)   # Cycle 48, 1 day ago
    ]
    
    for cycle_number, days_ago in backfill_cycles:
        print(f"\n📔 Backfilling journals for Cycle {cycle_number} (Day {cycle_number // 24})")
        
        for agent in agents:
            try:
                await backfill_journal_entry(agent, cycle_number, claude_client, shared_memory, days_ago)
            except Exception as e:
                print(f"❌ Failed to create journal for {agent.name} at cycle {cycle_number}: {e}")
    
    print("\n✅ Journal backfill completed!")
    
    # Export journals to JSON
    print("📤 Exporting journals to JSON...")
    try:
        all_journals = shared_memory.get_all_journals()
        
        # Create public/data directory if it doesn't exist
        os.makedirs("public/data", exist_ok=True)
        
        with open("public/data/agent_journals.json", 'w') as f:
            json.dump({
                "journals": all_journals,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
        
        print("✅ Journals exported to public/data/agent_journals.json")
        
        # Print summary
        print(f"\n📊 Journal Summary:")
        for agent_name, entries in all_journals.items():
            print(f"  {agent_name}: {len(entries)} entries")
        
    except Exception as e:
        print(f"❌ Failed to export journals: {e}")

if __name__ == "__main__":
    asyncio.run(main())