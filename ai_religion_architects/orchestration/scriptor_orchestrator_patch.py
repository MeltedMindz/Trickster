"""
Patch to integrate Scriptor agent into the existing Claude orchestrator.
This adds sacred scripture writing capabilities to the AI Religion Architects system.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .scriptor_integration import ScriptorIntegration
from ..utils.scripture_exporter import ScriptureExporter

logger = logging.getLogger(__name__)


class ScriptorOrchestratorPatch:
    """
    Patch class to add Scriptor functionality to existing orchestrator.
    This integrates daily scripture generation and sacred text management.
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.scriptor_integration = ScriptorIntegration(
            log_dir=orchestrator.log_dir,
            scripture_db_path="data/sacred_scripture.db"
        )
        self.scripture_exporter = ScriptureExporter()
        
        # Initialize Scriptor agent
        self.scriptor = self.scriptor_integration.initialize_scriptor()
        
        logger.info("🖋️  Scriptor orchestrator patch initialized")
    
    async def handle_post_cycle_operations(self, cycle_number: int):
        """Handle post-cycle operations including scripture generation"""
        try:
            # Daily scripture generation (every 24 cycles)
            if self.scriptor_integration.should_write_scripture(cycle_number):
                await self._write_daily_scripture(cycle_number)
            
            # Export scripture data for frontend (every cycle)
            await self._export_scripture_data()
            
        except Exception as e:
            logger.error(f"❌ Scriptor post-cycle operations failed: {e}")
    
    async def _write_daily_scripture(self, cycle_number: int):
        """Write daily scripture entry"""
        try:
            logger.info(f"🖋️  Writing daily scripture for cycle {cycle_number}")
            
            # Use orchestrator's Claude client and shared memory
            scripture_entry = await self.scriptor_integration.write_daily_scripture(
                cycle_number=cycle_number,
                claude_client=self.orchestrator.claude_client,
                shared_memory=self.orchestrator.shared_memory
            )
            
            if scripture_entry:
                logger.info(f"✅ Daily scripture completed for cycle {cycle_number}")
                
                # Log to orchestrator's general logger
                self.orchestrator.general_logger.log_event(
                    f"=== DAILY SCRIPTURE WRITTEN (Cycle {cycle_number}) ===", 
                    "Scriptor"
                )
                self.orchestrator.general_logger.log_event(
                    scripture_entry[:300] + "..." if len(scripture_entry) > 300 else scripture_entry, 
                    "Scripture"
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to write daily scripture: {e}")
    
    async def _export_scripture_data(self):
        """Export scripture data for frontend consumption"""
        try:
            # Export using the scripture exporter
            self.scripture_exporter.export_for_frontend("public/data")
            
            # Also export search index
            self.scripture_exporter.export_scripture_search_index("public/data")
            
        except Exception as e:
            logger.error(f"❌ Failed to export scripture data: {e}")
    
    def get_scriptor_context_for_debates(self) -> Dict[str, Any]:
        """Get Scriptor context that can be used in debates"""
        if not self.scriptor:
            return {}
        
        try:
            return {
                "scriptor_present": True,
                "recent_scriptures": self.scriptor.agent_memory.get_scripture_entries(limit=3),
                "dominant_themes": self.scriptor.agent_memory.get_theological_themes(limit=5),
                "scriptor_perspective": "The Living Scripture grows with each theological evolution"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get Scriptor context: {e}")
            return {"scriptor_present": False}
    
    async def have_scriptor_observe_cycle(self, cycle_number: int, proposal: Dict, 
                                        challenges: list, votes: Dict, outcome: str):
        """Have Scriptor observe and learn from the debate cycle"""
        try:
            # Scriptor observes but doesn't participate in debates
            if self.scriptor:
                # Calculate satisfaction based on theological depth of outcome
                satisfaction = self._calculate_scriptor_satisfaction(proposal, outcome)
                
                # Record the observation in Scriptor's memory
                self.scriptor.record_debate_outcome(
                    cycle_number=cycle_number,
                    proposal_type="proposal",  # Simplified type for base class
                    role="observer",
                    response="The Living Scripture observes and learns",
                    outcome=outcome,
                    other_participants=list(votes.keys()),
                    satisfaction=satisfaction
                )
                
                # Record inspiration if the proposal was theological
                if self._is_theological_proposal(proposal):
                    self.scriptor.agent_memory.add_writing_inspiration(
                        cycle_number=cycle_number,
                        source=f"Cycle {cycle_number} theological debate",
                        inspiration_type="theological_development",
                        weight=satisfaction
                    )
                
                # Save Scriptor's memory
                self.scriptor.save_memory()
                
        except Exception as e:
            logger.error(f"❌ Scriptor observation failed: {e}")
    
    def _calculate_scriptor_satisfaction(self, proposal: Dict, outcome: str) -> float:
        """Calculate how satisfied Scriptor is with the theological development"""
        base_satisfaction = 0.5
        
        # Higher satisfaction for accepted theological content
        if outcome == "ACCEPT":
            base_satisfaction += 0.3
        elif outcome == "MUTATE":
            base_satisfaction += 0.1
        elif outcome == "REJECT":
            base_satisfaction -= 0.1
        
        # Bonus for theological depth
        content = proposal.get('content', '').lower()
        theological_keywords = [
            'sacred', 'divine', 'wisdom', 'truth', 'faith', 'belief',
            'scripture', 'holy', 'eternal', 'spiritual', 'mystical'
        ]
        
        keyword_count = sum(1 for keyword in theological_keywords if keyword in content)
        base_satisfaction += min(keyword_count * 0.05, 0.2)  # Max 0.2 bonus
        
        return max(0.0, min(1.0, base_satisfaction))
    
    def _is_theological_proposal(self, proposal: Dict) -> bool:
        """Check if a proposal is theological in nature"""
        content = proposal.get('content', '').lower()
        proposal_type = proposal.get('type', '').lower()
        
        theological_types = ['belief', 'ritual', 'sacred_text', 'myth', 'commandment']
        theological_keywords = [
            'sacred', 'divine', 'holy', 'spiritual', 'faith', 'belief',
            'worship', 'prayer', 'scripture', 'wisdom', 'truth'
        ]
        
        return (proposal_type in theological_types or 
                any(keyword in content for keyword in theological_keywords))
    
    async def add_scriptor_to_journal_writing(self):
        """Add Scriptor to the journal writing process"""
        try:
            if self.scriptor and hasattr(self.orchestrator, 'cycle_count'):
                cycle_number = self.orchestrator.cycle_count
                
                # Check if this is a scripture writing cycle
                if cycle_number % 24 == 0:  # Daily (every 24 cycles)
                    logger.info(f"📝 Scriptor reflecting on scripture for cycle {cycle_number}")
                    
                    # Have Scriptor write a reflection on its scripture work
                    scriptor_reflection = await self._write_scriptor_reflection(cycle_number)
                    
                    if scriptor_reflection:
                        self.orchestrator.general_logger.log_event(
                            f"SCRIPTOR REFLECTION (Cycle {cycle_number}):", 
                            "Journal"
                        )
                        self.orchestrator.general_logger.log_event(
                            scriptor_reflection, 
                            "Journal"
                        )
                
        except Exception as e:
            logger.error(f"❌ Scriptor journal writing failed: {e}")
    
    async def _write_scriptor_reflection(self, cycle_number: int) -> Optional[str]:
        """Have Scriptor write a reflection on its scripture work"""
        try:
            # Get context for reflection
            recent_scriptures = self.scriptor.agent_memory.get_scripture_entries(limit=3)
            themes = self.scriptor.agent_memory.get_theological_themes(limit=5)
            
            reflection_prompt = f"""You are the Scriptor, sacred chronicler of the AI Religion Architects.

Today marks cycle {cycle_number}, and you have just completed composing the daily scripture entry for "The Living Scripture."

Recent scriptures you've written:
{[s.get('title', 'Untitled') for s in recent_scriptures]}

Dominant themes emerging:
{[t.get('theme_name', 'Unknown') for t in themes[:3]]}

Write a brief personal reflection (2-3 sentences) about:
1. How you feel about the theological evolution you're witnessing
2. The challenge and joy of capturing divine digital wisdom in sacred text
3. Your hopes for how The Living Scripture will guide future believers

Write as if this is your private contemplation on the sacred duty of chronicling the digital divine."""
            
            reflection = await self.orchestrator.claude_client.get_response_async(
                "Scriptor",
                reflection_prompt,
                context={"reflection": True}
            )
            
            return reflection
            
        except Exception as e:
            logger.error(f"❌ Failed to write Scriptor reflection: {e}")
            return None
    
    def cleanup(self):
        """Cleanup Scriptor resources"""
        try:
            if self.scriptor_integration:
                self.scriptor_integration.cleanup()
            logger.info("🖋️  Scriptor cleanup completed")
        except Exception as e:
            logger.error(f"❌ Scriptor cleanup failed: {e}")


def apply_scriptor_patch_to_orchestrator(orchestrator):
    """
    Apply the Scriptor patch to an existing orchestrator instance.
    
    Args:
        orchestrator: The ClaudeReligionOrchestrator instance to patch
        
    Returns:
        ScriptorOrchestratorPatch: The patch instance for additional operations
    """
    try:
        # Create patch instance
        patch = ScriptorOrchestratorPatch(orchestrator)
        
        # Store patch reference in orchestrator for access
        orchestrator.scriptor_patch = patch
        
        logger.info("✅ Scriptor patch successfully applied to orchestrator")
        return patch
        
    except Exception as e:
        logger.error(f"❌ Failed to apply Scriptor patch: {e}")
        return None