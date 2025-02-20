from pathlib import Path
import pytest
from benchmarks.base import BaseBenchmark
from parlat.core.engines.alpha import AlphaEngine
from parlat.core.common import AgentId, SessionId


class ResponseTimeBenchmark(BaseBenchmark):
    def __init__(self, engine: AlphaEngine, save_dir: Path):
        super().__init__("response_time", save_dir)
        self.engine = engine

    async def benchmark_response_time(self, agent_id: AgentId, session_id: SessionId, message: str):
        result = await self.measure_performance(
            self.engine.process_message, agent_id=agent_id, session_id=session_id, message=message
        )
        return result


@pytest.mark.asyncio
async def test_response_time_scenarios(
    benchmark_logger, tmp_path, alpha_engine, create_test_agent, generate_session_id
):
    benchmark = ResponseTimeBenchmark(alpha_engine, tmp_path)
    agent_id = await create_test_agent()
    session_id = generate_session_id()

    # Test different message lengths
    messages = [
        "Hi",
        "Can you help me with a question about my order?",
        "I need detailed information about all your products and services...",
    ]

    for msg in messages:
        result = await benchmark.benchmark_response_time(agent_id, session_id, msg)
        benchmark_logger.info(
            "response_time_benchmark",
            message_length=len(msg),
            duration_ms=result.duration_ms,
            memory_mb=result.memory_mb,
        )

    benchmark.save_results()
