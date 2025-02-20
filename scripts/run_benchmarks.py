import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import json
import matplotlib.pyplot as plt
import pandas as pd


async def run_benchmarks(save_dir: Path):
    # Run pytest with benchmark markers
    import pytest

    pytest.main(
        [
            "benchmarks",
            "-v",
            "--benchmark-only",
            f"--benchmark-json={save_dir}/benchmark_results.json",
        ]
    )


def generate_report(save_dir: Path):
    # Load all benchmark results
    results = []
    for result_file in save_dir.glob("*_results.json"):
        with open(result_file) as f:
            results.extend(json.load(f))

    # Convert to DataFrame for analysis
    df = pd.DataFrame(results)

    # Generate plots
    plt.figure(figsize=(12, 6))

    # Response time distribution
    plt.subplot(1, 2, 1)
    df[df["name"] == "response_time"]["duration_ms"].hist()
    plt.title("Response Time Distribution")
    plt.xlabel("Duration (ms)")

    # Memory usage by benchmark type
    plt.subplot(1, 2, 2)
    df.groupby("name")["memory_mb"].mean().plot(kind="bar")
    plt.title("Average Memory Usage by Benchmark Type")
    plt.xlabel("Benchmark Type")
    plt.ylabel("Memory (MB)")

    plt.tight_layout()
    plt.savefig(save_dir / "benchmark_report.png")

    # Generate summary statistics
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_benchmarks": len(results),
        "average_response_time": df["duration_ms"].mean(),
        "average_memory_usage": df["memory_mb"].mean(),
        "total_tokens_processed": df["tokens_processed"].sum(),
        "total_tokens_generated": df["tokens_generated"].sum(),
    }

    with open(save_dir / "benchmark_summary.json", "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Parlant benchmarks")
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=Path("benchmark_results"),
        help="Directory to save benchmark results",
    )
    args = parser.parse_args()

    args.save_dir.mkdir(exist_ok=True)
    asyncio.run(run_benchmarks(args.save_dir))
    generate_report(args.save_dir)
