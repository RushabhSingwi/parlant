from pathlib import Path
from parlant.core.engines.alpha import AlphaEngine
from benchmarks.base import BenchmarkSuite

async def run_feature_benchmarks(version: str, save_dir: Path):
    suite = BenchmarkSuite(version, save_dir)
    engine = AlphaEngine()
    
    # Example scenario measuring a pizza ordering conversation
    async def pizza_order_scenario(measure):
        agent = await measure('setup', create_test_agent)
        session_id = generate_session_id()
        
        # Measure guideline processing
        response = await measure(
            'process_message',
            engine.process_message,
            agent_id=agent.id,
            session_id=session_id,
            message="Can I order a large pepperoni pizza with Sprite?"
        )
        
        # Measure tool execution
        drinks = await measure(
            'check_drinks',
            engine.execute_tool,
            agent_id=agent.id,
            session_id=session_id,
            tool_name="get_available_drinks"
        )
        
        return response
    
    result = await suite.measure_scenario('pizza_order', pizza_order_scenario)
    suite.results.append(result)
    
    # Add more scenarios...
    
    suite.generate_report() 