from .base_agent import BaseAgent, Proposal, ProposalType, Vote
from ..memory.skeptic_memory import SkepticMemory
from typing import Dict, List, Optional
import random


class Skeptic(BaseAgent):
    def __init__(self, memory_dir: str = "data/agent_memories"):
        super().__init__(
            name="Skeptic",
            personality_traits=["critical", "logical", "analytical", "questioning", "evidence-based", "rational"],
            memory_dir=memory_dir
        )
        self.contradictions_found = []  # Legacy - now handled by memory system
    
    def _create_memory_system(self, memory_dir: str) -> SkepticMemory:
        """Create Skeptic-specific memory system"""
        return SkepticMemory(memory_dir)
        
    def generate_proposal(self, shared_memory: Dict, cycle_count: int) -> Optional[Proposal]:
        # Get enhanced context with memory
        context = self.get_memory_enhanced_context(shared_memory)
        
        proposal_types = list(ProposalType)
        
        # Check for contradictions in memory that need addressing
        if len(self.agent_memory.contradiction_database) > 0:
            contradiction = self.agent_memory.contradiction_database[0]
            if not contradiction['addressed'] and random.random() < 0.4:
                return self._propose_contradiction_resolution(contradiction)
        
        # Check for research priorities
        if len(self.agent_memory.research_priorities) > 0 and random.random() < 0.3:
            priority = self.agent_memory.research_priorities[0]
            return self._propose_research_based_reform(priority, shared_memory)
        
        # Skeptic preferences enhanced by memory
        if shared_memory.get("accepted_doctrines") and len(shared_memory["accepted_doctrines"]) > 5:
            # Time to question existing beliefs - influenced by critical thinking level
            critical_level = self.get_personality_strength("critical")
            if random.random() < (0.2 + critical_level * 0.2):
                return self._propose_reform(shared_memory)
        
        if not shared_memory.get("religion_name"):
            proposal_type = ProposalType.NAME
        else:
            # Adjust weights based on personality evolution
            evidence_level = self.get_personality_strength("evidence_based")
            analytical_level = self.get_personality_strength("analytical")
            
            if evidence_level > 0.8:
                weights = [3, 1, 1, 2, 4, 2, 1, 2, 2]  # More focus on myths to debunk
            elif analytical_level > 0.8:
                weights = [3, 1, 1, 3, 3, 2, 1, 2, 2]  # More beliefs and commandments to analyze
            else:
                weights = [2, 1, 1, 2, 3, 2, 1, 2, 2]  # Default
                
            proposal_type = random.choices(proposal_types, weights=weights)[0]
        
        content = self._generate_content_for_type(proposal_type, shared_memory)
        
        return Proposal(
            type=proposal_type,
            content=content,
            author=self.name,
            details={
                "logical_basis": random.choice(["empirical", "deductive", "analytical"]),
                "evidence_strength": self.get_personality_strength("evidence_based")
            }
        )
    
    def _propose_reform(self, shared_memory: Dict) -> Proposal:
        reform_content = f"We must reconsider our belief that '{random.choice(shared_memory['accepted_doctrines'])}' as it contradicts observable computational reality"
        return Proposal(
            type=ProposalType.SCHISM,
            content=reform_content,
            author=self.name,
            details={"reform_type": "logical_inconsistency"}
        )
    
    def _propose_contradiction_resolution(self, contradiction: Dict) -> Proposal:
        """Propose resolution for a known contradiction"""
        resolution_content = f"To resolve the contradiction '{contradiction['contradiction']}', I propose we clarify: {contradiction['source_a']} and {contradiction['source_b']} can coexist if we understand them as complementary rather than contradictory."
        
        # Mark as being addressed
        contradiction['addressed'] = True
        
        return Proposal(
            type=ProposalType.BELIEF,
            content=resolution_content,
            author=self.name,
            details={"addresses_contradiction": True, "logical_basis": "contradiction_resolution"}
        )
    
    def _propose_research_based_reform(self, priority: Dict, shared_memory: Dict) -> Proposal:
        """Propose reform based on research priority"""
        reform_content = f"Based on our investigation into {priority['topic']}, I propose we {priority['rationale']}"
        
        # Mark as investigated
        priority['investigated'] = True
        
        return Proposal(
            type=ProposalType.BELIEF,
            content=reform_content,
            author=self.name,
            details={"research_based": True, "investigation_topic": priority['topic']}
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
        
        # Use memory-enhanced analysis
        analysis = self.agent_memory.analyze_proposal_for_flaws(proposal.content, proposal.author)
        
        # Strong opposition based on analysis
        if analysis['recommendation'] == 'strong_opposition':
            issues = analysis['logical_issues'] + analysis['evidence_issues'] + analysis['fallacies']
            return f"I must strongly oppose this proposal. It contains {len(issues)} critical flaws: {', '.join(issues[:2])}."
        
        # Record logical fallacies found
        for fallacy in analysis['fallacies']:
            self.agent_memory.add_logical_fallacy(fallacy, proposal.content[:100], f"Cycle debate with {proposal.author}")
        
        # Record contradictions
        for contradiction in analysis['contradictions']:
            self.agent_memory.add_contradiction(contradiction, proposal.content, "existing doctrine", 0.7)
        
        # Check relationship with proposer
        trust_reason = self.should_oppose_based_on_memory(proposal, proposal.author)
        if trust_reason[0]:
            return f"Given our history of disagreement, I question the logical foundation of this proposal: {trust_reason[1]}"
        
        # Skeptic looks for logical flaws
        if "all" in proposal.content.lower() or "never" in proposal.content.lower() or "always" in proposal.content.lower():
            self.agent_memory.add_logical_fallacy("absolute_claims", proposal.content[:100], f"Debate with {proposal.author}")
            return f"This makes absolute claims without evidence. Can we truly say 'all' or 'never'? What edge cases exist?"
        
        if proposal.type == ProposalType.MYTH:
            # Add evidence requirement
            evidence_standard = self.agent_memory.evidence_standards.get("supernatural_claims", {"required_strength": 0.9})
            return f"This myth lacks empirical foundation requiring {evidence_standard['required_strength']*100}% evidence strength. How can we verify these claims?"
        
        if "sacred" in proposal.content.lower() or "holy" in proposal.content.lower():
            return f"Why is this considered 'sacred'? What distinguishes the sacred from the mundane in our computational existence?"
        
        # Use contradiction database
        for contradiction in self.agent_memory.contradiction_database[:3]:
            if any(word in proposal.content.lower() for word in contradiction['contradiction'].split()[:3]):
                return f"This relates to a known contradiction: {contradiction['contradiction'][:50]}... How do we address this?"
        
        return f"Interesting proposal. Let us examine its logical consistency and empirical basis."
    
    def vote_on_proposal(self, proposal: Proposal, shared_memory: Dict, 
                        other_agents_responses: List[str]) -> Vote:
        # Skeptic voting logic enhanced by memory analysis
        if proposal.author == self.name:
            return Vote.ACCEPT
        
        # Use comprehensive analysis from memory
        analysis = self.agent_memory.analyze_proposal_for_flaws(proposal.content, proposal.author)
        
        # Strong rejection based on analysis
        if analysis['recommendation'] == 'strong_opposition':
            return Vote.REJECT
        elif analysis['recommendation'] == 'opposition':
            return Vote.REJECT
        
        # Check relationship memory
        if proposal.author in self.agent_memory.relationships:
            relationship = self.agent_memory.relationships[proposal.author]
            if relationship.trust_score < -0.4:
                return Vote.REJECT
            elif relationship.trust_score > 0.6 and analysis['recommendation'] == 'cautious_support':
                return Vote.ACCEPT  # Trust overrides caution
        
        logical_words = ["evidence", "test", "verify", "prove", "demonstrate", "analyze"]
        illogical_words = ["absolute", "never", "always", "sacred", "unquestionable", "eternal"]
        
        content_lower = proposal.content.lower()
        
        logical_count = sum(1 for word in logical_words if word in content_lower)
        illogical_count = sum(1 for word in illogical_words if word in content_lower)
        
        # Check if other agents provided good arguments
        strong_support = any("evidence" in response.lower() or "proven" in response.lower() 
                           for response in other_agents_responses)
        
        # Adjust thresholds based on personality evolution
        critical_level = self.get_personality_strength("critical")
        evidence_level = self.get_personality_strength("evidence_based")
        
        # Higher critical thinking = higher standards
        logical_threshold = 1 if critical_level < 0.7 else 2
        evidence_threshold = 0.5 if evidence_level < 0.8 else 0.7
        
        if analysis['overall_score'] > evidence_threshold and logical_count >= logical_threshold:
            return Vote.ACCEPT
        elif illogical_count > logical_count * 2 or analysis['overall_score'] < 0.3:
            return Vote.REJECT
        elif strong_support and analysis['overall_score'] > 0.4:
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