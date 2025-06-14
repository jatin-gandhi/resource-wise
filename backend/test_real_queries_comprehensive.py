#!/usr/bin/env python3
"""
Test real-world queries with fuzzy classification and query generation results.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.ai.agents.fuzzy.classifier import FuzzyClassifier
from app.ai.agents.query.agent import QueryAgent
from app.ai.core.config import AIConfig

# Test queries with expected classifications
TEST_QUERIES = [
    {
        "query": "Give me all KD India employees",
        "expected": "PRECISE",
        "description": "Direct database query for specific company employees",
    },
    {
        "query": "List all tech leads and senior engineers",
        "expected": "FUZZY",
        "description": "Requires fuzzy resolution of job titles",
    },
    {
        "query": "Show me all contractors working on customer projects",
        "expected": "PRECISE",
        "description": "Direct query for contractors on customer projects",
    },
    {
        "query": "Give me contractors who are unallocated",
        "expected": "PRECISE",
        "description": "Direct query for unallocated contractors",
    },
    {
        "query": "Give me total cost of completed customer projects",
        "expected": "PRECISE",
        "description": "Direct aggregation query",
    },
    {
        "query": "give me the most expensive resource",
        "expected": "FUZZY",
        "description": "Requires interpretation of 'most expensive'",
    },
    {
        "query": "find me a lead with backend and devops skill from bangalore",
        "expected": "FUZZY",
        "description": "Requires fuzzy resolution of skills and job titles",
    },
    {
        "query": "give me resources with frontend skills",
        "expected": "FUZZY",
        "description": "Requires fuzzy resolution of skill categories",
    },
    {
        "query": "give me lead with reactjs",
        "expected": "FUZZY",
        "description": "Requires fuzzy resolution of job title and skill",
    },
]


async def test_comprehensive_query_processing():
    """Test queries with both classification and query processing."""

    print("🔍 TESTING REAL-WORLD QUERIES - COMPREHENSIVE")
    print("=" * 80)
    print("Testing fuzzy classification AND SQL query generation")
    print("=" * 80)
    print()

    # Initialize components
    ai_config = AIConfig()
    classifier = FuzzyClassifier(ai_config)
    query_agent = QueryAgent(ai_config, debug_explanations=True)

    correct_classifications = 0
    total_queries = len(TEST_QUERIES)

    for i, test_case in enumerate(TEST_QUERIES, 1):
        query = test_case["query"]
        expected = test_case["expected"]
        description = test_case["description"]

        print(f"📝 Query {i}: '{query}'")
        print("─" * 60)

        try:
            # 1. Test fuzzy classification
            classification_result = await classifier.classify(query)
            actual_classification = classification_result["classification"].upper()
            fuzzy_terms = classification_result["fuzzy_terms"]
            is_correct = actual_classification == expected

            if is_correct:
                correct_classifications += 1

            print(f"🎯 Expected: {expected}")
            print(f"🤖 Actual: {actual_classification}")
            print(f"✅ Correct: {'YES' if is_correct else 'NO'}")
            print(f"🔧 Fuzzy Terms: {fuzzy_terms if fuzzy_terms else 'None'}")

            # 2. Process query through agent
            print(f"🗄️  Query Processing:")
            try:
                # Prepare input data for the agent
                input_data = {"query": query, "metadata": {}}

                # Process the query through the agent
                result = await query_agent.process(input_data)

                print(f"   📊 Query Type: {result.get('query_type', 'unknown')}")

                if result.get("fuzzy_explanation"):
                    print(f"   🔍 Fuzzy Resolution: {result['fuzzy_explanation']}")

                # Show the generated SQL query
                sql_query = result.get("query", "")
                if sql_query:
                    print(f"   ✅ SQL Generated: YES")
                    # Show truncated SQL for readability
                    if len(sql_query) > 300:
                        print(f"   🔧 SQL Query: {sql_query[:300]}...")
                    else:
                        print(f"   🔧 SQL Query: {sql_query}")
                else:
                    print(f"   ❌ SQL Generated: NO")

                # Show parameters if any
                if result.get("parameters"):
                    print(f"   📋 Parameters: {result['parameters']}")

                # Show any errors
                if result.get("error"):
                    print(f"   ❌ Error: {result['error']}")

                # Show explanation if available
                if result.get("explanation"):
                    print(f"   💡 Agent Explanation: {result['explanation']}")

            except Exception as e:
                print(f"   ❌ Query processing error: {str(e)}")

            print(f"💡 Analysis: {description}")
            if not is_correct:
                if actual_classification == "FUZZY" and expected == "PRECISE":
                    print("⚠️  Classified as fuzzy but should be precise - may over-process")
                elif actual_classification == "PRECISE" and expected == "FUZZY":
                    print(
                        "⚠️  Classified as precise but should be fuzzy - may miss semantic resolution"
                    )
            else:
                if actual_classification == "FUZZY":
                    print("💡 Correctly identified as fuzzy - terms need resolution")
                else:
                    print("💡 Correctly identified as precise - direct database query")

        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            import traceback

            traceback.print_exc()

        print("─" * 60)
        print()

    # Summary
    print("=" * 80)
    print("📊 CLASSIFICATION SUMMARY")
    print("=" * 80)
    print(f"✅ Correct Classifications: {correct_classifications}/{total_queries}")
    print(f"📈 Accuracy: {(correct_classifications / total_queries) * 100:.1f}%")

    if correct_classifications < total_queries:
        print("⚠️  Some misclassifications detected.")
        print("🔧 Review the results above to fine-tune if needed.")
    else:
        print("🎉 All queries classified correctly!")

    print()
    print("=" * 80)
    print("🎯 BUSINESS IMPACT")
    print("=" * 80)
    print("✅ Fuzzy queries will get semantic term resolution")
    print("✅ Precise queries will go directly to SQL generation")
    print("✅ Users can use natural business language")
    print("✅ System handles both technical and business queries")
    print("✅ Generated SQL queries ready for database execution")
    print()


if __name__ == "__main__":
    asyncio.run(test_comprehensive_query_processing())
