import pytest
from benchmarks.base import BaseBenchmark
from parlat.core.engines.alpha import AlphaEngine
from parlat.core.common import AgentId, SessionId
from typing import Dict, Any
from pathlib import Path


class ToolExecutionBenchmark(BaseBenchmark):
    def __init__(self, engine: AlphaEngine, save_dir: Path):
        super().__init__("tool_execution", save_dir)
        self.engine = engine

    async def benchmark_tool_execution(
        self, agent_id: AgentId, session_id: SessionId, tool_name: str, tool_args: Dict[str, Any]
    ):
        result = await self.measure_performance(
            self.engine.execute_tool,
            agent_id=agent_id,
            session_id=session_id,
            tool_name=tool_name,
            tool_args=tool_args,
        )
        return result


@pytest.mark.asyncio
async def test_tool_execution_scenarios(
    benchmark_logger, tmp_path, alpha_engine, create_test_agent, generate_session_id
):
    benchmark = ToolExecutionBenchmark(alpha_engine, tmp_path)
    agent_id = await create_test_agent()
    session_id = generate_session_id()

    # Test different tools
    tool_scenarios = [
        ("get_available_drinks", {}),
        ("get_available_toppings", {}),
        ("add", {"numbers": [1, 2, 3, 4, 5]}),
    ]

    for tool_name, args in tool_scenarios:
        result = await benchmark.benchmark_tool_execution(agent_id, session_id, tool_name, args)
        benchmark_logger.info(
            "tool_execution_benchmark",
            tool=tool_name,
            duration_ms=result.duration_ms,
            memory_mb=result.memory_mb,
        )

    benchmark.save_results()
