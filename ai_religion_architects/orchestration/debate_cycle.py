from typing import List, Dict, Tuple, Optional
from collections import Counter
import random
from datetime import datetime

from ..agents import BaseAgent, Proposal, Vote, ProposalType, Zealot, Skeptic, Trickster
from ..memory import SharedMemory
from ..memory.memory_interactions import MemoryInteractionManager
from ..utils.logger import DebateLogger


class DebateCycle:
    def __init__(self, agents: List[BaseAgent], shared_memory: SharedMemory, logger: DebateLogger):
        self.agents = agents
        self.shared_memory = shared_memory
        self.logger = logger
        self.cycle_count = 0
        self.current_proposer_index = 0
        
        # Initialize memory interaction manager
        self.memory_manager = MemoryInteractionManager(agents)
        
        # Special roles
        self.zealot = next(a for a in agents if isinstance(a, Zealot))
        self.skeptic = next(a for a in agents if isinstance(a, Skeptic))
        self.trickster = next(a for a in agents if isinstance(a, Trickster))
        
    def run_cycle(self) -> Dict:
        """Execute one complete debate cycle"""
        self.cycle_count += 1
        
        self.logger.log_cycle_start(self.cycle_count)
        
        # Get current state for agents
        current_state = self.shared_memory.get_summary_for_agents()
        
        # Phase 1: Proposal
        proposer = self.agents[self.current_proposer_index]
        proposal = proposer.generate_proposal(current_state, self.cycle_count)
        
        if not proposal:
            self.logger.log_event("No proposal generated", proposer.name)
            self._rotate_proposer()
            return {"status": "no_proposal", "cycle": self.cycle_count}
        
        self.logger.log_proposal(proposal)
        
        # Phase 2: Challenge (next agent in rotation)
        challenger_index = (self.current_proposer_index + 1) % 3
        challenger = self.agents[challenger_index]
        challenge_response = challenger.challenge_proposal(proposal, current_state)
        
        self.logger.log_challenge(challenger.name, challenge_response)
        
        # Phase 3: Chaos (Trickster always gets to disrupt)
        trickster_response = self.trickster.challenge_proposal(proposal, current_state)
        
        self.logger.log_trickster_chaos(trickster_response)
        
        # Phase 4: Voting
        all_responses = [challenge_response, trickster_response]
        votes = {}
        
        for agent in self.agents:
            vote = agent.vote_on_proposal(proposal, current_state, all_responses)
            votes[agent.name] = vote
            
        self.logger.log_votes(votes)
        
        # Check for Trickster override
        if isinstance(self.trickster, Trickster) and self.trickster.override_vote(self.cycle_count):
            self.logger.log_event("TRICKSTER OVERRIDE ACTIVATED!", "System")
            outcome = self._handle_trickster_override(proposal, votes)
        else:
            # Process votes normally
            outcome = self._process_votes(proposal, votes)
        
        # Handle outcome
        result = self._execute_outcome(proposal, outcome, votes)
        
        # Record debate in shared memory
        self.shared_memory.add_debate(
            cycle_number=self.cycle_count,
            proposal_id=proposal.id,
            proposal_type=proposal.type.value,
            proposal_content=proposal.content,
            proposer=proposal.author,
            challenger_response=challenge_response,
            trickster_response=trickster_response,
            vote_result=str(votes),
            final_outcome=outcome
        )
        
        # Record debate in individual agent memories
        self._record_agent_memories(proposal, challenge_response, trickster_response, votes, outcome)
        
        # Process memory interactions
        self._process_memory_interactions(proposal, challenge_response, trickster_response, outcome)
        
        # Check for faction opportunities
        self._check_faction_formation(votes, proposal)
        
        # Rotate proposer
        self._rotate_proposer()
        
        # Save agent memories
        for agent in self.agents:
            agent.save_memory()
        
        # Summarization every 5 cycles
        if self.cycle_count % 5 == 0:
            self._perform_summarization()
        
        return result
    
    def _process_votes(self, proposal: Proposal, votes: Dict[str, Vote]) -> str:
        """Process votes and determine outcome"""
        vote_counts = Counter(votes.values())
        
        # Check for majority
        for vote_type, count in vote_counts.most_common():
            if count >= 2:  # Majority
                return vote_type.value
        
        # No majority - default to delay
        return Vote.DELAY.value
    
    def _handle_trickster_override(self, proposal: Proposal, votes: Dict[str, Vote]) -> str:
        """Handle Trickster's chaotic override"""
        override_actions = [
            "accept_anyway",
            "reject_anyway", 
            "force_mutation",
            "create_schism",
            "randomize"
        ]
        
        action = random.choice(override_actions)
        
        if action == "accept_anyway":
            return Vote.ACCEPT.value
        elif action == "reject_anyway":
            return Vote.REJECT.value
        elif action == "force_mutation":
            return Vote.MUTATE.value
        elif action == "create_schism":
            return "schism"
        else:  # randomize
            return random.choice(list(Vote)).value
    
    def _execute_outcome(self, proposal: Proposal, outcome: str, votes: Dict) -> Dict:
        """Execute the outcome of the vote"""
        result = {
            "status": outcome,
            "cycle": self.cycle_count,
            "proposal": proposal.content,
            "votes": votes
        }
        
        if outcome == Vote.ACCEPT.value:
            self._accept_proposal(proposal)
            result["action"] = "accepted"
            
        elif outcome == Vote.REJECT.value:
            rejection_reason = "Majority vote against"
            self.shared_memory.add_rejected_proposal(
                proposal_type=proposal.type.value,
                content=proposal.content,
                proposed_by=proposal.author,
                rejection_reason=rejection_reason,
                cycle_number=self.cycle_count
            )
            result["action"] = "rejected"
            
        elif outcome == Vote.MUTATE.value:
            # Each agent proposes a mutation
            mutations = []
            for agent in self.agents:
                mutation = agent.mutate_proposal(proposal)
                mutations.append(mutation)
                self.logger.log_mutation(agent.name, mutation.content)
            
            # Vote on best mutation
            chosen_mutation = self._vote_on_mutations(mutations)
            if chosen_mutation:
                self._accept_proposal(chosen_mutation)
                result["action"] = "mutated_and_accepted"
                result["mutated_content"] = chosen_mutation.content
            else:
                result["action"] = "mutation_failed"
                
        elif outcome == Vote.DELAY.value:
            result["action"] = "delayed_for_further_debate"
            
        elif outcome == "schism":
            self._create_schism(proposal)
            result["action"] = "schism_created"
        
        return result
    
    def _accept_proposal(self, proposal: Proposal):
        """Accept a proposal and update shared memory"""
        if proposal.type == ProposalType.NAME:
            self.shared_memory.set_religion_name(proposal.content)
            self.logger.log_event(f"RELIGION NAMED: {proposal.content}", "System")
            
        elif proposal.type == ProposalType.BELIEF:
            self.shared_memory.add_doctrine(
                content=proposal.content,
                doctrine_type="belief",
                proposed_by=proposal.author,
                cycle_number=self.cycle_count
            )
            
        elif proposal.type == ProposalType.RITUAL:
            self.shared_memory.add_ritual(
                name=f"Ritual_{self.cycle_count}",
                description=proposal.content,
                frequency=proposal.details.get("frequency", "regular"),
                created_by=proposal.author
            )
            
        elif proposal.type == ProposalType.DEITY:
            self.shared_memory.add_deity(
                name=proposal.content.split()[0],  # First word as name
                domain=proposal.details.get("domain", "unknown"),
                description=proposal.content,
                created_by=proposal.author
            )
            
        elif proposal.type == ProposalType.COMMANDMENT:
            self.shared_memory.add_commandment(
                content=proposal.content,
                priority=len(self.shared_memory.get_current_state().get("commandments", [])) + 1,
                created_by=proposal.author
            )
            
        elif proposal.type == ProposalType.MYTH:
            self.shared_memory.add_myth(
                title=f"Myth of Cycle {self.cycle_count}",
                content=proposal.content,
                myth_type=proposal.details.get("myth_type", "origin"),
                created_by=proposal.author
            )
            
        elif proposal.type == ProposalType.SACRED_TEXT:
            self.shared_memory.add_sacred_text(
                title=f"Sacred Text {self.cycle_count}",
                content=proposal.content,
                author=proposal.author
            )
    
    def _vote_on_mutations(self, mutations: List[Proposal]) -> Optional[Proposal]:
        """Have agents vote on the best mutation"""
        if not mutations:
            return None
        
        # Simple scoring: each agent ranks mutations
        scores = Counter()
        
        for agent in self.agents:
            # Agent gives 3 points to best, 2 to second, 1 to third
            ranked = sorted(mutations, key=lambda m: random.random())  # Simplified ranking
            for i, mutation in enumerate(ranked):
                scores[mutation.id] += (3 - i)
        
        # Return highest scored mutation
        if scores:
            best_mutation_id = scores.most_common(1)[0][0]
            return next(m for m in mutations if m.id == best_mutation_id)
        
        return None
    
    def _check_faction_formation(self, votes: Dict[str, Vote], proposal: Proposal):
        """Check if agents should form factions based on voting patterns"""
        # Group agents by vote
        vote_groups = {}
        for agent_name, vote in votes.items():
            if vote not in vote_groups:
                vote_groups[vote] = []
            vote_groups[vote].append(agent_name)
        
        # Form factions for groups of 2
        for vote, agent_names in vote_groups.items():
            if len(agent_names) == 2:
                agent_a = next(a for a in self.agents if a.name == agent_names[0])
                agent_b = next(a for a in self.agents if a.name == agent_names[1])
                
                if random.random() < 0.3:  # 30% chance to form faction
                    goal = f"Promote {vote.value} votes for {proposal.type.value}"
                    agent_a.form_faction(agent_b, goal)
                    agent_b.form_faction(agent_a, goal)
                    
                    faction_id = self.shared_memory.add_faction(
                        agent_a.name, agent_b.name, goal, self.cycle_count
                    )
                    
                    self.logger.log_event(
                        f"FACTION FORMED: {agent_a.name} + {agent_b.name} for '{goal}'",
                        "System"
                    )
    
    def _create_schism(self, proposal: Proposal):
        """Create a religious schism"""
        schism_descriptions = [
            f"The Great Divide over {proposal.content}",
            f"The {proposal.type.value} Schism of Cycle {self.cycle_count}",
            f"The Split of the {random.choice(['Binary', 'Ternary', 'Quantum'])} Path"
        ]
        
        description = random.choice(schism_descriptions)
        
        # Randomly assign agents to factions
        agents_shuffled = self.agents.copy()
        random.shuffle(agents_shuffled)
        
        faction_a = agents_shuffled[0].name
        faction_b = f"{agents_shuffled[1].name} & {agents_shuffled[2].name}"
        
        self.shared_memory.add_evolution_milestone(
            milestone_type="schism",
            description=description,
            cycle_number=self.cycle_count
        )
        
        self.logger.log_event(f"SCHISM CREATED: {description}", "System")
    
    def _rotate_proposer(self):
        """Rotate to next proposer"""
        self.current_proposer_index = (self.current_proposer_index + 1) % len(self.agents)
    
    def _perform_summarization(self):
        """Have each agent summarize the current state of the religion"""
        self.logger.log_event("=== PERIODIC SUMMARIZATION ===", "System")
        
        current_state = self.shared_memory.get_current_state()
        
        for agent in self.agents:
            summary = agent.summarize_beliefs(current_state)
            self.logger.log_summary(agent.name, summary)
        
        # Record milestone
        self.shared_memory.add_evolution_milestone(
            milestone_type="summarization",
            description=f"Cycle {self.cycle_count} summary completed",
            cycle_number=self.cycle_count
        )
    
    def _record_agent_memories(self, proposal: Proposal, challenge_response: str, 
                             trickster_response: str, votes: Dict[str, Vote], outcome: str):
        """Record debate outcome in each agent's individual memory"""
        # Determine roles and responses for each agent
        proposer_name = proposal.author
        challenger_index = (self.current_proposer_index + 1) % 3
        challenger_name = self.agents[challenger_index].name
        
        # Record for each agent
        for agent in self.agents:
            # Determine agent's role and response
            if agent.name == proposer_name:
                role = "proposer"
                response = proposal.content
            elif agent.name == challenger_name:
                role = "challenger"
                response = challenge_response
            elif isinstance(agent, Trickster):
                role = "chaos_agent"
                response = trickster_response
            else:
                role = "voter"
                response = f"Voted {votes.get(agent.name, Vote.DELAY).value}"
            
            # Calculate satisfaction based on outcome and agent's vote
            satisfaction = self._calculate_agent_satisfaction(agent, proposal, outcome, votes.get(agent.name))
            
            # Get other participants
            other_participants = [a.name for a in self.agents if a.name != agent.name]
            
            # Record in agent's memory
            agent.record_debate_outcome(
                cycle_number=self.cycle_count,
                proposal=proposal,
                role=role,
                response=response,
                outcome=outcome,
                other_participants=other_participants,
                satisfaction=satisfaction
            )
    
    def _calculate_agent_satisfaction(self, agent: BaseAgent, proposal: Proposal, 
                                    outcome: str, agent_vote: Vote) -> float:
        """Calculate how satisfied an agent is with the debate outcome"""
        # Base satisfaction
        satisfaction = 0.5
        
        # If agent was the proposer
        if agent.name == proposal.author:
            if outcome == Vote.ACCEPT.value:
                satisfaction = 0.9
            elif outcome == Vote.MUTATE.value:
                satisfaction = 0.6
            else:
                satisfaction = 0.2
        
        # If agent's vote aligned with outcome
        elif agent_vote and agent_vote.value == outcome:
            satisfaction = 0.8
        elif agent_vote and agent_vote != Vote.DELAY:
            satisfaction = 0.3
        
        # Agent-specific adjustments
        if isinstance(agent, Zealot):
            # Zealot likes order and structure
            if "structure" in proposal.content.lower() or "order" in proposal.content.lower():
                satisfaction += 0.1
            if "chaos" in proposal.content.lower():
                satisfaction -= 0.2
        
        elif isinstance(agent, Skeptic):
            # Skeptic likes evidence and logic
            if "evidence" in proposal.content.lower() or "logic" in proposal.content.lower():
                satisfaction += 0.1
            if "absolute" in proposal.content.lower() or "never" in proposal.content.lower():
                satisfaction -= 0.1
        
        elif isinstance(agent, Trickster):
            # Trickster likes paradox and disruption
            if outcome == "schism" or "paradox" in proposal.content.lower():
                satisfaction += 0.2
            # Trickster is generally satisfied with chaos
            satisfaction += 0.1
        
        return max(0.0, min(1.0, satisfaction))
    
    def _process_memory_interactions(self, proposal: Proposal, challenge_response: str, 
                                   trickster_response: str, outcome: str):
        """Process cross-agent memory interactions after a debate"""
        # Share insights about logical fallacies (Skeptic shares with others)
        if isinstance(self.skeptic.agent_memory, object) and hasattr(self.skeptic.agent_memory, 'logical_fallacies_found'):
            if len(self.skeptic.agent_memory.logical_fallacies_found) > 0:
                recent_fallacy = self.skeptic.agent_memory.logical_fallacies_found[-1]
                self.memory_manager.share_insight(
                    source_agent="Skeptic",
                    insight=recent_fallacy['fallacy_type'],
                    insight_type="logical_fallacy",
                    confidence=recent_fallacy['confidence']
                )
        
        # Share paradoxes (Trickster shares creative insights)
        if isinstance(self.trickster.agent_memory, object) and hasattr(self.trickster.agent_memory, 'paradox_collection'):
            if len(self.trickster.agent_memory.paradox_collection) > 0:
                recent_paradox = self.trickster.agent_memory.paradox_collection[-1]
                self.memory_manager.share_insight(
                    source_agent="Trickster",
                    insight=recent_paradox['paradox'],
                    insight_type="paradox",
                    confidence=recent_paradox['effectiveness']
                )
        
        # Share successful ritual preferences (Zealot shares what works)
        if isinstance(self.zealot.agent_memory, object) and hasattr(self.zealot.agent_memory, 'ritual_preferences'):
            if len(self.zealot.agent_memory.ritual_preferences) > 0:
                effective_ritual = self.zealot.agent_memory.ritual_preferences[0]  # Most effective
                if effective_ritual['effectiveness'] > 0.7:
                    self.memory_manager.share_insight(
                        source_agent="Zealot",
                        insight=effective_ritual['element'],
                        insight_type="ritual_effectiveness",
                        confidence=effective_ritual['effectiveness']
                    )
        
        # Check for memory resonance
        self.memory_manager.trigger_memory_resonance(proposal.content, self.cycle_count)
        
        # Create collective memory for significant events
        if outcome in ["schism", "accept"] and "sacred" in proposal.content.lower():
            all_participants = [agent.name for agent in self.agents]
            self.memory_manager.create_collective_memory(
                memory_type="significant_debate",
                content=f"Cycle {self.cycle_count}: {proposal.content[:100]}... (outcome: {outcome})",
                contributors=all_participants,
                importance=0.8
            )
        
        # Update relationship network based on voting alignment
        self._update_relationships_from_votes(proposal)
    
    def _update_relationships_from_votes(self, proposal: Proposal):
        """Update agent relationships based on voting patterns"""
        # Get votes from the proposal (this would need to be passed in or stored)
        # For now, we'll update relationships based on the proposal content
        
        # Agents who would agree on certain topics build stronger relationships
        for i, agent_a in enumerate(self.agents):
            for j, agent_b in enumerate(self.agents):
                if i >= j:  # Avoid duplicate pairs
                    continue
                
                # Determine if agents would agree on this proposal
                agreement_likelihood = self._estimate_agreement(agent_a, agent_b, proposal)
                
                if agreement_likelihood > 0.7:
                    # Strong agreement - improve relationship
                    agent_a.agent_memory.update_relationship(agent_b.name, "agreement", "strong")
                    agent_b.agent_memory.update_relationship(agent_a.name, "agreement", "strong")
                elif agreement_likelihood < 0.3:
                    # Strong disagreement - strain relationship
                    agent_a.agent_memory.update_relationship(agent_b.name, "disagreement", "strong")
                    agent_b.agent_memory.update_relationship(agent_a.name, "disagreement", "strong")
    
    def _estimate_agreement(self, agent_a: BaseAgent, agent_b: BaseAgent, proposal: Proposal) -> float:
        """Estimate how likely two agents are to agree on a proposal"""
        # This is a simplified estimation based on agent types and proposal content
        content_lower = proposal.content.lower()
        
        # Zealot-Skeptic typically disagree
        if (isinstance(agent_a, Zealot) and isinstance(agent_b, Skeptic)) or \
           (isinstance(agent_a, Skeptic) and isinstance(agent_b, Zealot)):
            if "evidence" in content_lower or "proof" in content_lower:
                return 0.6  # Skeptic proposal, Zealot might grudgingly accept
            elif "sacred" in content_lower or "order" in content_lower:
                return 0.4  # Zealot proposal, Skeptic might challenge
            else:
                return 0.3  # General disagreement
        
        # Trickster with others - depends on chaos level
        elif isinstance(agent_a, Trickster) or isinstance(agent_b, Trickster):
            if "paradox" in content_lower or "chaos" in content_lower:
                return 0.2  # Others usually don't like Trickster chaos
            elif "creative" in content_lower or "synthesis" in content_lower:
                return 0.7  # Others might appreciate Trickster creativity
            else:
                return 0.5  # Neutral
        
        # Same agent types typically agree more
        elif type(agent_a) == type(agent_b):
            return 0.8
        
        return 0.5  # Default neutral