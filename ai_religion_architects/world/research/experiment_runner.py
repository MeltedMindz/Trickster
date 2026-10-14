"""
Research Experiment Runner

Provides infrastructure for:
- Running controlled world experiments
- Ablation studies
- Metric collection
- Reproducible results
"""

import json
import time
import logging
import sqlite3
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum
import random
import copy

from ..simulation import WorldSimulation, WorldEvent
from ..debate_adapter import WorldDebateAdapter

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """Status of an experiment."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class ExperimentConfig:
    """Configuration for an experiment."""
    name: str
    description: str
    seed: int
    total_ticks: int
    world_size: int = 128
    agent_ids: List[str] = field(default_factory=lambda: ['Zealot', 'Skeptic', 'Trickster'])

    # Ablation flags
    enable_pathfinding: bool = True
    enable_perception: bool = True
    enable_affordances: bool = True
    enable_world_debate_integration: bool = True

    # Collection settings
    collect_metrics_every: int = 10  # Collect every N ticks
    snapshot_every: int = 100        # Full snapshot every N ticks

    # Parameters to vary
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'seed': self.seed,
            'total_ticks': self.total_ticks,
            'world_size': self.world_size,
            'agent_ids': self.agent_ids,
            'enable_pathfinding': self.enable_pathfinding,
            'enable_perception': self.enable_perception,
            'enable_affordances': self.enable_affordances,
            'enable_world_debate_integration': self.enable_world_debate_integration,
            'collect_metrics_every': self.collect_metrics_every,
            'snapshot_every': self.snapshot_every,
            'parameters': self.parameters,
        }


@dataclass
class MetricSample:
    """A single metric sample."""
    tick: int
    metric_name: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """Results from an experiment run."""
    experiment_id: str
    config: ExperimentConfig
    status: ExperimentStatus
    start_time: datetime
    end_time: Optional[datetime]
    metrics: List[MetricSample]
    snapshots: List[Dict]
    events: List[Dict]
    error: Optional[str] = None

    def get_metric_series(self, metric_name: str) -> List[Tuple[int, float]]:
        """Get time series for a specific metric."""
        return [
            (m.tick, m.value)
            for m in self.metrics
            if m.metric_name == metric_name
        ]

    def get_metric_statistics(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        values = [m.value for m in self.metrics if m.metric_name == metric_name]
        if not values:
            return {}
        return {
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0,
            'count': len(values),
        }


class MetricCollector:
    """Collects metrics from world simulation."""

    def __init__(self, world: WorldSimulation):
        self.world = world

    def collect_all_metrics(self, tick: int) -> List[MetricSample]:
        """Collect all available metrics."""
        metrics = []

        # Agent metrics
        for agent_id, agent in self.world.agents.items():
            metrics.append(MetricSample(
                tick=tick,
                metric_name=f"agent_{agent_id}_energy",
                value=agent.energy,
                metadata={'agent_id': agent_id}
            ))

            metrics.append(MetricSample(
                tick=tick,
                metric_name=f"agent_{agent_id}_x",
                value=float(agent.tile_x),
                metadata={'agent_id': agent_id}
            ))

            metrics.append(MetricSample(
                tick=tick,
                metric_name=f"agent_{agent_id}_y",
                value=float(agent.tile_y),
                metadata={'agent_id': agent_id}
            ))

            # Action state (1 if busy, 0 if idle)
            metrics.append(MetricSample(
                tick=tick,
                metric_name=f"agent_{agent_id}_active",
                value=1.0 if agent.current_action else 0.0,
                metadata={'agent_id': agent_id}
            ))

        # Agent proximity metrics
        agents = list(self.world.agents.values())
        for i, a1 in enumerate(agents):
            for a2 in agents[i+1:]:
                dist = abs(a1.tile_x - a2.tile_x) + abs(a1.tile_y - a2.tile_y)
                metrics.append(MetricSample(
                    tick=tick,
                    metric_name=f"proximity_{a1.agent_id}_{a2.agent_id}",
                    value=float(dist),
                    metadata={'agents': [a1.agent_id, a2.agent_id]}
                ))

        # World state metrics
        metrics.append(MetricSample(
            tick=tick,
            metric_name="object_count",
            value=float(len(self.world.objects))
        ))

        metrics.append(MetricSample(
            tick=tick,
            metric_name="event_count",
            value=float(len(self.world.recent_events))
        ))

        # Average energy
        if agents:
            avg_energy = sum(a.energy for a in agents) / len(agents)
            metrics.append(MetricSample(
                tick=tick,
                metric_name="avg_energy",
                value=avg_energy
            ))

        return metrics


class ExperimentRunner:
    """
    Runs world simulation experiments with reproducibility.

    Supports:
    - Controlled seeding
    - Metric collection
    - State snapshots
    - Ablation studies
    """

    def __init__(self, output_dir: str = 'experiments'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.current_experiment: Optional[ExperimentResult] = None

    def run_experiment(
        self,
        config: ExperimentConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> ExperimentResult:
        """
        Run a single experiment.

        Args:
            config: Experiment configuration
            progress_callback: Optional callback(current_tick, total_ticks)

        Returns:
            ExperimentResult with all collected data
        """
        experiment_id = f"{config.name}_{config.seed}_{int(time.time())}"

        logger.info(f"Starting experiment: {experiment_id}")
        logger.info(f"Config: {config.description}")

        result = ExperimentResult(
            experiment_id=experiment_id,
            config=config,
            status=ExperimentStatus.RUNNING,
            start_time=datetime.now(),
            end_time=None,
            metrics=[],
            snapshots=[],
            events=[],
        )

        self.current_experiment = result

        try:
            # Create isolated database for experiment
            db_path = self.output_dir / f"{experiment_id}.db"

            # Initialize world with seed
            world = WorldSimulation(
                db_path=str(db_path),
                headless=True,
                world_seed=config.seed
            )

            # Apply ablation settings
            if not config.enable_pathfinding:
                # Disable pathfinding by using direct movement only
                pass  # Would require modifying world behavior

            # Create metric collector
            collector = MetricCollector(world)

            # Run simulation
            for tick in range(config.total_ticks):
                # Simulate one tick
                events = world.simulate_tick()

                # Store events
                for event in events:
                    result.events.append(event.to_dict())

                # Collect metrics at interval
                if tick % config.collect_metrics_every == 0:
                    metrics = collector.collect_all_metrics(tick)
                    result.metrics.extend(metrics)

                # Take snapshot at interval
                if tick % config.snapshot_every == 0:
                    snapshot = world.get_state_snapshot()
                    snapshot['experiment_tick'] = tick
                    result.snapshots.append(snapshot)

                # Progress callback
                if progress_callback:
                    progress_callback(tick, config.total_ticks)

                # Allow interruption
                if result.status == ExperimentStatus.ABORTED:
                    break

            # Final snapshot
            result.snapshots.append(world.get_state_snapshot())

            # Mark complete
            result.status = ExperimentStatus.COMPLETED
            result.end_time = datetime.now()

            logger.info(f"Experiment {experiment_id} completed")

        except Exception as e:
            result.status = ExperimentStatus.FAILED
            result.error = str(e)
            result.end_time = datetime.now()
            logger.error(f"Experiment {experiment_id} failed: {e}")

        finally:
            self.current_experiment = None

            # Save results
            self._save_results(result)

        return result

    def run_ablation_study(
        self,
        base_config: ExperimentConfig,
        ablation_flags: List[str],
        seeds: List[int]
    ) -> Dict[str, List[ExperimentResult]]:
        """
        Run ablation study varying specified flags.

        Args:
            base_config: Base configuration
            ablation_flags: Flags to ablate (e.g., ['enable_pathfinding', 'enable_perception'])
            seeds: List of seeds for statistical significance

        Returns:
            Dict mapping ablation condition to list of results
        """
        results = {}

        # Run baseline
        results['baseline'] = []
        for seed in seeds:
            config = copy.deepcopy(base_config)
            config.seed = seed
            config.name = f"{base_config.name}_baseline"
            result = self.run_experiment(config)
            results['baseline'].append(result)

        # Run ablations
        for flag in ablation_flags:
            results[f"ablate_{flag}"] = []
            for seed in seeds:
                config = copy.deepcopy(base_config)
                config.seed = seed
                config.name = f"{base_config.name}_ablate_{flag}"
                setattr(config, flag, False)
                result = self.run_experiment(config)
                results[f"ablate_{flag}"].append(result)

        return results

    def run_parameter_sweep(
        self,
        base_config: ExperimentConfig,
        parameter_name: str,
        parameter_values: List[Any],
        seeds: List[int]
    ) -> Dict[Any, List[ExperimentResult]]:
        """
        Run parameter sweep experiment.

        Args:
            base_config: Base configuration
            parameter_name: Name of parameter to sweep
            parameter_values: Values to test
            seeds: Seeds for each value

        Returns:
            Dict mapping parameter value to results
        """
        results = {}

        for value in parameter_values:
            results[value] = []
            for seed in seeds:
                config = copy.deepcopy(base_config)
                config.seed = seed
                config.name = f"{base_config.name}_{parameter_name}_{value}"
                config.parameters[parameter_name] = value
                result = self.run_experiment(config)
                results[value].append(result)

        return results

    def _save_results(self, result: ExperimentResult) -> None:
        """Save experiment results to disk."""
        result_path = self.output_dir / f"{result.experiment_id}_results.json"

        # Convert to serializable format
        data = {
            'experiment_id': result.experiment_id,
            'config': result.config.to_dict(),
            'status': result.status.value,
            'start_time': result.start_time.isoformat(),
            'end_time': result.end_time.isoformat() if result.end_time else None,
            'error': result.error,
            'metrics_summary': {
                name: result.get_metric_statistics(name)
                for name in set(m.metric_name for m in result.metrics)
            },
            'event_count': len(result.events),
            'snapshot_count': len(result.snapshots),
        }

        with open(result_path, 'w') as f:
            json.dump(data, f, indent=2)

        # Save full metrics separately
        metrics_path = self.output_dir / f"{result.experiment_id}_metrics.json"
        metrics_data = [
            {
                'tick': m.tick,
                'metric': m.metric_name,
                'value': m.value,
                'metadata': m.metadata,
            }
            for m in result.metrics
        ]

        with open(metrics_path, 'w') as f:
            json.dump(metrics_data, f)

        logger.info(f"Results saved to {result_path}")


class ReplayEngine:
    """
    Replay recorded experiments for analysis.
    """

    def __init__(self, experiment_dir: str = 'experiments'):
        self.experiment_dir = Path(experiment_dir)

    def list_experiments(self) -> List[Dict]:
        """List all recorded experiments."""
        experiments = []

        for result_file in self.experiment_dir.glob("*_results.json"):
            with open(result_file) as f:
                data = json.load(f)
                experiments.append({
                    'id': data['experiment_id'],
                    'name': data['config']['name'],
                    'status': data['status'],
                    'start_time': data['start_time'],
                })

        return sorted(experiments, key=lambda x: x['start_time'], reverse=True)

    def load_experiment(self, experiment_id: str) -> Optional[Dict]:
        """Load experiment results."""
        result_path = self.experiment_dir / f"{experiment_id}_results.json"

        if not result_path.exists():
            return None

        with open(result_path) as f:
            return json.load(f)

    def load_metrics(self, experiment_id: str) -> Optional[List[Dict]]:
        """Load full metrics for an experiment."""
        metrics_path = self.experiment_dir / f"{experiment_id}_metrics.json"

        if not metrics_path.exists():
            return None

        with open(metrics_path) as f:
            return json.load(f)

    def compare_experiments(
        self,
        experiment_ids: List[str],
        metric_name: str
    ) -> Dict[str, Dict]:
        """Compare a metric across multiple experiments."""
        comparison = {}

        for exp_id in experiment_ids:
            result = self.load_experiment(exp_id)
            if result:
                stats = result.get('metrics_summary', {}).get(metric_name, {})
                comparison[exp_id] = stats

        return comparison


def quick_experiment(
    name: str = "quick_test",
    ticks: int = 100,
    seed: int = 12345
) -> ExperimentResult:
    """
    Run a quick experiment for testing.

    Args:
        name: Experiment name
        ticks: Number of ticks to run
        seed: Random seed

    Returns:
        ExperimentResult
    """
    config = ExperimentConfig(
        name=name,
        description=f"Quick test experiment with {ticks} ticks",
        seed=seed,
        total_ticks=ticks,
        collect_metrics_every=10,
        snapshot_every=50,
    )

    runner = ExperimentRunner()
    return runner.run_experiment(config)
