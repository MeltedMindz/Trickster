#!/usr/bin/env python3
"""
Test the agent memory system to ensure it's working correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_religion_architects.agents.zealot import Zealot
from ai_religion_architects.agents.base_agent import ProposalType, Proposal
from datetime import datetime

def test_agent_memory_save():
    """Test that agent memory saves correctly"""
    
    print("🧪 Testing Agent Memory System")
    print("=" * 40)
    
    # Create a test Zealot agent
    zealot = Zealot("logs_agent_memories")
    
    # Create a test proposal
    test_proposal = Proposal(
        type=ProposalType.BELIEF,
        content="Test belief for memory system",
        author="Zealot"
    )
    
    # Record a test debate outcome
    print("📝 Recording test debate outcome...")
    
    zealot.record_debate_outcome(
        cycle_number=99,
        proposal=test_proposal,
        role="proposer",
        response="I propose this test belief",
        outcome="accepted",
        other_participants=["Skeptic", "Trickster"],
        satisfaction=0.8
    )
    
    # Save memory
    print("💾 Saving agent memory...")
    zealot.save_memory()
    
    # Verify it was saved by checking in-memory stats
    memory_summary = zealot.agent_memory.get_memory_summary()
    stats = memory_summary['statistics']
    
    print("\n📊 Current Memory Statistics:")
    print(f"   Total Proposals: {stats['total_proposals']}")
    print(f"   Successful Proposals: {stats['successful_proposals']}")
    print(f"   Total Votes: {stats['total_votes']}")
    print(f"   Recent Debates: {len(memory_summary['recent_debates'])}")
    
    # Check if debate was recorded
    recent_debates = memory_summary['recent_debates']
    test_debate_found = any(debate['cycle_number'] == 99 for debate in recent_debates)
    
    if test_debate_found:
        print("✅ Test debate successfully recorded in memory!")
    else:
        print("❌ Test debate was not found in memory")
        
    print("\n🔍 Memory system test completed")
    return test_debate_found

if __name__ == "__main__":
    test_agent_memory_save()