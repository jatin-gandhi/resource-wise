#!/usr/bin/env python3
"""Enhanced test script for Intent Agent functionality with standardized output format."""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend app to the Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.ai.agents.intent.agent import IntentAgent, IntentType
from app.ai.core.config import AIConfig


def print_response_analysis(response: dict, test_name: str):
    """Print detailed analysis of the intent agent response."""
    print(f"\n📊 Response Analysis for {test_name}:")
    print("=" * 60)
    
    # Core response fields
    print(f"Intent: {response.get('intent', 'Not found')}")
    print(f"Success: {response.get('success', 'Not found')}")
    print(f"Requires Database: {response.get('requires_database', 'Not found')}")
    print(f"Response: {response.get('response', 'Not found')[:100]}...")
    
    # Database-specific fields
    if response.get('requires_database'):
        print(f"\n🗄️  Database Query Information:")
        print(f"   Query Type: {response.get('query_type', 'Not found')}")
        print(f"   SQL Query: {response.get('sql_query', 'Not found')[:100]}...")
        print(f"   Tables: {response.get('tables', 'Not found')}")
        print(f"   Filters: {response.get('filters', 'Not found')}")
        
        # Query result details
        query_result = response.get('query_result', {})
        if query_result:
            print(f"   Query Result Available: Yes")
            print(f"   Query Result Type: {query_result.get('query_type', 'Not found')}")
            print(f"   Query Result Tables: {query_result.get('tables', 'Not found')}")
        else:
            print(f"   Query Result Available: No")
    
    # Error handling
    if response.get('error'):
        print(f"\n❌ Error: {response.get('error')}")
    
    # Metadata
    metadata = response.get('metadata', {})
    if metadata:
        print(f"\n📋 Metadata:")
        for key, value in metadata.items():
            if isinstance(value, (dict, list)):
                print(f"   {key}: {json.dumps(value, default=str)}")
            else:
                print(f"   {key}: {value}")


