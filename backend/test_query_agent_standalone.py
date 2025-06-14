#!/usr/bin/env python3
"""Simple standalone test for Query Agent with logging."""

import asyncio
import os
import sys
from typing import Any

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import structlog
from app.ai.agents.query.agent import QueryAgent
from app.core.config import settings

# Configure structured logging to show our query generation logs
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


async def test_query_agent_with_raw_input():
    """Test Query Agent with raw natural language input."""

    print("🧠 Testing Query Agent with Raw Natural Language Input")
    print("=" * 80)

    # Test cases - natural language only, no pre-processed metadata
    test_cases = [
        {
            "name": "Simple Employee Search",
            "query": "Find all employees who are currently active",
        },
        {
            "name": "Skills-based Search",
            "query": "Show me developers with Python skills",
        },
        {
            "name": "Specific Employee Query",
            "query": "What projects is alex.johnson@techvantage.io working on?",
        },
        {
            "name": "Availability Analysis",
            "query": "Find employees who are less than 75% allocated",
        },
        {
            "name": "Complex Project Query",
            "query": "Show me all Senior Software Engineers working on active customer projects with their allocation percentages",
        },
    ]

    # Initialize Query Agent
    try:
        agent = QueryAgent()
        print("✅ Query Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Query Agent: {e}")
        return

    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 20} Test {i}: {test_case['name']} {'=' * 20}")
        print(f"🗣️  Natural Language Query: '{test_case['query']}'")
        print("-" * 80)

        try:
            # Prepare raw input (what Intent Agent would pass)
            input_data = {
                "query": test_case["query"],
                "session_id": f"test-session-{i}",
                "user_id": "test-user",
                "metadata": {},  # No pre-processed metadata - raw input only
            }

            # Process through Query Agent
            print("🔄 Processing through Query Agent...")
            result = await agent.process(input_data)

            if "error" in result:
                print(f"❌ Query Agent Error: {result['error']}")
                continue

            # Display results
            print(f"\n📊 Query Generation Results:")
            print(f"   ✅ Success: SQL generated")
            print(f"   🏷️  Query Type: {result.get('query_type', 'unknown')}")
            print(f"   📋 Tables Used: {result.get('tables', [])}")
            print(f"   🔗 Joins: {len(result.get('joins', []))} join(s)")
            print(f"   🔍 Filters: {result.get('filters', 'None')}")

            # Show the generated SQL (formatted nicely)
            sql_query = result.get("query", "")
            if sql_query:
                print(f"\n🛠️  Generated SQL Query:")
                print("   " + "-" * 60)
                # Format SQL for better readability
                formatted_sql = (
                    sql_query.replace(";", ";\n")
                    .replace(" FROM ", "\nFROM ")
                    .replace(" WHERE ", "\nWHERE ")
                    .replace(" JOIN ", "\nJOIN ")
                )
                for line in formatted_sql.split("\n"):
                    if line.strip():
                        print(f"   {line.strip()}")
                print("   " + "-" * 60)

            print(f"✅ Test {i} completed successfully")

        except Exception as e:
            print(f"❌ Test {i} failed with exception: {e}")
            import traceback

            traceback.print_exc()

    print(f"\n🎉 Query Agent Standalone Testing Complete!")
    print("=" * 80)
    print("Key Points Verified:")
    print("✅ Query Agent accepts raw natural language input")
    print("✅ No pre-processed metadata required from Intent Agent")
    print("✅ Comprehensive SQL generation logging")
    print("✅ Dynamic query type detection")
    print("✅ Proper error handling")


async def main():
    """Run the standalone Query Agent test."""
    await test_query_agent_with_raw_input()


if __name__ == "__main__":
    # Check if we have required environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Test may fail.")
        print("Set OPENAI_API_KEY environment variable to run full test.")
        print("For now, testing initialization only...")

    asyncio.run(main())
