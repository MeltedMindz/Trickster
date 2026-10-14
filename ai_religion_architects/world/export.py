"""
World Export Utilities

Exports world state to JSON for frontend consumption.
"""

import json
from pathlib import Path
from typing import Optional

from .simulation import WorldSimulation
from .terrain import TerrainGenerator


def export_terrain(
    simulation: WorldSimulation,
    output_path: str
) -> None:
    """
    Export terrain data to JSON.

    Args:
        simulation: WorldSimulation instance
        output_path: Path to write terrain JSON
    """
    terrain = simulation.terrain

    # Generate all chunks if not done
    terrain.generate_full_world()

    # Export as 2D array
    terrain_data = []
    for y in range(terrain.world_size):
        row = []
        for x in range(terrain.world_size):
            row.append(terrain.get_tile(x, y))
        terrain_data.append(row)

    data = {
        'seed': simulation.world_seed,
        'size': terrain.world_size,
        'tile_size': terrain.CHUNK_SIZE,
        'terrain': terrain_data,
    }

    with open(output_path, 'w') as f:
        json.dump(data, f)

    print(f"Exported terrain to {output_path}")


def export_world_state(
    simulation: WorldSimulation,
    output_path: str
) -> None:
    """
    Export current world state to JSON.

    Args:
        simulation: WorldSimulation instance
        output_path: Path to write state JSON
    """
    snapshot = simulation.get_state_snapshot()

    with open(output_path, 'w') as f:
        json.dump(snapshot, f, indent=2, default=str)

    print(f"Exported world state to {output_path}")


def export_all(
    db_path: str = 'data/religion_memory.db',
    output_dir: str = 'public/data'
) -> None:
    """
    Export all world data for frontend.

    Args:
        db_path: Path to database
        output_dir: Directory to write JSON files
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # Create simulation
    sim = WorldSimulation(db_path=db_path, headless=True)

    # Export terrain
    export_terrain(sim, str(output / 'world_terrain.json'))

    # Export world state
    export_world_state(sim, str(output / 'world_state.json'))

    print(f"All world data exported to {output_dir}")


if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'data/religion_memory.db'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'public/data'
    export_all(db_path, output_dir)
