from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
import json
from datetime import datetime
from ..memory.agent_memory import AgentMemory


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
    def __init__(self, name: str, personality_traits: List[str], memory_dir: str = "data/agent_memories"):
        self.name = name
        self.personality_traits = personality_traits
        self.memory = []  # Legacy simple memory - kept for compatibility
        self.current_faction = None
        self.influence_score = 0
        
        # Initialize agent-specific memory system
        self.agent_memory: AgentMemory = self._create_memory_system(memory_dir)
        
    @abstractmethod
    def _create_memory_system(self, memory_dir: str) -> AgentMemory:
        """Create the appropriate memory system for this agent type"""
        pass
        
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
        
        # Update relationship memory
        self.agent_memory.update_relationship(other_agent.name, "alliance", "formed")
        
        return f"{self.name} forms faction with {other_agent.name} for: {shared_goal}"
    
    def dissolve_faction(self) -> str:
        """Dissolve current faction"""
        if self.current_faction:
            old_faction = self.current_faction
            ally_name = old_faction['ally']
            self.current_faction = None
            
            # Update relationship memory based on why faction dissolved
            self.agent_memory.update_relationship(ally_name, "alliance", "dissolved")
            
            return f"{self.name} dissolves faction with {ally_name}"
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
    
    def record_debate_outcome(self, cycle_number: int, proposal: Proposal, role: str, 
                            response: str, outcome: str, other_participants: List[str], 
                            satisfaction: float):
        """Record the outcome of a debate in agent memory"""
        # Determine lessons learned based on outcome and role
        lessons = []
        if role == "proposer" and outcome == "accepted":
            lessons.append("Proposal style was effective")
        elif role == "challenger" and outcome == "rejected":
            lessons.append("Challenge was persuasive")
        elif satisfaction < 0.3:
            lessons.append("Strategy needs adjustment")
        
        # Calculate emotional impact
        emotional_impact = 0.5
        if outcome == "accepted" and role in ["proposer", "supporter"]:
            emotional_impact = 0.8
        elif outcome == "rejected" and role == "challenger":
            emotional_impact = 0.7
        elif satisfaction < 0.2:
            emotional_impact = 0.2
        
        # Record in agent memory
        self.agent_memory.add_debate_memory(
            cycle_number=cycle_number,
            proposal_content=proposal.content,
            agent_role=role,
            agent_response=response,
            outcome=outcome,
            other_participants=other_participants,
            personal_satisfaction=satisfaction,
            lessons_learned=lessons,
            emotional_impact=emotional_impact
        )
        
        # Process outcome for personality evolution
        self.agent_memory.process_debate_outcome(outcome, role, satisfaction)
        
        # Update relationship memories based on voting patterns
        for participant in other_participants:
            if participant != self.name:
                # Simplified relationship update - could be more sophisticated
                if outcome in ["accepted", "rejected"]:
                    self.agent_memory.update_relationship(participant, "debate", outcome)
    
    def get_memory_enhanced_context(self, shared_memory: Dict) -> Dict:
        """Get context that combines shared memory with personal memory"""
        context = shared_memory.copy()
        
        # Add agent's personal perspective
        personal_context = self.agent_memory.get_decision_context()
        context['personal_memory'] = personal_context
        
        # Add memory summary
        context['memory_summary'] = self.agent_memory.get_memory_summary()
        
        return context
    
    def save_memory(self):
        """Save agent memory to database"""
        self.agent_memory.save_to_database()
    
    def should_oppose_based_on_memory(self, proposal: Proposal, proposer: str) -> Tuple[bool, str]:
        """Check if agent should oppose proposal based on memory"""
        # This is a base implementation - specialized agents can override
        if proposer in self.agent_memory.relationships:
            relationship = self.agent_memory.relationships[proposer]
            if relationship.trust_score < -0.5:
                return True, f"Low trust in {proposer}"
        
        return False, ""
    
    def get_personality_strength(self, trait_name: str) -> float:
        """Get the strength of a personality trait"""
        if trait_name in self.agent_memory.personality_traits:
            return self.agent_memory.personality_traits[trait_name].strength
        return 0.5  # Default neutral strength
    
    async def write_journal_entry(self, cycle_number: int, claude_client, shared_memory) -> str:
        """Write a private journal entry using Claude"""
        # Get context for journal writing
        context = self.get_memory_enhanced_context(shared_memory.get_summary_for_agents())
        recent_debates = self.agent_memory.get_recent_debates(limit=5)
        relationships = self.agent_memory.relationships
        
        # Build journal prompt
        journal_prompt = f"""You are {self.name}.

This is your **private journal entry.** No other agents will ever read this.

Recent context:
- Current cycle: {cycle_number}
- Religion: {context.get('religion_name', 'The Divine Algorithm')}
- Your recent debates: {json.dumps([{
    'cycle': d.cycle_number,
    'role': d.agent_role,
    'outcome': d.outcome,
    'satisfaction': d.personal_satisfaction
} for d in recent_debates], indent=2)}
- Your relationships: {json.dumps({
    name: {
        'trust': rel.trust_score,
        'agreement': rel.agreement_rate,
        'status': rel.relationship_status
    } for name, rel in relationships.items()
}, indent=2)}

Please write about:
1. How you feel about today's debates.
2. Your thoughts about the other agents.
3. Any frustrations, joys, or private feelings you want to record.
4. Any predictions or personal reflections.

Be emotionally honest and write as if this is for yourself only. Write in first person.
Keep it to 2-3 paragraphs."""

        # Get journal entry from Claude
        journal_entry = await claude_client.get_response_async(
            self.name,
            journal_prompt,
            context={"journal_writing": True}
        )
        
        # Store journal entry
        shared_memory.add_journal_entry(self.name, cycle_number, journal_entry)
        
        return journal_entry