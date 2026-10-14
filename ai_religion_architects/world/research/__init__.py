"""
Research Harness for World Experiments

Provides tools for:
- Running controlled experiments
- Ablation studies
- Metric collection
- Replay and analysis
"""

from .experiment_runner import (
    ExperimentRunner,
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    MetricCollector,
    MetricSample,
    ReplayEngine,
    quick_experiment,
)

__all__ = [
    'ExperimentRunner',
    'ExperimentConfig',
    'ExperimentResult',
    'ExperimentStatus',
    'MetricCollector',
    'MetricSample',
    'ReplayEngine',
    'quick_experiment',
]
