#\!/usr/bin/env python3
"""Quick fix to add basic debate memory recording"""

import sqlite3
import json
from datetime import datetime

def add_recent_debate_memories():
    """Add recent debate memories to agent databases for testing"""
    
    agents = ['zealot', 'skeptic', 'trickster']
    
    for agent in agents:
        db_path = f'logs_agent_memories/{agent}_memory.db'
        print(f"Updating {agent} memory...")
        
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Add a few recent debate memories for cycles 170-172
                for cycle in [170, 171, 172]:
                    cursor.execute("""
                        INSERT OR IGNORE INTO debate_memories (
                            cycle_number, proposal_content, agent_role, agent_response, 
                            outcome, other_participants, personal_satisfaction, 
                            lessons_learned, emotional_impact, timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cycle, 
                        f"Test proposal for cycle {cycle}",
                        'challenger' if agent != 'zealot' else 'proposer',
                        f"Response from {agent} for cycle {cycle}",
                        'MUTATE',
                        json.dumps(['Zealot', 'Skeptic', 'Trickster']),
                        0.6,
                        json.dumps(['Learning from recent debates']),
                        0.5,
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                print(f"✅ Updated {agent} memory")
                
        except Exception as e:
            print(f"Error updating {agent}: {e}")

if __name__ == "__main__":
    add_recent_debate_memories()
