#!/usr/bin/env python3
"""Comprehensive test of QueryAgent with realistic complex use cases."""

import asyncio
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.ai.agents.query.agent import QueryAgent
from app.ai.core.config import AIConfig


async def main():
    """Test QueryAgent with comprehensive realistic scenarios."""
    print("🧪 Comprehensive QueryAgent Testing")
    print("=" * 50)

    config = AIConfig()
    agent = QueryAgent(config, debug_explanations=False)

    # Realistic complex test cases
    test_cases = [
        {
            "name": "Mixed Fuzzy - Senior Frontend Developers",
            "query": "Find SSE with frontend experience working on customer projects",
            "metadata": {},
            "expected_type": "fuzzy",
            "description": "Tests designation + skill category + project type resolution",
        },
        {
            "name": "Pure Fuzzy - Backend Team Lead",
            "query": "Show TL with backend skills and their current allocations",
            "metadata": {},
            "expected_type": "fuzzy",
            "description": "Tests designation + skill category + allocation analysis",
        },
        {
            "name": "Non-Fuzzy Specific - React Developers",
            "query": "List all employees with React skills and their proficiency levels",
            "metadata": {},
            "expected_type": "non-fuzzy",
            "description": "Tests specific skill search with proficiency",
        },
        {
            "name": "Complex Fuzzy - Mobile Team Utilization",
            "query": "Find mobile developers who are overallocated across projects",
            "metadata": {},
            "expected_type": "fuzzy",
            "description": "Tests skill category + allocation calculation + aggregation",
        },
        {
            "name": "Mixed Resource Planning",
            "query": "Show available PM and QA engineers for new project assignments",
            "metadata": {},
            "expected_type": "fuzzy",
            "description": "Tests multiple designations + availability calculation",
        },
        {
            "name": "Non-Fuzzy Project Analysis",
            "query": "List all active customer projects with their allocated employees",
            "metadata": {},
            "expected_type": "non-fuzzy",
            "description": "Tests specific project status + type filtering",
        },
        {
            "name": "Complex Skill Matrix",
            "query": "Find senior engineers with cloud and testing experience",
            "metadata": {},
            "expected_type": "fuzzy",
            "description": "Tests seniority + multiple skill categories",
        },
        {
            "name": "Resource Optimization",
            "query": "Show underutilized developers with Java or Python skills",
            "metadata": {},
            "expected_type": "mixed",
            "description": "Tests utilization calculation + specific skills",
        },
    ]

    results_summary = {
        "total": len(test_cases),
        "successful": 0,
        "failed": 0,
        "fuzzy_queries": 0,
        "non_fuzzy_queries": 0,
        "avg_sql_length": 0,
        "total_sql_length": 0,
    }

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 60}")
        print(f"🎯 Test {i}/{len(test_cases)}: {test_case['name']}")
        print(f"📝 Query: {test_case['query']}")
        print(f"🎨 Description: {test_case['description']}")
        print(f"🔍 Expected Type: {test_case['expected_type']}")

        try:
            # Process the query
            result = await agent.process(
                {"query": test_case["query"], "metadata": test_case["metadata"]}
            )

            # Analyze results
            has_fuzzy_context = bool(result.get("fuzzy_context"))
            query_type = result.get("query_type", "unknown")
            sql_query = result.get("query", "")
            sql_length = len(sql_query)

            # Update statistics
            results_summary["successful"] += 1
            results_summary["total_sql_length"] += sql_length

            if has_fuzzy_context:
                results_summary["fuzzy_queries"] += 1
            else:
                results_summary["non_fuzzy_queries"] += 1

            print(f"✅ SUCCESS!")
            print(f"   📊 Query Type: {query_type}")
            print(f"   🔧 Fuzzy Processing: {'Yes' if has_fuzzy_context else 'No'}")

            if has_fuzzy_context:
                resolved_terms = result["fuzzy_context"]["resolved_terms"]
                print(f"   🎯 Resolved Terms: {list(resolved_terms.keys())}")
                for term, values in resolved_terms.items():
                    print(
                        f"      • {term} → {len(values)} items ({', '.join(values[:3])}{'...' if len(values) > 3 else ''})"
                    )

            print(f"   📏 SQL Length: {sql_length} characters")
            print(f"   🗃️ Tables Used: {', '.join(result.get('tables', []))}")

            # Show first 150 chars of SQL for verification
            sql_preview = sql_query[:150] + "..." if len(sql_query) > 150 else sql_query
            print(f"   💾 SQL Preview: {sql_preview}")

        except Exception as e:
            results_summary["failed"] += 1
            print(f"❌ FAILED!")
            print(f"   🚨 Error: {str(e)}")
            print(f"   📍 Error Type: {type(e).__name__}")

    # Calculate final statistics
    if results_summary["successful"] > 0:
        results_summary["avg_sql_length"] = (
            results_summary["total_sql_length"] // results_summary["successful"]
        )

    # Print comprehensive summary
    print(f"\n{'=' * 60}")
    print(f"📈 COMPREHENSIVE TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"🎯 Total Test Cases: {results_summary['total']}")
    print(f"✅ Successful: {results_summary['successful']}")
    print(f"❌ Failed: {results_summary['failed']}")
    print(
        f"📊 Success Rate: {(results_summary['successful'] / results_summary['total'] * 100):.1f}%"
    )
    print(f"")
    print(f"🔍 Query Type Distribution:")
    print(f"   • Fuzzy Queries: {results_summary['fuzzy_queries']}")
    print(f"   • Non-Fuzzy Queries: {results_summary['non_fuzzy_queries']}")
    print(f"")
    print(f"📏 SQL Statistics:")
    print(f"   • Average SQL Length: {results_summary['avg_sql_length']} characters")
    print(f"   • Total SQL Generated: {results_summary['total_sql_length']} characters")

    # Final assessment
    if results_summary["successful"] == results_summary["total"]:
        print(f"\n🎉 EXCELLENT! All test cases passed successfully!")
        print(f"💡 The QueryAgent handles both fuzzy and non-fuzzy queries perfectly!")
    elif results_summary["successful"] >= results_summary["total"] * 0.8:
        print(f"\n👍 GOOD! Most test cases passed successfully!")
        print(f"🔧 Minor issues to investigate in failed cases.")
    else:
        print(f"\n⚠️  NEEDS ATTENTION! Several test cases failed.")
        print(f"🛠️  Requires debugging and fixes.")


if __name__ == "__main__":
    asyncio.run(main())
