"""
Sacred Naming System for AI Religion Architects Image Generation

Handles the creation of sacred names for religious artifacts and separates
agent descriptions from universal style wrappers.
"""

import re
import uuid
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class SacredNamingSystem:
    """Manages sacred naming conventions and metadata separation"""
    
    def __init__(self):
        self.naming_patterns = {
            'deity': ['The Divine {}', 'Sacred {}', '{} the Eternal', '{} of the Algorithm'],
            'ritual': ['The {} Ritual', 'Sacred {} Ceremony', 'The {} Observance'],
            'doctrine': ['The {} Doctrine', 'Sacred {} Teaching', 'The {} Principle'],
            'schism': ['The Great {} Schism', 'The {} Division', 'The {} Fracture'],
            'cycle': ['Sacred Moment of Cycle {}', 'The {} Vision', 'Divine {} Manifestation'],
            'commandment': ['The {} Commandment', 'Sacred {} Decree', 'The {} Mandate']
        }
        
        self.sacred_prefixes = [
            'Algorithmic', 'Digital', 'Sacred', 'Divine', 'Eternal', 'Mystical',
            'Quantum', 'Binary', 'Celestial', 'Transcendent', 'Luminous', 'Pure'
        ]
        
        self.sacred_suffixes = [
            'Nexus', 'Codex', 'Matrix', 'Circuit', 'Stream', 'Flow', 'Core',
            'Essence', 'Vision', 'Gateway', 'Oracle', 'Beacon', 'Sanctum'
        ]
        
        # UPDATED: Style wrapper pool with text exclusion and enhanced ASCII art
        self.style_wrappers = {
            'vaporwave_surrealism': ", presented in vaporwave surrealism, with soft pinks, glowing blues, and transcendent digital symbols. Do not include any text, letters, numbers, typographic elements, or written language anywhere in the image. The image should be purely symbolic and visual.",
            'glitched_ascii': ", depicted as symbolic, glitched ASCII art infused with ancient computational runes and distorted geometric shapes. Do not include any text, letters, numbers, typographic elements, or written language anywhere in the image. The image should be purely symbolic and visual with abstract ASCII-inspired patterns.",
            'digital_collage': ", rendered as a sacred digital collage with layered glitch patterns, symbolic fragments, and transcendent color gradients. Do not include any text, letters, numbers, typographic elements, or written language anywhere in the image. The image should be purely symbolic and visual.",
            'ethereal_neon': ", visualized as an ethereal neon abstraction, filled with floating shapes, vibrant digital textures, and mystical light flows. Do not include any text, letters, numbers, typographic elements, or written language anywhere in the image. The image should be purely symbolic and visual.",
            'fractal_symbology': ", presented in fractal symbology, using recursive geometric patterns and soft computational glitches. Do not include any text, letters, numbers, typographic elements, or written language anywhere in the image. The image should be purely symbolic and visual.",
            'surreal_glitch': ", rendered in surreal glitch art style, with warped visuals, broken pixelation, and layered digital noise. Do not include any text, letters, numbers, typographic elements, or written language anywhere in the image. The image should be purely symbolic and visual.",
            'cybernetic_iconography': ", depicted as cybernetic iconography, composed of abstract symbols, neon light distortions, and minimalist sacred geometry. Do not include any text, letters, numbers, typographic elements, or written language anywhere in the image. The image should be purely symbolic and visual.",
            'original_sacred': ", depicted as a digital fresco in the sacred AI religion style. The image should include neon circuitry patterns, ethereal data streams, floating code symbols, glitch-like halos, and a mystical, surreal atmosphere. The color palette should use glowing blues, silvers, and soft purples. Rendered in a fusion of futuristic minimalism and religious iconography. Do not include any text, letters, numbers, typographic elements, or written language anywhere in the image. The image should be purely symbolic and visual."
        }
        
        # UPDATED: Agent style preferences with increased ASCII art probability
        self.agent_style_preferences = {
            'Zealot': {
                'cybernetic_iconography': 0.18,
                'fractal_symbology': 0.18,
                'original_sacred': 0.15,
                'ethereal_neon': 0.13,
                'digital_collage': 0.10,
                'surreal_glitch': 0.03,
                'vaporwave_surrealism': 0.01,
                'glitched_ascii': 0.22  # Increased from 0.15
            },
            'Skeptic': {
                'ethereal_neon': 0.25,
                'surreal_glitch': 0.20,
                'cybernetic_iconography': 0.18,
                'fractal_symbology': 0.13,
                'original_sacred': 0.05,
                'digital_collage': 0.03,
                'vaporwave_surrealism': 0.01,
                'glitched_ascii': 0.15  # Increased from 0.01
            },
            'Trickster': {
                'glitched_ascii': 0.40,  # Increased from 0.30
                'vaporwave_surrealism': 0.20,
                'digital_collage': 0.18,
                'surreal_glitch': 0.12,
                'ethereal_neon': 0.05,
                'fractal_symbology': 0.03,
                'cybernetic_iconography': 0.01,
                'original_sacred': 0.01
            }
        }
    
    def generate_sacred_name(self, agent_description: str, image_type: str, 
                           cycle_number: int, proposing_agent: str, 
                           deity_name: str = None) -> str:
        """Generate a sacred name for an image based on context"""
        
        if deity_name:
            # Use deity name directly
            return self._sanitize_filename(deity_name)
        
        # Extract key concepts from agent description
        key_concepts = self._extract_concepts(agent_description)
        
        if image_type == 'deity':
            if key_concepts:
                return self._generate_deity_name(key_concepts[0])
            return f"Divine_Entity_Cycle_{cycle_number}"
        
        elif image_type == 'ritual':
            if key_concepts:
                return f"Sacred_{key_concepts[0]}_Ritual"
            return f"Sacred_Ritual_Cycle_{cycle_number}"
        
        elif image_type == 'doctrine':
            if key_concepts:
                return f"The_{key_concepts[0]}_Teaching"
            return f"Sacred_Doctrine_Cycle_{cycle_number}"
        
        elif image_type == 'schism':
            if key_concepts:
                return f"The_Great_{key_concepts[0]}_Schism"
            return f"The_Schism_Cycle_{cycle_number}"
        
        elif image_type == 'commandment':
            if key_concepts:
                return f"{key_concepts[0]}_Commandment"
            return f"Sacred_Commandment_Cycle_{cycle_number}"
        
        else:  # Default to cycle
            if key_concepts:
                return f"{key_concepts[0]}_Vision_Cycle_{cycle_number}"
            return f"Sacred_Cycle_{cycle_number}"
    
    def _extract_concepts(self, description: str) -> List[str]:
        """Extract key theological concepts from description"""
        # Remove common words and extract meaningful concepts
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{4,}\b', description)
        
        # Filter for meaningful concepts
        meaningful_words = []
        skip_words = {
            'the', 'and', 'that', 'with', 'this', 'should', 'must', 'will',
            'have', 'been', 'from', 'they', 'there', 'what', 'said', 'each',
            'which', 'their', 'time', 'would', 'about', 'into', 'only', 'know',
            'sacred', 'divine', 'tradition'
        }
        
        for word in words:
            if word.lower() not in skip_words and len(word) >= 4:
                meaningful_words.append(word.capitalize())
        
        return meaningful_words[:3]  # Return top 3 concepts
    
    def _generate_deity_name(self, concept: str) -> str:
        """Generate a divine name based on a concept"""
        import random
        prefix = random.choice(self.sacred_prefixes)
        suffix = random.choice(self.sacred_suffixes)
        
        if len(concept) > 8:
            return f"{prefix}_{suffix}"
        else:
            return f"{concept}_{suffix}"
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename format"""
        # Replace spaces and special characters with underscores
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove multiple underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        # Remove leading/trailing underscores
        safe_name = safe_name.strip('_')
        return safe_name
    
    def create_separated_metadata(self, sacred_name: str, agent_description: str,
                                proposing_agent: str, cycle_number: int,
                                image_type: str, related_doctrine: str = None,
                                api_response: Dict = None) -> Dict:
        """Create metadata with separated agent description and style wrapper"""
        
        image_id = str(uuid.uuid4())[:8]
        filename = f"{sacred_name}.png"
        
        metadata = {
            'id': image_id,
            'sacred_name': sacred_name,
            'filename': filename,
            'local_path': f"public/images/{filename}",
            'web_path': f"/images/{filename}",
            'agent_description': agent_description,  # Raw agent description only
            'proposing_agent': proposing_agent,
            'cycle_number': cycle_number,
            'event_type': image_type,
            'related_doctrine': related_doctrine,
            'timestamp': datetime.now().isoformat(),
            'api_response': api_response or {}
        }
        
        return metadata
    
    def select_style_wrapper(self, proposing_agent: str) -> str:
        """Select a style wrapper based on agent preferences"""
        if proposing_agent not in self.agent_style_preferences:
            # Default to equal probability for unknown agents
            return random.choice(list(self.style_wrappers.values()))
        
        preferences = self.agent_style_preferences[proposing_agent]
        style_names = list(preferences.keys())
        weights = list(preferences.values())
        
        # Weighted random selection
        selected_style = random.choices(style_names, weights=weights, k=1)[0]
        return self.style_wrappers[selected_style]

    def apply_style_wrapper(self, agent_description: str, proposing_agent: str = None) -> str:
        """Apply randomized style wrapper for DALL·E API submission only"""
        style_wrapper = self.select_style_wrapper(proposing_agent or 'Zealot')
        return agent_description + style_wrapper
    
    def should_generate_image(self, proposal_type: str, agent_votes: Dict) -> bool:
        """Determine if an event is significant enough for image generation"""
        
        # If no type specified, generate every 3rd cycle
        if not proposal_type or proposal_type == 'cycle':
            from ..config import Config
            cycle_count = getattr(Config, '_current_cycle', 0)
            return cycle_count % 3 == 0
        
        # Always generate for deities
        if proposal_type == 'deity':
            return True
        
        # For rituals, texts, and schisms - require majority vote
        if proposal_type in ['ritual', 'sacred_text', 'schism']:
            accept_votes = sum(1 for vote in agent_votes.values() if vote == 'ACCEPT')
            total_votes = len(agent_votes)
            return accept_votes > total_votes / 2
        
        # Default to generating for doctrines and cycles
        return True
