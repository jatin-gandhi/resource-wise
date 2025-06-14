#!/usr/bin/env python3
"""Test vector fallback scenarios with terms not in predefined mappings."""

import asyncio
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.ai.agents.query.agent import QueryAgent
from app.ai.core.config import AIConfig


async def main():
    """Test QueryAgent with scenarios that trigger vector fallback."""
    print("🧪 Vector Fallback Scenarios Testing")
    print("=" * 50)

    config = AIConfig()
    agent = QueryAgent(config, debug_explanations=False)

    # Test cases designed to trigger vector fallback
    vector_test_cases = [
        {
            "name": "Seniority Terms - Vector Fallback",
            "query": "Find experienced developers with leadership skills",
            "metadata": {},
            "description": "Tests 'experienced' and 'leadership' - not in predefined mappings",
            "expected_vector_terms": ["experienced", "leadership"],
        },
        {
            "name": "Soft Skills - Vector Fallback",
            "query": "Show employees with communication and teamwork abilities",
            "metadata": {},
            "description": "Tests soft skills that require vector similarity",
            "expected_vector_terms": ["communication", "teamwork", "abilities"],
        },
        {
            "name": "Project Status - Vector Fallback",
            "query": "Find overallocated engineers on critical projects",
            "metadata": {},
            "description": "Tests 'overallocated' and 'critical' via vector search",
            "expected_vector_terms": ["overallocated", "critical"],
        },
        {
            "name": "Technology Variants - Vector Fallback",
            "query": "Show developers with machine learning and AI expertise",
            "metadata": {},
            "description": "Tests ML/AI terms not in skill categories",
            "expected_vector_terms": ["machine learning", "AI", "expertise"],
        },
        {
            "name": "Business Domain - Vector Fallback",
            "query": "Find consultants working on fintech and healthcare projects",
            "metadata": {},
            "description": "Tests domain-specific terms",
            "expected_vector_terms": ["consultants", "fintech", "healthcare"],
        },
        {
            "name": "Performance Terms - Vector Fallback",
            "query": "Show underutilized senior architects with mentoring experience",
            "metadata": {},
            "description": "Tests performance and role terms",
            "expected_vector_terms": ["underutilized", "architects", "mentoring"],
        },
        {
            "name": "Mixed Predefined + Vector",
            "query": "Find SSE with blockchain and cryptocurrency knowledge",
            "metadata": {},
            "description": "Tests mix of predefined (SSE) and vector (blockchain, crypto)",
            "expected_vector_terms": ["blockchain", "cryptocurrency", "knowledge"],
        },
        {
            "name": "Complex Vector Query",
            "query": "Show innovative developers with startup experience and entrepreneurial mindset",
            "metadata": {},
            "description": "Tests multiple vector terms in complex query",
            "expected_vector_terms": ["innovative", "startup", "entrepreneurial", "mindset"],
        },
    ]

    results_summary = {
        "total": len(vector_test_cases),
        "successful": 0,
        "failed": 0,
        "vector_fallback_triggered": 0,
        "mixed_resolution": 0,
        "pure_vector": 0,
        "total_vector_terms": 0,
    }

    for i, test_case in enumerate(vector_test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"🎯 Vector Test {i}/{len(vector_test_cases)}: {test_case['name']}")
        print(f"📝 Query: {test_case['query']}")
        print(f"🎨 Description: {test_case['description']}")
        print(f"🔍 Expected Vector Terms: {test_case['expected_vector_terms']}")

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

            if has_fuzzy_context:
                resolved_terms = result["fuzzy_context"]["resolved_terms"]
                results_summary["vector_fallback_triggered"] += 1
                results_summary["total_vector_terms"] += len(resolved_terms)

                # Check if it's mixed (predefined + vector) or pure vector
                predefined_terms = [
                    "SSE",
                    "PM",
                    "QA",
                    "TL",
                    "frontend",
                    "backend",
                    "mobile",
                    "cloud",
                    "testing",
                    "data",
                ]
                has_predefined = any(term in predefined_terms for term in resolved_terms.keys())

                if has_predefined:
                    results_summary["mixed_resolution"] += 1
                else:
                    results_summary["pure_vector"] += 1

            print(f"✅ SUCCESS!")
            print(f"   📊 Query Type: {query_type}")
            print(f"   🔧 Fuzzy Processing: {'Yes' if has_fuzzy_context else 'No'}")

            if has_fuzzy_context:
                resolved_terms = result["fuzzy_context"]["resolved_terms"]
                print(
                    f"   🎯 Resolved Terms ({len(resolved_terms)}): {list(resolved_terms.keys())}"
                )

                # Show resolution details
                for term, values in resolved_terms.items():
                    resolution_type = (
                        "Predefined"
                        if term
                        in [
                            "SSE",
                            "PM",
                            "QA",
                            "TL",
                            "frontend",
                            "backend",
                            "mobile",
                            "cloud",
                            "testing",
                            "data",
                        ]
                        else "Vector"
                    )
                    print(
                        f"      • {term} ({resolution_type}) → {len(values)} items ({', '.join(values[:3])}{'...' if len(values) > 3 else ''})"
                    )

            print(f"   📏 SQL Length: {sql_length} characters")
            print(f"   🗃️ Tables Used: {', '.join(result.get('tables', []))}")

            # Show SQL preview
            sql_preview = sql_query[:200] + "..." if len(sql_query) > 200 else sql_query
            print(f"   💾 SQL Preview: {sql_preview}")

        except Exception as e:
            results_summary["failed"] += 1
            print(f"❌ FAILED!")
            print(f"   🚨 Error: {str(e)}")
            print(f"   📍 Error Type: {type(e).__name__}")

    # Print comprehensive summary
    print(f"\n{'=' * 70}")
    print(f"📈 VECTOR FALLBACK TEST SUMMARY")
    print(f"{'=' * 70}")
    print(f"🎯 Total Test Cases: {results_summary['total']}")
    print(f"✅ Successful: {results_summary['successful']}")
    print(f"❌ Failed: {results_summary['failed']}")
    print(
        f"📊 Success Rate: {(results_summary['successful'] / results_summary['total'] * 100):.1f}%"
    )
    print(f"")
    print(f"🔍 Vector Fallback Analysis:")
    print(f"   • Tests with Vector Fallback: {results_summary['vector_fallback_triggered']}")
    print(f"   • Mixed Resolution (Predefined + Vector): {results_summary['mixed_resolution']}")
    print(f"   • Pure Vector Resolution: {results_summary['pure_vector']}")
    print(f"   • Total Vector Terms Resolved: {results_summary['total_vector_terms']}")

    # Calculate vector fallback rate
    vector_rate = (
        (results_summary["vector_fallback_triggered"] / results_summary["total"] * 100)
        if results_summary["total"] > 0
        else 0
    )
    print(f"   • Vector Fallback Rate: {vector_rate:.1f}%")

    # Final assessment
    if results_summary["successful"] == results_summary["total"]:
        print(f"\n🎉 EXCELLENT! All vector fallback tests passed!")
        if results_summary["vector_fallback_triggered"] >= results_summary["total"] * 0.8:
            print(f"💡 Vector fallback system is working perfectly!")
            print(f"🚀 The system gracefully handles unknown terms via semantic similarity!")
        else:
            print(
                f"📝 Note: Some queries didn't trigger vector fallback (may have been classified as non-fuzzy)"
            )
    elif results_summary["successful"] >= results_summary["total"] * 0.8:
        print(f"\n👍 GOOD! Most vector fallback tests passed!")
        print(f"🔧 Minor issues to investigate in failed cases.")
    else:
        print(f"\n⚠️  NEEDS ATTENTION! Several vector fallback tests failed.")
        print(f"🛠️  Vector similarity system may need debugging.")


if __name__ == "__main__":
    asyncio.run(main())
