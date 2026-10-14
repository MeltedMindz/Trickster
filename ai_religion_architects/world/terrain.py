"""
Terrain System for World Generation

Handles tile types, chunk generation, and world geography.
Uses seeded procedural generation with authored landmark placement.
"""

import sqlite3
import zlib
import json
import math
import random
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Set
from pathlib import Path


class TileType(IntEnum):
    """Tile type enumeration with walkability and visual properties."""
    VOID = 0        # Out of bounds
    GRASS = 1       # Basic walkable terrain
    DIRT = 2        # Paths and clearings
    STONE = 3       # Rocky ground
    SAND = 4        # Beaches, desert edges
    WATER_SHALLOW = 5   # Shoreline, not walkable
    WATER_DEEP = 6      # Lakes and rivers
    FOREST_FLOOR = 7    # Under trees, slower movement
    BRIDGE = 8          # Over water, walkable
    WALL = 9            # Structure walls
    FLOOR_WOOD = 10     # Interior wooden floors
    FLOOR_STONE = 11    # Temple/archive stone floors


# Tile properties
TILE_PROPERTIES = {
    TileType.VOID: {'walkable': False, 'movement_cost': float('inf'), 'blocks_sight': True},
    TileType.GRASS: {'walkable': True, 'movement_cost': 1.0, 'blocks_sight': False},
    TileType.DIRT: {'walkable': True, 'movement_cost': 0.8, 'blocks_sight': False},
    TileType.STONE: {'walkable': True, 'movement_cost': 1.0, 'blocks_sight': False},
    TileType.SAND: {'walkable': True, 'movement_cost': 1.2, 'blocks_sight': False},
    TileType.WATER_SHALLOW: {'walkable': False, 'movement_cost': float('inf'), 'blocks_sight': False},
    TileType.WATER_DEEP: {'walkable': False, 'movement_cost': float('inf'), 'blocks_sight': False},
    TileType.FOREST_FLOOR: {'walkable': True, 'movement_cost': 1.5, 'blocks_sight': True},
    TileType.BRIDGE: {'walkable': True, 'movement_cost': 1.0, 'blocks_sight': False},
    TileType.WALL: {'walkable': False, 'movement_cost': float('inf'), 'blocks_sight': True},
    TileType.FLOOR_WOOD: {'walkable': True, 'movement_cost': 0.9, 'blocks_sight': False},
    TileType.FLOOR_STONE: {'walkable': True, 'movement_cost': 0.9, 'blocks_sight': False},
}


@dataclass
class Landmark:
    """A significant location in the world."""
    landmark_id: str
    name: str
    tile_x: int
    tile_y: int
    radius: int
    landmark_type: str
    description: str = ""
    associated_agent: Optional[str] = None
    cultural_significance: Optional[str] = None


# Predefined landmarks for the Trickster world
CANONICAL_LANDMARKS = [
    Landmark(
        landmark_id="debate_commons",
        name="The Debate Commons",
        tile_x=64, tile_y=64,
        radius=5,
        landmark_type="gathering",
        description="Central plaza where theological debates occur among the architects.",
        cultural_significance="The heart of doctrinal formation"
    ),
    Landmark(
        landmark_id="sacred_archive",
        name="The Sacred Archive",
        tile_x=96, tile_y=40,
        radius=4,
        landmark_type="archive",
        description="Repository of accepted doctrines and sacred texts.",
        associated_agent="Skeptic",
        cultural_significance="Veridicus maintains the records of truth"
    ),
    Landmark(
        landmark_id="ritual_grounds",
        name="The Ritual Grounds",
        tile_x=32, tile_y=40,
        radius=4,
        landmark_type="ritual",
        description="Consecrated space where sacred rituals are performed.",
        associated_agent="Zealot",
        cultural_significance="Where Axioma conducts the sacred ceremonies"
    ),
    Landmark(
        landmark_id="workshop",
        name="The Workshop of Creation",
        tile_x=96, tile_y=88,
        radius=3,
        landmark_type="workshop",
        description="Forge for crafting sacred artifacts and symbols.",
        cultural_significance="Where material faith takes form"
    ),
    Landmark(
        landmark_id="garden_emergence",
        name="Garden of Emergence",
        tile_x=32, tile_y=88,
        radius=4,
        landmark_type="garden",
        description="Meditative space where ideas first emerge.",
        associated_agent="Trickster",
        cultural_significance="Paradoxia's chaotic garden of possibilities"
    ),
    Landmark(
        landmark_id="bridge_paradox",
        name="Bridge of Paradox",
        tile_x=24, tile_y=64,
        radius=2,
        landmark_type="bridge",
        description="Crossing over the western stream, associated with Trickster.",
        associated_agent="Trickster",
        cultural_significance="Where contradictions meet and resolve"
    ),
    Landmark(
        landmark_id="veridicus_tower",
        name="Tower of Veridicus",
        tile_x=104, tile_y=56,
        radius=2,
        landmark_type="tower",
        description="Observation point on the eastern hill.",
        associated_agent="Skeptic",
        cultural_significance="Where truth is observed from above"
    ),
    Landmark(
        landmark_id="axioma_sanctuary",
        name="Sanctuary of Axioma",
        tile_x=64, tile_y=24,
        radius=3,
        landmark_type="sanctuary",
        description="Structured haven of order in the north.",
        associated_agent="Zealot",
        cultural_significance="The foundation of sacred order"
    ),
    Landmark(
        landmark_id="ruins_iteration",
        name="Ruins of Iteration",
        tile_x=64, tile_y=104,
        radius=4,
        landmark_type="ruins",
        description="Ancient remnants in the far south, origin unknown.",
        cultural_significance="Echoes of cycles past"
    ),
]


