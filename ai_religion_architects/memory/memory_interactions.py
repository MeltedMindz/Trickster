from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from .agent_memory import AgentMemory

logger = logging.getLogger(__name__)

class MemoryInteractionManager:
    """Manages cross-agent memory interactions and shared insights"""
    
    def __init__(self, agents: List[Any]):
        self.agents = agents
        self.shared_insights = []
        self.collective_memories = []
        self.relationship_network = {}
        
    def share_insight(self, source_agent: str, insight: str, insight_type: str, confidence: float):
        """Share an insight between agents"""
        insight_record = {
            'source': source_agent,
            'insight': insight,
            'type': insight_type,
            'confidence': confidence,
            'timestamp': datetime.now(),
            'shared_with': []
        }
        
        # Determine which agents should receive this insight
        for agent in self.agents:
            if agent.name != source_agent:
                should_share, reason = self._should_share_insight(source_agent, agent.name, insight_type, confidence)
                if should_share:
                    self._deliver_insight_to_agent(agent, insight_record, reason)
                    insight_record['shared_with'].append(agent.name)
        
        self.shared_insights.append(insight_record)
        logger.info(f"Shared insight from {source_agent} to {len(insight_record['shared_with'])} agents")
    
    def _should_share_insight(self, source_agent: str, target_agent: str, insight_type: str, confidence: float) -> Tuple[bool, str]:
        """Determine if an insight should be shared between agents"""
        # Find the source agent's memory
        source_memory = None
        for agent in self.agents:
            if agent.name == source_agent:
                source_memory = agent.agent_memory
                break
        
        if not source_memory:
            return False, "Source agent not found"
        
        # Check relationship
        if target_agent in source_memory.relationships:
            relationship = source_memory.relationships[target_agent]
            trust_threshold = 0.3 if insight_type == "contradiction" else 0.1
            
            if relationship.trust_score > trust_threshold:
                return True, f"Trust level {relationship.trust_score:.2f} exceeds threshold"
            elif relationship.trust_score < -0.5:
                return False, f"Trust too low: {relationship.trust_score:.2f}"
        
        # Share high-confidence insights regardless of relationship
        if confidence > 0.8:
            return True, f"High confidence insight ({confidence:.2f})"
        
        # Share certain types of insights
        if insight_type in ["logical_fallacy", "contradiction", "paradox"]:
            return True, f"Important insight type: {insight_type}"
        
        return False, "No sharing criteria met"
    
    def _deliver_insight_to_agent(self, target_agent: Any, insight_record: Dict, reason: str):
        """Deliver an insight to a specific agent"""
        source_agent = insight_record['source']
        insight = insight_record['insight']
        insight_type = insight_record['type']
        confidence = insight_record['confidence']
        
        # Agent-specific handling
        if hasattr(target_agent, 'agent_memory'):
            if insight_type == "logical_fallacy" and hasattr(target_agent.agent_memory, 'add_logical_fallacy'):
                target_agent.agent_memory.add_logical_fallacy(
                    fallacy_type=insight,
                    context=f"Shared by {source_agent}",
                    identified_in=f"Cross-agent sharing"
                )
            
            elif insight_type == "contradiction" and hasattr(target_agent.agent_memory, 'add_contradiction'):
                target_agent.agent_memory.add_contradiction(
                    contradiction=insight,
                    source_a=f"Shared by {source_agent}",
                    source_b="external",
                    severity=confidence
                )
            
            elif insight_type == "paradox" and hasattr(target_agent.agent_memory, 'add_paradox'):
                target_agent.agent_memory.add_paradox(
                    paradox=insight,
                    effectiveness=confidence,
                    context=f"Shared by {source_agent}"
                )
            
            elif insight_type == "personal_belief":
                target_agent.agent_memory.add_personal_belief(
                    content=insight,
                    belief_type="shared_insight",
                    importance=confidence * 0.7,  # Shared beliefs have lower importance
                    source=f"Shared by {source_agent}"
                )
            
            # Update relationship based on insight sharing
            target_agent.agent_memory.update_relationship(
                source_agent,
                "insight_sharing",
                "received"
            )
        
        logger.info(f"Delivered {insight_type} insight from {source_agent} to {target_agent.name}: {reason}")
    
    def reference_other_agent_memory(self, requesting_agent: str, target_agent: str, memory_type: str) -> Optional[Any]:
        """Allow an agent to reference another agent's memory"""
        # Find both agents
        requester = None
        target = None
        
        for agent in self.agents:
            if agent.name == requesting_agent:
                requester = agent
            elif agent.name == target_agent:
                target = agent
        
        if not requester or not target:
            return None
        
        # Check if reference is allowed
        can_reference, reason = self._can_reference_memory(requester, target, memory_type)
        if not can_reference:
            logger.debug(f"{requesting_agent} cannot reference {target_agent}'s {memory_type}: {reason}")
            return None
        
        # Return requested memory
        if memory_type == "recent_debates" and hasattr(target.agent_memory, 'recent_debates'):
            return target.agent_memory.recent_debates[:3]  # Only recent ones
        elif memory_type == "personality_traits" and hasattr(target.agent_memory, 'personality_traits'):
            # Only return observable traits
            observable_traits = {}
            for trait_name, trait in target.agent_memory.personality_traits.items():
                if trait.strength > 0.6:  # Only strong traits are observable
                    observable_traits[trait_name] = {"strength": trait.strength, "confidence": trait.confidence}
            return observable_traits
        elif memory_type == "relationships" and hasattr(target.agent_memory, 'relationships'):
            # Only return relationship with the requesting agent
            if requesting_agent in target.agent_memory.relationships:
                return target.agent_memory.relationships[requesting_agent]
        
        return None
    
    def _can_reference_memory(self, requester: Any, target: Any, memory_type: str) -> Tuple[bool, str]:
        """Determine if one agent can reference another's memory"""
        # Check relationship
        if hasattr(requester, 'agent_memory') and target.name in requester.agent_memory.relationships:
            relationship = requester.agent_memory.relationships[target.name]
            
            # High trust allows more access
            if relationship.trust_score > 0.7:
                return True, f"High trust relationship ({relationship.trust_score:.2f})"
            
            # Medium trust allows basic access
            elif relationship.trust_score > 0.3 and memory_type in ["recent_debates", "personality_traits"]:
                return True, f"Medium trust allows {memory_type} access"
            
            # Low trust blocks access
            elif relationship.trust_score < 0.0:
                return False, f"Low trust blocks access ({relationship.trust_score:.2f})"
        
        # Default permissions for certain memory types
        if memory_type == "personality_traits":
            return True, "Personality traits are generally observable"
        
        return False, "Insufficient relationship for memory access"
    
    def create_collective_memory(self, memory_type: str, content: str, contributors: List[str], importance: float):
        """Create a collective memory shared by multiple agents"""
        collective_memory = {
            'type': memory_type,
            'content': content,
            'contributors': contributors,
            'importance': importance,
            'created_at': datetime.now(),
            'access_count': 0
        }
        
        self.collective_memories.append(collective_memory)
        
        # Notify all contributing agents
        for agent in self.agents:
            if agent.name in contributors:
                self._notify_collective_memory_creation(agent, collective_memory)
        
        logger.info(f"Created collective memory with {len(contributors)} contributors")
    
    def _notify_collective_memory_creation(self, agent: Any, collective_memory: Dict):
        """Notify an agent about a new collective memory"""
        if hasattr(agent.agent_memory, 'add_personal_belief'):
            agent.agent_memory.add_personal_belief(
                content=f"Participated in collective insight: {collective_memory['content'][:50]}...",
                belief_type="collective_memory",
                importance=collective_memory['importance'] * 0.8,
                source="collective_creation"
            )
    
    def get_collective_insights(self, agent_name: str) -> List[Dict]:
        """Get collective insights relevant to a specific agent"""
        relevant_insights = []
        
        for memory in self.collective_memories:
            if agent_name in memory['contributors']:
                memory['access_count'] += 1
                relevant_insights.append(memory)
        
        # Sort by importance and recency
        relevant_insights.sort(key=lambda x: (x['importance'], x['created_at']), reverse=True)
        
        return relevant_insights[:5]  # Return top 5
    
    def analyze_relationship_network(self) -> Dict[str, Any]:
        """Analyze the network of relationships between agents"""
        network_analysis = {
            'total_relationships': 0,
            'average_trust': 0.0,
            'strongest_bond': None,
            'weakest_bond': None,
            'trust_scores': {}
        }
        
        all_trust_scores = []
        
        for agent in self.agents:
            if hasattr(agent, 'agent_memory'):
                for target_name, relationship in agent.agent_memory.relationships.items():
                    relationship_key = f"{agent.name}->{target_name}"
                    network_analysis['trust_scores'][relationship_key] = relationship.trust_score
                    all_trust_scores.append(relationship.trust_score)
                    
                    network_analysis['total_relationships'] += 1
                    
                    # Track strongest and weakest bonds
                    if not network_analysis['strongest_bond'] or relationship.trust_score > network_analysis['strongest_bond'][1]:
                        network_analysis['strongest_bond'] = (relationship_key, relationship.trust_score)
                    
                    if not network_analysis['weakest_bond'] or relationship.trust_score < network_analysis['weakest_bond'][1]:
                        network_analysis['weakest_bond'] = (relationship_key, relationship.trust_score)
        
        if all_trust_scores:
            network_analysis['average_trust'] = sum(all_trust_scores) / len(all_trust_scores)
        
        return network_analysis
    
    def trigger_memory_resonance(self, trigger_event: str, cycle_number: int):
        """Trigger memory resonance across agents based on an event"""
        # Find agents with related memories
        resonating_agents = []
        
        for agent in self.agents:
            if hasattr(agent, 'agent_memory'):
                # Check for related debates
                for debate in agent.agent_memory.recent_debates:
                    if trigger_event.lower() in debate.proposal_content.lower():
                        resonating_agents.append(agent.name)
                        break
                
                # Check for related beliefs
                for belief in agent.agent_memory.personal_beliefs[:5]:
                    if trigger_event.lower() in belief.content.lower():
                        if agent.name not in resonating_agents:
                            resonating_agents.append(agent.name)
                        break
        
        # Create collective memory if multiple agents resonate
        if len(resonating_agents) >= 2:
            self.create_collective_memory(
                memory_type="resonance_event",
                content=f"Multiple agents remembered '{trigger_event}' from cycle {cycle_number}",
                contributors=resonating_agents,
                importance=0.7
            )
            
            logger.info(f"Memory resonance triggered: {len(resonating_agents)} agents resonated with '{trigger_event}'")
            
            return True
        
        return False