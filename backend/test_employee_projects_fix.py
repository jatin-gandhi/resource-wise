#!/usr/bin/env python3
"""
Test script to verify the employee-project relationship fix.
Tests that "projects of Tyler Hall" returns both managed and allocated projects.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.ai.agents.query.agent import QueryAgent
from app.ai.core.config import AIConfig


async def test_employee_projects_fix():
    """Test the employee-project relationship fix."""

    print("🔍 TESTING EMPLOYEE-PROJECT RELATIONSHIP FIX")
    print("=" * 60)
    print("Testing that 'projects of Tyler Hall' returns comprehensive results")
    print("=" * 60)
    print()

    # Initialize query agent
    ai_config = AIConfig()
    query_agent = QueryAgent(ai_config, debug_explanations=True)

    # Test queries that should use comprehensive employee-project logic
    test_queries = [
        "give me all projects of Tyler Hall",
        "show me projects of John Smith",
        "list all projects Sarah Johnson is involved in",
        "what projects is Mike Davis working on",  # Should focus on allocations
        "which projects does Lisa Chen manage",  # Should focus on project manager role
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"📝 Query {i}: '{query}'")
        print("─" * 50)

        try:
            # Prepare input data for the agent
            input_data = {"query": query, "metadata": {}}

            # Process the query through the agent
            result = await query_agent.process(input_data)

            print(f"📊 Query Type: {result.get('query_type', 'unknown')}")

            if result.get("fuzzy_explanation"):
                print(f"🔍 Fuzzy Resolution: {result['fuzzy_explanation']}")

            # Show the generated SQL query
            sql_query = result.get("query", "")
            if sql_query:
                print(f"✅ SQL Generated: YES")
                print(f"🔧 SQL Query:")
                print(f"   {sql_query}")

                # Check if the SQL includes comprehensive logic
                if "project_manager_id" in sql_query and (
                    "allocations" in sql_query or "LEFT JOIN" in sql_query
                ):
                    print(
                        f"✅ COMPREHENSIVE: Query includes both manager and allocation relationships"
                    )
                elif "project_manager_id" in sql_query and "manages" in query.lower():
                    print(f"✅ MANAGER-FOCUSED: Query correctly focuses on project manager role")
                elif "allocations" in sql_query and "working on" in query.lower():
                    print(f"✅ ALLOCATION-FOCUSED: Query correctly focuses on team member role")
                elif "project_manager_id" in sql_query and "allocations" not in sql_query:
                    print(
                        f"⚠️  MANAGER-ONLY: Query only checks project manager (may miss team member projects)"
                    )
                elif "allocations" in sql_query and "project_manager_id" not in sql_query:
                    print(
                        f"⚠️  ALLOCATION-ONLY: Query only checks allocations (may miss managed projects)"
                    )
                else:
                    print(f"❓ UNCLEAR: Unable to determine relationship logic")
            else:
                print(f"❌ SQL Generated: NO")

            # Show parameters if any
            if result.get("parameters"):
                print(f"📋 Parameters: {result['parameters']}")

            # Show any errors
            if result.get("error"):
                print(f"❌ Error: {result['error']}")

        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            import traceback

            traceback.print_exc()

        print("─" * 50)
        print()

    print("=" * 60)
    print("🎯 EXPECTED BEHAVIOR")
    print("=" * 60)
    print("✅ 'projects of [employee]' → COMPREHENSIVE (manager + allocations)")
    print("✅ 'projects [employee] is involved in' → COMPREHENSIVE (manager + allocations)")
    print("✅ 'projects [employee] is working on' → ALLOCATION-FOCUSED")
    print("✅ 'projects [employee] manages' → MANAGER-FOCUSED")
    print()
    print("The fix should ensure Tyler Hall gets ALL his projects,")
    print("not just the ones he manages!")


if __name__ == "__main__":
    asyncio.run(test_employee_projects_fix())
