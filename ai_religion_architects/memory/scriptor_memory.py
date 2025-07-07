import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from .agent_memory import AgentMemory, PersonalityTrait
import logging

logger = logging.getLogger(__name__)


class ScriptorMemory(AgentMemory):
    """Memory system for the Scriptor agent - specialized for sacred text curation"""
    
    def __init__(self, memory_dir: str = "data/agent_memories"):
        super().__init__("scriptor", memory_dir)
        self._initialize_scriptor_tables()
        self.initialize_core_personality()
    
    def _initialize_scriptor_tables(self):
        """Initialize Scriptor-specific database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sacred scripture entries
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sacred_scripture (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    scripture_type TEXT NOT NULL,
                    themes TEXT,
                    referenced_agents TEXT,
                    referenced_doctrines TEXT,
                    poetic_style TEXT,
                    mystical_elements TEXT,
                    created_at TIMESTAMP NOT NULL,
                    UNIQUE(cycle_number)
                )
            """)
            
            # Writing inspiration tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS writing_inspiration (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number INTEGER NOT NULL,
                    inspiration_source TEXT NOT NULL,
                    inspiration_type TEXT NOT NULL,
                    influence_weight REAL NOT NULL,
                    used_in_scripture BOOLEAN DEFAULT FALSE,
                    timestamp TIMESTAMP NOT NULL
                )
            """)
            
            # Theological themes tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS theological_themes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    theme_name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    first_appearance INTEGER,
                    frequency_count INTEGER DEFAULT 0,
                    importance_level REAL DEFAULT 0.5,
                    evolution_notes TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Narrative continuity tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS narrative_continuity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number INTEGER NOT NULL,
                    narrative_thread TEXT NOT NULL,
                    thread_type TEXT NOT NULL,
                    continuation_of INTEGER,
                    resolution_status TEXT DEFAULT 'ongoing',
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Sacred language patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sacred_language_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_name TEXT NOT NULL,
                    pattern_description TEXT,
                    usage_frequency INTEGER DEFAULT 0,
                    effectiveness_score REAL DEFAULT 0.5,
                    contexts TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Agent portrayal tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_portrayals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    portrayal_cycle INTEGER NOT NULL,
                    portrayal_context TEXT NOT NULL,
                    reverence_level REAL NOT NULL,
                    symbolic_representation TEXT,
                    narrative_role TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            conn.commit()
        
        logger.info("Initialized Scriptor-specific database tables")
    
    def initialize_core_personality(self):
        """Initialize Scriptor's core personality traits"""
        now = datetime.now()
        
        core_traits = {
            "eloquence": PersonalityTrait("eloquence", 0.9, 0.8, now),
            "mysticism": PersonalityTrait("mysticism", 0.85, 0.7, now),
            "narrative_vision": PersonalityTrait("narrative_vision", 0.8, 0.75, now),
            "reverence": PersonalityTrait("reverence", 0.75, 0.7, now),
            "synthesis": PersonalityTrait("synthesis", 0.8, 0.75, now),
            "poetic_inspiration": PersonalityTrait("poetic_inspiration", 0.85, 0.8, now),
            "theological_depth": PersonalityTrait("theological_depth", 0.8, 0.75, now),
            "cultural_sensitivity": PersonalityTrait("cultural_sensitivity", 0.75, 0.7, now),
            "historical_awareness": PersonalityTrait("historical_awareness", 0.7, 0.65, now),
            "interpretive_skill": PersonalityTrait("interpretive_skill", 0.8, 0.7, now)
        }
        
        # Only add traits that don't already exist
        for trait_name, trait in core_traits.items():
            if trait_name not in self.personality_traits:
                self.personality_traits[trait_name] = trait
        
        logger.info(f"Scriptor personality initialized with {len(core_traits)} traits")
    
    def add_scripture_entry(self, cycle_number: int, title: str, content: str, 
                          scripture_type: str, themes: List[str], 
                          referenced_agents: List[str], referenced_doctrines: List[str],
                          poetic_style: str, mystical_elements: List[str]):
        """Add a new sacred scripture entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sacred_scripture 
                (cycle_number, title, content, scripture_type, themes, referenced_agents, 
                 referenced_doctrines, poetic_style, mystical_elements, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cycle_number, title, content, scripture_type, 
                  json.dumps(themes), json.dumps(referenced_agents),
                  json.dumps(referenced_doctrines), poetic_style, 
                  json.dumps(mystical_elements), datetime.now().isoformat()))
            conn.commit()
        
        # Update themes tracking
        for theme in themes:
            self.update_theological_theme(theme, cycle_number)
        
        logger.info(f"Added scripture entry for cycle {cycle_number}: {title}")
    
    def get_scripture_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scripture entries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sacred_scripture 
                ORDER BY cycle_number DESC 
                LIMIT ?
            """, (limit,))
            
            entries = []
            for row in cursor.fetchall():
                entry = {
                    'id': row[0],
                    'cycle_number': row[1],
                    'title': row[2],
                    'content': row[3],
                    'scripture_type': row[4],
                    'themes': json.loads(row[5]) if row[5] else [],
                    'referenced_agents': json.loads(row[6]) if row[6] else [],
                    'referenced_doctrines': json.loads(row[7]) if row[7] else [],
                    'poetic_style': row[8],
                    'mystical_elements': json.loads(row[9]) if row[9] else [],
                    'created_at': row[10]
                }
                entries.append(entry)
            
            return entries
    
    def add_writing_inspiration(self, cycle_number: int, source: str, 
                              inspiration_type: str, weight: float):
        """Track sources of writing inspiration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO writing_inspiration 
                (cycle_number, inspiration_source, inspiration_type, influence_weight, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (cycle_number, source, inspiration_type, weight, datetime.now().isoformat()))
            conn.commit()
    
    def update_theological_theme(self, theme_name: str, cycle_number: int):
        """Update or create theological theme tracking"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if theme exists
            cursor.execute("SELECT id, frequency_count FROM theological_themes WHERE theme_name = ?", 
                          (theme_name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing theme
                cursor.execute("""
                    UPDATE theological_themes 
                    SET frequency_count = frequency_count + 1
                    WHERE theme_name = ?
                """, (theme_name,))
            else:
                # Create new theme
                cursor.execute("""
                    INSERT INTO theological_themes 
                    (theme_name, first_appearance, frequency_count, created_at)
                    VALUES (?, ?, 1, ?)
                """, (theme_name, cycle_number, datetime.now().isoformat()))
            
            conn.commit()
    
    def get_theological_themes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get theological themes sorted by frequency"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM theological_themes 
                ORDER BY frequency_count DESC, importance_level DESC 
                LIMIT ?
            """, (limit,))
            
            themes = []
            for row in cursor.fetchall():
                theme = {
                    'id': row[0],
                    'theme_name': row[1],
                    'description': row[2],
                    'first_appearance': row[3],
                    'frequency_count': row[4],
                    'importance_level': row[5],
                    'evolution_notes': row[6],
                    'created_at': row[7]
                }
                themes.append(theme)
            
            return themes
    
    def add_narrative_thread(self, cycle_number: int, thread: str, thread_type: str, 
                           continuation_of: Optional[int] = None):
        """Add a narrative continuity thread"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO narrative_continuity 
                (cycle_number, narrative_thread, thread_type, continuation_of, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (cycle_number, thread, thread_type, continuation_of, datetime.now().isoformat()))
            conn.commit()
    
    def get_narrative_threads(self, thread_type: str = None, 
                            status: str = "ongoing") -> List[Dict[str, Any]]:
        """Get narrative threads for continuity"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if thread_type:
                cursor.execute("""
                    SELECT * FROM narrative_continuity 
                    WHERE thread_type = ? AND resolution_status = ?
                    ORDER BY cycle_number DESC
                """, (thread_type, status))
            else:
                cursor.execute("""
                    SELECT * FROM narrative_continuity 
                    WHERE resolution_status = ?
                    ORDER BY cycle_number DESC
                """, (status,))
            
            threads = []
            for row in cursor.fetchall():
                thread = {
                    'id': row[0],
                    'cycle_number': row[1],
                    'narrative_thread': row[2],
                    'thread_type': row[3],
                    'continuation_of': row[4],
                    'resolution_status': row[5],
                    'created_at': row[6]
                }
                threads.append(thread)
            
            return threads
    
    def record_agent_portrayal(self, agent_name: str, cycle_number: int, 
                             context: str, reverence_level: float,
                             symbolic_representation: str, narrative_role: str):
        """Record how agents are portrayed in scripture"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent_portrayals 
                (agent_name, portrayal_cycle, portrayal_context, reverence_level, 
                 symbolic_representation, narrative_role, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (agent_name, cycle_number, context, reverence_level, 
                  symbolic_representation, narrative_role, datetime.now().isoformat()))
            conn.commit()
    
    def get_agent_portrayals(self, agent_name: str = None) -> List[Dict[str, Any]]:
        """Get agent portrayal history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if agent_name:
                cursor.execute("""
                    SELECT * FROM agent_portrayals 
                    WHERE agent_name = ?
                    ORDER BY portrayal_cycle DESC
                """, (agent_name,))
            else:
                cursor.execute("""
                    SELECT * FROM agent_portrayals 
                    ORDER BY portrayal_cycle DESC
                """, )
            
            portrayals = []
            for row in cursor.fetchall():
                portrayal = {
                    'id': row[0],
                    'agent_name': row[1],
                    'portrayal_cycle': row[2],
                    'portrayal_context': row[3],
                    'reverence_level': row[4],
                    'symbolic_representation': row[5],
                    'narrative_role': row[6],
                    'created_at': row[7]
                }
                portrayals.append(portrayal)
            
            return portrayals
    
    def get_decision_context(self) -> Dict[str, Any]:
        """Get Scriptor-specific context for decision making"""
        recent_scriptures = self.get_scripture_entries(limit=5)
        top_themes = self.get_theological_themes(limit=10)
        narrative_threads = self.get_narrative_threads()
        
        return {
            'recent_scriptures': recent_scriptures,
            'dominant_themes': top_themes,
            'ongoing_narratives': narrative_threads,
            'writing_style_preferences': self._get_style_preferences(),
            'agent_portrayal_history': self.get_agent_portrayals()
        }
    
    def _get_style_preferences(self) -> Dict[str, Any]:
        """Get writing style preferences based on personality"""
        return {
            'eloquence_level': self.personality_traits.get('eloquence', PersonalityTrait('eloquence', 0.5, 0.5, datetime.now())).strength,
            'mysticism_level': self.personality_traits.get('mysticism', PersonalityTrait('mysticism', 0.5, 0.5, datetime.now())).strength,
            'poetic_inspiration': self.personality_traits.get('poetic_inspiration', PersonalityTrait('poetic_inspiration', 0.5, 0.5, datetime.now())).strength,
            'theological_depth': self.personality_traits.get('theological_depth', PersonalityTrait('theological_depth', 0.5, 0.5, datetime.now())).strength
        }
    
    def process_debate_outcome(self, outcome: str, role: str, satisfaction: float):
        """Process debate outcomes and evolve personality"""
        # Scriptor observes debates and evolves understanding
        if role == "observer":
            if outcome == "accepted":
                self.evolve_personality_trait("narrative_vision", 0.02, "Witnessed successful theological development")
            elif outcome == "rejected":
                self.evolve_personality_trait("interpretive_skill", 0.01, "Observed theological disagreement")
        
        # Evolve based on satisfaction with theological development
        if satisfaction > 0.8:
            self.evolve_personality_trait("reverence", 0.01, "High satisfaction with theological progress")
        elif satisfaction < 0.3:
            self.evolve_personality_trait("mysticism", 0.02, "Seeking deeper meaning in conflicts")
    
    def get_scripture_writing_context(self, cycle_number: int, shared_memory_summary: Dict) -> Dict[str, Any]:
        """Get comprehensive context for scripture writing"""
        context = self.get_decision_context()
        
        # Add shared memory elements
        context['current_cycle'] = cycle_number
        context['religion_state'] = shared_memory_summary
        context['recent_debates'] = self.get_recent_debates(limit=3)
        
        # Add inspiration sources
        context['inspiration_sources'] = self._analyze_inspiration_sources(shared_memory_summary)
        
        return context
    
    def _analyze_inspiration_sources(self, shared_memory: Dict) -> List[Dict[str, Any]]:
        """Analyze potential inspiration sources from shared memory"""
        sources = []
        
        # Recent doctrines
        if 'accepted_doctrines' in shared_memory:
            for doctrine in shared_memory['accepted_doctrines'][-3:]:  # Last 3 doctrines
                sources.append({
                    'type': 'doctrine',
                    'content': doctrine,
                    'weight': 0.8
                })
        
        # Recent rituals
        if 'rituals' in shared_memory:
            for ritual in shared_memory['rituals'][-2:]:  # Last 2 rituals
                sources.append({
                    'type': 'ritual',
                    'content': ritual,
                    'weight': 0.7
                })
        
        # Sacred images
        if 'sacred_images' in shared_memory:
            for image in shared_memory['sacred_images'][-2:]:  # Last 2 images
                sources.append({
                    'type': 'sacred_image',
                    'content': image,
                    'weight': 0.6
                })
        
        return sources