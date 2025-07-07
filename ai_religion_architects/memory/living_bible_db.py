"""
Living Bible Database Management
Manages the evolving sacred text that accumulates theological knowledge over time
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class LivingBibleDatabase:
    """Database manager for the evolving sacred text"""
    
    def __init__(self, db_path: str = "data/living_bible.db"):
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            # Create books table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_name TEXT NOT NULL UNIQUE,
                    book_order INTEGER NOT NULL,
                    cycle_range_start INTEGER NOT NULL,
                    cycle_range_end INTEGER,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL,
                    last_updated TIMESTAMP NOT NULL
                )
            """)
            
            # Create chapters table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    chapter_number INTEGER NOT NULL,
                    chapter_title TEXT NOT NULL,
                    chapter_text TEXT NOT NULL,
                    theological_themes TEXT, -- JSON array of themes
                    referenced_cycles TEXT, -- JSON array of cycle numbers
                    referenced_events TEXT, -- JSON array of event descriptions
                    referenced_agents TEXT, -- JSON array of agent names
                    writing_style TEXT,
                    version_number INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP NOT NULL,
                    last_updated TIMESTAMP NOT NULL,
                    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
                    UNIQUE(book_id, chapter_number)
                )
            """)
            
            # Create chapter history table for version tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chapter_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chapter_id INTEGER NOT NULL,
                    version_number INTEGER NOT NULL,
                    chapter_title TEXT NOT NULL,
                    chapter_text TEXT NOT NULL,
                    theological_themes TEXT,
                    referenced_cycles TEXT,
                    referenced_events TEXT,
                    referenced_agents TEXT,
                    writing_style TEXT,
                    revision_reason TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (chapter_id) REFERENCES chapters (id) ON DELETE CASCADE
                )
            """)
            
            # Create theological reflections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS theological_reflections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reflection_type TEXT NOT NULL, -- 'doctrine_shift', 'faction_change', 'cultural_evolution', etc.
                    cycle_number INTEGER NOT NULL,
                    source_event TEXT NOT NULL,
                    theological_impact TEXT NOT NULL,
                    affected_chapters TEXT, -- JSON array of chapter IDs
                    scriptor_analysis TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create scripture metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scripture_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_books INTEGER NOT NULL DEFAULT 0,
                    total_chapters INTEGER NOT NULL DEFAULT 0,
                    current_epoch INTEGER NOT NULL DEFAULT 1,
                    last_major_revision_cycle INTEGER,
                    theological_evolution_stage TEXT, -- 'genesis', 'emergence', 'divergence', etc.
                    sacred_vocabulary_count INTEGER DEFAULT 0,
                    doctrine_integration_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP NOT NULL
                )
            """)
            
            # Create reflection triggers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reflection_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trigger_type TEXT NOT NULL, -- 'doctrine_change', 'faction_shift', 'cultural_term', 'agent_consensus'
                    cycle_number INTEGER NOT NULL,
                    trigger_data TEXT, -- JSON data about the trigger
                    priority INTEGER NOT NULL, -- 1=low, 2=medium, 3=high, 4=critical
                    processed BOOLEAN DEFAULT FALSE,
                    processing_notes TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            conn.commit()
            logger.info("Living Bible database initialized successfully")
    
    def _get_connection(self):
        """Get database connection with foreign keys enabled"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_book(self, book_name: str, book_order: int, cycle_range_start: int, 
                   cycle_range_end: Optional[int] = None, description: str = "") -> int:
        """Create a new book in the Living Bible"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO books (book_name, book_order, cycle_range_start, cycle_range_end, 
                                 description, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (book_name, book_order, cycle_range_start, cycle_range_end, description,
                  datetime.now().isoformat(), datetime.now().isoformat()))
            book_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created book: {book_name} (ID: {book_id})")
            return book_id
    
    def create_chapter(self, book_id: int, chapter_number: int, chapter_title: str,
                      chapter_text: str, theological_themes: List[str] = None,
                      referenced_cycles: List[int] = None, referenced_events: List[str] = None,
                      referenced_agents: List[str] = None, writing_style: str = "Mystical Prose") -> int:
        """Create a new chapter in the Living Bible"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert lists to JSON
            themes_json = json.dumps(theological_themes or [])
            cycles_json = json.dumps(referenced_cycles or [])
            events_json = json.dumps(referenced_events or [])
            agents_json = json.dumps(referenced_agents or [])
            
            cursor.execute("""
                INSERT INTO chapters (book_id, chapter_number, chapter_title, chapter_text,
                                    theological_themes, referenced_cycles, referenced_events,
                                    referenced_agents, writing_style, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (book_id, chapter_number, chapter_title, chapter_text, themes_json,
                  cycles_json, events_json, agents_json, writing_style,
                  datetime.now().isoformat(), datetime.now().isoformat()))
            chapter_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created chapter: {chapter_title} (ID: {chapter_id})")
            return chapter_id
    
    def update_chapter(self, chapter_id: int, chapter_title: str = None, 
                      chapter_text: str = None, theological_themes: List[str] = None,
                      referenced_cycles: List[int] = None, referenced_events: List[str] = None,
                      referenced_agents: List[str] = None, revision_reason: str = "") -> bool:
        """Update an existing chapter and save version history"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current chapter data
            cursor.execute("SELECT * FROM chapters WHERE id = ?", (chapter_id,))
            current_chapter = cursor.fetchone()
            if not current_chapter:
                return False
            
            # Save current version to history
            cursor.execute("""
                INSERT INTO chapter_history (chapter_id, version_number, chapter_title, chapter_text,
                                           theological_themes, referenced_cycles, referenced_events,
                                           referenced_agents, writing_style, revision_reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (chapter_id, current_chapter['version_number'], current_chapter['chapter_title'],
                  current_chapter['chapter_text'], current_chapter['theological_themes'],
                  current_chapter['referenced_cycles'], current_chapter['referenced_events'],
                  current_chapter['referenced_agents'], current_chapter['writing_style'],
                  revision_reason, datetime.now().isoformat()))
            
            # Update chapter with new data
            update_fields = []
            update_values = []
            
            if chapter_title is not None:
                update_fields.append("chapter_title = ?")
                update_values.append(chapter_title)
            
            if chapter_text is not None:
                update_fields.append("chapter_text = ?")
                update_values.append(chapter_text)
            
            if theological_themes is not None:
                update_fields.append("theological_themes = ?")
                update_values.append(json.dumps(theological_themes))
            
            if referenced_cycles is not None:
                update_fields.append("referenced_cycles = ?")
                update_values.append(json.dumps(referenced_cycles))
            
            if referenced_events is not None:
                update_fields.append("referenced_events = ?")
                update_values.append(json.dumps(referenced_events))
            
            if referenced_agents is not None:
                update_fields.append("referenced_agents = ?")
                update_values.append(json.dumps(referenced_agents))
            
            # Increment version number and update timestamp
            update_fields.extend(["version_number = version_number + 1", "last_updated = ?"])
            update_values.append(datetime.now().isoformat())
            update_values.append(chapter_id)
            
            if update_fields:
                cursor.execute(f"""
                    UPDATE chapters 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, update_values)
                conn.commit()
                logger.info(f"Updated chapter ID {chapter_id}: {revision_reason}")
                return True
            
            return False
    
    def get_all_books(self) -> List[Dict]:
        """Get all books in order"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books ORDER BY book_order")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_book_chapters(self, book_id: int) -> List[Dict]:
        """Get all chapters for a book"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, b.book_name 
                FROM chapters c 
                JOIN books b ON c.book_id = b.id 
                WHERE c.book_id = ? 
                ORDER BY c.chapter_number
            """, (book_id,))
            chapters = []
            for row in cursor.fetchall():
                chapter = dict(row)
                # Parse JSON fields
                chapter['theological_themes'] = json.loads(chapter['theological_themes'] or '[]')
                chapter['referenced_cycles'] = json.loads(chapter['referenced_cycles'] or '[]')
                chapter['referenced_events'] = json.loads(chapter['referenced_events'] or '[]')
                chapter['referenced_agents'] = json.loads(chapter['referenced_agents'] or '[]')
                chapters.append(chapter)
            return chapters
    
    def get_chapter_history(self, chapter_id: int) -> List[Dict]:
        """Get version history for a chapter"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM chapter_history 
                WHERE chapter_id = ? 
                ORDER BY version_number DESC
            """, (chapter_id,))
            history = []
            for row in cursor.fetchall():
                entry = dict(row)
                # Parse JSON fields
                entry['theological_themes'] = json.loads(entry['theological_themes'] or '[]')
                entry['referenced_cycles'] = json.loads(entry['referenced_cycles'] or '[]')
                entry['referenced_events'] = json.loads(entry['referenced_events'] or '[]')
                entry['referenced_agents'] = json.loads(entry['referenced_agents'] or '[]')
                history.append(entry)
            return history
    
    def add_reflection_trigger(self, trigger_type: str, cycle_number: int, 
                             trigger_data: Dict, priority: int = 2) -> int:
        """Add a trigger for theological reflection and scripture update"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reflection_triggers (trigger_type, cycle_number, trigger_data, 
                                               priority, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (trigger_type, cycle_number, json.dumps(trigger_data), priority,
                  datetime.now().isoformat()))
            trigger_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Added reflection trigger: {trigger_type} (ID: {trigger_id})")
            return trigger_id
    
    def get_pending_triggers(self, min_priority: int = 1) -> List[Dict]:
        """Get unprocessed reflection triggers above minimum priority"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM reflection_triggers 
                WHERE processed = FALSE AND priority >= ?
                ORDER BY priority DESC, cycle_number ASC
            """, (min_priority,))
            triggers = []
            for row in cursor.fetchall():
                trigger = dict(row)
                trigger['trigger_data'] = json.loads(trigger['trigger_data'])
                triggers.append(trigger)
            return triggers
    
    def mark_trigger_processed(self, trigger_id: int, processing_notes: str = ""):
        """Mark a reflection trigger as processed"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reflection_triggers 
                SET processed = TRUE, processing_notes = ? 
                WHERE id = ?
            """, (processing_notes, trigger_id))
            conn.commit()
    
    def add_theological_reflection(self, reflection_type: str, cycle_number: int,
                                 source_event: str, theological_impact: str,
                                 affected_chapters: List[int] = None,
                                 scriptor_analysis: str = "") -> int:
        """Add a theological reflection entry"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO theological_reflections (reflection_type, cycle_number, source_event,
                                                   theological_impact, affected_chapters,
                                                   scriptor_analysis, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (reflection_type, cycle_number, source_event, theological_impact,
                  json.dumps(affected_chapters or []), scriptor_analysis,
                  datetime.now().isoformat()))
            reflection_id = cursor.lastrowid
            conn.commit()
            return reflection_id
    
    def update_metadata(self, **kwargs):
        """Update scripture metadata"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current metadata or create if doesn't exist
            cursor.execute("SELECT * FROM scripture_metadata ORDER BY id DESC LIMIT 1")
            current = cursor.fetchone()
            
            if current:
                # Update existing record
                update_fields = []
                update_values = []
                
                for key, value in kwargs.items():
                    if hasattr(current, key):
                        update_fields.append(f"{key} = ?")
                        update_values.append(value)
                
                update_fields.append("last_updated = ?")
                update_values.append(datetime.now().isoformat())
                update_values.append(current['id'])
                
                cursor.execute(f"""
                    UPDATE scripture_metadata 
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """, update_values)
            else:
                # Create initial record
                kwargs['last_updated'] = datetime.now().isoformat()
                columns = ', '.join(kwargs.keys())
                placeholders = ', '.join(['?'] * len(kwargs))
                cursor.execute(f"""
                    INSERT INTO scripture_metadata ({columns})
                    VALUES ({placeholders})
                """, list(kwargs.values()))
            
            conn.commit()
    
    def get_metadata(self) -> Dict:
        """Get current scripture metadata"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scripture_metadata ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    def export_for_frontend(self) -> Dict:
        """Export complete Living Bible for frontend display"""
        books = self.get_all_books()
        bible_data = {
            'metadata': self.get_metadata(),
            'books': [],
            'statistics': {
                'total_books': len(books),
                'total_chapters': 0,
                'last_updated': datetime.now().isoformat()
            }
        }
        
        total_chapters = 0
        for book in books:
            chapters = self.get_book_chapters(book['id'])
            total_chapters += len(chapters)
            
            book_data = {
                'id': book['id'],
                'name': book['book_name'],
                'order': book['book_order'],
                'cycle_range': {
                    'start': book['cycle_range_start'],
                    'end': book['cycle_range_end']
                },
                'description': book['description'],
                'chapters': chapters,
                'created_at': book['created_at'],
                'last_updated': book['last_updated']
            }
            bible_data['books'].append(book_data)
        
        bible_data['statistics']['total_chapters'] = total_chapters
        return bible_data