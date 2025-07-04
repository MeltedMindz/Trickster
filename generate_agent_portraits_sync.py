#!/usr/bin/env python3
"""
Generate Agent Portrait Gallery (Synchronous Version)
Creates DALL-E portraits for each agent based on their identity manifestation descriptions.
"""

import sys
import os
import json
import uuid
import requests
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_religion_architects.agents.zealot import Zealot
from ai_religion_architects.agents.skeptic import Skeptic  
from ai_religion_architects.agents.trickster import Trickster
from ai_religion_architects.config import Config
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class SyncAgentPortraitGallery:
    """Generate visual portraits for all agent identities (synchronous version)"""
    
    def __init__(self):
        logger.info("🎨 Initializing Agent Portrait Gallery")
        
        # Initialize agents to get their identity data
        self.agents = {
            'Zealot': Zealot(),
            'Skeptic': Skeptic(),
            'Trickster': Trickster()
        }
        
        # Image generation config
        self.api_key = Config.DALLE_API_KEY
        self.api_url = Config.DALLE_API_URL
        self.model = Config.DALLE_MODEL
        self.quality = Config.DALLE_QUALITY
        self.size = Config.DALLE_SIZE
        self.style = Config.DALLE_STYLE
        self.image_dir = Path(Config.IMAGE_DIR)
        
        # Create images directory
        self.image_dir.mkdir(parents=True, exist_ok=True)
        
        # Agent identity mappings (from the ceremony)
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
        
    def generate_all_portraits(self):
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
                # Generate the portrait
                result = self._generate_portrait(chosen_name, manifestation, role)
                
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
        
    def _generate_portrait(self, chosen_name, manifestation, role):
        """Generate a single portrait"""
        
        if not Config.IMAGE_GENERATION_ENABLED:
            logger.info("Image generation is disabled")
            return None
        
        if not self.api_key:
            logger.error("DALL·E API key not configured")
            return None
        
        # Create portrait prompt
        prompt = self._create_portrait_prompt(chosen_name, manifestation)
        
        # Create unique filename
        image_id = str(uuid.uuid4())[:8]
        filename = f"{chosen_name}_Portrait.png"
        
        # Generate image via DALL-E API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": self.size,
            "quality": self.quality,
            "style": self.style
        }
        
        try:
            logger.info(f"Calling DALL-E API for {chosen_name}...")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                image_url = result["data"][0]["url"]
                
                # Download and save the image
                local_path = self._download_image(image_url, filename)
                
                if local_path:
                    # Create metadata
                    metadata = {
                        "id": image_id,
                        "filename": filename,
                        "local_path": str(local_path),
                        "web_path": f"/images/{filename}",
                        "prompt": "",  # Don't store full prompt in public metadata
                        "cycle_number": 0,
                        "event_type": "avatar",
                        "timestamp": datetime.now().isoformat(),
                        "sacred_name": f"{chosen_name}_Portrait",
                        "agent_description": f"Portrait of {chosen_name}, the transcended identity of {role}",
                        "proposing_agent": chosen_name,
                        "related_doctrine": "",
                        "deity_name": "",
                        "api_response": {
                            "image_url": image_url,
                            "model": self.model,
                            "size": self.size,
                            "quality": self.quality,
                            "style": self.style
                        }
                    }
                    
                    # Save metadata
                    self._save_metadata(metadata)
                    
                    # Update sacred images registry
                    self._update_sacred_images_registry(metadata)
                    
                    logger.info(f"✨ Portrait generated: {filename}")
                    return metadata
                    
            else:
                logger.error(f"DALL·E API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling DALL·E API: {e}")
            return None
    
    def _create_portrait_prompt(self, chosen_name, manifestation):
        """Create optimized DALL-E prompt for agent portrait"""
        # Create a detailed portrait prompt
        prompt = f"Portrait of {manifestation}. Digital art style, highly detailed, mystical atmosphere, ethereal lighting, sacred geometry elements, transcendent AI being, cosmic and technological themes, professional artwork, 4K quality masterpiece."
        
        # Ensure prompt length is appropriate
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."
        
        logger.info(f"Created portrait prompt for {chosen_name}: {prompt[:100]}...")
        return prompt
        
    def _download_image(self, image_url, filename):
        """Download image from URL and save locally"""
        try:
            local_path = self.image_dir / filename
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image: {filename}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download image {filename}: {e}")
            return None
    
    def _save_metadata(self, metadata):
        """Save metadata file for the generated image"""
        metadata_path = self.image_dir / f"{metadata['filename']}.json"
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _update_sacred_images_registry(self, metadata):
        """Update the sacred images registry with the new portrait"""
        registry_path = Path("public/data/sacred_images.json")
        
        try:
            # Load existing registry
            if registry_path.exists():
                with open(registry_path, 'r') as f:
                    registry = json.load(f)
            else:
                registry = {"images": [], "total": 0, "last_updated": ""}
            
            # Add new image
            registry["images"].insert(0, metadata)  # Add to beginning
            registry["total"] = len(registry["images"])
            registry["last_updated"] = datetime.now().isoformat()
            
            # Save updated registry
            with open(registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
                
            logger.info(f"Updated sacred images registry with {metadata['filename']}")
            
        except Exception as e:
            logger.error(f"Failed to update sacred images registry: {e}")
    
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

def main():
    """Run the Agent Portrait Gallery generation"""
    gallery = SyncAgentPortraitGallery()
    gallery.generate_all_portraits()

if __name__ == "__main__":
    main()