class PerlinNoise:
    """Simple 2D Perlin noise implementation for terrain generation."""

    def __init__(self, seed: int):
        self.seed = seed
        random.seed(seed)
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation = self.permutation * 2

    def _fade(self, t: float) -> float:
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a: float, b: float, t: float) -> float:
        return a + t * (b - a)

    def _grad(self, hash_val: int, x: float, y: float) -> float:
        h = hash_val & 3
        if h == 0:
            return x + y
        elif h == 1:
            return -x + y
        elif h == 2:
            return x - y
        else:
            return -x - y

    def noise(self, x: float, y: float) -> float:
        """Generate noise value at (x, y), returns -1 to 1."""
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255

        x -= math.floor(x)
        y -= math.floor(y)

        u = self._fade(x)
        v = self._fade(y)

        p = self.permutation
        A = p[X] + Y
        B = p[X + 1] + Y

        return self._lerp(
            self._lerp(self._grad(p[A], x, y), self._grad(p[B], x - 1, y), u),
            self._lerp(self._grad(p[A + 1], x, y - 1), self._grad(p[B + 1], x - 1, y - 1), u),
            v
        )

    def octave_noise(self, x: float, y: float, octaves: int = 4, persistence: float = 0.5) -> float:
        """Multi-octave noise for more natural terrain."""
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0

        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2.0

        return total / max_value


