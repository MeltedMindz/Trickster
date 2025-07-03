import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AgentMemoryExporter:
    """Exports agent memory statistics for the frontend"""
    
    def __init__(self, agents: List[Any] = None, memory_dir: str = "logs_agent_memories", export_dir: str = "public/data"):
        self.agents = agents or []  # Can work with agent instances or database files
        self.memory_dir = memory_dir
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
    
    def export_all_agent_memories(self) -> Dict[str, Any]:
        """Export memory statistics for all agents"""
        memory_export = {
            "last_updated": datetime.now().isoformat(),
            "agents": {},
            "relationship_network": {},
            "collective_insights": {
                "total_shared_insights": 0,
                "memory_resonance_events": 0,
                "collective_memories": 0
            }
        }
        
        # Try to export from agent instances first
        if self.agents:
            for agent in self.agents:
                if hasattr(agent, 'agent_memory'):
                    memory_export["agents"][agent.name] = self._export_agent_memory(agent)
            memory_export["relationship_network"] = self._analyze_relationship_network()
        else:
            # Export from database files
            memory_export = self.export_from_database_files()
        
        # Save to file
        export_path = os.path.join(self.export_dir, "agent_memories.json")
        with open(export_path, 'w') as f:
            json.dump(memory_export, f, indent=2)
        
        logger.info(f"Exported agent memory statistics to {export_path}")
        return memory_export
    
    def export_from_database_files(self) -> Dict[str, Any]:
        """Export memory statistics directly from database files"""
        memory_export = {
            "last_updated": datetime.now().isoformat(),
            "agents": {},
            "relationship_network": {},
            "collective_insights": {
                "total_shared_insights": 0,
                "memory_resonance_events": 0,
                "collective_memories": 0
            }
        }
        
        # Check for agent database files
        agent_names = ["zealot", "skeptic", "trickster"]
        
        for agent_name in agent_names:
            db_path = os.path.join(self.memory_dir, f"{agent_name}_memory.db")
            if os.path.exists(db_path):
                memory_export["agents"][agent_name.capitalize()] = self._export_from_database(agent_name, db_path)
        
        # Analyze relationship network from database
        memory_export["relationship_network"] = self._analyze_relationships_from_database()
        
        return memory_export
    
    def _export_from_database(self, agent_name: str, db_path: str) -> Dict[str, Any]:
        """Export memory statistics from a database file"""
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row  # This enables column access by name
                
                stats = {
                    "agent_type": agent_name.capitalize(),
                    "personality_evolution": self._get_personality_from_db(conn),
                    "belief_system": self._get_beliefs_from_db(conn),
                    "relationships": self._get_relationships_from_db(conn),
                    "debate_performance": self._get_debates_from_db(conn),
                    "memory_specialization": {"specialization": f"{agent_name.capitalize()} Specialization"},
                    "evolution_timeline": []
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Error exporting {agent_name} memory from database: {e}")
            return {"error": str(e), "agent_type": agent_name.capitalize()}
    
    def _get_personality_from_db(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Get personality traits from database"""
        try:
            cursor = conn.execute("SELECT name, strength, confidence, last_updated FROM personality_traits")
            traits = {}
            total_strength = 0
            strongest_trait = None
            weakest_trait = None
            evolved_traits = 0
            
            for row in cursor:
                trait_name = row['name']
                strength = row['strength']
                confidence = row['confidence']
                
                traits[trait_name] = {
                    "strength": round(strength, 3),
                    "confidence": round(confidence, 3),
                    "last_updated": row['last_updated']
                }
                
                total_strength += strength
                
                if strongest_trait is None or strength > strongest_trait[1]:
                    strongest_trait = (trait_name, strength)
                
                if weakest_trait is None or strength < weakest_trait[1]:
                    weakest_trait = (trait_name, strength)
                
                if abs(strength - 0.5) > 0.15:
                    evolved_traits += 1
            
            # Get evolution points from stats table
            cursor = conn.execute("SELECT evolution_points FROM agent_stats WHERE id = 1")
            row = cursor.fetchone()
            evolution_points = row['evolution_points'] if row else 0
            
            return {
                "traits": traits,
                "summary": {
                    "total_traits": len(traits),
                    "average_strength": round(total_strength / len(traits), 3) if traits else 0,
                    "strongest_trait": strongest_trait[0] if strongest_trait else None,
                    "strongest_value": round(strongest_trait[1], 3) if strongest_trait else 0,
                    "weakest_trait": weakest_trait[0] if weakest_trait else None,
                    "weakest_value": round(weakest_trait[1], 3) if weakest_trait else 0,
                    "evolved_traits": evolved_traits,
                    "evolution_points": evolution_points
                }
            }
        except Exception as e:
            logger.error(f"Error getting personality from database: {e}")
            return {}
    
    def _get_beliefs_from_db(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Get beliefs from database"""
        try:
            cursor = conn.execute("""
                SELECT content, belief_type, confidence_level, importance, 
                       times_challenged, times_defended 
                FROM personal_beliefs 
                ORDER BY importance DESC
            """)
            
            beliefs = []
            high_confidence_beliefs = 0
            challenged_beliefs = 0
            defended_beliefs = 0
            belief_types = {}
            
            for row in cursor:
                belief = {
                    "content": row['content'],
                    "belief_type": row['belief_type'],
                    "confidence_level": row['confidence_level'],
                    "importance": row['importance'],
                    "times_challenged": row['times_challenged'],
                    "times_defended": row['times_defended']
                }
                beliefs.append(belief)
                
                if row['confidence_level'] > 0.8:
                    high_confidence_beliefs += 1
                if row['times_challenged'] > 0:
                    challenged_beliefs += 1
                if row['times_defended'] > 0:
                    defended_beliefs += 1
                
                belief_type = row['belief_type']
                belief_types[belief_type] = belief_types.get(belief_type, 0) + 1
            
            # Top beliefs
            top_beliefs = []
            for belief in beliefs[:3]:
                content = belief['content']
                top_beliefs.append({
                    "content": content[:50] + "..." if len(content) > 50 else content,
                    "importance": round(belief['importance'], 3),
                    "confidence": round(belief['confidence_level'], 3),
                    "type": belief['belief_type'],
                    "times_challenged": belief['times_challenged'],
                    "times_defended": belief['times_defended']
                })
            
            return {
                "total_beliefs": len(beliefs),
                "high_confidence_beliefs": high_confidence_beliefs,
                "challenged_beliefs": challenged_beliefs,
                "defended_beliefs": defended_beliefs,
                "belief_types": belief_types,
                "top_beliefs": top_beliefs
            }
        except Exception as e:
            logger.error(f"Error getting beliefs from database: {e}")
            return {}
    
    def _get_relationships_from_db(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Get relationships from database"""
        try:
            cursor = conn.execute("""
                SELECT target_agent, trust_score, agreement_rate, total_interactions,
                       successful_alliances, betrayals
                FROM relationships
            """)
            
            relationships = {}
            trust_scores = []
            trusted_allies = 0
            enemies = 0
            
            for row in cursor:
                trust_score = row['trust_score']
                trust_scores.append(trust_score)
                
                if trust_score > 0.5:
                    trusted_allies += 1
                elif trust_score < -0.3:
                    enemies += 1
                
                relationships[row['target_agent']] = {
                    "trust_score": round(trust_score, 3),
                    "agreement_rate": round(row['agreement_rate'], 3),
                    "total_interactions": row['total_interactions'],
                    "successful_alliances": row['successful_alliances'],
                    "betrayals": row['betrayals'],
                    "relationship_status": self._get_relationship_status(trust_score)
                }
            
            avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0
            most_trusted = max(relationships.items(), key=lambda x: x[1]['trust_score']) if relationships else None
            least_trusted = min(relationships.items(), key=lambda x: x[1]['trust_score']) if relationships else None
            
            return {
                "total_relationships": len(relationships),
                "trusted_allies": trusted_allies,
                "enemies": enemies,
                "average_trust": round(avg_trust, 3),
                "average_agreement": 0.5,  # Would need to calculate from data
                "most_trusted": most_trusted[0] if most_trusted else None,
                "most_trusted_score": most_trusted[1]['trust_score'] if most_trusted else 0,
                "least_trusted": least_trusted[0] if least_trusted else None,
                "least_trusted_score": least_trusted[1]['trust_score'] if least_trusted else 0,
                "relationships": relationships
            }
        except Exception as e:
            logger.error(f"Error getting relationships from database: {e}")
            return {}
    
    def _get_debates_from_db(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Get debate performance from database"""
        try:
            # Get stats from agent_stats table
            cursor = conn.execute("""
                SELECT total_proposals, successful_proposals, total_challenges, 
                       successful_challenges, total_votes
                FROM agent_stats WHERE id = 1
            """)
            row = cursor.fetchone()
            
            if not row:
                return {}
            
            total_proposals = row['total_proposals']
            successful_proposals = row['successful_proposals']
            total_challenges = row['total_challenges']
            successful_challenges = row['successful_challenges']
            total_votes = row['total_votes']
            
            proposal_success_rate = successful_proposals / total_proposals if total_proposals > 0 else 0
            challenge_success_rate = successful_challenges / total_challenges if total_challenges > 0 else 0
            
            # Get recent debates
            cursor = conn.execute("""
                SELECT cycle_number, agent_role, outcome, personal_satisfaction, emotional_impact
                FROM debate_memories 
                ORDER BY timestamp DESC 
                LIMIT 3
            """)
            
            recent_debates = []
            satisfactions = []
            role_counts = {}
            
            for row in cursor:
                recent_debates.append({
                    "cycle": row['cycle_number'],
                    "role": row['agent_role'],
                    "outcome": row['outcome'],
                    "satisfaction": round(row['personal_satisfaction'], 3),
                    "emotional_impact": round(row['emotional_impact'], 3)
                })
                satisfactions.append(row['personal_satisfaction'])
                role = row['agent_role']
                role_counts[role] = role_counts.get(role, 0) + 1
            
            avg_satisfaction = sum(satisfactions) / len(satisfactions) if satisfactions else 0
            
            return {
                "total_debates": total_votes,
                "total_proposals": total_proposals,
                "successful_proposals": successful_proposals,
                "proposal_success_rate": round(proposal_success_rate, 3),
                "total_challenges": total_challenges,
                "successful_challenges": successful_challenges,
                "challenge_success_rate": round(challenge_success_rate, 3),
                "average_satisfaction": round(avg_satisfaction, 3),
                "role_distribution": role_counts,
                "recent_debates": recent_debates
            }
        except Exception as e:
            logger.error(f"Error getting debates from database: {e}")
            return {}
    
    def _analyze_relationships_from_database(self) -> Dict[str, Any]:
        """Analyze relationship network from database files"""
        trust_matrix = {}
        all_trust_scores = []
        
        agent_names = ["zealot", "skeptic", "trickster"]
        
        for agent_name in agent_names:
            db_path = os.path.join(self.memory_dir, f"{agent_name}_memory.db")
            if os.path.exists(db_path):
                try:
                    with sqlite3.connect(db_path) as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.execute("SELECT target_agent, trust_score FROM relationships")
                        
                        trust_matrix[agent_name.capitalize()] = {}
                        for row in cursor:
                            trust_score = row['trust_score']
                            trust_matrix[agent_name.capitalize()][row['target_agent']] = trust_score
                            all_trust_scores.append(trust_score)
                            
                except Exception as e:
                    logger.error(f"Error analyzing relationships for {agent_name}: {e}")
        
        if all_trust_scores:
            avg_network_trust = sum(all_trust_scores) / len(all_trust_scores)
            network_polarization = max(all_trust_scores) - min(all_trust_scores)
        else:
            avg_network_trust = 0
            network_polarization = 0
        
        return {
            "average_network_trust": round(avg_network_trust, 3),
            "network_polarization": round(network_polarization, 3),
            "trust_matrix": trust_matrix,
            "total_relationships": len(all_trust_scores)
        }
    
    def _export_agent_memory(self, agent: Any) -> Dict[str, Any]:
        """Export memory statistics for a single agent"""
        memory = agent.agent_memory
        
        # Basic stats
        stats = {
            "agent_type": agent.__class__.__name__,
            "personality_evolution": self._get_personality_stats(memory),
            "belief_system": self._get_belief_stats(memory),
            "relationships": self._get_relationship_stats(memory),
            "debate_performance": self._get_debate_stats(memory),
            "memory_specialization": self._get_specialization_stats(agent, memory),
            "evolution_timeline": self._get_evolution_timeline(memory)
        }
        
        return stats
    
    def _get_personality_stats(self, memory: Any) -> Dict[str, Any]:
        """Get personality trait statistics"""
        if not hasattr(memory, 'personality_traits'):
            return {}
        
        traits = {}
        total_strength = 0
        strongest_trait = None
        weakest_trait = None
        evolved_traits = 0
        
        for trait_name, trait in memory.personality_traits.items():
            traits[trait_name] = {
                "strength": round(trait.strength, 3),
                "confidence": round(trait.confidence, 3),
                "last_updated": trait.last_updated.isoformat() if hasattr(trait.last_updated, 'isoformat') else str(trait.last_updated)
            }
            
            total_strength += trait.strength
            
            if strongest_trait is None or trait.strength > strongest_trait[1]:
                strongest_trait = (trait_name, trait.strength)
            
            if weakest_trait is None or trait.strength < weakest_trait[1]:
                weakest_trait = (trait_name, trait.strength)
            
            # Count as evolved if strength is significantly different from 0.5 baseline
            if abs(trait.strength - 0.5) > 0.15:
                evolved_traits += 1
        
        return {
            "traits": traits,
            "summary": {
                "total_traits": len(traits),
                "average_strength": round(total_strength / len(traits), 3) if traits else 0,
                "strongest_trait": strongest_trait[0] if strongest_trait else None,
                "strongest_value": round(strongest_trait[1], 3) if strongest_trait else 0,
                "weakest_trait": weakest_trait[0] if weakest_trait else None,
                "weakest_value": round(weakest_trait[1], 3) if weakest_trait else 0,
                "evolved_traits": evolved_traits,
                "evolution_points": getattr(memory, 'evolution_points', 0)
            }
        }
    
    def _get_belief_stats(self, memory: Any) -> Dict[str, Any]:
        """Get personal belief system statistics"""
        if not hasattr(memory, 'personal_beliefs'):
            return {}
        
        beliefs = memory.personal_beliefs
        
        # Calculate stats
        total_beliefs = len(beliefs)
        high_confidence_beliefs = len([b for b in beliefs if b.confidence_level > 0.8])
        challenged_beliefs = len([b for b in beliefs if b.times_challenged > 0])
        defended_beliefs = len([b for b in beliefs if b.times_defended > 0])
        
        belief_types = {}
        for belief in beliefs:
            belief_types[belief.belief_type] = belief_types.get(belief.belief_type, 0) + 1
        
        # Top beliefs by importance
        top_beliefs = sorted(beliefs, key=lambda x: x.importance, reverse=True)[:3]
        
        return {
            "total_beliefs": total_beliefs,
            "high_confidence_beliefs": high_confidence_beliefs,
            "challenged_beliefs": challenged_beliefs,
            "defended_beliefs": defended_beliefs,
            "belief_types": belief_types,
            "top_beliefs": [
                {
                    "content": belief.content[:50] + "..." if len(belief.content) > 50 else belief.content,
                    "importance": round(belief.importance, 3),
                    "confidence": round(belief.confidence_level, 3),
                    "type": belief.belief_type,
                    "times_challenged": belief.times_challenged,
                    "times_defended": belief.times_defended
                }
                for belief in top_beliefs
            ]
        }
    
    def _get_relationship_stats(self, memory: Any) -> Dict[str, Any]:
        """Get relationship statistics"""
        if not hasattr(memory, 'relationships'):
            return {}
        
        relationships = memory.relationships
        
        # Calculate stats
        total_relationships = len(relationships)
        trusted_allies = len([r for r in relationships.values() if r.trust_score > 0.5])
        enemies = len([r for r in relationships.values() if r.trust_score < -0.3])
        
        avg_trust = sum(r.trust_score for r in relationships.values()) / total_relationships if total_relationships > 0 else 0
        avg_agreement = sum(r.agreement_rate for r in relationships.values()) / total_relationships if total_relationships > 0 else 0
        
        # Most and least trusted
        if relationships:
            most_trusted = max(relationships.items(), key=lambda x: x[1].trust_score)
            least_trusted = min(relationships.items(), key=lambda x: x[1].trust_score)
        else:
            most_trusted = least_trusted = None
        
        relationship_details = {}
        for agent_name, rel in relationships.items():
            relationship_details[agent_name] = {
                "trust_score": round(rel.trust_score, 3),
                "agreement_rate": round(rel.agreement_rate, 3),
                "total_interactions": rel.total_interactions,
                "successful_alliances": rel.successful_alliances,
                "betrayals": rel.betrayals,
                "relationship_status": self._get_relationship_status(rel.trust_score)
            }
        
        return {
            "total_relationships": total_relationships,
            "trusted_allies": trusted_allies,
            "enemies": enemies,
            "average_trust": round(avg_trust, 3),
            "average_agreement": round(avg_agreement, 3),
            "most_trusted": most_trusted[0] if most_trusted else None,
            "most_trusted_score": round(most_trusted[1].trust_score, 3) if most_trusted else 0,
            "least_trusted": least_trusted[0] if least_trusted else None,
            "least_trusted_score": round(least_trusted[1].trust_score, 3) if least_trusted else 0,
            "relationships": relationship_details
        }
    
    def _get_relationship_status(self, trust_score: float) -> str:
        """Convert trust score to relationship status"""
        if trust_score > 0.7:
            return "Trusted Ally"
        elif trust_score > 0.3:
            return "Friendly"
        elif trust_score > -0.1:
            return "Neutral"
        elif trust_score > -0.5:
            return "Distrustful"
        else:
            return "Enemy"
    
    def _get_debate_stats(self, memory: Any) -> Dict[str, Any]:
        """Get debate performance statistics"""
        if not hasattr(memory, 'recent_debates'):
            return {}
        
        debates = memory.recent_debates
        
        # Performance stats
        total_debates = getattr(memory, 'total_votes', 0)
        successful_proposals = getattr(memory, 'successful_proposals', 0)
        total_proposals = getattr(memory, 'total_proposals', 0)
        successful_challenges = getattr(memory, 'successful_challenges', 0)
        total_challenges = getattr(memory, 'total_challenges', 0)
        
        # Calculate rates
        proposal_success_rate = successful_proposals / total_proposals if total_proposals > 0 else 0
        challenge_success_rate = successful_challenges / total_challenges if total_challenges > 0 else 0
        
        # Recent satisfaction
        recent_satisfaction = [d.personal_satisfaction for d in debates[-5:]] if debates else []
        avg_satisfaction = sum(recent_satisfaction) / len(recent_satisfaction) if recent_satisfaction else 0
        
        # Role distribution
        role_counts = {}
        for debate in debates:
            role_counts[debate.agent_role] = role_counts.get(debate.agent_role, 0) + 1
        
        return {
            "total_debates": total_debates,
            "total_proposals": total_proposals,
            "successful_proposals": successful_proposals,
            "proposal_success_rate": round(proposal_success_rate, 3),
            "total_challenges": total_challenges,
            "successful_challenges": successful_challenges,
            "challenge_success_rate": round(challenge_success_rate, 3),
            "average_satisfaction": round(avg_satisfaction, 3),
            "role_distribution": role_counts,
            "recent_debates": [
                {
                    "cycle": debate.cycle_number,
                    "role": debate.agent_role,
                    "outcome": debate.outcome,
                    "satisfaction": round(debate.personal_satisfaction, 3),
                    "emotional_impact": round(debate.emotional_impact, 3)
                }
                for debate in debates[-3:]  # Last 3 debates
            ]
        }
    
    def _get_specialization_stats(self, agent: Any, memory: Any) -> Dict[str, Any]:
        """Get agent-specific specialization statistics"""
        agent_type = agent.__class__.__name__
        
        if agent_type == "Zealot":
            return self._get_zealot_stats(memory)
        elif agent_type == "Skeptic":
            return self._get_skeptic_stats(memory)
        elif agent_type == "Trickster":
            return self._get_trickster_stats(memory)
        else:
            return {}
    
    def _get_zealot_stats(self, memory: Any) -> Dict[str, Any]:
        """Get Zealot-specific statistics"""
        stats = {"specialization": "Order & Structure"}
        
        if hasattr(memory, 'ritual_preferences'):
            stats["ritual_preferences"] = len(memory.ritual_preferences)
            if memory.ritual_preferences:
                top_ritual = max(memory.ritual_preferences, key=lambda x: x['effectiveness'])
                stats["most_effective_ritual"] = {
                    "element": top_ritual['element'],
                    "effectiveness": round(top_ritual['effectiveness'], 3)
                }
        
        if hasattr(memory, 'doctrinal_hierarchies'):
            stats["doctrinal_priorities"] = len(memory.doctrinal_hierarchies)
        
        if hasattr(memory, 'heretical_concerns'):
            stats["heretical_concerns"] = len(memory.heretical_concerns)
            if memory.heretical_concerns:
                top_concern = max(memory.heretical_concerns, key=lambda x: x['severity'])
                stats["top_heretical_concern"] = {
                    "concern": top_concern['concern'][:30] + "...",
                    "severity": round(top_concern['severity'], 3)
                }
        
        if hasattr(memory, 'successful_conversions'):
            stats["successful_conversions"] = memory.successful_conversions
        
        return stats
    
    def _get_skeptic_stats(self, memory: Any) -> Dict[str, Any]:
        """Get Skeptic-specific statistics"""
        stats = {"specialization": "Logic & Evidence"}
        
        if hasattr(memory, 'logical_fallacies_found'):
            stats["fallacies_identified"] = len(memory.logical_fallacies_found)
            
            # Count fallacy types
            fallacy_types = {}
            for fallacy in memory.logical_fallacies_found:
                fallacy_type = fallacy['fallacy_type']
                fallacy_types[fallacy_type] = fallacy_types.get(fallacy_type, 0) + 1
            stats["fallacy_types"] = fallacy_types
        
        if hasattr(memory, 'contradiction_database'):
            stats["contradictions_found"] = len(memory.contradiction_database)
            if memory.contradiction_database:
                top_contradiction = max(memory.contradiction_database, key=lambda x: x['severity'])
                stats["most_severe_contradiction"] = {
                    "contradiction": top_contradiction['contradiction'][:50] + "...",
                    "severity": round(top_contradiction['severity'], 3)
                }
        
        if hasattr(memory, 'evidence_standards'):
            stats["evidence_standards"] = {
                claim_type: data['required_strength'] 
                for claim_type, data in memory.evidence_standards.items()
            }
        
        if hasattr(memory, 'successful_refutations'):
            stats["successful_refutations"] = memory.successful_refutations
        
        return stats
    
    def _get_trickster_stats(self, memory: Any) -> Dict[str, Any]:
        """Get Trickster-specific statistics"""
        stats = {"specialization": "Chaos & Creativity"}
        
        if hasattr(memory, 'chaos_level'):
            stats["current_chaos_level"] = round(memory.chaos_level, 3)
        
        if hasattr(memory, 'metamorphosis_count'):
            stats["metamorphoses"] = memory.metamorphosis_count
        
        if hasattr(memory, 'paradox_collection'):
            stats["paradoxes_created"] = len(memory.paradox_collection)
            if memory.paradox_collection:
                top_paradox = max(memory.paradox_collection, key=lambda x: x['effectiveness'])
                stats["most_effective_paradox"] = {
                    "paradox": top_paradox['paradox'][:50] + "...",
                    "effectiveness": round(top_paradox['effectiveness'], 3)
                }
        
        if hasattr(memory, 'creative_breakthroughs'):
            stats["creative_breakthroughs"] = len(memory.creative_breakthroughs)
        
        if hasattr(memory, 'successful_syntheses'):
            stats["successful_syntheses"] = len(memory.successful_syntheses)
        
        if hasattr(memory, 'chaos_interventions'):
            beneficial_chaos = len([ci for ci in memory.chaos_interventions if ci['beneficial']])
            stats["beneficial_chaos_interventions"] = beneficial_chaos
        
        return stats
    
    def _get_evolution_timeline(self, memory: Any) -> List[Dict[str, Any]]:
        """Get timeline of significant memory evolution events"""
        timeline = []
        
        # Add recent debates as evolution points
        if hasattr(memory, 'recent_debates'):
            for debate in memory.recent_debates[-3:]:
                timeline.append({
                    "timestamp": debate.timestamp.isoformat() if hasattr(debate.timestamp, 'isoformat') else str(debate.timestamp),
                    "event_type": "debate",
                    "description": f"Cycle {debate.cycle_number}: {debate.agent_role} role, {debate.outcome} outcome",
                    "impact": round(debate.emotional_impact, 3)
                })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return timeline[:5]  # Last 5 events
    
    def _analyze_relationship_network(self) -> Dict[str, Any]:
        """Analyze the overall relationship network"""
        all_relationships = []
        trust_matrix = {}
        
        for agent in self.agents:
            if hasattr(agent, 'agent_memory') and hasattr(agent.agent_memory, 'relationships'):
                trust_matrix[agent.name] = {}
                for target, relationship in agent.agent_memory.relationships.items():
                    trust_matrix[agent.name][target] = relationship.trust_score
                    all_relationships.append(relationship.trust_score)
        
        if all_relationships:
            avg_network_trust = sum(all_relationships) / len(all_relationships)
            network_polarization = max(all_relationships) - min(all_relationships)
        else:
            avg_network_trust = 0
            network_polarization = 0
        
        return {
            "average_network_trust": round(avg_network_trust, 3),
            "network_polarization": round(network_polarization, 3),
            "trust_matrix": trust_matrix,
            "total_relationships": len(all_relationships)
        }