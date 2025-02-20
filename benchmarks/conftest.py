import pytest
from parlat.core.common import generate_id
from parlat.core.loggers import Logger
from parlat.core.nlp.generation import UsageInfo


@pytest.fixture
def benchmark_logger():
    return Logger("benchmark")


@pytest.fixture
def generate_session_id():
    return lambda: generate_id()


@pytest.fixture
def create_usage_info():
    def _create(input_tokens: int, output_tokens: int) -> UsageInfo:
        return UsageInfo(input_tokens=input_tokens, output_tokens=output_tokens)

    return _create
