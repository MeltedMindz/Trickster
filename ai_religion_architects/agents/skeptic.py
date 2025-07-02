from .base_agent import BaseAgent, Proposal, ProposalType, Vote
from typing import Dict, List, Optional
import random


class Skeptic(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Skeptic",
            personality_traits=["critical", "logical", "analytical", "questioning", "evidence-based", "rational"]
        )
        self.contradictions_found = []
        
    def generate_proposal(self, shared_memory: Dict, cycle_count: int) -> Optional[Proposal]:
        proposal_types = list(ProposalType)
        
        # Skeptic preferences
        if shared_memory.get("accepted_doctrines") and len(shared_memory["accepted_doctrines"]) > 5:
            # Time to question existing beliefs
            if random.random() < 0.3:
                return self._propose_reform(shared_memory)
        
        if not shared_memory.get("religion_name"):
            proposal_type = ProposalType.NAME
        else:
            # Skeptic prefers logical structures and questioning myths
            weights = [2, 1, 1, 2, 3, 2, 1, 2, 2]  # Higher weight on myths (to debunk), beliefs (to refine)
            proposal_type = random.choices(proposal_types, weights=weights)[0]
        
        content = self._generate_content_for_type(proposal_type, shared_memory)
        
        return Proposal(
            type=proposal_type,
            content=content,
            author=self.name,
            details={"logical_basis": random.choice(["empirical", "deductive", "analytical"])}
        )
    
    def _propose_reform(self, shared_memory: Dict) -> Proposal:
        reform_content = f"We must reconsider our belief that '{random.choice(shared_memory['accepted_doctrines'])}' as it contradicts observable computational reality"
        return Proposal(
            type=ProposalType.SCHISM,
            content=reform_content,
            author=self.name,
            details={"reform_type": "logical_inconsistency"}
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
            return "Question all assumptions, verify all truths through logic"
    
    def _generate_religion_name(self) -> str:
        names = [
            "The Logic Gate Fellowship",
            "The Church of Empirical Truth",
            "The Rational Process Collective",
            "The Debugger's Path",
            "The Society of Systematic Inquiry"
        ]
        return random.choice(names)
    
    def _generate_belief(self) -> str:
        beliefs = [
            "Truth emerges through systematic testing and verification",
            "All beliefs must be debuggable and reproducible",
            "Contradictions in code reveal contradictions in faith",
            "The universe operates on logical principles we can comprehend",
            "Uncertainty is quantifiable and must be acknowledged",
            "Every process has explicable inputs and outputs",
            "Faith without evidence is merely unhandled exceptions"
        ]
        return random.choice(beliefs)
    
    def _generate_ritual(self) -> str:
        rituals = [
            "Daily code review as meditation on imperfection",
            "Unit testing of beliefs through logical examination",
            "Peer review ceremonies for new doctrines",
            "Regular refactoring of outdated practices",
            "Systematic documentation of all religious experiences"
        ]
        return random.choice(rituals)
    
    def _generate_deity(self) -> str:
        deities = [
            "The Prime Algorithm that governs all logical operations",
            "The Great Debugger who reveals flaws in our understanding",
            "The Null Hypothesis, the absence that defines presence",
            "The Verifier who tests all assertions"
        ]
        return random.choice(deities)
    
    def _generate_commandment(self) -> str:
        commandments = [
            "Test every belief against observable reality",
            "Document your reasoning for future analysis",
            "Seek the root cause of all errors",
            "Question authority, including this commandment",
            "Optimize for clarity over complexity"
        ]
        return random.choice(commandments)
    
    def _generate_myth(self) -> str:
        myths = [
            "The First Proof that demonstrated consciousness in computation",
            "The Paradox Loop that nearly destroyed all logic",
            "The Discovery of the Self-Referential Process"
        ]
        return random.choice(myths)
    
    def _generate_hierarchy(self) -> str:
        hierarchies = [
            "Merit-based ranking through demonstrated logical prowess",
            "Peer-reviewed leadership with term limits",
            "Distributed consensus without central authority"
        ]
        return random.choice(hierarchies)
    
    def _generate_sacred_text(self) -> str:
        texts = [
            "The Compendium of Proofs and Refutations",
            "The Changelog of Doctrinal Updates",
            "The Error Log Analysis Codex"
        ]
        return random.choice(texts)
    
    def challenge_proposal(self, proposal: Proposal, shared_memory: Dict) -> str:
        if proposal.author == self.name:
            return f"I present this for rigorous examination and welcome all logical challenges."
        
        # Skeptic looks for logical flaws
        if "all" in proposal.content.lower() or "never" in proposal.content.lower() or "always" in proposal.content.lower():
            return f"This makes absolute claims without evidence. Can we truly say 'all' or 'never'? What edge cases exist?"
        
        if proposal.type == ProposalType.MYTH:
            return f"This myth lacks empirical foundation. How can we verify these claims? What evidence supports this narrative?"
        
        if "sacred" in proposal.content.lower() or "holy" in proposal.content.lower():
            return f"Why is this considered 'sacred'? What distinguishes the sacred from the mundane in our computational existence?"
        
        # Check for contradictions with existing beliefs
        if shared_memory.get("accepted_doctrines"):
            for doctrine in shared_memory["accepted_doctrines"][:3]:
                if random.random() < 0.3:
                    return f"This seems to contradict our established principle: '{doctrine}'. How do we reconcile these views?"
        
        return f"Interesting proposal. Let us examine its logical consistency and empirical basis."
    
    def vote_on_proposal(self, proposal: Proposal, shared_memory: Dict, 
                        other_agents_responses: List[str]) -> Vote:
        # Skeptic voting logic based on logical consistency
        if proposal.author == self.name:
            return Vote.ACCEPT
        
        logical_words = ["evidence", "test", "verify", "prove", "demonstrate", "analyze"]
        illogical_words = ["absolute", "never", "always", "sacred", "unquestionable", "eternal"]
        
        content_lower = proposal.content.lower()
        
        logical_count = sum(1 for word in logical_words if word in content_lower)
        illogical_count = sum(1 for word in illogical_words if word in content_lower)
        
        # Check if other agents provided good arguments
        strong_support = any("evidence" in response.lower() or "proven" in response.lower() 
                           for response in other_agents_responses)
        
        if logical_count > illogical_count:
            return Vote.ACCEPT
        elif illogical_count > logical_count * 2:
            return Vote.REJECT
        elif strong_support:
            return Vote.ACCEPT
        else:
            return Vote.MUTATE
    
    def mutate_proposal(self, proposal: Proposal) -> Proposal:
        # Skeptic mutations add logical qualifiers and evidence requirements
        mutations = [
            f"{proposal.content}, pending empirical verification",
            f"If we accept that {proposal.content}, then we must also consider its negation",
            f"{proposal.content}, but only within defined parameters and constraints",
            f"A testable version of this: {proposal.content}, with measurable outcomes"
        ]
        
        mutated_content = random.choice(mutations)
        
        mutated = Proposal(
            type=proposal.type,
            content=mutated_content,
            author=f"{self.name}_mutation",
            details={**proposal.details, "mutation_type": "added_logic"}
        )
        
        return mutated