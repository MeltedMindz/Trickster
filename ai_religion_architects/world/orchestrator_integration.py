"""
World-Orchestrator Integration

Provides hooks and utilities to integrate the world simulation
with the existing ClaudeReligionOrchestrator.

Usage in orchestrator:
    from ai_religion_architects.world.orchestrator_integration import WorldOrchestratorHooks

    class ClaudeReligionOrchestrator:
        def __init__(self, ...):
            ...
            self.world_hooks = WorldOrchestratorHooks(self.db_path)

        async def _run_scheduled_cycle(self):
            ...
            # Get world context for proposals
            world_context = self.world_hooks.get_proposal_context(proposer_name)

            # After voting
            self.world_hooks.apply_outcome(outcome, proposal, votes, self.cycle_count)

            # Advance world time
            self.world_hooks.advance_simulation()
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .simulation import WorldSimulation
from .debate_adapter import WorldDebateAdapter, DebateContext

logger = logging.getLogger(__name__)


class WorldOrchestratorHooks:
    """
    Integration hooks for the ClaudeReligionOrchestrator.

    Provides methods that can be called at various points in the
    debate cycle to incorporate world state.
    """

    def __init__(
        self,
        db_path: str = 'data/religion_memory.db',
        auto_advance: bool = True,
        ticks_per_cycle: int = 10
    ):
        """
        Initialize world hooks.

        Args:
            db_path: Path to shared database
            auto_advance: Whether to advance world each cycle
            ticks_per_cycle: World ticks per debate cycle
        """
        self.db_path = db_path
        self.auto_advance = auto_advance
        self.ticks_per_cycle = ticks_per_cycle

        # Initialize adapter (creates world if needed)
        try:
            self.adapter = WorldDebateAdapter(db_path=db_path)
            self.enabled = self.adapter.world is not None
            if self.enabled:
                logger.info("World-debate integration enabled")
            else:
                logger.warning("World simulation not available, integration disabled")
        except Exception as e:
            logger.warning(f"Could not initialize world integration: {e}")
            self.adapter = None
            self.enabled = False

    def get_proposal_context(self, agent_id: str) -> Optional[str]:
        """
        Get world context for an agent's proposal.

        Called before proposal generation to provide spatial context.

        Args:
            agent_id: The proposing agent

        Returns:
            Text to append to proposal prompt, or None
        """
        if not self.enabled or not self.adapter:
            return None

        try:
            context = self.adapter.get_debate_context(agent_id)
            if context:
                return context.to_prompt_context()
        except Exception as e:
            logger.warning(f"Error getting world context: {e}")

        return None

    def get_agent_location(self, agent_id: str) -> Optional[Dict]:
        """
        Get an agent's current location information.

        Args:
            agent_id: Agent to query

        Returns:
            Dict with location info or None
        """
        if not self.enabled or not self.adapter:
            return None

        try:
            context = self.adapter.get_debate_context(agent_id)
            if context:
                return {
                    'name': context.location_name,
                    'type': context.location_type,
                    'nearby_agents': [a['chosen_name'] for a in context.nearby_agents],
                }
        except Exception as e:
            logger.warning(f"Error getting agent location: {e}")

        return None

    def get_suggested_themes(self, agent_id: str) -> List[str]:
        """
        Get location-influenced theme suggestions.

        Args:
            agent_id: The agent to get themes for

        Returns:
            List of suggested proposal themes
        """
        if not self.enabled or not self.adapter:
            return []

        try:
            context = self.adapter.get_debate_context(agent_id)
            if context:
                return context.suggested_themes
        except Exception as e:
            logger.warning(f"Error getting suggested themes: {e}")

        return []

    def apply_outcome(
        self,
        outcome: str,
        proposal: Dict,
        votes: Dict[str, str],
        cycle_number: int
    ) -> None:
        """
        Apply debate outcome to world state.

        Called after voting to update world based on results.

        Args:
            outcome: Vote result (ACCEPT, REJECT, etc.)
            proposal: The proposal dict
            votes: How agents voted
            cycle_number: Current cycle
        """
        if not self.enabled or not self.adapter:
            return

        try:
            effects = self.adapter.apply_debate_outcome(
                outcome=outcome,
                proposal_type=proposal.get('type', 'unknown'),
                proposal_content=proposal.get('content', ''),
                proposer=proposal.get('author', 'Unknown'),
                votes=votes,
                cycle_number=cycle_number
            )

            if effects:
                logger.info(f"Applied {len(effects)} world effects from debate outcome")
                for effect in effects:
                    logger.debug(f"  - {effect.description}")

        except Exception as e:
            logger.error(f"Error applying debate outcome to world: {e}")

    def advance_simulation(self, ticks: Optional[int] = None) -> None:
        """
        Advance world simulation.

        Called after debate cycle to progress world time.

        Args:
            ticks: Number of ticks to advance (default: ticks_per_cycle)
        """
        if not self.enabled or not self.adapter or not self.auto_advance:
            return

        ticks = ticks or self.ticks_per_cycle

        try:
            events = self.adapter.advance_world(ticks)
            if events:
                logger.debug(f"World advanced {ticks} ticks, {len(events)} events occurred")
        except Exception as e:
            logger.warning(f"Error advancing world simulation: {e}")

    def get_world_summary(self) -> Dict:
        """
        Get world state summary for logging/export.

        Returns:
            Dict with world state summary
        """
        if not self.enabled or not self.adapter:
            return {'enabled': False}

        try:
            return self.adapter.get_world_summary_for_debate()
        except Exception as e:
            logger.warning(f"Error getting world summary: {e}")
            return {'enabled': False, 'error': str(e)}

    def save_state(self) -> None:
        """Save world state to database."""
        if self.enabled and self.adapter:
            try:
                self.adapter.save_state()
            except Exception as e:
                logger.error(f"Error saving world state: {e}")

    def export_for_frontend(self, output_dir: str = 'public/data') -> None:
        """
        Export world data for frontend visualization.

        Args:
            output_dir: Directory to write JSON files
        """
        if not self.enabled or not self.adapter or not self.adapter.world:
            return

        try:
            from .export import export_all
            export_all(self.db_path, output_dir)
            logger.info(f"Exported world data to {output_dir}")
        except Exception as e:
            logger.warning(f"Error exporting world data: {e}")


def patch_orchestrator_with_world(orchestrator) -> None:
    """
    Monkey-patch an existing orchestrator with world hooks.

    This can be used to add world integration to an already-instantiated
    orchestrator without modifying the original class.

    Usage:
        orchestrator = ClaudeReligionOrchestrator(...)
        patch_orchestrator_with_world(orchestrator)

    Args:
        orchestrator: ClaudeReligionOrchestrator instance
    """
    if hasattr(orchestrator, 'world_hooks'):
        logger.warning("Orchestrator already has world hooks")
        return

    # Create hooks
    orchestrator.world_hooks = WorldOrchestratorHooks(
        db_path=orchestrator.db_path
    )

    # Store original method
    original_run_cycle = orchestrator._run_scheduled_cycle

    async def enhanced_run_cycle():
        """Enhanced cycle with world integration."""
        # Get world context before cycle
        if orchestrator.world_hooks.enabled:
            world_summary = orchestrator.world_hooks.get_world_summary()
            logger.debug(f"World state: tick {world_summary.get('tick', 0)}")

        # Run original cycle
        result = await original_run_cycle()

        # Advance world after cycle
        if orchestrator.world_hooks.enabled:
            orchestrator.world_hooks.advance_simulation()
            orchestrator.world_hooks.save_state()
            orchestrator.world_hooks.export_for_frontend()

        return result

    # Replace method
    orchestrator._run_scheduled_cycle = enhanced_run_cycle

    logger.info("Orchestrator patched with world integration")


def create_world_enabled_orchestrator(**kwargs):
    """
    Factory to create an orchestrator with world integration.

    This returns a modified orchestrator class that includes
    world hooks by default.

    Usage:
        orchestrator = create_world_enabled_orchestrator(db_path='data/religion_memory.db')
        await orchestrator.start()

    Args:
        **kwargs: Arguments to pass to ClaudeReligionOrchestrator

    Returns:
        Orchestrator instance with world integration
    """
    from ..orchestration.claude_orchestrator import ClaudeReligionOrchestrator

    orchestrator = ClaudeReligionOrchestrator(**kwargs)
    patch_orchestrator_with_world(orchestrator)

    return orchestrator
