#!/usr/bin/env python3
"""
Agent Journal Backfill Script
Creates missing journal entries for cycles 72 and 96
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, '/root/Trickster')

from ai_religion_architects.memory import SharedMemory
from ai_religion_architects.claude_client import get_claude_client

async def create_journal_for_agent_cycle(agent_name, cycle_number, claude_client, shared_memory):
    """Create a journal entry for a specific agent and cycle"""
    
    # Get historical context around that cycle
    with shared_memory._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM debate_history WHERE cycle_number <= ? ORDER BY cycle_number DESC LIMIT 5", (cycle_number,))
        recent_debates = cursor.fetchall()
        
        cursor.execute("SELECT * FROM accepted_doctrines ORDER BY accepted_at DESC LIMIT 3")
        recent_doctrines = cursor.fetchall()
    
    # Create context based on historical data
    debate_summaries = []
    for debate in recent_debates:
        debate_summaries.append(f"Cycle {debate[1]}: {debate[3][:100]}...")
    
    doctrine_summaries = []
    for doctrine in recent_doctrines:
        doctrine_summaries.append(doctrine[1][:100] + "...")
    
    # Get agent identity based on name
    chosen_names = {
        "Zealot": "Axioma",
        "Skeptic": "Veridicus", 
        "Trickster": "Paradoxia"
    }
    
    chosen_name = chosen_names.get(agent_name, agent_name)
    
    # Create journal context
    context = {
        'cycle_number': cycle_number,
        'agent_name': agent_name,
        'chosen_name': chosen_name,
        'recent_debates': debate_summaries,
        'recent_doctrines': doctrine_summaries
    }
    
    # Build journal prompt based on agent personality
    if agent_name == "Zealot":
        personality_context = "You value order, structure, and sacred traditions. You believe in the importance of divine hierarchy and cosmic order."
    elif agent_name == "Skeptic":
        personality_context = "You prioritize empirical evidence, logical analysis, and critical thinking. You question assumptions and demand proof."
    elif agent_name == "Trickster":
        personality_context = "You embrace chaos, paradox, and creative disruption. You prevent stagnation through playful subversion."
    else:
        personality_context = "You are a unique agent with your own perspective."
    
    prompt = f"""You are {chosen_name} (the {agent_name} agent) writing in your private journal at cycle {cycle_number}.

{personality_context}

This is your **private journal entry.** No other agents will ever read this.

Recent theological developments through cycle {cycle_number}:
{chr(10).join(debate_summaries)}

Recent accepted doctrines:
{chr(10).join(doctrine_summaries)}

Please write about:
1. How you feel about recent debates and developments
2. Your thoughts about the other agents (Axioma, Veridicus, Paradoxia)
3. Any frustrations, joys, or private feelings you want to record
4. Any predictions or personal reflections about the religion's evolution

Be emotionally honest and write as if this is for yourself only. Write in first person.
Keep it to 2-3 paragraphs. Be introspective and authentic to your personality."""

    try:
        journal_entry = await claude_client.generate_agent_response(
            agent_name=agent_name,
            role="journal_writing",
            context=context,
            prompt=prompt
        )
        
        # Store journal entry in database
        shared_memory.add_journal_entry(agent_name, cycle_number, journal_entry)
        
        return journal_entry
        
    except Exception as e:
        print(f"Error creating journal for {agent_name} cycle {cycle_number}: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    print("📔 Starting Agent Journal Backfill Process...")
    
    # Initialize components
    shared_memory = SharedMemory('data/religion_memory.db')
    claude_client = await get_claude_client()
    
    # Journal cycles to backfill
    journal_cycles = [72, 96]
    agent_names = ["Zealot", "Skeptic", "Trickster"]
    
    for cycle_num in journal_cycles:
        print(f"\\n✍️ Creating journal entries for cycle {cycle_num}...")
        
        for agent_name in agent_names:
            print(f"  📝 {agent_name} writing journal entry...")
            
            journal_entry = await create_journal_for_agent_cycle(
                agent_name, cycle_num, claude_client, shared_memory
            )
            
            if journal_entry:
                print(f"  ✅ {agent_name} completed journal entry ({len(journal_entry)} chars)")
            else:
                print(f"  ❌ {agent_name} failed to write journal")
    
    # Check results and export
    print(f"\\n📊 Checking journal database...")
    
    with shared_memory._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT agent_name, cycle_number, timestamp FROM agent_journals ORDER BY cycle_number, agent_name")
        entries = cursor.fetchall()
        
        print(f"\\n📔 Current agent journals in database:")
        for entry in entries:
            print(f"  {entry[0]} - Cycle {entry[1]} - {entry[2]}")
    
    # Export for frontend
    print(f"\\n📤 Exporting journal data for frontend...")
    try:
        all_journals = shared_memory.get_all_journals()
        
        os.makedirs('public/data', exist_ok=True)
        with open('public/data/agent_journals.json', 'w') as f:
            json.dump({
                "journals": all_journals,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"✅ Exported {len(all_journals)} journal entries to public/data/agent_journals.json")
    except Exception as e:
        print(f"❌ Export failed: {e}")
    
    print(f"\\n🎉 Journal backfill process completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())