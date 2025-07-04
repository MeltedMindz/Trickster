#!/usr/bin/env python3
"""
Rebuild agent memories from shared memory database.
This script will reconstruct the missing debate memories and statistics
for all agents based on the complete debate history in shared memory.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import os

def get_debates_from_shared_memory():
    """Get all debates from shared memory database"""
    shared_db_path = "data/religion_memory.db"
    
    if not os.path.exists(shared_db_path):
        print(f"❌ Shared memory database not found at {shared_db_path}")
        return []
    
    with sqlite3.connect(shared_db_path) as conn:
        cursor = conn.cursor()
        
        # Get all debates with full details
        cursor.execute("""
            SELECT cycle_number, proposal_content, proposal_type, proposer, final_outcome, 
                   challenger_response, trickster_response, vote_result
            FROM debate_history 
            ORDER BY cycle_number
        """)
        
        debates = cursor.fetchall()
        print(f"📊 Found {len(debates)} debates in shared memory")
        return debates

def rebuild_agent_memory(agent_name, agent_type, debates):
    """Rebuild memory for a specific agent"""
    agent_db_path = f"logs_agent_memories/{agent_name.lower()}_memory.db"
    
    print(f"\n🔧 Rebuilding memory for {agent_name} ({agent_type})")
    
    # Initialize counters
    total_proposals = 0
    successful_proposals = 0
    total_challenges = 0
    successful_challenges = 0
    total_votes = 0
    
    # Process each debate
    debate_memories = []
    
    for debate in debates:
        cycle_number, proposal_content, proposal_type, proposed_by, outcome, challenge_response, trickster_response, vote_result = debate
        
        # Determine agent's role in this debate
        agent_role = "voter"  # default
        agent_response = f"Voted {vote_result or 'delay'}"
        
        if proposed_by == agent_name:
            agent_role = "proposer"
            agent_response = proposal_content
            total_proposals += 1
            if outcome == "accept":
                successful_proposals += 1
                
        elif agent_name == "Skeptic":  # Skeptic is typically the challenger
            agent_role = "challenger"  
            agent_response = challenge_response or "Challenged proposal"
            total_challenges += 1
            if outcome == "reject":
                successful_challenges += 1
                
        elif agent_name == "Trickster" and trickster_response:
            agent_role = "chaos_agent"
            agent_response = trickster_response
        
        # Count votes (every agent votes)
        total_votes += 1
        
        # Calculate satisfaction (simplified based on outcome)
        satisfaction = 0.5  # default neutral
        if agent_role == "proposer" and outcome == "accept":
            satisfaction = 0.8
        elif agent_role == "challenger" and outcome == "reject":
            satisfaction = 0.8
        elif outcome in ["DELAY", "MUTATE"]:
            satisfaction = 0.3
        
        # Determine other participants
        other_participants = []
        for participant in ["Zealot", "Skeptic", "Trickster"]:
            if participant != agent_name:
                other_participants.append(participant)
        
        # Create debate memory
        debate_memory = {
            'cycle_number': cycle_number,
            'proposal_content': proposal_content,
            'agent_role': agent_role,
            'agent_response': agent_response,
            'outcome': outcome,
            'other_participants': other_participants,
            'personal_satisfaction': satisfaction,
            'lessons_learned': [],  # Will be populated based on outcome
            'emotional_impact': 0.5,  # Default neutral
            'timestamp': datetime.now().isoformat()  # Approximate timestamp
        }
        
        # Add lessons based on outcome and role
        if agent_role == "proposer" and outcome == "accept":
            debate_memory['lessons_learned'] = ["Proposal style was effective"]
        elif agent_role == "challenger" and outcome == "reject":
            debate_memory['lessons_learned'] = ["Challenge was persuasive"]
        elif satisfaction < 0.3:
            debate_memory['lessons_learned'] = ["Strategy needs adjustment"]
        
        debate_memories.append(debate_memory)
    
    # Save to agent database
    with sqlite3.connect(agent_db_path) as conn:
        cursor = conn.cursor()
        
        # Clear existing debate memories
        cursor.execute("DELETE FROM debate_memories")
        
        # Insert all debate memories (keep only last 10)
        recent_debates = debate_memories[-10:] if len(debate_memories) > 10 else debate_memories
        
        for debate in recent_debates:
            cursor.execute("""
                INSERT INTO debate_memories (cycle_number, proposal_content, agent_role, agent_response, outcome, other_participants, personal_satisfaction, lessons_learned, emotional_impact, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                debate['cycle_number'],
                debate['proposal_content'], 
                debate['agent_role'],
                debate['agent_response'],
                debate['outcome'],
                json.dumps(debate['other_participants']),
                debate['personal_satisfaction'],
                json.dumps(debate['lessons_learned']),
                debate['emotional_impact'],
                debate['timestamp']
            ))
        
        # Update statistics
        cursor.execute("DELETE FROM agent_stats")
        cursor.execute("""
            INSERT INTO agent_stats (id, total_proposals, successful_proposals, total_challenges, successful_challenges, total_votes, evolution_points, last_updated)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        """, (total_proposals, successful_proposals, total_challenges, successful_challenges, total_votes, 0, datetime.now().isoformat()))
        
        conn.commit()
    
    print(f"✅ {agent_name} memory rebuilt:")
    print(f"   📝 Proposals: {total_proposals} (success rate: {successful_proposals/max(total_proposals,1)*100:.1f}%)")
    print(f"   🔍 Challenges: {total_challenges} (success rate: {successful_challenges/max(total_challenges,1)*100:.1f}%)")
    print(f"   🗳️  Total votes: {total_votes}")
    print(f"   💾 Recent debates stored: {len(recent_debates)}")

def main():
    """Main rebuild process"""
    print("🔄 Rebuilding Agent Memories from Shared Database")
    print("=" * 50)
    
    # Create agent memories directory if it doesn't exist
    os.makedirs("logs_agent_memories", exist_ok=True)
    
    # Get all debates from shared memory
    debates = get_debates_from_shared_memory()
    
    if not debates:
        print("❌ No debates found in shared memory")
        return
    
    # Rebuild each agent's memory
    agents = [
        ("Zealot", "zealot"),
        ("Skeptic", "skeptic"), 
        ("Trickster", "trickster")
    ]
    
    for agent_name, agent_type in agents:
        rebuild_agent_memory(agent_name, agent_type, debates)
    
    print(f"\n🎉 Memory rebuild complete! All agents now have accurate debate statistics.")
    print("💡 The system should now show correct debate counts and participation rates.")

if __name__ == "__main__":
    main()