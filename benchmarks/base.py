from dataclasses import dataclass
from typing import Dict, List
import time
import psutil
import json
from pathlib import Path
from parlant.core.engines.alpha import AlphaEngine
from parlant.core.common import generate_id


@dataclass
class ComponentMetrics:
    duration_ms: float
    input_tokens: int
    output_tokens: int
    memory_mb: float


@dataclass
class ScenarioResult:
    name: str
    success: bool
    total_duration_ms: float
    total_memory_mb: float
    total_input_tokens: int
    total_output_tokens: int
    components: Dict[str, ComponentMetrics]


class BenchmarkSuite:
    def __init__(self, version: str, save_dir: Path):
        self.version = version
        self.save_dir = save_dir
        self.results: List[ScenarioResult] = []
        self.components: Dict[str, ComponentMetrics] = {}  # Initialize components dict

    def measure_scenario(self, name: str, scenario_func) -> ScenarioResult:
        components = {}
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        scenario_result = None

        try:
            start_time = time.perf_counter()
            scenario_result = scenario_func(self._measure_component)  # Store the result
            success = True
        except Exception as e:
            success = False
            print(f"Scenario {name} failed: {e}")

        end_time = time.perf_counter()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024

        return ScenarioResult(
            name=name,
            success=success and scenario_result is not None,  # Update success condition
            total_duration_ms=(end_time - start_time) * 1000,
            total_memory_mb=end_memory - start_memory,
            total_input_tokens=sum(c.input_tokens for c in components.values()),
            total_output_tokens=sum(c.output_tokens for c in components.values()),
            components=components,
        )

    def _measure_component(self, name: str, func, *args, **kwargs):
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        start_time = time.perf_counter()

        result = func(*args, **kwargs)

        duration = (time.perf_counter() - start_time) * 1000
        memory = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory

        # Extract token usage from result if available
        usage_info = getattr(result, "usage_info", None)
        input_tokens = usage_info.input_tokens if usage_info else 0
        output_tokens = usage_info.output_tokens if usage_info else 0

        self.components[name] = ComponentMetrics(
            duration_ms=duration,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            memory_mb=memory,
        )

        return result

    def generate_report(self):
        report = {
            "version": self.version,
            "summary": {
                "total_scenarios": len(self.results),
                "successful_scenarios": sum(1 for r in self.results if r.success),
                "average_response_time": sum(r.total_duration_ms for r in self.results)
                / len(self.results),
                "total_tokens_processed": sum(
                    r.total_input_tokens + r.total_output_tokens for r in self.results
                ),
            },
            "scenarios": [vars(r) for r in self.results],
        }

        # Save JSON report
        report_path = self.save_dir / f"benchmark_report_{self.version}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        # Generate visual report
        self._generate_visual_report()

    def _generate_visual_report(self):
        import matplotlib.pyplot as plt
        import pandas as pd

        # Create DataFrame from results
        df = pd.DataFrame([vars(r) for r in self.results])

        plt.figure(figsize=(15, 10))

        # Success Rate
        plt.subplot(2, 2, 1)
        success_rate = df["success"].mean() * 100
        plt.pie([success_rate, 100 - success_rate], labels=["Success", "Failure"])
        plt.title("Scenario Success Rate")

        # Response Times
        plt.subplot(2, 2, 2)
        df["total_duration_ms"].hist()
        plt.title("Response Time Distribution")
        plt.xlabel("Duration (ms)")

        # Token Usage
        plt.subplot(2, 2, 3)
        token_data = df[["total_input_tokens", "total_output_tokens"]].mean()
        token_data.plot(kind="bar")
        plt.title("Average Token Usage")

        # Memory Usage
        plt.subplot(2, 2, 4)
        df["total_memory_mb"].hist()
        plt.title("Memory Usage Distribution")
        plt.xlabel("Memory (MB)")

        plt.tight_layout()
        plt.savefig(self.save_dir / f"benchmark_visual_{self.version}.png")


async def run_feature_benchmarks(version: str, save_dir: Path):
    suite = BenchmarkSuite(version, save_dir)
    engine = AlphaEngine()

    # Example scenario measuring a pizza ordering conversation
    async def pizza_order_scenario(measure):
        agent = await measure("setup", engine.create_agent)  # Use engine method instead
        session_id = generate_id()  # Use imported function

        # Measure guideline processing
        response = await measure(
            "process_message",
            engine.process_message,
            agent_id=agent.id,
            session_id=session_id,
            message="Can I order a large pepperoni pizza with Sprite?",
        )

        # Measure tool execution
        await measure(  # Remove unused variable
            "check_drinks",
            engine.execute_tool,
            agent_id=agent.id,
            session_id=session_id,
            tool_name="get_available_drinks",
        )

        return response

    result = await suite.measure_scenario("pizza_order", pizza_order_scenario)
    suite.results.append(result)
    # Add more scenarios...
    suite.generate_report()
