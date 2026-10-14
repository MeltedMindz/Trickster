"""
Pathfinding System

A* pathfinding with support for:
- Variable movement costs
- Dynamic obstacles
- Agent collision avoidance
- Path caching
"""

import heapq
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Set, Dict, Callable
from enum import Enum


@dataclass(order=True)
class PathNode:
    """Node in the A* priority queue."""
    f_score: float
    position: Tuple[int, int] = field(compare=False)
    g_score: float = field(compare=False)
    parent: Optional['PathNode'] = field(default=None, compare=False)


class PathResult(Enum):
    """Result of pathfinding attempt."""
    SUCCESS = "success"
    NO_PATH = "no_path"
    ALREADY_THERE = "already_there"
    TARGET_BLOCKED = "target_blocked"


@dataclass
class Path:
    """A computed path through the world."""
    result: PathResult
    waypoints: List[Tuple[int, int]] = field(default_factory=list)
    total_cost: float = 0.0
    computed_at_tick: int = 0

    def __len__(self) -> int:
        return len(self.waypoints)

    def __bool__(self) -> bool:
        return self.result == PathResult.SUCCESS and len(self.waypoints) > 0

    @property
    def destination(self) -> Optional[Tuple[int, int]]:
        return self.waypoints[-1] if self.waypoints else None


