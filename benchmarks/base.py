from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import time
import psutil
import json
from pathlib import Path


@dataclass
class BenchmarkResult:
    name: str
    duration_ms: float
    memory_mb: float
    tokens_processed: int
    tokens_generated: int
    extra_metrics: Optional[Dict[str, Any]] = None


class BaseBenchmark:
    def __init__(self, name: str, save_dir: Path):
        self.name = name
        self.save_dir = save_dir
        self.results: List[BenchmarkResult] = []

    def measure_performance(self, func, *args, **kwargs) -> BenchmarkResult:
        # Measure memory before
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # Convert to MB

        # Measure time
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = (time.perf_counter() - start_time) * 1000  # Convert to ms

        # Measure memory after
        memory_after = process.memory_info().rss / 1024 / 1024
        memory_used = memory_after - memory_before

        # Get token metrics from result
        usage_info = getattr(result, "usage_info", None)
        tokens_in = usage_info.input_tokens if usage_info else 0
        tokens_out = usage_info.output_tokens if usage_info else 0

        benchmark_result = BenchmarkResult(
            name=self.name,
            duration_ms=duration,
            memory_mb=memory_used,
            tokens_processed=tokens_in,
            tokens_generated=tokens_out,
        )
        self.results.append(benchmark_result)
        return benchmark_result

    def save_results(self):
        results_file = self.save_dir / f"{self.name}_results.json"
        with open(results_file, "w") as f:
            json.dump([vars(result) for result in self.results], f, indent=2)
