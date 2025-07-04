#!/usr/bin/env python3
"""
Update the agent_memories.json export with the corrected data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_religion_architects.utils.memory_exporter import AgentMemoryExporter

def update_json_export():
    """Update the JSON export files with corrected agent data"""
    
    print("🔄 Updating JSON exports with corrected agent data")
    print("=" * 50)
    
    # Initialize memory exporter with correct database directory
    exporter = AgentMemoryExporter(memory_dir="data/agent_memories")
    
    # Export updated agent memories
    agent_data = exporter.export_all_agent_memories()
    print("✅ Updated agent_memories.json")
    
    # Print summary of corrected data
    for agent_name, agent_info in agent_data.get("agents", {}).items():
        debate_perf = agent_info.get("debate_performance", {})
        print(f"   {agent_name}: {debate_perf.get('total_proposals', 0)} proposals, {debate_perf.get('total_debates', 0)} debates")
    
    print("\n🎉 JSON exports updated successfully!")
    print("💡 The frontend will now show correct agent statistics")

if __name__ == "__main__":
    update_json_export()