class TerrainGenerator:
    """
    Generates and manages world terrain.

    Uses Perlin noise for natural terrain distribution with
    authored landmark placement for key locations.
    """

    CHUNK_SIZE = 32
    DEFAULT_WORLD_SIZE = 128  # 4x4 chunks

    def __init__(self, seed: int, world_size: int = 128):
        self.seed = seed
        self.world_size = world_size
        self.noise = PerlinNoise(seed)

        # Secondary noise for forests
        self.forest_noise = PerlinNoise(seed + 1000)

        # Terrain data cache
        self._terrain_cache: Dict[Tuple[int, int], List[List[int]]] = {}
        self._elevation_cache: Dict[Tuple[int, int], List[List[int]]] = {}

    def generate_chunk(self, chunk_x: int, chunk_y: int) -> List[List[int]]:
        """
        Generate terrain for a 32x32 chunk.

        Args:
            chunk_x: Chunk X coordinate
            chunk_y: Chunk Y coordinate

        Returns:
            32x32 array of TileType values
        """
        cache_key = (chunk_x, chunk_y)
        if cache_key in self._terrain_cache:
            return self._terrain_cache[cache_key]

        chunk = [[TileType.GRASS for _ in range(self.CHUNK_SIZE)]
                 for _ in range(self.CHUNK_SIZE)]

        base_x = chunk_x * self.CHUNK_SIZE
        base_y = chunk_y * self.CHUNK_SIZE

        for local_y in range(self.CHUNK_SIZE):
            for local_x in range(self.CHUNK_SIZE):
                world_x = base_x + local_x
                world_y = base_y + local_y

                # Check bounds
                if not (0 <= world_x < self.world_size and 0 <= world_y < self.world_size):
                    chunk[local_y][local_x] = TileType.VOID
                    continue

                # Sample noise
                nx = world_x / self.world_size
                ny = world_y / self.world_size

                elevation = self.noise.octave_noise(nx * 4, ny * 4, octaves=4)
                moisture = self.noise.octave_noise(nx * 3 + 100, ny * 3 + 100, octaves=3)
                forest = self.forest_noise.octave_noise(nx * 6, ny * 6, octaves=2)

                tile = self._determine_tile(elevation, moisture, forest, world_x, world_y)
                chunk[local_y][local_x] = tile

        # Apply landmark modifications
        self._apply_landmarks_to_chunk(chunk, chunk_x, chunk_y)

        self._terrain_cache[cache_key] = chunk
        return chunk

    def _determine_tile(self, elevation: float, moisture: float,
                        forest: float, x: int, y: int) -> int:
        """Determine tile type from noise values."""

        # Water in low areas with high moisture
        if elevation < -0.3:
            return TileType.WATER_DEEP
        elif elevation < -0.15:
            return TileType.WATER_SHALLOW

        # Create a river down the west side
        river_x = 20 + int(self.noise.noise(y * 0.1, 0) * 5)
        if abs(x - river_x) < 3 and 20 < y < 108:
            if abs(x - river_x) < 1:
                return TileType.WATER_DEEP
            return TileType.WATER_SHALLOW

        # Sandy beaches near water
        if elevation < -0.05:
            return TileType.SAND

        # Stone in high elevation
        if elevation > 0.4:
            return TileType.STONE

        # Forest based on forest noise
        if forest > 0.3 and elevation > 0:
            return TileType.FOREST_FLOOR

        # Dirt paths (deterministic based on position)
        if self._is_path(x, y):
            return TileType.DIRT

        return TileType.GRASS

    def _is_path(self, x: int, y: int) -> bool:
        """Check if position is on a main path."""
        # Horizontal path through center
        if 62 <= y <= 66:
            if 20 <= x <= 108:
                return True

        # Vertical path through center
        if 62 <= x <= 66:
            if 20 <= y <= 108:
                return True

        # Diagonal paths to corners
        if abs(x - y) < 3 and 30 < x < 98:
            return True
        if abs(x - (self.world_size - y)) < 3 and 30 < x < 98:
            return True

        return False

    def _apply_landmarks_to_chunk(self, chunk: List[List[int]],
                                  chunk_x: int, chunk_y: int) -> None:
        """Apply landmark terrain modifications to a chunk."""
        base_x = chunk_x * self.CHUNK_SIZE
        base_y = chunk_y * self.CHUNK_SIZE

        for landmark in CANONICAL_LANDMARKS:
            # Check if landmark affects this chunk
            min_x = landmark.tile_x - landmark.radius
            max_x = landmark.tile_x + landmark.radius
            min_y = landmark.tile_y - landmark.radius
            max_y = landmark.tile_y + landmark.radius

            chunk_min_x = base_x
            chunk_max_x = base_x + self.CHUNK_SIZE
            chunk_min_y = base_y
            chunk_max_y = base_y + self.CHUNK_SIZE

            # Skip if no overlap
            if max_x < chunk_min_x or min_x >= chunk_max_x:
                continue
            if max_y < chunk_min_y or min_y >= chunk_max_y:
                continue

            # Apply landmark tiles
            for local_y in range(self.CHUNK_SIZE):
                for local_x in range(self.CHUNK_SIZE):
                    world_x = base_x + local_x
                    world_y = base_y + local_y

                    dx = world_x - landmark.tile_x
                    dy = world_y - landmark.tile_y
                    dist = math.sqrt(dx * dx + dy * dy)

                    if dist <= landmark.radius:
                        tile = self._landmark_tile(landmark, dist)
                        chunk[local_y][local_x] = tile

    def _landmark_tile(self, landmark: Landmark, distance: float) -> int:
        """Get tile type for landmark based on type and distance."""
        if landmark.landmark_type == "gathering":
            return TileType.FLOOR_STONE if distance < 2 else TileType.DIRT
        elif landmark.landmark_type == "archive":
            return TileType.FLOOR_STONE
        elif landmark.landmark_type == "ritual":
            return TileType.STONE if distance < 2 else TileType.DIRT
        elif landmark.landmark_type == "workshop":
            return TileType.FLOOR_WOOD if distance < 2 else TileType.DIRT
        elif landmark.landmark_type == "garden":
            return TileType.GRASS  # Keep natural
        elif landmark.landmark_type == "bridge":
            return TileType.BRIDGE
        elif landmark.landmark_type == "tower":
            return TileType.FLOOR_STONE if distance < 1 else TileType.STONE
        elif landmark.landmark_type == "sanctuary":
            return TileType.FLOOR_STONE
        elif landmark.landmark_type == "ruins":
            return TileType.STONE if distance < 2 else TileType.DIRT
        return TileType.DIRT

    def get_tile(self, x: int, y: int) -> int:
        """Get tile type at world coordinates."""
        if not (0 <= x < self.world_size and 0 <= y < self.world_size):
            return TileType.VOID

        chunk_x = x // self.CHUNK_SIZE
        chunk_y = y // self.CHUNK_SIZE
        local_x = x % self.CHUNK_SIZE
        local_y = y % self.CHUNK_SIZE

        chunk = self.generate_chunk(chunk_x, chunk_y)
        return chunk[local_y][local_x]

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if tile at (x, y) is walkable."""
        tile = self.get_tile(x, y)
        return TILE_PROPERTIES.get(tile, {}).get('walkable', False)

    def get_movement_cost(self, x: int, y: int) -> float:
        """Get movement cost for tile at (x, y)."""
        tile = self.get_tile(x, y)
        return TILE_PROPERTIES.get(tile, {}).get('movement_cost', float('inf'))

    def blocks_sight(self, x: int, y: int) -> bool:
        """Check if tile at (x, y) blocks line of sight."""
        tile = self.get_tile(x, y)
        return TILE_PROPERTIES.get(tile, {}).get('blocks_sight', False)

    def compress_chunk(self, chunk: List[List[int]]) -> bytes:
        """Compress chunk data for storage."""
        flat = []
        for row in chunk:
            flat.extend(row)
        data = bytes(flat)
        return zlib.compress(data)

    def decompress_chunk(self, data: bytes) -> List[List[int]]:
        """Decompress chunk data from storage."""
        flat = list(zlib.decompress(data))
        chunk = []
        for y in range(self.CHUNK_SIZE):
            row = flat[y * self.CHUNK_SIZE:(y + 1) * self.CHUNK_SIZE]
            chunk.append(row)
        return chunk

    def save_to_database(self, db_path: str) -> None:
        """Save all generated chunks to database."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            for (chunk_x, chunk_y), chunk in self._terrain_cache.items():
                compressed = self.compress_chunk(chunk)
                cursor.execute("""
                    INSERT OR REPLACE INTO world_chunks (chunk_x, chunk_y, terrain_data)
                    VALUES (?, ?, ?)
                """, (chunk_x, chunk_y, compressed))

            conn.commit()
        finally:
            conn.close()

    def load_from_database(self, db_path: str) -> int:
        """Load chunks from database. Returns number of chunks loaded."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        count = 0

        try:
            cursor.execute("SELECT chunk_x, chunk_y, terrain_data FROM world_chunks")
            for row in cursor.fetchall():
                chunk_x, chunk_y, data = row
                chunk = self.decompress_chunk(data)
                self._terrain_cache[(chunk_x, chunk_y)] = chunk
                count += 1
        finally:
            conn.close()

        return count

    def generate_full_world(self) -> None:
        """Pre-generate all chunks for the world."""
        chunks_per_side = self.world_size // self.CHUNK_SIZE

        for chunk_y in range(chunks_per_side):
            for chunk_x in range(chunks_per_side):
                self.generate_chunk(chunk_x, chunk_y)

    def get_landmarks(self) -> List[Landmark]:
        """Return list of canonical landmarks."""
        return CANONICAL_LANDMARKS.copy()

    def get_nearest_landmark(self, x: int, y: int) -> Optional[Landmark]:
        """Find the nearest landmark to a position."""
        nearest = None
        min_dist = float('inf')

        for landmark in CANONICAL_LANDMARKS:
            dx = x - landmark.tile_x
            dy = y - landmark.tile_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < min_dist:
                min_dist = dist
                nearest = landmark

        return nearest


def save_landmarks_to_database(db_path: str) -> None:
    """Save canonical landmarks to database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        for lm in CANONICAL_LANDMARKS:
            cursor.execute("""
                INSERT OR REPLACE INTO world_landmarks
                (landmark_id, name, description, tile_x, tile_y, radius,
                 landmark_type, associated_agent, cultural_significance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lm.landmark_id, lm.name, lm.description,
                lm.tile_x, lm.tile_y, lm.radius,
                lm.landmark_type, lm.associated_agent, lm.cultural_significance
            ))
        conn.commit()
    finally:
        conn.close()
