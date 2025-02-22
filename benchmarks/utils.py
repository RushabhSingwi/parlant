from typing import Optional, Dict, Any
from parlant.core.agents import Agent
from parlant.core.services.tools.plugins import ToolPlugin


class TestToolPlugin(ToolPlugin):
    """A simple tool plugin for testing purposes."""

    def __init__(self, name: str = "test_tool"):
        super().__init__(name=name)

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Mock execution that returns the input parameters."""
        return kwargs


async def create_test_agent(
    agent_id: str = "test-agent",
    name: str = "Test Agent",
    description: Optional[str] = None,
    tools: Optional[list[ToolPlugin]] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> Agent:
    """
    Creates a test agent with configurable parameters for testing purposes.

    Args:
        agent_id: Unique identifier for the agent
        name: Display name for the agent
        description: Optional description of the agent's purpose
        tools: Optional list of tool plugins available to the agent
        properties: Optional dictionary of additional agent properties

    Returns:
        Agent: Configured test agent instance
    """
    if description is None:
        description = "A test agent for benchmark scenarios"

    if tools is None:
        tools = [TestToolPlugin()]

    if properties is None:
        properties = {"test_mode": True, "benchmark_ready": True}

    agent = Agent(
        id=agent_id,
        name=name,
        description=description,
        tools=tools,
        properties=properties,
    )

    return agent


def get_default_test_properties() -> Dict[str, Any]:
    """
    Returns a default set of properties used for test agents.

    Returns:
        Dict[str, Any]: Default test properties
    """
    return {
        "test_mode": True,
        "benchmark_ready": True,
        "response_delay": 0,
        "error_rate": 0.0,
        "max_tokens": 1000,
        "temperature": 0.7,
        "memory_enabled": True,
    }


async def create_test_agents(count: int) -> list[Agent]:
    """
    Creates multiple test agents with incrementing IDs.

    Args:
        count: Number of test agents to create

    Returns:
        list[Agent]: List of configured test agents
    """
    agents = []
    for i in range(count):
        agent = await create_test_agent(
            agent_id=f"test-agent-{i}",
            name=f"Test Agent {i}",
            properties=get_default_test_properties(),
        )
        agents.append(agent)
    return agents


async def create_specialized_test_agent(
    specialization: str,
    custom_tools: Optional[list[ToolPlugin]] = None,
) -> Agent:
    """
    Creates a test agent with specialized configuration for specific test scenarios.

    Args:
        specialization: Type of specialized agent ("memory", "tools", "performance")
        custom_tools: Optional list of custom tools for the specialized agent

    Returns:
        Agent: Specialized test agent instance
    """
    properties = get_default_test_properties()

    if specialization == "memory":
        properties.update(
            {
                "memory_enabled": True,
                "memory_window": 100,
                "memory_type": "conversation",
            }
        )
    elif specialization == "tools":
        properties.update({"tool_usage_enabled": True, "tool_timeout": 5.0})
    elif specialization == "performance":
        properties.update({"response_delay": 0, "batch_processing": True, "cache_enabled": True})

    return await create_test_agent(
        agent_id=f"specialized-{specialization}-agent",
        name=f"Specialized {specialization.title()} Agent",
        description=f"Test agent specialized for {specialization} testing",
        tools=custom_tools,
        properties=properties,
    )


async def cleanup_test_agents(agents: list[Agent]) -> None:
    """
    Performs cleanup operations on test agents after testing.

    Args:
        agents: List of test agents to cleanup
    """
    for agent in agents:
        # Clear any cached data
        agent.properties.clear()
        # Reset any stateful properties
        if hasattr(agent, "tools"):
            agent.tools = []