class Pathfinder:
    """
    A* pathfinding for agent navigation.

    Supports:
    - Terrain-based movement costs
    - Dynamic obstacle avoidance
    - Path caching with invalidation
    - Configurable heuristics
    """

    # Movement directions: 4-way (no diagonals for tile-based movement)
    DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W
    DIRECTION_NAMES = ['north', 'east', 'south', 'west']

    def __init__(
        self,
        is_walkable: Callable[[int, int], bool],
        get_cost: Callable[[int, int], float],
        world_width: int = 128,
        world_height: int = 128,
        max_iterations: int = 5000
    ):
        """
        Initialize pathfinder.

        Args:
            is_walkable: Function(x, y) -> bool
            get_cost: Function(x, y) -> float (movement cost)
            world_width: World width in tiles
            world_height: World height in tiles
            max_iterations: Maximum A* iterations before giving up
        """
        self.is_walkable = is_walkable
        self.get_cost = get_cost
        self.world_width = world_width
        self.world_height = world_height
        self.max_iterations = max_iterations

        # Dynamic obstacles (agent positions, temporary blocks)
        self._obstacles: Set[Tuple[int, int]] = set()

        # Path cache
        self._cache: Dict[Tuple[Tuple[int, int], Tuple[int, int]], Path] = {}
        self._cache_tick: int = 0

    def add_obstacle(self, x: int, y: int) -> None:
        """Add a dynamic obstacle (e.g., agent position)."""
        self._obstacles.add((x, y))
        self._invalidate_cache_through(x, y)

    def remove_obstacle(self, x: int, y: int) -> None:
        """Remove a dynamic obstacle."""
        self._obstacles.discard((x, y))
        self._invalidate_cache_through(x, y)

    def clear_obstacles(self) -> None:
        """Clear all dynamic obstacles."""
        self._obstacles.clear()
        self._cache.clear()

    def update_obstacles(self, positions: Set[Tuple[int, int]]) -> None:
        """Update all dynamic obstacles at once."""
        if positions != self._obstacles:
            self._obstacles = positions.copy()
            self._cache.clear()

    def _invalidate_cache_through(self, x: int, y: int) -> None:
        """Invalidate cached paths that go through a position."""
        # Simple approach: clear entire cache when obstacles change
        # Could be optimized with spatial indexing
        self._cache.clear()

    def _heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Manhattan distance heuristic."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def _is_valid(self, x: int, y: int, ignore_obstacles: bool = False) -> bool:
        """Check if position is valid for pathfinding."""
        # Bounds check
        if not (0 <= x < self.world_width and 0 <= y < self.world_height):
            return False

        # Terrain check
        if not self.is_walkable(x, y):
            return False

        # Dynamic obstacle check
        if not ignore_obstacles and (x, y) in self._obstacles:
            return False

        return True

    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        ignore_goal_obstacle: bool = True,
        current_tick: int = 0
    ) -> Path:
        """
        Find path from start to goal using A*.

        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)
            ignore_goal_obstacle: If True, allow goal even if occupied
            current_tick: Current simulation tick for cache

        Returns:
            Path object with result and waypoints
        """
        # Same position check
        if start == goal:
            return Path(
                result=PathResult.ALREADY_THERE,
                waypoints=[],
                total_cost=0.0,
                computed_at_tick=current_tick
            )

        # Check cache
        cache_key = (start, goal)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if cached.computed_at_tick >= self._cache_tick:
                return cached

        # Goal validity check
        if not self._is_valid(goal[0], goal[1], ignore_obstacles=ignore_goal_obstacle):
            return Path(
                result=PathResult.TARGET_BLOCKED,
                waypoints=[],
                total_cost=0.0,
                computed_at_tick=current_tick
            )

        # Start validity check
        if not self._is_valid(start[0], start[1], ignore_obstacles=True):
            return Path(
                result=PathResult.NO_PATH,
                waypoints=[],
                total_cost=0.0,
                computed_at_tick=current_tick
            )

        # A* algorithm
        open_set: List[PathNode] = []
        start_node = PathNode(
            f_score=self._heuristic(start, goal),
            position=start,
            g_score=0.0
        )
        heapq.heappush(open_set, start_node)

        # Best g_score for each position
        g_scores: Dict[Tuple[int, int], float] = {start: 0.0}

        # Track visited for reconstruction
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

        iterations = 0

        while open_set and iterations < self.max_iterations:
            iterations += 1

            current = heapq.heappop(open_set)
            current_pos = current.position

            # Goal reached
            if current_pos == goal:
                path = self._reconstruct_path(came_from, current_pos, start)
                result = Path(
                    result=PathResult.SUCCESS,
                    waypoints=path,
                    total_cost=current.g_score,
                    computed_at_tick=current_tick
                )
                self._cache[cache_key] = result
                return result

            # Explore neighbors
            for dx, dy in self.DIRECTIONS:
                nx, ny = current_pos[0] + dx, current_pos[1] + dy
                neighbor = (nx, ny)

                # Skip invalid positions (allow goal even if occupied)
                if neighbor == goal:
                    is_valid = self._is_valid(nx, ny, ignore_obstacles=ignore_goal_obstacle)
                else:
                    is_valid = self._is_valid(nx, ny)

                if not is_valid:
                    continue

                # Calculate tentative g_score
                move_cost = self.get_cost(nx, ny)
                tentative_g = current.g_score + move_cost

                # Skip if we've found a better path
                if neighbor in g_scores and tentative_g >= g_scores[neighbor]:
                    continue

                # This is a better path
                g_scores[neighbor] = tentative_g
                came_from[neighbor] = current_pos

                f_score = tentative_g + self._heuristic(neighbor, goal)
                neighbor_node = PathNode(
                    f_score=f_score,
                    position=neighbor,
                    g_score=tentative_g
                )
                heapq.heappush(open_set, neighbor_node)

        # No path found
        return Path(
            result=PathResult.NO_PATH,
            waypoints=[],
            total_cost=0.0,
            computed_at_tick=current_tick
        )

    def _reconstruct_path(
        self,
        came_from: Dict[Tuple[int, int], Tuple[int, int]],
        current: Tuple[int, int],
        start: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Reconstruct path from A* search."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            if current != start:  # Don't include start in waypoints
                path.append(current)
        path.reverse()
        return path

    def find_nearest_walkable(
        self,
        start: Tuple[int, int],
        max_radius: int = 10
    ) -> Optional[Tuple[int, int]]:
        """Find nearest walkable tile to start position."""
        if self._is_valid(start[0], start[1]):
            return start

        for radius in range(1, max_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) == radius or abs(dy) == radius:
                        x, y = start[0] + dx, start[1] + dy
                        if self._is_valid(x, y):
                            return (x, y)

        return None

    def get_direction(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> str:
        """Get direction name from one position to adjacent position."""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]

        for i, (ddx, ddy) in enumerate(self.DIRECTIONS):
            if dx == ddx and dy == ddy:
                return self.DIRECTION_NAMES[i]

        # Default for non-adjacent
        if abs(dx) >= abs(dy):
            return 'east' if dx > 0 else 'west'
        else:
            return 'south' if dy > 0 else 'north'

    def get_adjacent_positions(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get walkable adjacent positions."""
        result = []
        for dx, dy in self.DIRECTIONS:
            nx, ny = pos[0] + dx, pos[1] + dy
            if self._is_valid(nx, ny):
                result.append((nx, ny))
        return result

    def are_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """Check if two positions are adjacent."""
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

    def distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance between positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def line_of_sight(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        blocks_sight: Callable[[int, int], bool]
    ) -> bool:
        """
        Check line of sight using Bresenham's line algorithm.

        Args:
            from_pos: Starting position
            to_pos: Target position
            blocks_sight: Function(x, y) -> bool

        Returns:
            True if there is clear line of sight
        """
        x0, y0 = from_pos
        x1, y1 = to_pos

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            # Skip start position
            if (x0, y0) != from_pos and (x0, y0) != to_pos:
                if blocks_sight(x0, y0):
                    return False

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return True

    def invalidate_cache(self) -> None:
        """Invalidate all cached paths."""
        self._cache.clear()
        self._cache_tick += 1
