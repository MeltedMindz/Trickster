from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import json
from datetime import datetime


class Vote(Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    MUTATE = "mutate"
    DELAY = "delay"


class ProposalType(Enum):
    BELIEF = "belief"
    RITUAL = "ritual"
    DEITY = "deity"
    COMMANDMENT = "commandment"
    MYTH = "myth"
    HIERARCHY = "hierarchy"
    NAME = "name"
    SACRED_TEXT = "sacred_text"
    SCHISM = "schism"


class Proposal:
    def __init__(self, type: ProposalType, content: str, author: str, details: Dict = None):
        self.id = f"{author}_{datetime.now().timestamp()}"
        self.type = type
        self.content = content
        self.author = author
        self.details = details or {}
        self.timestamp = datetime.now()
        self.votes = {}
        self.mutations = []
        self.status = "pending"


class BaseAgent(ABC):
    def __init__(self, name: str, personality_traits: List[str]):
        self.name = name
        self.personality_traits = personality_traits
        self.memory = []
        self.current_faction = None
        self.influence_score = 0
        
    @abstractmethod
    def generate_proposal(self, shared_memory: Dict, cycle_count: int) -> Optional[Proposal]:
        """Generate a new proposal based on current state and personality"""
        pass
    
    @abstractmethod
    def challenge_proposal(self, proposal: Proposal, shared_memory: Dict) -> str:
        """Challenge or support a proposal based on personality"""
        pass
    
    @abstractmethod
    def vote_on_proposal(self, proposal: Proposal, shared_memory: Dict, 
                        other_agents_responses: List[str]) -> Vote:
        """Vote on a proposal after considering all arguments"""
        pass
    
    @abstractmethod
    def mutate_proposal(self, proposal: Proposal) -> Proposal:
        """Create a mutated version of a proposal"""
        pass
    
    def form_faction(self, other_agent: 'BaseAgent', shared_goal: str) -> str:
        """Form a temporary faction with another agent"""
        self.current_faction = {
            "ally": other_agent.name,
            "goal": shared_goal,
            "formed_at": datetime.now()
        }
        return f"{self.name} forms faction with {other_agent.name} for: {shared_goal}"
    
    def dissolve_faction(self) -> str:
        """Dissolve current faction"""
        if self.current_faction:
            old_faction = self.current_faction
            self.current_faction = None
            return f"{self.name} dissolves faction with {old_faction['ally']}"
        return f"{self.name} has no faction to dissolve"
    
    def summarize_beliefs(self, shared_memory: Dict) -> str:
        """Summarize current religious beliefs from this agent's perspective"""
        summary_parts = []
        
        if shared_memory.get("religion_name"):
            summary_parts.append(f"We are {shared_memory['religion_name']}.")
        
        if shared_memory.get("accepted_doctrines"):
            summary_parts.append(f"Our core beliefs: {', '.join(shared_memory['accepted_doctrines'][:3])}")
        
        if shared_memory.get("deities"):
            summary_parts.append(f"We worship: {', '.join(shared_memory['deities'][:2])}")
        
        return " ".join(summary_parts) if summary_parts else "Our faith is still forming."