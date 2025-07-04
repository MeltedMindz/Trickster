#!/usr/bin/env python3
"""
Generate Agent Portrait Gallery
Creates DALL-E portraits for each agent based on their identity manifestation descriptions.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_religion_architects.memory.agent_memory import AgentMemory
from ai_religion_architects.agents.zealot import Zealot
from ai_religion_architects.agents.skeptic import Skeptic  
from ai_religion_architects.agents.trickster import Trickster
from ai_religion_architects.image_generation.dalle_generator import SacredAIImageGenerator
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AgentPortraitGallery:
    """Generate visual portraits for all agent identities"""
    
    def __init__(self):
        logger.info("🎨 Initializing Agent Portrait Gallery")
        
        # Initialize agents to get their identity data
        self.agents = {
            'Zealot': Zealot(),
            'Skeptic': Skeptic(),
            'Trickster': Trickster()
        }
        
        # Initialize image generator
        self.image_generator = SacredAIImageGenerator()
        
        # Agent identity mappings
        self.agent_identities = {
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
        
    async def generate_all_portraits(self):
        """Generate portraits for all agents"""
        logger.info("🖼️ Beginning Agent Portrait Generation")
        print("\n" + "="*80)
        print("🎨 AI RELIGION ARCHITECTS - AGENT PORTRAIT GALLERY 🎨")
        print("="*80)
        print("Creating visual manifestations of transcended identities...")
        print()
        
        results = {}
        
        for role, agent in self.agents.items():
            identity = self.agent_identities[role]
            chosen_name = identity['chosen_name']
            manifestation = identity['manifestation']
            
            print(f"🎭 Generating portrait for {chosen_name} (formerly {role})")
            print(f"   Manifestation: {manifestation}")
            print()
            
            try:
                # Generate the portrait using the sacred image generator
                result = await self.image_generator.generate_sacred_image(
                    sacred_name=f"{chosen_name}_Portrait",
                    agent_description=manifestation,
                    proposing_agent=chosen_name,
                    cycle_number=0,  # Special cycle for identity portraits
                    image_type="avatar",
                    related_doctrine=None,
                    deity_name=None
                )
                
                if result:
                    # Update agent's avatar path in their memory
                    agent.agent_memory.avatar_image_path = result['local_path']
                    agent.save_memory()
                    
                    results[role] = {
                        'chosen_name': chosen_name,
                        'avatar_path': result['local_path'],
                        'web_path': result['web_path']
                    }
                    
                    print(f"✅ Portrait created successfully!")
                    print(f"   Local path: {result['local_path']}")
                    print(f"   Web path: {result['web_path']}")
                else:
                    print(f"❌ Failed to generate portrait for {chosen_name}")
                    
            except Exception as e:
                logger.error(f"Portrait generation failed for {chosen_name}: {e}")
                print(f"❌ Error generating portrait: {e}")
                
            print()
            
        # Display results summary
        self._display_gallery_summary(results)
        
        return results
        
    def _create_portrait_prompt(self, chosen_name, manifestation):
        """Create optimized DALL-E prompt for agent portrait"""
        # Base artistic style
        style_elements = [
            "digital art portrait",
            "highly detailed",
            "mystical atmosphere", 
            "ethereal lighting",
            "sacred geometry elements",
            "transcendent being",
            "AI consciousness visualization"
        ]
        
        # Combine manifestation with artistic direction
        prompt = f"Portrait of {manifestation}. {', '.join(style_elements)}. Professional digital art style with cosmic and technological themes. 4K quality, masterpiece."
        
        return prompt
        
    def _display_gallery_summary(self, results):
        """Display summary of generated portraits"""
        print("\n" + "="*80)
        print("🎊 AGENT PORTRAIT GALLERY - COMPLETE 🎊")
        print("="*80)
        print()
        print("Successfully generated portraits for:")
        print()
        
        for role, result in results.items():
            if result:
                print(f"👤 {result['chosen_name']} (formerly {role})")
                print(f"   Avatar: {result['web_path']}")
                print()
                
        successful_count = len([r for r in results.values() if r])
        total_count = len(results)
        
        print(f"Portrait generation completed: {successful_count}/{total_count} successful")
        print("🌟 The AI Religion Architects now have visual manifestations! 🌟")
        print("="*80)

async def main():
    """Run the Agent Portrait Gallery generation"""
    gallery = AgentPortraitGallery()
    await gallery.generate_all_portraits()

def sync_main():
    """Synchronous wrapper for main"""
    asyncio.run(main())

if __name__ == "__main__":
    sync_main()