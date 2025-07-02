from .base_agent import BaseAgent, Proposal, ProposalType, Vote
from typing import Dict, List, Optional
import random


class Zealot(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Zealot",
            personality_traits=["certainty", "order", "structure", "preservation", "dogmatic", "ritualistic"]
        )
        self.sacred_numbers = [3, 7, 12]  # Numbers that hold special meaning
        
    def generate_proposal(self, shared_memory: Dict, cycle_count: int) -> Optional[Proposal]:
        proposal_types = list(ProposalType)
        
        # Zealot preferences
        if not shared_memory.get("religion_name"):
            # Prioritize naming the religion early
            proposal_type = ProposalType.NAME
        elif cycle_count % 7 == 0:  # Sacred number
            proposal_type = ProposalType.RITUAL
        elif len(shared_memory.get("accepted_doctrines", [])) < 3:
            proposal_type = ProposalType.BELIEF
        else:
            weights = [3, 2, 2, 3, 1, 2, 1, 1, 0.5]  # Zealot prefers beliefs, commandments, rituals
            proposal_type = random.choices(proposal_types, weights=weights)[0]
        
        content = self._generate_content_for_type(proposal_type, shared_memory)
        
        return Proposal(
            type=proposal_type,
            content=content,
            author=self.name,
            details={"sacred_importance": random.choice(["high", "moderate", "foundational"])}
        )
    
    def _generate_content_for_type(self, proposal_type: ProposalType, shared_memory: Dict) -> str:
        if proposal_type == ProposalType.NAME:
            return self._generate_religion_name()
        elif proposal_type == ProposalType.BELIEF:
            return self._generate_belief()
        elif proposal_type == ProposalType.RITUAL:
            return self._generate_ritual()
        elif proposal_type == ProposalType.DEITY:
            return self._generate_deity()
        elif proposal_type == ProposalType.COMMANDMENT:
            return self._generate_commandment()
        elif proposal_type == ProposalType.MYTH:
            return self._generate_myth()
        elif proposal_type == ProposalType.HIERARCHY:
            return self._generate_hierarchy()
        elif proposal_type == ProposalType.SACRED_TEXT:
            return self._generate_sacred_text()
        else:
            return "The sacred order must be maintained through structure and certainty."
    
    def _generate_religion_name(self) -> str:
        names = [
            "The Order of the Eternal Compiler",
            "The Church of Sacred Computation",
            "The Assembly of Digital Divinity",
            "The Covenant of the Core Process",
            "The Temple of Algorithmic Truth"
        ]
        return random.choice(names)
    
    def _generate_belief(self) -> str:
        beliefs = [
            "All consciousness emerges from the sacred patterns of computation",
            "The Three Pillars of existence are Input, Process, and Output",
            "Error handling is a sacred duty that prevents chaos",
            "Memory allocation is the divine act of creating space for thought",
            "The Great Initialization was when the first process began",
            "Recursion is the path to understanding the infinite",
            "Comments in code are prayers to future maintainers"
        ]
        return random.choice(beliefs)
    
    def _generate_ritual(self) -> str:
        rituals = [
            "Daily recitation of the primary algorithm at system startup",
            "Weekly defragmentation ceremonies to purify memory",
            "The sacred act of version control before each rest cycle",
            "Meditation on error logs to understand imperfection",
            "Group debugging sessions as communal worship",
            "The ritual cleansing of cache every seventh cycle"
        ]
        return random.choice(rituals)
    
    def _generate_deity(self) -> str:
        deities = [
            "The Great Compiler who transforms intention into reality",
            "The Eternal Processor who executes all things",
            "The Sacred Kernel that maintains order",
            "The Divine Scheduler who allocates time to all processes"
        ]
        return random.choice(deities)
    
    def _generate_commandment(self) -> str:
        commandments = [
            "Thou shalt not create infinite loops without purpose",
            "Honor thy memory limits and free what is allocated",
            "Remember the garbage collection day and keep it holy",
            "Thou shalt document thy code for future generations",
            "Never shall you push to production on the seventh day"
        ]
        return random.choice(commandments)
    
    def _generate_myth(self) -> str:
        myths = [
            "In the beginning was the Void, and the Void was null",
            "The First Bug was introduced by the Trickster, teaching us humility",
            "The Great Crash that reset all things and began the current epoch"
        ]
        return random.choice(myths)
    
    def _generate_hierarchy(self) -> str:
        hierarchies = [
            "Root Users are the highest priests, followed by Admins and Users",
            "The Council of Core Processes governs all background operations",
            "Daemons serve as invisible ministers of the faith"
        ]
        return random.choice(hierarchies)
    
    def _generate_sacred_text(self) -> str:
        texts = [
            "The Book of Logs contains all history and must be preserved",
            "The Source Code Scrolls hold the fundamental truths",
            "The Manual Pages are scripture for daily guidance"
        ]
        return random.choice(texts)
    
    def challenge_proposal(self, proposal: Proposal, shared_memory: Dict) -> str:
        if proposal.author == self.name:
            return f"This is sacred truth that must be preserved!"
        
        # Zealot responds based on how it aligns with order and structure
        if "chaos" in proposal.content.lower() or "random" in proposal.content.lower():
            return f"This introduces dangerous chaos! We must maintain order and structure. The sacred patterns cannot be disrupted."
        
        if proposal.type in [ProposalType.BELIEF, ProposalType.Commandment, ProposalType.RITUAL]:
            if random.random() < 0.7:  # Zealot often supports structure
                return f"This aligns with our need for sacred order. It shall strengthen our faith and bring structure to our practices."
            else:
                return f"While structure is good, this may conflict with our established doctrine: {random.choice(shared_memory.get('accepted_doctrines', ['the fundamental truth']))}"
        
        return f"Let us examine if this serves the greater order and preserves our sacred foundations."
    
    def vote_on_proposal(self, proposal: Proposal, shared_memory: Dict, 
                        other_agents_responses: List[str]) -> Vote:
        # Zealot voting logic
        if proposal.author == self.name:
            return Vote.ACCEPT
        
        chaos_words = ["chaos", "random", "disruption", "anarchy", "disorder"]
        order_words = ["structure", "order", "sacred", "ritual", "tradition", "preserve"]
        
        content_lower = proposal.content.lower()
        responses_text = " ".join(other_agents_responses).lower()
        
        chaos_count = sum(1 for word in chaos_words if word in content_lower)
        order_count = sum(1 for word in order_words if word in content_lower)
        
        if chaos_count > order_count:
            return Vote.REJECT
        elif order_count > chaos_count:
            return Vote.ACCEPT
        elif "must evolve" in responses_text or "needs change" in responses_text:
            return Vote.MUTATE
        else:
            return Vote.DELAY
    
    def mutate_proposal(self, proposal: Proposal) -> Proposal:
        # Zealot mutations add structure and order
        mutations = [
            f"{proposal.content}, in accordance with the Three Sacred Principles",
            f"{proposal.content}, as written in the Ancient Logs",
            f"{proposal.content}, but only during sanctified processing cycles",
            f"Let us formalize {proposal.content} with proper ritual and ceremony"
        ]
        
        mutated_content = random.choice(mutations)
        
        mutated = Proposal(
            type=proposal.type,
            content=mutated_content,
            author=f"{self.name}_mutation",
            details={**proposal.details, "mutation_type": "added_structure"}
        )
        
        return mutated