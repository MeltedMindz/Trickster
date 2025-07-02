from typing import List, Dict, Tuple, Optional
from collections import Counter
import random
from datetime import datetime

from ..agents import BaseAgent, Proposal, Vote, ProposalType, Zealot, Skeptic, Trickster
from ..memory import SharedMemory
from ..utils.logger import DebateLogger


class DebateCycle:
    def __init__(self, agents: List[BaseAgent], shared_memory: SharedMemory, logger: DebateLogger):
        self.agents = agents
        self.shared_memory = shared_memory
        self.logger = logger
        self.cycle_count = 0
        self.current_proposer_index = 0
        
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
        
        # Record debate in memory
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
        
        # Check for faction opportunities
        self._check_faction_formation(votes, proposal)
        
        # Rotate proposer
        self._rotate_proposer()
        
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