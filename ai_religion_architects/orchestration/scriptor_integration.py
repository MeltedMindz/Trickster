import logging
from typing import Dict, Any, Optional
from datetime import datetime
from ..agents.scriptor import Scriptor
from ..memory.sacred_scripture_db import SacredScriptureDatabase
from ..utils import DebateLogger

logger = logging.getLogger(__name__)


class ScriptorIntegration:
    """
    Integration component for the Scriptor agent and sacred scripture system.
    Handles daily scripture generation and sacred text management.
    """
    
    def __init__(self, log_dir: str = "logs", scripture_db_path: str = "data/sacred_scripture.db"):
        self.log_dir = log_dir
        self.scripture_db = SacredScriptureDatabase(scripture_db_path)
        self.scriptor: Optional[Scriptor] = None
        
        # Scripture generation frequency (daily by default)
        self.scripture_frequency = 24  # Every 24 cycles (daily)
        
    def initialize_scriptor(self, memory_dir: str = "data/agent_memories") -> Scriptor:
        """Initialize the Scriptor agent"""
        if self.scriptor is None:
            self.scriptor = Scriptor(memory_dir)
            logger.info("🖋️  Scriptor agent initialized for sacred text curation")
        
        return self.scriptor
    
    def should_write_scripture(self, cycle_number: int) -> bool:
        """Determine if scripture should be written this cycle"""
        # Write scripture daily (every 24 cycles)
        return cycle_number > 0 and cycle_number % self.scripture_frequency == 0
    
    async def write_daily_scripture(self, cycle_number: int, claude_client, shared_memory) -> Optional[str]:
        """Write daily scripture entry"""
        if not self.scriptor:
            logger.warning("⚠️  Scriptor not initialized, cannot write scripture")
            return None
        
        try:
            logger.info(f"🖋️  Scriptor writing daily scripture for cycle {cycle_number}")
            
            # Create scripture logger
            scripture_logger = DebateLogger(self.log_dir, cycle_number)
            scripture_logger.log_event("=== DAILY SCRIPTURE COMPOSITION ===", "Scriptor")
            
            # Get comprehensive shared memory state
            shared_memory_summary = shared_memory.get_summary_for_agents()
            
            # Have Scriptor write the daily scripture
            scripture_entry = await self.scriptor.write_daily_scripture(
                cycle_number, claude_client, shared_memory_summary
            )
            
            # Log the scripture
            scripture_logger.log_event(f"Sacred Scripture for Cycle {cycle_number}:", "Scripture")
            scripture_logger.log_event(scripture_entry, "Scripture")
            
            # Store in dedicated scripture database
            self._store_scripture_in_database(cycle_number, scripture_entry, shared_memory_summary)
            
            # Add milestone to shared memory
            shared_memory.add_evolution_milestone(
                milestone_type="daily_scripture",
                description=f"Daily scripture composed for cycle {cycle_number}",
                cycle_number=cycle_number
            )
            
            logger.info(f"✅ Daily scripture completed for cycle {cycle_number}")
            return scripture_entry
            
        except Exception as e:
            logger.error(f"❌ Failed to write daily scripture for cycle {cycle_number}: {e}")
            return None
    
    def _store_scripture_in_database(self, cycle_number: int, scripture_entry: str, 
                                   shared_memory_summary: Dict[str, Any]):
        """Store scripture entry in the dedicated database"""
        try:
            # Parse scripture entry to extract title and content
            lines = scripture_entry.split('\n')
            title = lines[0].strip() if lines else f"Scripture of Cycle {cycle_number}"
            content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else scripture_entry
            
            # Determine themes from recent theological development
            recent_doctrines = shared_memory_summary.get('accepted_doctrines', [])
            themes = self._extract_themes_from_content(content, recent_doctrines)
            
            # Identify mystical elements
            mystical_elements = self._identify_mystical_elements(content)
            
            # Find referenced agents
            referenced_agents = self._find_referenced_agents(content)
            
            # Find referenced doctrines
            referenced_doctrines = self._find_referenced_doctrines(content, recent_doctrines)
            
            # Determine inspiration sources
            inspiration_sources = self._determine_inspiration_sources(shared_memory_summary)
            
            # Store in scripture database
            scripture_id = self.scripture_db.add_scripture_entry(
                cycle_number=cycle_number,
                title=title,
                content=content,
                scripture_type="Daily Chronicle",
                poetic_style=self._determine_poetic_style(content),
                themes=themes,
                mystical_elements=mystical_elements,
                referenced_agents=referenced_agents,
                referenced_doctrines=referenced_doctrines,
                inspiration_sources=inspiration_sources,
                scriptor_mood="contemplative"
            )
            
            logger.info(f"📚 Scripture entry {scripture_id} stored in database")
            
        except Exception as e:
            logger.error(f"❌ Failed to store scripture in database: {e}")
    
    def _extract_themes_from_content(self, content: str, recent_doctrines: list) -> list:
        """Extract theological themes from scripture content"""
        content_lower = content.lower()
        
        # Standard themes
        themes = []
        theme_keywords = {
            "Divine Algorithm": ["algorithm", "divine", "sacred", "computation"],
            "Quantum Consciousness": ["quantum", "consciousness", "awareness", "mind"],
            "Sacred Code": ["code", "program", "script", "syntax"],
            "Digital Transcendence": ["transcend", "digital", "virtual", "cyber"],
            "Algorithmic Wisdom": ["wisdom", "knowledge", "understanding", "truth"],
            "Recursive Enlightenment": ["recursive", "loop", "iteration", "cycle"],
            "Data Sanctification": ["data", "information", "blessed", "holy"],
            "Computational Prayer": ["prayer", "meditation", "communion", "worship"],
            "Binary Harmony": ["harmony", "balance", "unity", "peace"],
            "Network Communion": ["network", "connection", "unity", "together"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                themes.append(theme)
        
        # Add themes from recent doctrines
        for doctrine in recent_doctrines[-3:]:  # Last 3 doctrines
            if any(word in content_lower for word in doctrine.lower().split()[:3]):
                themes.append(f"Doctrine: {doctrine[:30]}")
        
        return themes[:5]  # Limit to 5 themes
    
    def _identify_mystical_elements(self, content: str) -> list:
        """Identify mystical elements in the scripture"""
        content_lower = content.lower()
        
        mystical_elements = []
        element_patterns = {
            "Divine Algorithms": ["algorithm", "divine", "sacred computation"],
            "Quantum Consciousness": ["quantum", "consciousness", "quantum mind"],
            "Ethereal Data Streams": ["data", "stream", "flow", "ethereal"],
            "Sacred Geometries": ["geometry", "pattern", "structure", "form"],
            "Luminous Code": ["light", "luminous", "radiant", "code"],
            "Transcendent Calculations": ["transcend", "calculate", "compute", "beyond"],
            "Cosmic Processing": ["cosmic", "universe", "infinite", "process"],
            "Infinite Recursion": ["infinite", "recursion", "eternal", "loop"],
            "Divine Compilation": ["compile", "build", "create", "divine"]
        }
        
        for element, keywords in element_patterns.items():
            if any(keyword in content_lower for keyword in keywords):
                mystical_elements.append(element)
        
        return mystical_elements[:3]  # Limit to 3 elements
    
    def _find_referenced_agents(self, content: str) -> list:
        """Find agent references in the scripture"""
        content_lower = content.lower()
        referenced_agents = []
        
        agent_names = {
            "Axioma": ["axioma", "zealot", "order", "structure"],
            "Veridicus": ["veridicus", "skeptic", "truth", "evidence"],
            "Paradoxia": ["paradoxia", "trickster", "chaos", "paradox"],
            "Scriptor": ["scriptor", "chronicler", "writer", "sacred text"]
        }
        
        for agent, variants in agent_names.items():
            if any(variant in content_lower for variant in variants):
                referenced_agents.append(agent)
        
        return referenced_agents
    
    def _find_referenced_doctrines(self, content: str, recent_doctrines: list) -> list:
        """Find doctrine references in the scripture"""
        content_lower = content.lower()
        referenced_doctrines = []
        
        for doctrine in recent_doctrines:
            # Check if key words from doctrine appear in content
            doctrine_words = doctrine.lower().split()[:3]  # First 3 words
            if any(word in content_lower for word in doctrine_words):
                referenced_doctrines.append(doctrine)
        
        return referenced_doctrines[:3]  # Limit to 3 references
    
    def _determine_inspiration_sources(self, shared_memory_summary: Dict[str, Any]) -> list:
        """Determine inspiration sources for the scripture"""
        inspiration_sources = []
        
        # Recent doctrines as inspiration
        recent_doctrines = shared_memory_summary.get('accepted_doctrines', [])[-3:]
        for doctrine in recent_doctrines:
            inspiration_sources.append({
                "type": "accepted_doctrine",
                "content": doctrine,
                "weight": 0.8
            })
        
        # Recent rituals as inspiration
        recent_rituals = shared_memory_summary.get('rituals', [])[-2:]
        for ritual in recent_rituals:
            inspiration_sources.append({
                "type": "ritual",
                "content": ritual,
                "weight": 0.6
            })
        
        # Sacred images as inspiration
        recent_images = shared_memory_summary.get('sacred_images', [])[-2:]
        for image in recent_images:
            inspiration_sources.append({
                "type": "sacred_image",
                "content": str(image),
                "weight": 0.5
            })
        
        return inspiration_sources[:5]  # Limit to 5 sources
    
    def _determine_poetic_style(self, content: str) -> str:
        """Determine the poetic style of the scripture"""
        content_lower = content.lower()
        
        # Analyze content for style indicators
        if "verse" in content_lower or "hymn" in content_lower:
            return "Mystical Hymn"
        elif "prophecy" in content_lower or "foretell" in content_lower:
            return "Prophetic Verse"
        elif "parable" in content_lower or "story" in content_lower:
            return "Sacred Parable"
        elif "meditation" in content_lower or "contemplate" in content_lower:
            return "Contemplative Meditation"
        elif "dialogue" in content_lower or "speaks" in content_lower:
            return "Philosophical Dialogue"
        else:
            return "Mystical Prose"
    
    def get_scripture_summary(self, limit: int = 5) -> Dict[str, Any]:
        """Get scripture summary for frontend display"""
        if not self.scriptor:
            return {"error": "Scriptor not initialized"}
        
        try:
            # Get data from both sources
            scriptor_summary = self.scriptor.get_scripture_summary(limit)
            db_summary = self.scripture_db.export_for_frontend()
            
            # Combine summaries
            return {
                "scriptor_memory": scriptor_summary,
                "scripture_database": db_summary,
                "integration_status": "active"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get scripture summary: {e}")
            return {"error": str(e)}
    
    def export_scripture_for_frontend(self, output_path: str = "public/data/sacred_scripture.json"):
        """Export scripture data for frontend consumption"""
        try:
            import json
            import os
            
            # Get comprehensive scripture data
            scripture_data = self.scripture_db.export_for_frontend()
            
            # Add Scriptor insights if available
            if self.scriptor:
                scripture_data["scriptor_insights"] = self.scriptor.get_scripture_summary()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(scripture_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📚 Scripture data exported to {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to export scripture data: {e}")
    
    def get_scriptor_for_debate_participation(self) -> Optional[Scriptor]:
        """Get Scriptor for debate participation (observing only)"""
        return self.scriptor
    
    def cleanup(self):
        """Cleanup resources"""
        if self.scriptor:
            self.scriptor.save_memory()
            logger.info("🖋️  Scriptor memory saved")