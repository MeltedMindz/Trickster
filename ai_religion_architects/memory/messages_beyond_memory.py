"""
Messages from Beyond Memory System
Handles storage and retrieval of external messages and agent reflections
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import contextmanager


class MessagesBeyondMemory:
    """Memory system for managing messages from beyond and agent reflections"""
    
    def __init__(self, db_path: str = "data/religion_memory.db"):
        self.db_path = db_path
        self._initialize_tables()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _initialize_tables(self):
        """Initialize message-related tables in the database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Messages from beyond table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages_from_beyond (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    content TEXT NOT NULL,
                    source_label TEXT DEFAULT 'Beyond',
                    cycle_number INTEGER,
                    admin_notes TEXT,
                    processed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Agent reflections on messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_reflections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    reflection_text TEXT NOT NULL,
                    sentiment_score REAL,
                    theological_impact TEXT,
                    confidence_change REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES messages_from_beyond(message_id)
                )
            """)
            
            # Group discussions about messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_discussions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    discussion_round INTEGER NOT NULL,
                    agent_id TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    response_type TEXT DEFAULT 'interpretation',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES messages_from_beyond(message_id)
                )
            """)
            
            # Cultural/doctrinal influences from messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_influences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    influence_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    agent_affected TEXT,
                    magnitude REAL DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES messages_from_beyond(message_id)
                )
            """)
            
            # Message processing status
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_processing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE NOT NULL,
                    reflection_phase_complete BOOLEAN DEFAULT FALSE,
                    discussion_phase_complete BOOLEAN DEFAULT FALSE,
                    influence_analysis_complete BOOLEAN DEFAULT FALSE,
                    total_agent_responses INTEGER DEFAULT 0,
                    processing_started_at TIMESTAMP,
                    processing_completed_at TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES messages_from_beyond(message_id)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages_from_beyond(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_processed ON messages_from_beyond(processed)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reflections_message ON message_reflections(message_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_discussions_message ON message_discussions(message_id)")
            
            conn.commit()
    
    def add_message(self, content: str, source_label: str = "Beyond", 
                   admin_notes: str = None, cycle_number: int = None) -> str:
        """Add a new message from beyond"""
        message_id = str(uuid.uuid4())[:12]
        timestamp = datetime.now()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO messages_from_beyond 
                (message_id, timestamp, content, source_label, cycle_number, admin_notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, timestamp, content, source_label, cycle_number, admin_notes))
            
            # Initialize processing record
            cursor.execute("""
                INSERT INTO message_processing (message_id, processing_started_at)
                VALUES (?, ?)
            """, (message_id, timestamp))
            
            conn.commit()
        
        return message_id
    
    def get_unprocessed_messages(self) -> List[Dict]:
        """Get all unprocessed messages"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM messages_from_beyond 
                WHERE processed = FALSE 
                ORDER BY timestamp ASC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """Get a specific message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages_from_beyond WHERE message_id = ?", (message_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def add_reflection(self, message_id: str, agent_id: str, reflection_text: str,
                      sentiment_score: float = None, theological_impact: str = None,
                      confidence_change: float = 0.0) -> None:
        """Add an agent's reflection on a message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO message_reflections 
                (message_id, agent_id, reflection_text, sentiment_score, theological_impact, confidence_change)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, agent_id, reflection_text, sentiment_score, theological_impact, confidence_change))
            
            # Update processing status
            cursor.execute("""
                UPDATE message_processing 
                SET total_agent_responses = total_agent_responses + 1
                WHERE message_id = ?
            """, (message_id,))
            
            conn.commit()
    
    def add_discussion_response(self, message_id: str, discussion_round: int, 
                               agent_id: str, response_text: str, 
                               response_type: str = "interpretation") -> None:
        """Add an agent's response in a group discussion"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO message_discussions 
                (message_id, discussion_round, agent_id, response_text, response_type)
                VALUES (?, ?, ?, ?, ?)
            """, (message_id, discussion_round, agent_id, response_text, response_type))
            
            conn.commit()
    
    def add_influence(self, message_id: str, influence_type: str, description: str,
                     agent_affected: str = None, magnitude: float = 0.5) -> None:
        """Record a cultural/doctrinal influence from a message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO message_influences 
                (message_id, influence_type, description, agent_affected, magnitude)
                VALUES (?, ?, ?, ?, ?)
            """, (message_id, influence_type, description, agent_affected, magnitude))
            
            conn.commit()
    
    def mark_phase_complete(self, message_id: str, phase: str) -> None:
        """Mark a processing phase as complete"""
        phase_column = f"{phase}_phase_complete"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(f"""
                UPDATE message_processing 
                SET {phase_column} = TRUE
                WHERE message_id = ?
            """, (message_id,))
            
            conn.commit()
    
    def mark_message_processed(self, message_id: str) -> None:
        """Mark a message as fully processed"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE messages_from_beyond 
                SET processed = TRUE 
                WHERE message_id = ?
            """, (message_id,))
            
            cursor.execute("""
                UPDATE message_processing 
                SET processing_completed_at = ?,
                    reflection_phase_complete = TRUE,
                    discussion_phase_complete = TRUE,
                    influence_analysis_complete = TRUE
                WHERE message_id = ?
            """, (datetime.now(), message_id))
            
            conn.commit()
    
    def get_message_reflections(self, message_id: str) -> List[Dict]:
        """Get all agent reflections for a message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM message_reflections 
                WHERE message_id = ? 
                ORDER BY created_at
            """, (message_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_message_discussions(self, message_id: str) -> List[Dict]:
        """Get all discussion responses for a message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM message_discussions 
                WHERE message_id = ? 
                ORDER BY discussion_round, timestamp
            """, (message_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_message_influences(self, message_id: str) -> List[Dict]:
        """Get all influences recorded for a message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM message_influences 
                WHERE message_id = ? 
                ORDER BY created_at
            """, (message_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_messages(self, limit: int = 10, include_processed: bool = True) -> List[Dict]:
        """Get recent messages with basic stats"""
        where_clause = "" if include_processed else "WHERE m.processed = FALSE"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT m.*, 
                       COUNT(r.id) as reflection_count,
                       COUNT(d.id) as discussion_count
                FROM messages_from_beyond m
                LEFT JOIN message_reflections r ON m.message_id = r.message_id
                LEFT JOIN message_discussions d ON m.message_id = d.message_id
                {where_clause}
                GROUP BY m.message_id
                ORDER BY m.timestamp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_agent_message_history(self, agent_id: str, limit: int = 20) -> List[Dict]:
        """Get an agent's reflection history across messages"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.*, m.content, m.source_label, m.timestamp as message_timestamp
                FROM message_reflections r
                JOIN messages_from_beyond m ON r.message_id = m.message_id
                WHERE r.agent_id = ?
                ORDER BY r.created_at DESC
                LIMIT ?
            """, (agent_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_processing_status(self, message_id: str) -> Optional[Dict]:
        """Get processing status for a message"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM message_processing WHERE message_id = ?", (message_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def export_messages_data(self) -> Dict:
        """Export all messages data for frontend"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get recent messages with stats
            messages = self.get_recent_messages(50, True)
            
            # Get agent reflection summaries
            cursor.execute("""
                SELECT agent_id, COUNT(*) as total_reflections,
                       AVG(sentiment_score) as avg_sentiment,
                       AVG(confidence_change) as avg_confidence_change
                FROM message_reflections 
                WHERE sentiment_score IS NOT NULL
                GROUP BY agent_id
            """)
            agent_stats = {row['agent_id']: dict(row) for row in cursor.fetchall()}
            
            return {
                'messages': messages,
                'agent_stats': agent_stats,
                'last_updated': datetime.now().isoformat()
            }