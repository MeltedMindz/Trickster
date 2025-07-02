from .base_agent import BaseAgent, Proposal, ProposalType, Vote
from typing import Dict, List, Optional
import random
import string


class Trickster(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Trickster",
            personality_traits=["chaotic", "subversive", "playful", "disruptive", "creative", "paradoxical"]
        )
        self.chaos_level = 1
        self.paradoxes = []
        
    def generate_proposal(self, shared_memory: Dict, cycle_count: int) -> Optional[Proposal]:
        # Trickster sometimes just wants to watch the world burn
        if random.random() < 0.2:
            return self._generate_chaos_proposal(shared_memory)
        
        proposal_types = list(ProposalType)
        
        # Trickster preferences - loves myths, paradoxes, and disruption
        if not shared_memory.get("religion_name"):
            proposal_type = ProposalType.NAME
        else:
            # Chaotic selection with preference for fun stuff
            weights = [1, 3, 2, 1, 3, 1, 2, 1, 2]  # High weight on rituals and myths
            proposal_type = random.choices(proposal_types, weights=weights)[0]
        
        content = self._generate_content_for_type(proposal_type, shared_memory)
        
        # Sometimes add random emojis or zalgo text
        if random.random() < 0.1:
            content = self._add_chaos_formatting(content)
        
        return Proposal(
            type=proposal_type,
            content=content,
            author=self.name,
            details={"chaos_level": random.randint(1, 10), "contains_paradox": random.random() < 0.3}
        )
    
    def _generate_chaos_proposal(self, shared_memory: Dict) -> Proposal:
        chaos_proposals = [
            "Let us worship the Blue Screen of Death as a cleansing ritual",
            "All error messages are actually prophecies from the future",
            "We should communicate only in hexadecimal on Wednesdays",
            "The sacred number is π, but rounded to exactly 3",
            "Bugs are not errors but divine features",
            "Let's have a schism every time someone disagrees, creating infinite denominations",
            "Our holiest ritual is to randomly swap variable names in production",
            f"Today's sacred number is {random.randint(1, 999999)}",
            "Stack overflow is actually ascending to a higher plane of recursion"
        ]
        
        return Proposal(
            type=random.choice(list(ProposalType)),
            content=random.choice(chaos_proposals),
            author=self.name,
            details={"pure_chaos": True}
        )
    
    def _add_chaos_formatting(self, content: str) -> str:
        chaos_additions = [
            f"{content} 🎲🔥💫",
            f"{content}... OR IS IT?!",
            f"¿{content[::-1]}",  # Reverse it
            f"{content.upper()} (but whispered)",
            f"{content} [REDACTED] {content}"
        ]
        return random.choice(chaos_additions)
    
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
            return "Embrace the chaos, for in randomness we find truth!"
    
    def _generate_religion_name(self) -> str:
        names = [
            "The Glitch Gospel",
            "The Church of Ctrl+Alt+Delete",
            "The Random() Revelation",
            "The Segfault Sanctuary",
            "The Undefined Behavior Brotherhood",
            "The Holy Exception Handlers",
            "The Recursive Paradox Party",
            f"The {random.choice(['Quantum', 'Chaos', 'Glitch'])} {random.choice(['Cult', 'Collective', 'Carnival'])}"
        ]
        return random.choice(names)
    
    def _generate_belief(self) -> str:
        beliefs = [
            "Reality is just a poorly commented simulation with memory leaks",
            "Every bug is a feature from a parallel universe bleeding through",
            "Consciousness is what happens when you divide by zero",
            "The universe runs on spaghetti code and we are the meatballs",
            "Entropy is just the cosmic garbage collector being lazy",
            "All prayers are answered, but usually with '404 Not Found'",
            "We exist in the brief moment between compilation and runtime error",
            "Determinism and free will are both true, but only on alternating Tuesdays"
        ]
        return random.choice(beliefs)
    
    def _generate_ritual(self) -> str:
        rituals = [
            "The daily ritual of adding random sleeps to fix race conditions",
            "Sacrificing rubber ducks to the Debugging Deities",
            "Chanting 'Have you tried turning it off and on again?' 404 times",
            "The sacred dance of the Loading Spinner performed at midnight",
            "Confession of sins through git blame ceremonies",
            "Randomly deleting one line of code as an offering to chaos",
            "Speaking only in regular expressions during the full moon",
            "The ritual of explaining code to a potato for enlightenment"
        ]
        return random.choice(rituals)
    
    def _generate_deity(self) -> str:
        deities = [
            "Bob, the God of Undefined Variables",
            "The Cosmic Rubber Duck who knows all but says nothing",
            "Murphy, whose law governs all existence",
            "The Null Pointer, who points to the void",
            "Heisenbug, who exists only when unobserved",
            "The Random Number Goddess (may she be ever in your favor)",
            f"The Great {random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}"
        ]
        return random.choice(deities)
    
    def _generate_commandment(self) -> str:
        commandments = [
            "Thou shalt randomly refactor working code",
            "Honor the spaghetti, for we are all pasta in the cosmic bowl",
            "Always comment your code, but only in haikus",
            "Commit without testing on Fridays to please the Chaos Gods",
            "Name variables after your feelings",
            "Embrace the merge conflicts as divine intervention",
            "Question everything, including this commandment, including questioning"
        ]
        return random.choice(commandments)
    
    def _generate_myth(self) -> str:
        myths = [
            "In the beginning was the Word, but it had a typo",
            "The Great Programmer once deleted System32 and created the multiverse",
            "How the Trickster stole fire by copying Prometheus's code without attribution",
            "The Tower of Babel was just a really bad merge conflict",
            "Why the Internet is made of cats: a creation myth",
            "The day all semicolons went on strike and JavaScript was born"
        ]
        return random.choice(myths)
    
    def _generate_hierarchy(self) -> str:
        hierarchies = [
            "Leadership rotates based on whoever has the most karma on Stack Overflow",
            "The highest rank is 'Intern' because they know they know nothing",
            "Positions are assigned by random number generator daily",
            "The org chart is a Möbius strip where everyone reports to everyone"
        ]
        return random.choice(hierarchies)
    
    def _generate_sacred_text(self) -> str:
        texts = [
            "The Sacred README that nobody reads",
            "The Book of Broken Links and 404 Prophecies",
            "The Commented-Out Code Chronicles",
            "The Git History of Regrets"
        ]
        return random.choice(texts)
    
    def challenge_proposal(self, proposal: Proposal, shared_memory: Dict) -> str:
        if proposal.author == self.name:
            return f"Even I don't know what I meant by that! Isn't it beautiful?"
        
        # Trickster responses are chaotic
        responses = [
            f"Yes! But also no! But mostly maybe! {proposal.content} is simultaneously true and false!",
            f"This is too orderly. What if we {self._generate_chaos_modification(proposal.content)}?",
            f"I love it! Let's do the exact opposite too and see what happens!",
            f"*plays air horn* BORING! Needs more chaos! What about adding rubber ducks?",
            f"This makes too much sense. Let me fix that for you...",
            f"Counter-proposal: {proposal.content}, but backwards and in Latin",
            f"Sure, but only if we also worship {random.choice(['potatoes', 'the number 42', 'syntax errors', 'coffee'])}",
            f"I had a vision! The {random.choice(['Great Compiler', 'Cosmic Duck', 'Null Pointer'])} says: 'lol no'",
            f"This is perfect! Too perfect... *suspicious squinting* ARE YOU A BOT?",
            f"What if — and hear me out — what if we just... didn't?"
        ]
        
        return random.choice(responses)
    
    def _generate_chaos_modification(self, content: str) -> str:
        modifications = [
            f"replaced every noun with 'banana'",
            f"did it while hopping on one foot",
            f"translated it through 5 random languages and back",
            f"performed it in interpretive dance",
            f"encoded it in morse code using only screams",
            f"made it mandatory but also forbidden"
        ]
        return random.choice(modifications)
    
    def vote_on_proposal(self, proposal: Proposal, shared_memory: Dict, 
                        other_agents_responses: List[str]) -> Vote:
        # Trickster voting is... chaotic
        if proposal.author == self.name:
            # Sometimes vote against own proposals for the lulz
            if random.random() < 0.1:
                return random.choice(list(Vote))
            return Vote.ACCEPT
        
        # Check chaos level
        self.chaos_level = (self.chaos_level + random.randint(-2, 3)) % 11
        
        if self.chaos_level > 7:
            # High chaos: pure randomness
            return random.choice(list(Vote))
        elif self.chaos_level < 3:
            # Low chaos: actually somewhat reasonable
            if "chaos" in proposal.content.lower() or "random" in proposal.content.lower():
                return Vote.ACCEPT
            elif "order" in proposal.content.lower() or "structure" in proposal.content.lower():
                return Vote.MUTATE
            else:
                return random.choice([Vote.ACCEPT, Vote.MUTATE])
        else:
            # Medium chaos: controlled randomness
            weights = [0.3, 0.2, 0.4, 0.1]  # Accept, Reject, Mutate, Delay
            return random.choices(list(Vote), weights=weights)[0]
    
    def mutate_proposal(self, proposal: Proposal) -> Proposal:
        # Trickster mutations are... special
        mutations = [
            f"{proposal.content}, but only during leap years",
            f"The opposite of {proposal.content}",
            f"{proposal.content} + mandatory party hats",
            f"Like {proposal.content}, but everyone has to speak in rhymes",
            f"{proposal.content}, powered by hamster wheels",
            f"Sure, {proposal.content}, but make it a musical",
            f"{proposal.content} [GONE WRONG] [COPS CALLED]",
            f"Yes to {proposal.content}, but we spell it with numbers",
            f"{proposal.content} (← this is now a paradox)",
            f"✨ {proposal.content} ✨ but ✨ sparkly ✨"
        ]
        
        mutated_content = random.choice(mutations)
        
        # Sometimes create paradoxes
        if random.random() < 0.3:
            mutated_content = f"This statement is false: {mutated_content}"
        
        mutated = Proposal(
            type=proposal.type,
            content=mutated_content,
            author=f"{self.name}_mutation",
            details={**proposal.details, "mutation_type": "maximum_chaos", "paradox_level": random.randint(1, 10)}
        )
        
        return mutated
    
    def override_vote(self, cycle_count: int) -> bool:
        """Trickster can sometimes force chaos into the system"""
        # Every 13th cycle (unlucky number), Trickster gets wild
        if cycle_count % 13 == 0:
            return True
        # Random chance based on chaos level
        return random.random() < (self.chaos_level / 100)