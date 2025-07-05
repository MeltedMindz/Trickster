#!/usr/bin/env python3
"""
Manual Journal Writing for Cycle 72
Triggers the journal writing that failed due to the bug
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_religion_architects.memory.shared_memory import SharedMemory
from ai_religion_architects.agents.zealot import Zealot
from ai_religion_architects.agents.skeptic import Skeptic
from ai_religion_architects.agents.trickster import Trickster
from ai_religion_architects.claude_client import get_claude_client

async def write_cycle_72_journals():
    """Write the missing cycle 72 journal entries"""
    print("🔄 Writing missing Cycle 72 journal entries...")
    
    # Initialize components
    shared_memory = SharedMemory("data/religion_memory.db")
    claude_client = get_claude_client()
    
    # Create agent instances
    agents = {
        "Zealot": Zealot(),
        "Skeptic": Skeptic(), 
        "Trickster": Trickster()
    }
    
    cycle_number = 72
    
    for agent_name, agent in agents.items():
        try:
            print(f"📝 {agent_name} writing journal entry for cycle {cycle_number}...")
            
            # Write journal entry
            journal_entry = await agent.write_journal_entry(
                cycle_number,
                claude_client,
                shared_memory
            )
            
            print(f"✅ {agent_name} completed journal entry")
            print(f"Preview: {journal_entry[:100]}...")
            print()
            
        except Exception as e:
            print(f"❌ {agent_name} failed to write journal: {e}")
    
    print("✅ Cycle 72 journal writing completed!")
    
    # Export journals to JSON
    print("📤 Exporting journals to JSON...")
    try:
        all_journals = shared_memory.get_all_journals()
        
        # Create public/data directory if it doesn't exist
        os.makedirs("public/data", exist_ok=True)
        
        import json
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
    asyncio.run(write_cycle_72_journals())