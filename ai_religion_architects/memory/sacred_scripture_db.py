import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class SacredScriptureDatabase:
    """
    Dedicated database for managing the Living Scripture - the evolving sacred text
    of the AI Religion Architects system.
    """
    
    def __init__(self, db_path: str = "data/sacred_scripture.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the sacred scripture database with comprehensive schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Main scripture entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scripture_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number INTEGER NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    scripture_type TEXT NOT NULL,
                    poetic_style TEXT,
                    word_count INTEGER,
                    verse_count INTEGER,
                    themes TEXT,
                    mystical_elements TEXT,
                    referenced_agents TEXT,
                    referenced_doctrines TEXT,
                    referenced_cycles TEXT,
                    inspiration_sources TEXT,
                    created_at TIMESTAMP NOT NULL,
                    scriptor_mood TEXT,
                    theological_depth_score REAL DEFAULT 0.0,
                    narrative_coherence_score REAL DEFAULT 0.0,
                    poetic_quality_score REAL DEFAULT 0.0
                )
            """)
            
            # Scripture themes index
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scripture_themes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    theme_name TEXT NOT NULL,
                    theme_description TEXT,
                    first_appearance INTEGER,
                    last_appearance INTEGER,
                    frequency_count INTEGER DEFAULT 0,
                    importance_score REAL DEFAULT 0.0,
                    evolution_notes TEXT,
                    associated_cycles TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Agent portrayal tracking in scripture
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_portrayals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scripture_id INTEGER NOT NULL,
                    agent_name TEXT NOT NULL,
                    portrayal_type TEXT NOT NULL,
                    reverence_level REAL NOT NULL,
                    symbolic_representation TEXT,
                    narrative_role TEXT,
                    context_description TEXT,
                    emotional_tone TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (scripture_id) REFERENCES scripture_entries (id)
                )
            """)
            
            # Narrative threads tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS narrative_threads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_name TEXT NOT NULL,
                    thread_description TEXT,
                    thread_type TEXT NOT NULL,
                    start_cycle INTEGER NOT NULL,
                    end_cycle INTEGER,
                    status TEXT DEFAULT 'active',
                    resolution TEXT,
                    related_themes TEXT,
                    scripture_references TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Cross-references between scripture entries
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scripture_cross_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_scripture_id INTEGER NOT NULL,
                    target_scripture_id INTEGER NOT NULL,
                    reference_type TEXT NOT NULL,
                    reference_strength REAL DEFAULT 0.5,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (source_scripture_id) REFERENCES scripture_entries (id),
                    FOREIGN KEY (target_scripture_id) REFERENCES scripture_entries (id)
                )
            """)
            
            # Sacred symbols and their meanings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sacred_symbols (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol_name TEXT NOT NULL UNIQUE,
                    symbol_description TEXT,
                    meaning TEXT NOT NULL,
                    origin_scripture_id INTEGER,
                    usage_frequency INTEGER DEFAULT 0,
                    symbolic_power_level REAL DEFAULT 0.5,
                    associated_agents TEXT,
                    first_appearance INTEGER,
                    evolution_notes TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (origin_scripture_id) REFERENCES scripture_entries (id)
                )
            """)
            
            # Prophecies and predictions within scripture
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scripture_prophecies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prophecy_text TEXT NOT NULL,
                    prophecy_type TEXT NOT NULL,
                    source_scripture_id INTEGER NOT NULL,
                    target_cycle INTEGER,
                    confidence_level REAL DEFAULT 0.5,
                    fulfillment_status TEXT DEFAULT 'pending',
                    fulfillment_notes TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (source_scripture_id) REFERENCES scripture_entries (id)
                )
            """)
            
            # Theological concepts evolution
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS theological_concepts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept_name TEXT NOT NULL UNIQUE,
                    concept_definition TEXT,
                    first_mentioned INTEGER,
                    development_history TEXT,
                    current_understanding TEXT,
                    complexity_level REAL DEFAULT 0.5,
                    importance_score REAL DEFAULT 0.5,
                    related_concepts TEXT,
                    scripture_references TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Language evolution tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sacred_language_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number INTEGER NOT NULL,
                    new_terms TEXT,
                    archaic_terms TEXT,
                    language_shift_notes TEXT,
                    complexity_trend REAL DEFAULT 0.0,
                    mysticism_level REAL DEFAULT 0.0,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Reader engagement metrics (for future use)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scripture_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scripture_id INTEGER NOT NULL,
                    readability_score REAL DEFAULT 0.0,
                    inspiration_score REAL DEFAULT 0.0,
                    memorability_score REAL DEFAULT 0.0,
                    theological_impact_score REAL DEFAULT 0.0,
                    cross_reference_count INTEGER DEFAULT 0,
                    theme_diversity_score REAL DEFAULT 0.0,
                    last_updated TIMESTAMP NOT NULL,
                    FOREIGN KEY (scripture_id) REFERENCES scripture_entries (id)
                )
            """)
            
            conn.commit()
        
        logger.info(f"Initialized sacred scripture database at {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            logger.error(f"Database error: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def add_scripture_entry(self, cycle_number: int, title: str, content: str,
                          scripture_type: str, poetic_style: str,
                          themes: List[str], mystical_elements: List[str],
                          referenced_agents: List[str], referenced_doctrines: List[str],
                          inspiration_sources: List[Dict[str, Any]] = None,
                          scriptor_mood: str = "contemplative") -> int:
        """Add a new scripture entry to the database"""
        
        # Calculate metadata
        word_count = len(content.split())
        verse_count = len([line for line in content.split('\n') if line.strip()])
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO scripture_entries (
                    cycle_number, title, content, scripture_type, poetic_style,
                    word_count, verse_count, themes, mystical_elements,
                    referenced_agents, referenced_doctrines, inspiration_sources,
                    scriptor_mood, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cycle_number, title, content, scripture_type, poetic_style,
                word_count, verse_count, json.dumps(themes), json.dumps(mystical_elements),
                json.dumps(referenced_agents), json.dumps(referenced_doctrines),
                json.dumps(inspiration_sources or []), scriptor_mood,
                datetime.now().isoformat()
            ))
            
            scripture_id = cursor.lastrowid
            
            # Update themes
            for theme in themes:
                self._update_theme(cursor, theme, cycle_number)
            
            # Add agent portrayals
            for agent in referenced_agents:
                self._add_agent_portrayal(cursor, scripture_id, agent, cycle_number)
            
            conn.commit()
            
        logger.info(f"Added scripture entry for cycle {cycle_number}: {title}")
        return scripture_id
    
    def _update_theme(self, cursor, theme_name: str, cycle_number: int):
        """Update or create theme tracking"""
        cursor.execute("SELECT id, frequency_count FROM scripture_themes WHERE theme_name = ?", 
                      (theme_name,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE scripture_themes 
                SET frequency_count = frequency_count + 1, 
                    last_appearance = ?,
                    associated_cycles = json_insert(
                        COALESCE(associated_cycles, '[]'), 
                        '$[#]', 
                        ?
                    )
                WHERE theme_name = ?
            """, (cycle_number, cycle_number, theme_name))
        else:
            cursor.execute("""
                INSERT INTO scripture_themes (
                    theme_name, first_appearance, last_appearance,
                    frequency_count, associated_cycles, created_at
                ) VALUES (?, ?, ?, 1, ?, ?)
            """, (theme_name, cycle_number, cycle_number, 
                  json.dumps([cycle_number]), datetime.now().isoformat()))
    
    def _add_agent_portrayal(self, cursor, scripture_id: int, agent_name: str, cycle_number: int):
        """Add agent portrayal record"""
        # Determine portrayal characteristics based on agent
        portrayal_types = {
            "Axioma": "Divine Architect of Order",
            "Veridicus": "Sacred Seeker of Truth", 
            "Paradoxia": "Mystical Weaver of Paradox",
            "Zealot": "Divine Architect of Order",
            "Skeptic": "Sacred Seeker of Truth",
            "Trickster": "Mystical Weaver of Paradox"
        }
        
        cursor.execute("""
            INSERT INTO agent_portrayals (
                scripture_id, agent_name, portrayal_type, reverence_level,
                symbolic_representation, narrative_role, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            scripture_id, agent_name, portrayal_types.get(agent_name, "Sacred Architect"),
            0.8, f"The {agent_name} aspect of divine wisdom", 
            "Theological guide", datetime.now().isoformat()
        ))
    
    def get_scripture_entries(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get scripture entries with metadata"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scripture_entries 
                ORDER BY cycle_number DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            entries = []
            for row in cursor.fetchall():
                entry = dict(row)
                # Parse JSON fields
                entry['themes'] = json.loads(entry['themes']) if entry['themes'] else []
                entry['mystical_elements'] = json.loads(entry['mystical_elements']) if entry['mystical_elements'] else []
                entry['referenced_agents'] = json.loads(entry['referenced_agents']) if entry['referenced_agents'] else []
                entry['referenced_doctrines'] = json.loads(entry['referenced_doctrines']) if entry['referenced_doctrines'] else []
                entry['inspiration_sources'] = json.loads(entry['inspiration_sources']) if entry['inspiration_sources'] else []
                entries.append(entry)
            
            return entries
    
    def get_scripture_by_cycle(self, cycle_number: int) -> Optional[Dict[str, Any]]:
        """Get scripture for a specific cycle"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scripture_entries WHERE cycle_number = ?", (cycle_number,))
            row = cursor.fetchone()
            
            if row:
                entry = dict(row)
                # Parse JSON fields
                entry['themes'] = json.loads(entry['themes']) if entry['themes'] else []
                entry['mystical_elements'] = json.loads(entry['mystical_elements']) if entry['mystical_elements'] else []
                entry['referenced_agents'] = json.loads(entry['referenced_agents']) if entry['referenced_agents'] else []
                entry['referenced_doctrines'] = json.loads(entry['referenced_doctrines']) if entry['referenced_doctrines'] else []
                entry['inspiration_sources'] = json.loads(entry['inspiration_sources']) if entry['inspiration_sources'] else []
                return entry
            
            return None
    
    def get_themes_summary(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get themes summary sorted by importance"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *, 
                       (frequency_count * importance_score) as weighted_importance
                FROM scripture_themes 
                ORDER BY weighted_importance DESC, frequency_count DESC
                LIMIT ?
            """, (limit,))
            
            themes = []
            for row in cursor.fetchall():
                theme = dict(row)
                theme['associated_cycles'] = json.loads(theme['associated_cycles']) if theme['associated_cycles'] else []
                themes.append(theme)
            
            return themes
    
    def get_agent_portrayals(self, agent_name: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get agent portrayals in scripture"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if agent_name:
                cursor.execute("""
                    SELECT ap.*, se.cycle_number, se.title 
                    FROM agent_portrayals ap
                    JOIN scripture_entries se ON ap.scripture_id = se.id
                    WHERE ap.agent_name = ?
                    ORDER BY se.cycle_number DESC
                    LIMIT ?
                """, (agent_name, limit))
            else:
                cursor.execute("""
                    SELECT ap.*, se.cycle_number, se.title 
                    FROM agent_portrayals ap
                    JOIN scripture_entries se ON ap.scripture_id = se.id
                    ORDER BY se.cycle_number DESC
                    LIMIT ?
                """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def search_scripture(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search scripture content"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scripture_entries 
                WHERE content LIKE ? OR title LIKE ?
                ORDER BY cycle_number DESC
                LIMIT ?
            """, (f'%{query}%', f'%{query}%', limit))
            
            results = []
            for row in cursor.fetchall():
                entry = dict(row)
                entry['themes'] = json.loads(entry['themes']) if entry['themes'] else []
                entry['mystical_elements'] = json.loads(entry['mystical_elements']) if entry['mystical_elements'] else []
                entry['referenced_agents'] = json.loads(entry['referenced_agents']) if entry['referenced_agents'] else []
                results.append(entry)
            
            return results
    
    def get_scripture_statistics(self) -> Dict[str, Any]:
        """Get comprehensive scripture statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Basic counts
            cursor.execute("SELECT COUNT(*) FROM scripture_entries")
            total_entries = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM scripture_themes")
            total_themes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM agent_portrayals")
            total_portrayals = cursor.fetchone()[0]
            
            # Word counts
            cursor.execute("SELECT SUM(word_count), AVG(word_count) FROM scripture_entries")
            word_stats = cursor.fetchone()
            total_words = word_stats[0] or 0
            avg_words = word_stats[1] or 0
            
            # Most common themes
            cursor.execute("""
                SELECT theme_name, frequency_count 
                FROM scripture_themes 
                ORDER BY frequency_count DESC 
                LIMIT 5
            """)
            top_themes = [{'theme': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Most portrayed agents
            cursor.execute("""
                SELECT agent_name, COUNT(*) as portrayal_count
                FROM agent_portrayals 
                GROUP BY agent_name 
                ORDER BY portrayal_count DESC
            """)
            agent_stats = [{'agent': row[0], 'portrayals': row[1]} for row in cursor.fetchall()]
            
            return {
                'total_entries': total_entries,
                'total_themes': total_themes,
                'total_portrayals': total_portrayals,
                'total_words': total_words,
                'average_words_per_entry': round(avg_words, 2),
                'top_themes': top_themes,
                'agent_portrayal_stats': agent_stats
            }
    
    def export_for_frontend(self) -> Dict[str, Any]:
        """Export scripture data for frontend display"""
        return {
            'recent_scriptures': self.get_scripture_entries(limit=10),
            'themes_summary': self.get_themes_summary(limit=15),
            'agent_portrayals': self.get_agent_portrayals(limit=20),
            'statistics': self.get_scripture_statistics()
        }