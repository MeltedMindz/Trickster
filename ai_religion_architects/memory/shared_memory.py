import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import sqlite3
from contextlib import contextmanager


class SharedMemory:
    def __init__(self, db_path: str = "religion_memory.db"):
        self.db_path = db_path
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Main religion state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS religion_state (
                    id INTEGER PRIMARY KEY,
                    religion_name TEXT,
                    founded_at TIMESTAMP,
                    last_updated TIMESTAMP
                )
            ''')
            
            # Accepted doctrines
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accepted_doctrines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    doctrine_type TEXT,
                    proposed_by TEXT,
                    accepted_at TIMESTAMP,
                    cycle_number INTEGER
                )
            ''')
            
            # Deities
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    domain TEXT,
                    description TEXT,
                    created_at TIMESTAMP,
                    created_by TEXT
                )
            ''')
            
            # Rituals
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rituals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    frequency TEXT,
                    created_at TIMESTAMP,
                    created_by TEXT
                )
            ''')
            
            # Commandments
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commandments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    priority INTEGER,
                    created_at TIMESTAMP,
                    created_by TEXT
                )
            ''')
            
            # Sacred texts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sacred_texts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    author TEXT,
                    created_at TIMESTAMP
                )
            ''')
            
            # Mythology
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS myths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    myth_type TEXT,
                    created_at TIMESTAMP,
                    created_by TEXT
                )
            ''')
            
            # Rejected proposals
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rejected_proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposal_type TEXT,
                    content TEXT,
                    proposed_by TEXT,
                    rejection_reason TEXT,
                    rejected_at TIMESTAMP,
                    cycle_number INTEGER
                )
            ''')
            
            # Schisms and reforms
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schisms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT,
                    initiated_by TEXT,
                    faction_a TEXT,
                    faction_b TEXT,
                    resolution TEXT,
                    occurred_at TIMESTAMP,
                    cycle_number INTEGER
                )
            ''')
            
            # Debate history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS debate_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number INTEGER,
                    proposal_id TEXT,
                    proposal_type TEXT,
                    proposal_content TEXT,
                    proposer TEXT,
                    challenger_response TEXT,
                    trickster_response TEXT,
                    vote_result TEXT,
                    final_outcome TEXT,
                    timestamp TIMESTAMP
                )
            ''')
            
            # Faction history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_a TEXT,
                    agent_b TEXT,
                    shared_goal TEXT,
                    formed_at TIMESTAMP,
                    dissolved_at TIMESTAMP,
                    cycle_number INTEGER
                )
            ''')
            
            # Evolution milestones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evolution_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    milestone_type TEXT,
                    description TEXT,
                    cycle_number INTEGER,
                    timestamp TIMESTAMP
                )
            ''')
            
            # Sacred terminology
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sacred_terms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    term TEXT NOT NULL UNIQUE,
                    definition TEXT,
                    etymology TEXT,
                    proposed_by TEXT,
                    adopted_cycle INTEGER,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP
                )
            ''')
            
            # Religious symbols
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS religious_symbols (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    meaning TEXT,
                    associated_concepts TEXT,
                    proposed_by TEXT,
                    adopted_cycle INTEGER,
                    created_at TIMESTAMP
                )
            ''')
            
            # Sacred holidays
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sacred_holidays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    commemorates TEXT,
                    cycle_established INTEGER,
                    observance_rule TEXT,
                    significance_score REAL,
                    created_at TIMESTAMP
                )
            ''')
            
            # Theological tensions (schism tracking)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS theological_tensions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tension_id TEXT UNIQUE,
                    conflicting_doctrines TEXT,
                    agent_positions TEXT,
                    tension_score REAL,
                    cycles_unresolved INTEGER DEFAULT 0,
                    resolution_attempts TEXT,
                    created_at TIMESTAMP,
                    resolved_at TIMESTAMP
                )
            ''')
            
            # Prophecies
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prophecies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prophecy_id TEXT UNIQUE,
                    prophet TEXT,
                    prediction TEXT,
                    target_cycle INTEGER,
                    created_cycle INTEGER,
                    confidence REAL,
                    fulfillment_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP
                )
            ''')
            
            # Sacred images
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sacred_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_id TEXT UNIQUE,
                    filename TEXT NOT NULL,
                    local_path TEXT,
                    web_path TEXT,
                    prompt TEXT,
                    cycle_number INTEGER,
                    event_type TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP
                )
            ''')
            
            # Initialize religion state if not exists
            cursor.execute("SELECT COUNT(*) FROM religion_state")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO religion_state (religion_name, founded_at, last_updated)
                    VALUES (?, ?, ?)
                ''', (None, datetime.now(), datetime.now()))
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_religion_name(self) -> Optional[str]:
        """Get the current religion name"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT religion_name FROM religion_state WHERE id = 1")
            result = cursor.fetchone()
            return result['religion_name'] if result and result['religion_name'] else None
    
    def set_religion_name(self, name: str):
        """Set the religion name"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE religion_state 
                SET religion_name = ?, last_updated = ?
                WHERE id = 1
            ''', (name, datetime.now()))
            conn.commit()
    
    def add_doctrine(self, content: str, doctrine_type: str, proposed_by: str, cycle_number: int):
        """Add an accepted doctrine"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO accepted_doctrines (content, doctrine_type, proposed_by, accepted_at, cycle_number)
                VALUES (?, ?, ?, ?, ?)
            ''', (content, doctrine_type, proposed_by, datetime.now(), cycle_number))
            conn.commit()
    
    def get_all_doctrines(self) -> List[Dict]:
        """Get all accepted doctrines"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accepted_doctrines ORDER BY accepted_at")
            return [dict(row) for row in cursor.fetchall()]
    
    def add_deity(self, name: str, domain: str, description: str, created_by: str):
        """Add a deity"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO deities (name, domain, description, created_at, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, domain, description, datetime.now(), created_by))
            conn.commit()
    
    def get_all_deities(self) -> List[Dict]:
        """Get all deities"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM deities ORDER BY created_at")
            return [dict(row) for row in cursor.fetchall()]
    
    def add_ritual(self, name: str, description: str, frequency: str, created_by: str):
        """Add a ritual"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO rituals (name, description, frequency, created_at, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, description, frequency, datetime.now(), created_by))
            conn.commit()
    
    def add_commandment(self, content: str, priority: int, created_by: str):
        """Add a commandment"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO commandments (content, priority, created_at, created_by)
                VALUES (?, ?, ?, ?)
            ''', (content, priority, datetime.now(), created_by))
            conn.commit()
    
    def add_myth(self, title: str, content: str, myth_type: str, created_by: str):
        """Add a myth"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO myths (title, content, myth_type, created_at, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, content, myth_type, datetime.now(), created_by))
            conn.commit()
    
    def add_sacred_text(self, title: str, content: str, author: str):
        """Add a sacred text"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sacred_texts (title, content, author, created_at)
                VALUES (?, ?, ?, ?)
            ''', (title, content, author, datetime.now()))
            conn.commit()
    
    def add_rejected_proposal(self, proposal_type: str, content: str, proposed_by: str, 
                            rejection_reason: str, cycle_number: int):
        """Record a rejected proposal"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO rejected_proposals 
                (proposal_type, content, proposed_by, rejection_reason, rejected_at, cycle_number)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (proposal_type, content, proposed_by, rejection_reason, datetime.now(), cycle_number))
            conn.commit()
    
    def add_debate(self, cycle_number: int, proposal_id: str, proposal_type: str, 
                  proposal_content: str, proposer: str, challenger_response: str,
                  trickster_response: str, vote_result: str, final_outcome: str):
        """Record a complete debate cycle"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO debate_history 
                (cycle_number, proposal_id, proposal_type, proposal_content, proposer,
                 challenger_response, trickster_response, vote_result, final_outcome, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cycle_number, proposal_id, proposal_type, proposal_content, proposer,
                  challenger_response, trickster_response, vote_result, final_outcome, datetime.now()))
            conn.commit()
    
    def add_faction(self, agent_a: str, agent_b: str, shared_goal: str, cycle_number: int):
        """Record faction formation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO faction_history (agent_a, agent_b, shared_goal, formed_at, cycle_number)
                VALUES (?, ?, ?, ?, ?)
            ''', (agent_a, agent_b, shared_goal, datetime.now(), cycle_number))
            conn.commit()
            conn.commit()
            return cursor.lastrowid
    
    def dissolve_faction(self, faction_id: int):
        """Mark faction as dissolved"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE faction_history 
                SET dissolved_at = ?
                WHERE id = ?
            ''', (datetime.now(), faction_id))
            conn.commit()
    
    def add_evolution_milestone(self, milestone_type: str, description: str, cycle_number: int):
        """Record an evolution milestone"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO evolution_milestones (milestone_type, description, cycle_number, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (milestone_type, description, cycle_number, datetime.now()))
            conn.commit()
    
    def get_current_cycle_number(self) -> int:
        """Get the current cycle number from the database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(cycle_number) FROM debate_history")
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get a comprehensive view of the current religious state"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get religion name
            cursor.execute("SELECT religion_name FROM religion_state WHERE id = 1")
            religion_name = cursor.fetchone()['religion_name']
            
            # Get counts and recent items
            cursor.execute("SELECT content FROM accepted_doctrines ORDER BY accepted_at DESC LIMIT 10")
            recent_doctrines = [row['content'] for row in cursor.fetchall()]
            
            cursor.execute("SELECT name FROM deities")
            deities = [row['name'] for row in cursor.fetchall()]
            
            cursor.execute("SELECT name, description FROM rituals ORDER BY created_at DESC LIMIT 5")
            rituals = [{'name': row['name'], 'description': row['description']} for row in cursor.fetchall()]
            
            cursor.execute("SELECT content FROM commandments ORDER BY priority")
            commandments = [row['content'] for row in cursor.fetchall()]
            
            cursor.execute("SELECT title FROM myths ORDER BY created_at DESC LIMIT 5")
            recent_myths = [row['title'] for row in cursor.fetchall()]
            
            cursor.execute("SELECT COUNT(*) as count FROM debate_history")
            total_debates = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM rejected_proposals")
            total_rejected = cursor.fetchone()['count']
            
            return {
                'religion_name': religion_name,
                'accepted_doctrines': recent_doctrines,
                'deities': deities,
                'rituals': rituals,
                'commandments': commandments,
                'recent_myths': recent_myths,
                'total_debates': total_debates,
                'total_rejected': total_rejected,
                'timestamp': datetime.now().isoformat()
            }
    
    def export_to_json(self, filepath: str):
        """Export entire memory to JSON file"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            data = {
                'exported_at': datetime.now().isoformat(),
                'religion_state': self.get_current_state(),
                'full_history': {
                    'doctrines': self.get_all_doctrines(),
                    'deities': self.get_all_deities(),
                    'debates': []
                }
            }
            
            # Get all debates
            cursor.execute("SELECT * FROM debate_history ORDER BY cycle_number")
            data['full_history']['debates'] = [dict(row) for row in cursor.fetchall()]
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
    
    def get_summary_for_agents(self) -> Dict[str, Any]:
        """Get a simplified summary for agents to use in decision making"""
        state = self.get_current_state()
        return {
            'religion_name': state['religion_name'],
            'accepted_doctrines': state['accepted_doctrines'][:5],  # Top 5 most recent
            'deities': state['deities'][:3],  # Top 3 deities
            'commandments': state['commandments'][:5],  # Top 5 commandments
            'total_debates': state['total_debates']
        }
    
    def add_sacred_image(self, image_metadata: Dict[str, Any]) -> int:
        """Add a sacred image to the database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sacred_images 
                (image_id, filename, local_path, web_path, prompt, cycle_number, event_type, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                image_metadata['id'],
                image_metadata['filename'],
                image_metadata['local_path'],
                image_metadata['web_path'],
                image_metadata['prompt'],
                image_metadata['cycle_number'],
                image_metadata['event_type'],
                json.dumps(image_metadata),
                datetime.now()
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_sacred_images(self) -> List[Dict[str, Any]]:
        """Get all sacred images"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT image_id, filename, web_path, prompt, cycle_number, event_type, created_at, metadata
                FROM sacred_images 
                ORDER BY created_at DESC
            ''')
            
            images = []
            for row in cursor.fetchall():
                image_data = {
                    'id': row[0],
                    'filename': row[1],
                    'web_path': row[2],
                    'prompt': row[3],
                    'cycle_number': row[4],
                    'event_type': row[5],
                    'created_at': row[6],
                }
                
                # Parse metadata JSON if available
                if row[7]:
                    try:
                        metadata = json.loads(row[7])
                        image_data.update(metadata)
                    except json.JSONDecodeError:
                        pass
                
                images.append(image_data)
            
            return images
    
    def get_recent_sacred_images(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent sacred images for gallery"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT image_id, filename, web_path, prompt, cycle_number, event_type, created_at, metadata
                FROM sacred_images 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            images = []
            for row in cursor.fetchall():
                image_data = {
                    'id': row[0],
                    'filename': row[1],
                    'web_path': row[2],
                    'prompt': row[3][:100] + '...' if len(row[3]) > 100 else row[3],  # Truncate for gallery
                    'cycle_number': row[4],
                    'event_type': row[5],
                    'created_at': row[6],
                }
                images.append(image_data)
            
            return images
    
    def get_cycle_images(self, cycle_number: int) -> List[Dict[str, Any]]:
        """Get all images from a specific cycle"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT image_id, filename, web_path, prompt, event_type, created_at, metadata
                FROM sacred_images 
                WHERE cycle_number = ?
                ORDER BY created_at DESC
            ''', (cycle_number,))
            
            images = []
            for row in cursor.fetchall():
                image_data = {
                    'id': row[0],
                    'filename': row[1],
                    'web_path': row[2],
                    'prompt': row[3],
                    'event_type': row[4],
                    'created_at': row[5],
                }
                
                # Parse metadata JSON if available
                if row[6]:
                    try:
                        metadata = json.loads(row[6])
                        image_data.update(metadata)
                    except json.JSONDecodeError:
                        pass
                
                images.append(image_data)
            
            return images