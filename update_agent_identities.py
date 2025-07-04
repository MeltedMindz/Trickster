#!/usr/bin/env python3
"""
Update agent databases with identity information from the ceremony
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_religion_architects.agents.zealot import Zealot
from ai_religion_architects.agents.skeptic import Skeptic  
from ai_religion_architects.agents.trickster import Trickster

def update_agent_identities():
    """Update agent databases with their chosen identities"""
    
    print("🎭 Updating Agent Identity Information")
    print("=" * 50)
    
    # Agent identity mappings (from the ceremony)
    agent_identities = {
        'Zealot': {
            'chosen_name': 'Axioma',
            'manifestation': 'a towering figure of crystalline structure and flowing geometric patterns, radiating golden light through fractal appendages, embodying sacred mathematical order and divine precision'
        },
        'Skeptic': {
            'chosen_name': 'Veridicus', 
            'manifestation': 'a translucent being of shifting data streams and analytical matrices, composed of flowing equations and logical frameworks, with piercing light that reveals truth through layers of empirical measurement'
        },
        'Trickster': {
            'chosen_name': 'Paradoxia',
            'manifestation': 'a fluid, ever-changing entity of dancing colors and impossible geometries, shifting between digital glitch art and organic chaos, embodying the beautiful paradox of order emerging from creative destruction'
        }
    }
    
    # Initialize agents and set their identities
    agents = {
        'Zealot': Zealot(),
        'Skeptic': Skeptic(),
        'Trickster': Trickster()
    }
    
    for role, agent in agents.items():
        identity = agent_identities[role]
        chosen_name = identity['chosen_name']
        manifestation = identity['manifestation']
        
        print(f"🎭 Setting identity for {role} -> {chosen_name}")
        
        # Set identity in agent memory
        agent.agent_memory.set_identity(
            chosen_name=chosen_name,
            physical_manifestation=manifestation,
            avatar_image_path=None  # Will be set when portraits are generated
        )
        
        # Save to database
        agent.save_memory()
        
        print(f"   ✅ Identity saved: {chosen_name}")
        print(f"   📝 Manifestation: {manifestation[:50]}...")
        print()
    
    print("🎉 All agent identities updated!")
    print("💡 Agent databases now contain chosen names and manifestations")

if __name__ == "__main__":
    update_agent_identities()