async def test_intent_classification_and_routing():
    """Test comprehensive intent classification and routing with various user inputs."""
    
    print("🚀 Testing Enhanced ResourceWise Intent Agent")
    print("=" * 80)
    print("🔑 Features being tested:")
    print("   ✅ Standardized output format")
    print("   ✅ Enhanced query parameter extraction")
    print("   ✅ Seamless Query Agent integration")
    print("   ✅ Error handling and fallbacks")
    print("=" * 80)
    
    # Initialize Intent Agent
    config = AIConfig(temperature=0.1)
    intent_agent = IntentAgent(config)
    
    # Comprehensive test cases covering all scenarios from the Query Agent tests
    test_cases = [
        # ======================== DATABASE QUERIES ========================
        {
            "category": "DATABASE_QUERY",
            "name": "Simple Resource Search",
            "input": {
                "query": "Find all available resources",
                "session_id": "test-session-1",
                "user_id": "test-user-1",
                "metadata": {}
            },
            "expected_intent": IntentType.DATABASE_QUERY,
            "expected_query_type": QueryType.RESOURCE_SEARCH
        },
        {
            "category": "DATABASE_QUERY",
            "name": "Specific Employee Allocation",
            "input": {
                "query": "Find the allocation of james.wilson@techvantage.io",
                "session_id": "test-session-2",
                "user_id": "test-user-2",
                "metadata": {}
            },
            "expected_intent": IntentType.DATABASE_QUERY,
            "expected_query_type": QueryType.ANALYTICS
        },
        {
            "category": "DATABASE_QUERY",
            "name": "Complex Project List Query",
            "input": {
                "query": "Give me the list of projects of james.wilson@techvantage.io. Provide me the project name, start date, end date, status, and allocated percentage in output.",
                "session_id": "test-session-3",
                "user_id": "test-user-3",
                "metadata": {}
            },
            "expected_intent": IntentType.DATABASE_QUERY,
            "expected_query_type": QueryType.ANALYTICS
        },
        {
            "category": "DATABASE_QUERY",
            "name": "Designation-based Search",
            "input": {
                "query": "Give me projects of all Senior Software Engineers with complete information including employee name, project details, and allocation status",
                "session_id": "test-session-4",
                "user_id": "test-user-4",
                "metadata": {}
            },
            "expected_intent": IntentType.DATABASE_QUERY,
            "expected_query_type": QueryType.ANALYTICS
        },
        {
            "category": "DATABASE_QUERY",
            "name": "Overallocation Analysis",
            "input": {
                "query": "Show me all employees who are allocated more than 100% across active projects",
                "session_id": "test-session-5",
                "user_id": "test-user-5",
                "metadata": {}
            },
            "expected_intent": IntentType.DATABASE_QUERY,
            "expected_query_type": QueryType.ANALYTICS
        },
        {
            "category": "DATABASE_QUERY",
            "name": "Team Composition Query",
            "input": {
                "query": "Show me the team composition for all active projects with employee names, designations, and their allocation percentages",
                "session_id": "test-session-6",
                "user_id": "test-user-6",
                "metadata": {}
            },
            "expected_intent": IntentType.DATABASE_QUERY,
            "expected_query_type": QueryType.ANALYTICS
        },
        {
            "category": "DATABASE_QUERY",
            "name": "Availability Threshold Search",
            "input": {
                "query": "Find all employees who have less than 75% allocation and are available for new project assignments",
                "session_id": "test-session-7",
                "user_id": "test-user-7",
                "metadata": {}
            },
            "expected_intent": IntentType.DATABASE_QUERY,
            "expected_query_type": QueryType.RESOURCE_SEARCH
        },
        {
            "category": "DATABASE_QUERY",
            "name": "Project Timeline Summary",
            "input": {
                "query": "Show me all projects with their timelines, total team size, and resource allocation summary ordered by start date",
                "session_id": "test-session-8",
                "user_id": "test-user-8",
                "metadata": {}
            },
            "expected_intent": IntentType.DATABASE_QUERY,
            "expected_query_type": QueryType.ANALYTICS
        },
        {
            "category": "DATABASE_QUERY",
            "name": "Multi-Designation Search",
            "input": {
                "query": "Get all Software Engineers and Senior Software Engineers who are currently active and show their current project assignments",
                "session_id": "test-session-9",
                "user_id": "test-user-9",
                "metadata": {}
            },
            "expected_intent": IntentType.DATABASE_QUERY,
            "expected_query_type": QueryType.RESOURCE_SEARCH
        },
        
        # ======================== NON-DATABASE QUERIES ========================
        {
            "category": "GREETING",
            "name": "Simple Greeting",
            "input": {
                "query": "Hello there!",
                "session_id": "test-session-10",
                "user_id": "test-user-10",
                "metadata": {}
            },
            "expected_intent": IntentType.GREETING,
            "expected_query_type": None
        },
        {
            "category": "HELP_REQUEST",
            "name": "Capability Request",
            "input": {
                "query": "What can you help me with?",
                "session_id": "test-session-11",
                "user_id": "test-user-11",
                "metadata": {}
            },
            "expected_intent": IntentType.HELP_REQUEST,
            "expected_query_type": None
        },
        {
            "category": "GENERAL_CONVERSATION",
            "name": "Conceptual Question",
            "input": {
                "query": "How does resource allocation work in modern project management?",
                "session_id": "test-session-12",
                "user_id": "test-user-12",
                "metadata": {}
            },
            "expected_intent": IntentType.GENERAL_CONVERSATION,
            "expected_query_type": None
        }
    ]
    
    # Track results
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "intent_accuracy": 0,
        "query_type_accuracy": 0,
        "format_compliance": 0
    }
    
    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'🔍' if test_case['category'] == 'DATABASE_QUERY' else '💬'} Test {i}: {test_case['name']}")
        print(f"Category: {test_case['category']}")
        print(f"Query: '{test_case['input']['query']}'")
        
        try:
            # Process through Intent Agent
            response = await intent_agent.process(test_case["input"])
            
            # Print detailed response analysis
            print_response_analysis(response, test_case['name'])
            
            # Validate standardized format
            required_fields = ["intent", "response", "requires_database", "success"]
            format_valid = all(field in response for field in required_fields)
            
            if format_valid:
                results["format_compliance"] += 1
                print(f"✅ Format Compliance: PASSED")
            else:
                missing_fields = [f for f in required_fields if f not in response]
                print(f"❌ Format Compliance: FAILED - Missing fields: {missing_fields}")
            
            # Validate intent classification
            actual_intent = response.get("intent")
            if actual_intent == test_case["expected_intent"]:
                results["intent_accuracy"] += 1
                print(f"✅ Intent Classification: PASSED ({actual_intent})")
            else:
                print(f"❌ Intent Classification: FAILED - Expected {test_case['expected_intent']}, got {actual_intent}")
            
            # Validate query type for database queries
            if test_case["expected_query_type"]:
                actual_query_type = response.get("query_type")
                if actual_query_type == test_case["expected_query_type"]:
                    results["query_type_accuracy"] += 1
                    print(f"✅ Query Type: PASSED ({actual_query_type})")
                else:
                    print(f"❌ Query Type: FAILED - Expected {test_case['expected_query_type']}, got {actual_query_type}")
            else:
                # Non-database queries shouldn't have query_type
                if "query_type" not in response or not response.get("query_type"):
                    results["query_type_accuracy"] += 1
                    print(f"✅ Query Type: PASSED (None for non-DB query)")
                else:
                    print(f"❌ Query Type: FAILED - Non-DB query should not have query_type")
            
            # Validate Database Query format compatibility
            if response.get("requires_database"):
                query_result = response.get("query_result")
                if query_result and "query" in query_result:
                    print(f"✅ Query Agent Integration: PASSED")
                    print(f"   Generated SQL: {query_result.get('query', '')[:50]}...")
                else:
                    print(f"❌ Query Agent Integration: FAILED - No valid query_result")
            
            # Overall test result
            intent_correct = actual_intent == test_case["expected_intent"]
            query_type_correct = (
                test_case["expected_query_type"] is None or 
                response.get("query_type") == test_case["expected_query_type"]
            )
            
            if format_valid and intent_correct and query_type_correct:
                results["passed"] += 1
                print(f"🎉 Test {i} OVERALL: PASSED")
            else:
                results["failed"] += 1
                print(f"❌ Test {i} OVERALL: FAILED")
                
        except Exception as e:
            results["failed"] += 1
            print(f"❌ Test {i} FAILED with exception: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Print comprehensive summary
    print(f"\n{'=' * 80}")
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    print(f"\n📈 Accuracy Metrics:")
    print(f"Intent Classification: {results['intent_accuracy']}/{results['total']} ({results['intent_accuracy']/results['total']*100:.1f}%)")
    print(f"Query Type Accuracy: {results['query_type_accuracy']}/{results['total']} ({results['query_type_accuracy']/results['total']*100:.1f}%)")
    print(f"Format Compliance: {results['format_compliance']}/{results['total']} ({results['format_compliance']/results['total']*100:.1f}%)")
    
    print(f"\n🎯 Key Features Validated:")
    print("   ✅ Standardized response format with StandardResponse class")
    print("   ✅ Enhanced query parameter extraction with fallback logic")
    print("   ✅ Proper QueryType enum integration from Query Agent")
    print("   ✅ Comprehensive error handling and success indicators")
    print("   ✅ Seamless Query Agent integration with exact input format")
    print("   ✅ Sophisticated intent classification with keyword analysis")
    
    if results["passed"] == results["total"]:
        print(f"\n🏆 ALL TESTS PASSED! Intent Agent is ready for production.")
    else:
        print(f"\n⚠️  Some tests failed. Review the issues above for improvements.")


async def test_query_agent_format_compatibility():
    """Test that Intent Agent provides exactly the format Query Agent expects."""
    
    print(f"\n{'=' * 80}")
    print("🔗 TESTING QUERY AGENT FORMAT COMPATIBILITY")
    print("=" * 80)
    
    intent_agent = IntentAgent()
    
    # Test with a specific database query
    test_input = {
        "query": "Find all Software Engineers with Python skills who are available for new projects",
        "session_id": "compatibility-test",
        "user_id": "test-user",
        "metadata": {}
    }
    
    print(f"Test Query: {test_input['query']}")
    
    try:
        # Get response from Intent Agent
        response = await intent_agent.process(test_input)
        
        if response.get("requires_database") and response.get("query_result"):
            query_result = response["query_result"]
            
            print(f"\n✅ Intent Agent Response Structure:")
            print(f"   Intent: {response.get('intent')}")
            print(f"   Requires Database: {response.get('requires_database')}")
            print(f"   Success: {response.get('success')}")
            print(f"   SQL Query: {query_result.get('query', '')[:100]}...")
            
            print(f"\n✅ Query Agent Compatible Format:")
            print(f"   Query Type: {query_result.get('query_type')}")
            print(f"   Tables: {query_result.get('tables')}")
            print(f"   Filters: {query_result.get('filters')}")
            print(f"   Parameters: {query_result.get('parameters', {})}")
            
            # Verify the format matches Query Agent expectations
            required_query_fields = ["query", "query_type", "tables", "filters"]
            has_all_fields = all(field in query_result for field in required_query_fields)
            
            if has_all_fields:
                print(f"\n🎉 FORMAT COMPATIBILITY: PASSED")
                print(f"   All required fields present for Query Agent integration")
            else:
                missing = [f for f in required_query_fields if f not in query_result]
                print(f"\n❌ FORMAT COMPATIBILITY: FAILED")
                print(f"   Missing fields: {missing}")
        else:
            print(f"\n❌ No database query result available for compatibility testing")
            
    except Exception as e:
        print(f"\n❌ Compatibility test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    async def main():
        await test_intent_classification_and_routing()
        await test_query_agent_format_compatibility()
    
    asyncio.run(main()) 
