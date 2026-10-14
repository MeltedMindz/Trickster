#!/usr/bin/env python3
"""
Test script for the World System

Verifies all components work correctly:
- Database migrations
- Terrain generation
- Agent positioning
- Pathfinding
- Perception
- Actions
- Export
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_religion_architects.world.migrations import run_migrations, verify_schema, initialize_agent_positions
from ai_religion_architects.world.terrain import TerrainGenerator, TileType, save_landmarks_to_database
from ai_religion_architects.world.pathfinding import Pathfinder, PathResult
from ai_religion_architects.world.perception import PerceptionSystem
from ai_religion_architects.world.affordances import AffordanceRegistry, ActionType
from ai_religion_architects.world.simulation import WorldSimulation
from ai_religion_architects.world.export import export_all


def test_migrations():
    """Test database migrations"""
    print("\n1. Testing Database Migrations...")
    result = run_migrations('data/religion_memory.db')
    assert result['success'], f"Migration failed: {result['errors']}"
    print(f"   Created tables: {len(result.get('tables_created', []))}")

    verify = verify_schema('data/religion_memory.db')
    assert verify['complete'], f"Missing tables: {verify['missing_tables']}"
    print("   Schema verification: PASS")


def test_terrain():
    """Test terrain generation"""
    print("\n2. Testing Terrain Generation...")
    generator = TerrainGenerator(seed=12345, world_size=128)

    # Generate world
    generator.generate_full_world()

    # Check tile types
    center = generator.get_tile(64, 64)
    assert center == TileType.FLOOR_STONE, f"Center should be stone floor, got {center}"
    print(f"   Center tile: {TileType(center).name}")

    # Check walkability
    assert generator.is_walkable(64, 64), "Center should be walkable"
    assert not generator.is_walkable(21, 64), "River should not be walkable"

    # Check landmarks
    landmarks = generator.get_landmarks()
    assert len(landmarks) == 9, f"Expected 9 landmarks, got {len(landmarks)}"
    print(f"   Landmarks: {len(landmarks)}")
    print("   Terrain generation: PASS")


def test_pathfinding():
    """Test A* pathfinding"""
    print("\n3. Testing Pathfinding...")
    generator = TerrainGenerator(seed=12345, world_size=128)
    generator.generate_full_world()

    pathfinder = Pathfinder(
        is_walkable=generator.is_walkable,
        get_cost=generator.get_movement_cost,
        world_width=128,
        world_height=128
    )

    # Find path from center to archive
    path = pathfinder.find_path((64, 64), (96, 40))
    assert path.result == PathResult.SUCCESS, f"Pathfinding failed: {path.result}"
    print(f"   Path found: {len(path.waypoints)} steps")

    # Test blocked path
    path_blocked = pathfinder.find_path((64, 64), (21, 64))  # Into river
    assert path_blocked.result == PathResult.TARGET_BLOCKED
    print("   Blocked path detection: PASS")
    print("   Pathfinding: PASS")


def test_perception():
    """Test perception system"""
    print("\n4. Testing Perception...")
    generator = TerrainGenerator(seed=12345, world_size=128)
    generator.generate_full_world()

    pathfinder = Pathfinder(
        is_walkable=generator.is_walkable,
        get_cost=generator.get_movement_cost,
        world_width=128,
        world_height=128
    )

    perception = PerceptionSystem(
        get_tile=generator.get_tile,
        blocks_sight=generator.blocks_sight,
        line_of_sight=pathfinder.line_of_sight
    )

    # Test perception range
    range_normal = perception.get_perception_range('Zealot', 64, 64)
    assert range_normal == 8, f"Expected range 8, got {range_normal}"
    print(f"   Perception range: {range_normal}")

    # Test visible tiles
    visible = perception.calculate_visible_tiles((64, 64), 8)
    assert len(visible) > 100, f"Should see many tiles, got {len(visible)}"
    print(f"   Visible tiles: {len(visible)}")
    print("   Perception: PASS")


def test_affordances():
    """Test affordance system"""
    print("\n5. Testing Affordances...")
    registry = AffordanceRegistry()

    # Check all 12 affordance types exist
    for action_type in ActionType:
        affordance = registry.get_affordance(action_type)
        assert affordance is not None, f"Missing affordance: {action_type}"

    print(f"   Affordance types: {len(ActionType)}")

    # Test action creation
    action = registry.create_action(
        ActionType.MOVE,
        agent_id='Zealot',
        tick=1,
        target_position=(65, 64)
    )
    assert action.action_type == ActionType.MOVE
    print("   Action creation: PASS")
    print("   Affordances: PASS")


def test_simulation():
    """Test full simulation"""
    print("\n6. Testing Simulation...")
    sim = WorldSimulation(db_path='data/religion_memory.db', headless=True)

    print(f"   World seed: {sim.world_seed}")
    print(f"   Initial tick: {sim.tick}")
    print(f"   Agents: {list(sim.agents.keys())}")

    # Verify agents loaded
    assert len(sim.agents) == 3, f"Expected 3 agents, got {len(sim.agents)}"

    # Run some ticks
    initial_tick = sim.tick
    for _ in range(10):
        sim.simulate_tick()
    assert sim.tick == initial_tick + 10
    print(f"   After 10 ticks: {sim.tick}")

    # Test pathfinding command - move to a nearby walkable tile
    zealot = sim.agents['Zealot']
    start_pos = (zealot.tile_x, zealot.tile_y)

    # Find a nearby walkable target
    target_found = False
    for dx, dy in [(5, 0), (-5, 0), (0, 5), (0, -5), (3, 3), (-3, -3)]:
        target_x = zealot.tile_x + dx
        target_y = zealot.tile_y + dy
        if 0 <= target_x < 128 and 0 <= target_y < 128:
            if sim.terrain.is_walkable(target_x, target_y):
                success = sim.move_agent_to('Zealot', target_x, target_y)
                if success:
                    target_found = True
                    print(f"   Movement to ({target_x}, {target_y}): PASS")
                    break

    if not target_found:
        # Fallback: just verify simulation runs without pathfinding
        print("   Skipping movement test (no reachable target)")

    # Run more ticks
    for _ in range(30):
        sim.simulate_tick()
    end_pos = (zealot.tile_x, zealot.tile_y)
    print(f"   Agent position: {start_pos} -> {end_pos}")

    # Test perception
    perception = sim.get_perception('Zealot')
    assert perception is not None
    print(f"   Perception visible tiles: {len(perception.visible_tiles)}")

    # Save state
    sim.save_state()
    print("   State saved: PASS")
    print("   Simulation: PASS")


def test_export():
    """Test data export"""
    print("\n7. Testing Export...")
    export_all('data/religion_memory.db', 'public/data')

    import os
    assert os.path.exists('public/data/world_state.json')
    assert os.path.exists('public/data/world_terrain.json')
    print("   Export files created: PASS")
    print("   Export: PASS")


def test_debate_adapter():
    """Test debate-world integration"""
    print("\n8. Testing Debate Adapter...")
    from ai_religion_architects.world.debate_adapter import WorldDebateAdapter

    adapter = WorldDebateAdapter(db_path='data/religion_memory.db')
    assert adapter.world is not None, "World should be initialized"
    print("   Adapter initialized: PASS")

    # Test context generation
    context = adapter.get_debate_context('Zealot')
    assert context is not None, "Should get context for Zealot"
    assert context.agent_id == 'Zealot'
    print(f"   Zealot context: {context.location_name} ({context.location_type})")

    # Test prompt context generation
    prompt_text = context.to_prompt_context()
    assert len(prompt_text) > 0, "Prompt context should not be empty"
    print(f"   Prompt context length: {len(prompt_text)} chars")

    # Test world summary
    summary = adapter.get_world_summary_for_debate()
    assert 'tick' in summary
    assert 'agents' in summary
    print(f"   World summary: tick {summary['tick']}, {len(summary['agents'])} agents")

    # Test outcome application
    effects = adapter.apply_debate_outcome(
        outcome='ACCEPT',
        proposal_type='doctrine',
        proposal_content='Test doctrine for world integration',
        proposer='Zealot',
        votes={'Zealot': 'ACCEPT', 'Skeptic': 'ACCEPT', 'Trickster': 'REJECT'},
        cycle_number=999
    )
    print(f"   Applied {len(effects)} effects from outcome")

    print("   Debate Adapter: PASS")


def test_research_harness():
    """Test research experiment runner"""
    print("\n9. Testing Research Harness...")
    from ai_religion_architects.world.research import (
        ExperimentRunner, ExperimentConfig, ExperimentStatus
    )

    # Create config
    config = ExperimentConfig(
        name="test_experiment",
        description="Quick test of research harness",
        seed=12345,
        total_ticks=50,  # Short experiment
        collect_metrics_every=10,
        snapshot_every=25,
    )
    print(f"   Config created: {config.name}")

    # Run experiment
    runner = ExperimentRunner(output_dir='experiments')
    result = runner.run_experiment(config)

    assert result.status == ExperimentStatus.COMPLETED, f"Expected COMPLETED, got {result.status}"
    print(f"   Experiment status: {result.status.value}")

    assert len(result.metrics) > 0, "Should have collected metrics"
    print(f"   Metrics collected: {len(result.metrics)}")

    assert len(result.snapshots) > 0, "Should have snapshots"
    print(f"   Snapshots taken: {len(result.snapshots)}")

    # Check metric statistics
    stats = result.get_metric_statistics('avg_energy')
    assert 'mean' in stats, "Should have mean statistic"
    print(f"   Avg energy mean: {stats['mean']:.3f}")

    print("   Research Harness: PASS")


def main():
    """Run all tests"""
    print("=" * 60)
    print("   WORLD SYSTEM TEST SUITE")
    print("=" * 60)

    tests = [
        test_migrations,
        test_terrain,
        test_pathfinding,
        test_perception,
        test_affordances,
        test_simulation,
        test_export,
        test_debate_adapter,
        test_research_harness,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"   FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"   RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
