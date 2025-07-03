import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

@dataclass
class PersonalityTrait:
    """Represents a dynamic personality trait that can evolve"""
    name: str
    strength: float  # 0.0 to 1.0
    confidence: float  # How certain the agent is about this trait
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'strength': self.strength,
            'confidence': self.confidence,
            'last_updated': self.last_updated.isoformat()
        }

@dataclass
class PersonalBelief:
    """Represents an individual belief with confidence and evolution tracking"""
    content: str
    belief_type: str  # 'doctrine', 'ritual', 'theological_position', etc.
    confidence_level: float  # 0.0 to 1.0
    importance: float  # How important this belief is to the agent
    source: str  # Where this belief came from
    created_at: datetime
    last_reinforced: datetime
    times_challenged: int
    times_defended: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'belief_type': self.belief_type,
            'confidence_level': self.confidence_level,
            'importance': self.importance,
            'source': self.source,
            'created_at': self.created_at.isoformat(),
            'last_reinforced': self.last_reinforced.isoformat(),
            'times_challenged': self.times_challenged,
            'times_defended': self.times_defended
        }

@dataclass
class RelationshipMemory:
    """Tracks relationships with other agents"""
    target_agent: str
    trust_score: float  # -1.0 to 1.0
    agreement_rate: float  # 0.0 to 1.0
    total_interactions: int
    successful_alliances: int
    betrayals: int
    shared_beliefs: List[str]
    conflicts: List[str]
    last_interaction: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'target_agent': self.target_agent,
            'trust_score': self.trust_score,
            'agreement_rate': self.agreement_rate,
            'total_interactions': self.total_interactions,
            'successful_alliances': self.successful_alliances,
            'betrayals': self.betrayals,
            'shared_beliefs': self.shared_beliefs,
            'conflicts': self.conflicts,
            'last_interaction': self.last_interaction.isoformat()
        }

@dataclass
class DebateMemory:
    """Stores memory of specific debates and their outcomes"""
    cycle_number: int
    proposal_content: str
    agent_role: str  # 'proposer', 'challenger', 'voter'
    agent_response: str
    outcome: str  # 'accepted', 'rejected', 'modified'
    other_participants: List[str]
    personal_satisfaction: float  # How satisfied the agent was with the outcome
    lessons_learned: List[str]
    emotional_impact: float  # How emotionally significant this was
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'cycle_number': self.cycle_number,
            'proposal_content': self.proposal_content,
            'agent_role': self.agent_role,
            'agent_response': self.agent_response,
            'outcome': self.outcome,
            'other_participants': self.other_participants,
            'personal_satisfaction': self.personal_satisfaction,
            'lessons_learned': self.lessons_learned,
            'emotional_impact': self.emotional_impact,
            'timestamp': self.timestamp.isoformat()
        }

