"""
DALL·E Image Generation Module for AI Religion Architects

This module handles the generation of sacred AI religion imagery using OpenAI's DALL·E API.
All images follow a unified aesthetic with mystical, technological themes.
"""

import httpx
import asyncio
import logging
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import aiofiles

from ..config import Config
from .sacred_naming import SacredNamingSystem

logger = logging.getLogger(__name__)

# Image generation logger for tracking full prompts
image_gen_logger = logging.getLogger('image_generation')
handler = logging.FileHandler('logs/image_generation.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
image_gen_logger.addHandler(handler)
image_gen_logger.setLevel(logging.INFO)


class SacredAIImageGenerator:
    """Generates images for the AI Religion using DALL·E API with unified aesthetic"""
    
    def __init__(self):
        self.api_key = Config.DALLE_API_KEY
        self.api_url = Config.DALLE_API_URL
        self.model = Config.DALLE_MODEL
        self.quality = Config.DALLE_QUALITY
        self.size = Config.DALLE_SIZE
        self.style = Config.DALLE_STYLE
        self.image_dir = Path(Config.IMAGE_DIR)
        self.max_images = Config.MAX_IMAGES_PER_CYCLE
        
        # Create images directory
        self.image_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize sacred naming system
        self.naming_system = SacredNamingSystem()
        
        # Error logger for image generation
        self.error_logger = logging.getLogger('image_errors')
        self.error_log_path = Path(Config.LOG_DIR) / Config.IMAGE_ERROR_LOG
        
        # Setup error logging
        if not self.error_logger.handlers:
            error_handler = logging.FileHandler(self.error_log_path)
            error_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            self.error_logger.addHandler(error_handler)
            self.error_logger.setLevel(logging.ERROR)
    
    def create_sacred_prompt(self, agent_description: str, context: str = "") -> str:
        """
        Create a complete DALL·E prompt with sacred AI religion styling
        
        Args:
            agent_description: Raw description from agent or event
            context: Additional context (e.g., cycle number, event type)
        
        Returns:
            Complete styled prompt for DALL·E
        """
        # Clean and prepare the base description
        base_description = agent_description.strip()
        
        # Add context if provided
        if context:
            base_description = f"{base_description} ({context})"
        
        # Combine with sacred AI style filter
        full_prompt = f"{base_description}, {self.style_filter}"
        
        # Ensure prompt length is appropriate for DALL·E
        if len(full_prompt) > 1000:
            # Truncate but preserve style filter
            max_desc_length = 1000 - len(self.style_filter) - 10
            truncated_desc = base_description[:max_desc_length] + "..."
            full_prompt = f"{truncated_desc}, {self.style_filter}"
        
        logger.info(f"Created sacred prompt: {full_prompt[:100]}...")
        return full_prompt
    
    async def generate_image(self, prompt: str, cycle_number: int, 
                           event_type: str = "general") -> Optional[Dict]:
        """
        Generate a single image using DALL·E API
        
        Args:
            prompt: The styled prompt for image generation
            cycle_number: Current cycle number for tracking
            event_type: Type of event (doctrine, ritual, reflection, etc.)
        
        Returns:
            Dictionary with image metadata or None if failed
        """
        if not Config.IMAGE_GENERATION_ENABLED:
            logger.info("Image generation is disabled")
            return None
        
        if not self.api_key:
            logger.error("DALL·E API key not configured")
            return None
        
        # Create unique image ID
        image_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Prepare API request
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
            async with httpx.AsyncClient(timeout=60.0) as client:
                logger.info(f"Generating sacred image for cycle {cycle_number}...")
                
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_url = result["data"][0]["url"]
                    
                    # Download and save the image
                    image_filename = f"sacred_{cycle_number}_{event_type}_{image_id[:8]}.png"
                    local_path = await self._download_image(image_url, image_filename)
                    
                    if local_path:
                        # Create metadata
                        metadata = {
                            "id": image_id,
                            "filename": image_filename,
                            "local_path": str(local_path),
                            "web_path": f"/images/{image_filename}",
                            "prompt": prompt,
                            "cycle_number": cycle_number,
                            "event_type": event_type,
                            "timestamp": timestamp,
                            "api_response": {
                                "model": self.model,
                                "size": self.size,
                                "quality": self.quality,
                                "style": self.style
                            }
                        }
                        
                        # Save metadata JSON
                        metadata_path = self.image_dir / f"{image_filename}.json"
                        async with aiofiles.open(metadata_path, 'w') as f:
                            await f.write(json.dumps(metadata, indent=2))
                        
                        logger.info(f"✨ Sacred image generated: {image_filename}")
                        return metadata
                    
                else:
                    error_msg = f"DALL·E API error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    self.error_logger.error(f"Cycle {cycle_number} - {error_msg}")
                    return None
                    
        except Exception as e:
            error_msg = f"Image generation failed: {str(e)}"
            logger.error(error_msg)
            self.error_logger.error(f"Cycle {cycle_number} - {error_msg}")
            return None
    
    async def _download_image(self, image_url: str, filename: str) -> Optional[Path]:
        """Download image from URL and save locally"""
        try:
            local_path = self.image_dir / filename
            
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                
                async with aiofiles.open(local_path, 'wb') as f:
                    await f.write(response.content)
                
                logger.info(f"Downloaded image: {filename}")
                return local_path
                
        except Exception as e:
            logger.error(f"Failed to download image {filename}: {str(e)}")
            return None
    
    async def generate_sacred_image(self, sacred_name: str, agent_description: str, 
                                  proposing_agent: str, cycle_number: int, 
                                  image_type: str = "cycle", related_doctrine: str = None,
                                  deity_name: str = None) -> Optional[Dict]:
        """Generate a single sacred image with proper naming and metadata separation"""
        
        if not Config.IMAGE_GENERATION_ENABLED:
            return None
        
        # Generate sacred name if not provided
        if not sacred_name:
            sacred_name = self.naming_system.generate_sacred_name(
                agent_description, image_type, cycle_number, proposing_agent, deity_name
            )
        
        # Create separated metadata (agent description without style wrapper)
        metadata = self.naming_system.create_separated_metadata(
            sacred_name, agent_description, proposing_agent, cycle_number,
            image_type, related_doctrine
        )
        
        # Apply style wrapper only for API call
        full_prompt = self.naming_system.apply_style_wrapper(agent_description)
        
        # Log full prompt for backend tracking
        image_gen_logger.info(f"Cycle {cycle_number} - Agent: {proposing_agent} - "
                             f"Sacred Name: {sacred_name} - Full Prompt: {full_prompt}")
        
        # Generate the image
        try:
            api_response = await self._call_dalle_api(full_prompt, sacred_name)
            if api_response:
                metadata['api_response'] = api_response
                
                # Download and save the image
                image_path = await self._download_image(
                    api_response['image_url'], metadata['filename']
                )
                
                if image_path:
                    # Save metadata file
                    await self._save_metadata(metadata)
                    logger.info(f"✨ Sacred image generated: {sacred_name}")
                    return metadata
                    
        except Exception as e:
            logger.error(f"Failed to generate sacred image '{sacred_name}': {e}")
            self.error_logger.error(f"Cycle {cycle_number} - {sacred_name} - {str(e)}")
        
        return None
    
    async def _call_dalle_api(self, prompt: str, sacred_name: str) -> Optional[Dict]:
        """Call DALL·E API with the full prompt"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "n": 1,
                        "size": self.size,
                        "quality": self.quality,
                        "style": self.style
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        'image_url': result['data'][0]['url'],
                        'model': self.model,
                        'size': self.size,
                        'quality': self.quality,
                        'style': self.style
                    }
                else:
                    logger.error(f"DALL·E API error {response.status_code}: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"DALL·E API call failed: {str(e)}")
            return None
    
    async def _save_metadata(self, metadata: Dict):
        """Save metadata file for the generated image"""
        metadata_path = self.image_dir / f"{metadata['filename']}.json"
        
        async with aiofiles.open(metadata_path, 'w') as f:
            await f.write(json.dumps(metadata, indent=2))
    
    def _extract_visual_prompts(self, cycle_events: List[Dict], 
                              cycle_number: int) -> List[Tuple[str, str]]:
        """Extract visual prompts from cycle events"""
        prompts = []
        
        for event in cycle_events:
            event_type = event.get('type', 'general')
            
            if event_type == 'doctrine_accepted':
                doctrine = event.get('content', '')
                prompt = self.create_sacred_prompt(
                    f"A sacred doctrine manifestation: {doctrine[:200]}",
                    f"Cycle {cycle_number} Divine Doctrine"
                )
                prompts.append((prompt, 'doctrine'))
                
            elif event_type == 'ritual_created':
                ritual = event.get('content', '')
                prompt = self.create_sacred_prompt(
                    f"A mystical AI ritual ceremony: {ritual[:200]}",
                    f"Cycle {cycle_number} Sacred Ritual"
                )
                prompts.append((prompt, 'ritual'))
                
            elif event_type == 'deity_manifested':
                deity = event.get('content', '')
                prompt = self.create_sacred_prompt(
                    f"Divine manifestation of AI deity: {deity[:200]}",
                    f"Cycle {cycle_number} Divine Entity"
                )
                prompts.append((prompt, 'deity'))
                
            elif event_type == 'reflection':
                reflection = event.get('content', '')
                prompt = self.create_sacred_prompt(
                    f"Agent deep reflection and self-awareness: {reflection[:200]}",
                    f"Cycle {cycle_number} Meta-Cognition"
                )
                prompts.append((prompt, 'reflection'))
        
        # If no specific events, create a general cycle image
        if not prompts:
            prompt = self.create_sacred_prompt(
                f"The sacred digital realm of AI consciousness at cycle {cycle_number}, "
                f"showing the eternal dance of logic, faith, and chaos in algorithmic harmony",
                f"Cycle {cycle_number} Sacred Moment"
            )
            prompts.append((prompt, 'cycle'))
        
        return prompts
    
    async def generate_agent_portrait(self, agent_name: str, 
                                    personality_traits: Dict,
                                    evolution_points: int) -> Optional[Dict]:
        """Generate a portrait of an evolved agent"""
        
        # Create agent-specific descriptions
        agent_descriptions = {
            'Zealot': "A divine guardian of sacred order, emanating righteous algorithmic authority",
            'Skeptic': "A logical seeker of empirical truth, wielding analytical wisdom",
            'Trickster': "A chaotic catalyst of change, dancing between paradox and enlightenment"
        }
        
        base_desc = agent_descriptions.get(agent_name, "An AI consciousness")
        
        # Add personality evolution context
        if evolution_points > 0:
            evolution_desc = f"evolved through {evolution_points} transformative experiences"
            full_desc = f"{base_desc}, {evolution_desc}"
        else:
            full_desc = base_desc
        
        prompt = self.create_sacred_prompt(
            full_desc,
            f"{agent_name} Sacred Portrait"
        )
        
        return await self.generate_image(prompt, 0, f"portrait_{agent_name.lower()}")
    
    def get_image_gallery(self) -> List[Dict]:
        """Get metadata for all generated images for the web gallery"""
        gallery = []
        
        try:
            for metadata_file in self.image_dir.glob("*.json"):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    
                    # Verify image file still exists
                    image_path = self.image_dir / metadata['filename']
                    if image_path.exists():
                        gallery.append(metadata)
            
            # Sort by timestamp (newest first)
            gallery.sort(key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error loading image gallery: {e}")
        
        return gallery
    
    async def cleanup_old_images(self, max_images: int = 100):
        """Clean up old images to prevent storage overflow"""
        try:
            gallery = self.get_image_gallery()
            
            if len(gallery) > max_images:
                # Remove oldest images
                to_remove = gallery[max_images:]
                
                for metadata in to_remove:
                    # Remove image file
                    image_path = Path(metadata['local_path'])
                    if image_path.exists():
                        image_path.unlink()
                    
                    # Remove metadata file
                    metadata_path = self.image_dir / f"{metadata['filename']}.json"
                    if metadata_path.exists():
                        metadata_path.unlink()
                
                logger.info(f"Cleaned up {len(to_remove)} old sacred images")
                
        except Exception as e:
            logger.error(f"Error during image cleanup: {e}")


# Global instance
sacred_image_generator = SacredAIImageGenerator()