from pathlib import Path
from uuid import uuid4
from parlant.core.engines.alpha import AlphaEngine
from parlant.core.agents import Agent
from benchmarks.base import BenchmarkSuite
from benchmarks.utils import create_test_agent


async def run_feature_benchmarks(version: str, save_dir: Path) -> None:
    suite = BenchmarkSuite(version, save_dir)
    engine = AlphaEngine()

    # Example scenario measuring a pizza ordering conversation
    async def pizza_order_scenario(measure) -> dict:
        agent: Agent = await measure("setup", create_test_agent)
        session_id: str = str(uuid4())

        # Measure guideline processing
        response = await measure(
            "process_message",
            engine.process_message,
            agent_id=agent.id,
            session_id=session_id,
            message="Can I order a large pepperoni pizza with Sprite?",
        )

        # Measure tool execution
        await measure(
            "check_drinks",
            engine.execute_tool,
        )

        return response

    result = await suite.measure_scenario("pizza_order", pizza_order_scenario)
    suite.results.append(result)

    # Add more scenarios...
    suite.generate_report()