class AgentMemory(ABC):
    """Base class for individual agent memory management"""
    
    def __init__(self, agent_name: str, memory_dir: str = "data/agent_memories"):
        self.agent_name = agent_name
        self.memory_dir = memory_dir
        self.db_path = os.path.join(memory_dir, f"{agent_name.lower()}_memory.db")
        
        # In-memory caches for frequently accessed data
        self.personality_traits: Dict[str, PersonalityTrait] = {}
        self.personal_beliefs: List[PersonalBelief] = []
        self.relationships: Dict[str, RelationshipMemory] = {}
        self.recent_debates: List[DebateMemory] = []
        
        # Statistics
        self.total_proposals: int = 0
        self.successful_proposals: int = 0
        self.total_challenges: int = 0
        self.successful_challenges: int = 0
        self.total_votes: int = 0
        self.evolution_points: int = 0
        
        self._initialize_database()
        self._load_from_database()
    
    def _initialize_database(self):
        """Initialize the agent's personal database"""
        os.makedirs(self.memory_dir, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Personality traits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personality_traits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    strength REAL NOT NULL,
                    confidence REAL NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            
            # Personal beliefs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personal_beliefs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    belief_type TEXT NOT NULL,
                    confidence_level REAL NOT NULL,
                    importance REAL NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_reinforced TEXT NOT NULL,
                    times_challenged INTEGER DEFAULT 0,
                    times_defended INTEGER DEFAULT 0
                )
            """)
            
            # Relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_agent TEXT UNIQUE NOT NULL,
                    trust_score REAL NOT NULL,
                    agreement_rate REAL NOT NULL,
                    total_interactions INTEGER DEFAULT 0,
                    successful_alliances INTEGER DEFAULT 0,
                    betrayals INTEGER DEFAULT 0,
                    shared_beliefs TEXT DEFAULT '[]',
                    conflicts TEXT DEFAULT '[]',
                    last_interaction TEXT NOT NULL
                )
            """)
            
            # Debate memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS debate_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number INTEGER NOT NULL,
                    proposal_content TEXT NOT NULL,
                    agent_role TEXT NOT NULL,
                    agent_response TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    other_participants TEXT NOT NULL,
                    personal_satisfaction REAL NOT NULL,
                    lessons_learned TEXT NOT NULL,
                    emotional_impact REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # Agent statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_stats (
                    id INTEGER PRIMARY KEY,
                    total_proposals INTEGER DEFAULT 0,
                    successful_proposals INTEGER DEFAULT 0,
                    total_challenges INTEGER DEFAULT 0,
                    successful_challenges INTEGER DEFAULT 0,
                    total_votes INTEGER DEFAULT 0,
                    evolution_points INTEGER DEFAULT 0,
                    last_updated TEXT NOT NULL
                )
            """)
            
            conn.commit()
        
        logger.info(f"Initialized database for {self.agent_name}")
    
    def _load_from_database(self):
        """Load agent memory from database into in-memory structures"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Load personality traits
            cursor.execute("SELECT name, strength, confidence, last_updated FROM personality_traits")
            for row in cursor.fetchall():
                name, strength, confidence, last_updated = row
                self.personality_traits[name] = PersonalityTrait(
                    name=name,
                    strength=strength,
                    confidence=confidence,
                    last_updated=datetime.fromisoformat(last_updated)
                )
            
            # Load personal beliefs
            cursor.execute("""
                SELECT content, belief_type, confidence_level, importance, source, 
                       created_at, last_reinforced, times_challenged, times_defended
                FROM personal_beliefs ORDER BY importance DESC
            """)
            self.personal_beliefs = []
            for row in cursor.fetchall():
                content, belief_type, confidence_level, importance, source, created_at, last_reinforced, times_challenged, times_defended = row
                self.personal_beliefs.append(PersonalBelief(
                    content=content,
                    belief_type=belief_type,
                    confidence_level=confidence_level,
                    importance=importance,
                    source=source,
                    created_at=datetime.fromisoformat(created_at),
                    last_reinforced=datetime.fromisoformat(last_reinforced),
                    times_challenged=times_challenged,
                    times_defended=times_defended
                ))
            
            # Load relationships
            cursor.execute("""
                SELECT target_agent, trust_score, agreement_rate, total_interactions,
                       successful_alliances, betrayals, shared_beliefs, conflicts, last_interaction
                FROM relationships
            """)
            self.relationships = {}
            for row in cursor.fetchall():
                target_agent, trust_score, agreement_rate, total_interactions, successful_alliances, betrayals, shared_beliefs, conflicts, last_interaction = row
                self.relationships[target_agent] = RelationshipMemory(
                    target_agent=target_agent,
                    trust_score=trust_score,
                    agreement_rate=agreement_rate,
                    total_interactions=total_interactions,
                    successful_alliances=successful_alliances,
                    betrayals=betrayals,
                    shared_beliefs=json.loads(shared_beliefs),
                    conflicts=json.loads(conflicts),
                    last_interaction=datetime.fromisoformat(last_interaction)
                )
            
            # Load recent debates (last 10)
            cursor.execute("""
                SELECT cycle_number, proposal_content, agent_role, agent_response, outcome,
                       other_participants, personal_satisfaction, lessons_learned, emotional_impact, timestamp
                FROM debate_memories ORDER BY timestamp DESC LIMIT 10
            """)
            self.recent_debates = []
            for row in cursor.fetchall():
                cycle_number, proposal_content, agent_role, agent_response, outcome, other_participants, personal_satisfaction, lessons_learned, emotional_impact, timestamp = row
                self.recent_debates.append(DebateMemory(
                    cycle_number=cycle_number,
                    proposal_content=proposal_content,
                    agent_role=agent_role,
                    agent_response=agent_response,
                    outcome=outcome,
                    other_participants=json.loads(other_participants),
                    personal_satisfaction=personal_satisfaction,
                    lessons_learned=json.loads(lessons_learned),
                    emotional_impact=emotional_impact,
                    timestamp=datetime.fromisoformat(timestamp)
                ))
            
            # Load statistics
            cursor.execute("SELECT * FROM agent_stats WHERE id = 1")
            stats = cursor.fetchone()
            if stats:
                _, self.total_proposals, self.successful_proposals, self.total_challenges, self.successful_challenges, self.total_votes, self.evolution_points, _ = stats
    
    def save_to_database(self):
        """Save current in-memory state to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Save personality traits
            cursor.execute("DELETE FROM personality_traits")
            for trait in self.personality_traits.values():
                cursor.execute("""
                    INSERT INTO personality_traits (name, strength, confidence, last_updated)
                    VALUES (?, ?, ?, ?)
                """, (trait.name, trait.strength, trait.confidence, trait.last_updated.isoformat()))
            
            # Save personal beliefs
            cursor.execute("DELETE FROM personal_beliefs")
            for belief in self.personal_beliefs:
                cursor.execute("""
                    INSERT INTO personal_beliefs (content, belief_type, confidence_level, importance, source, created_at, last_reinforced, times_challenged, times_defended)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (belief.content, belief.belief_type, belief.confidence_level, belief.importance, belief.source, 
                      belief.created_at.isoformat(), belief.last_reinforced.isoformat(), 
                      belief.times_challenged, belief.times_defended))
            
            # Save relationships
            cursor.execute("DELETE FROM relationships")
            for relationship in self.relationships.values():
                cursor.execute("""
                    INSERT INTO relationships (target_agent, trust_score, agreement_rate, total_interactions, successful_alliances, betrayals, shared_beliefs, conflicts, last_interaction)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (relationship.target_agent, relationship.trust_score, relationship.agreement_rate, 
                      relationship.total_interactions, relationship.successful_alliances, relationship.betrayals,
                      json.dumps(relationship.shared_beliefs), json.dumps(relationship.conflicts), 
                      relationship.last_interaction.isoformat()))
            
            # Save statistics
            cursor.execute("DELETE FROM agent_stats")
            cursor.execute("""
                INSERT INTO agent_stats (id, total_proposals, successful_proposals, total_challenges, successful_challenges, total_votes, evolution_points, last_updated)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            """, (self.total_proposals, self.successful_proposals, self.total_challenges, 
                  self.successful_challenges, self.total_votes, self.evolution_points, 
                  datetime.now().isoformat()))
            
            conn.commit()
        
        logger.info(f"Saved memory state for {self.agent_name}")
    
    def evolve_personality_trait(self, trait_name: str, delta: float, reason: str = ""):
        """Evolve a personality trait based on experience"""
        if trait_name in self.personality_traits:
            trait = self.personality_traits[trait_name]
            old_strength = trait.strength
            trait.strength = max(0.0, min(1.0, trait.strength + delta))
            trait.last_updated = datetime.now()
            
            if abs(delta) > 0.1:  # Significant change
                trait.confidence = min(1.0, trait.confidence + 0.1)
            
            logger.info(f"{self.agent_name}: {trait_name} evolved from {old_strength:.2f} to {trait.strength:.2f} ({reason})")
            self.evolution_points += 1
    
    def add_personal_belief(self, content: str, belief_type: str, importance: float, source: str):
        """Add a new personal belief"""
        belief = PersonalBelief(
            content=content,
            belief_type=belief_type,
            confidence_level=0.7,  # Start with moderate confidence
            importance=importance,
            source=source,
            created_at=datetime.now(),
            last_reinforced=datetime.now(),
            times_challenged=0,
            times_defended=0
        )
        self.personal_beliefs.append(belief)
        # Keep only top 20 beliefs by importance
        self.personal_beliefs.sort(key=lambda x: x.importance, reverse=True)
        self.personal_beliefs = self.personal_beliefs[:20]
        
        logger.info(f"{self.agent_name}: Added new belief: {content[:50]}...")
    
    def update_relationship(self, target_agent: str, interaction_type: str, outcome: str):
        """Update relationship memory based on interaction"""
        if target_agent not in self.relationships:
            self.relationships[target_agent] = RelationshipMemory(
                target_agent=target_agent,
                trust_score=0.0,
                agreement_rate=0.5,
                total_interactions=0,
                successful_alliances=0,
                betrayals=0,
                shared_beliefs=[],
                conflicts=[],
                last_interaction=datetime.now()
            )
        
        relationship = self.relationships[target_agent]
        relationship.total_interactions += 1
        relationship.last_interaction = datetime.now()
        
        # Update trust and agreement based on interaction
        if interaction_type == "alliance" and outcome == "success":
            relationship.successful_alliances += 1
            relationship.trust_score = min(1.0, relationship.trust_score + 0.1)
        elif interaction_type == "betrayal":
            relationship.betrayals += 1
            relationship.trust_score = max(-1.0, relationship.trust_score - 0.3)
        elif interaction_type == "agreement":
            relationship.agreement_rate = (relationship.agreement_rate * (relationship.total_interactions - 1) + 1.0) / relationship.total_interactions
        elif interaction_type == "disagreement":
            relationship.agreement_rate = (relationship.agreement_rate * (relationship.total_interactions - 1) + 0.0) / relationship.total_interactions
        
        logger.info(f"{self.agent_name}: Updated relationship with {target_agent} - trust: {relationship.trust_score:.2f}")
    
    def add_debate_memory(self, cycle_number: int, proposal_content: str, agent_role: str, 
                         agent_response: str, outcome: str, other_participants: List[str], 
                         personal_satisfaction: float, lessons_learned: List[str], 
                         emotional_impact: float):
        """Add a new debate memory"""
        debate_memory = DebateMemory(
            cycle_number=cycle_number,
            proposal_content=proposal_content,
            agent_role=agent_role,
            agent_response=agent_response,
            outcome=outcome,
            other_participants=other_participants,
            personal_satisfaction=personal_satisfaction,
            lessons_learned=lessons_learned,
            emotional_impact=emotional_impact,
            timestamp=datetime.now()
        )
        
        self.recent_debates.insert(0, debate_memory)  # Add to beginning
        self.recent_debates = self.recent_debates[:10]  # Keep only last 10
        
        # Update statistics
        if agent_role == "proposer":
            self.total_proposals += 1
            if outcome == "accepted":
                self.successful_proposals += 1
        elif agent_role == "challenger":
            self.total_challenges += 1
            if outcome == "rejected":
                self.successful_challenges += 1
        
        self.total_votes += 1
        
        logger.info(f"{self.agent_name}: Added debate memory from cycle {cycle_number}")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's memory for decision making"""
        return {
            'personality_traits': {name: trait.to_dict() for name, trait in self.personality_traits.items()},
            'top_beliefs': [belief.to_dict() for belief in self.personal_beliefs[:5]],
            'relationships': {name: rel.to_dict() for name, rel in self.relationships.items()},
            'recent_debates': [debate.to_dict() for debate in self.recent_debates[:3]],
            'statistics': {
                'total_proposals': self.total_proposals,
                'successful_proposals': self.successful_proposals,
                'total_challenges': self.total_challenges,
                'successful_challenges': self.successful_challenges,
                'total_votes': self.total_votes,
                'evolution_points': self.evolution_points
            }
        }
    
    @abstractmethod
    def initialize_core_personality(self):
        """Initialize the core personality traits for this agent type"""
        pass
    
    @abstractmethod
    def process_debate_outcome(self, outcome: str, role: str, satisfaction: float):
        """Process the outcome of a debate and evolve accordingly"""
        pass
    
    @abstractmethod
    def get_decision_context(self) -> Dict[str, Any]:
        """Get agent-specific context for decision making"""
        pass