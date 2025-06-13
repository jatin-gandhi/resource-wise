#!/usr/bin/env python3
"""Test script for enhanced workflow with intent and query agents."""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.ai.core.config import AIConfig
from app.ai.workflow.graph import AgentWorkflow


async def test_workflow():
    """Test the enhanced workflow with different types of queries."""
    
    # Initialize configuration
    config = AIConfig()
    
    # Initialize workflow
    workflow = AgentWorkflow(config)
    
    # Test cases
    test_cases = [
        {
            "name": "Database Query - Employee Search",
            "input": "Find all software engineers with Python skills",
            "expected_route": "intent -> query -> end"
        },
        {
            "name": "Database Query - Person Lookup",
            "input": "Tell me Rohit Mehra's current allocation?",
            "expected_route": "intent -> query -> end"
        },
        {
            "name": "General Conversation",
            "input": "Hello, how are you?",
            "expected_route": "intent -> end"
        },
        {
            "name": "Help Request",
            "input": "What can you help me with?",
            "expected_route": "intent -> end"
        },
        {
            "name": "Database Query - Analytics",
            "input": "Show me overallocated employees",
            "expected_route": "intent -> query -> end"
        }
    ]
    
    print("🚀 Testing Enhanced Workflow with Intent and Query Agents")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        print(f"Expected Route: {test_case['expected_route']}")
        print("-" * 40)
        
        try:
            # Process the query
            result = await workflow.process(
                user_input=test_case['input'],
                session_id=f"test_session_{i}",
                context={"user_id": "test_user", "test_case": test_case['name']}
            )
            
            # Display results
            print(f"✅ Status: {result.current_stage}")
            print(f"🎯 Intent: {result.query_result.get('intent', 'unknown')}")
            print(f"🔍 Requires Database: {result.query_result.get('requires_database', False)}")
            
            if result.query_result.get('sql_query'):
                print(f"📊 SQL Query Generated: Yes")
                print(f"🗂️  Tables Used: {result.query_result.get('tables_used', [])}")
            else:
                print(f"📊 SQL Query Generated: No")
            
            print(f"💬 Response Preview: {result.query_result.get('response', '')[:100]}...")
            
            if result.error:
                print(f"⚠️  Error: {result.error}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()
    
    print("🎉 Workflow testing completed!")


async def test_workflow_routing():
    """Test the conditional routing logic specifically."""
    
    print("\n🔀 Testing Workflow Routing Logic")
    print("=" * 40)
    
    config = AIConfig()
    workflow = AgentWorkflow(config)
    
    # Test database query routing
    print("Testing database query routing...")
    db_result = await workflow.process(
        user_input="Find employees with Java skills",
        session_id="routing_test_1",
        context={"user_id": "test_user"}
    )
    
    print(f"Database Query Route - Stage: {db_result.current_stage}")
    print(f"Has SQL Query: {bool(db_result.query_result.get('sql_query'))}")
    
    # Test general conversation routing
    print("\nTesting general conversation routing...")
    general_result = await workflow.process(
        user_input="Hello there!",
        session_id="routing_test_2", 
        context={"user_id": "test_user"}
    )
    
    print(f"General Query Route - Stage: {general_result.current_stage}")
    print(f"Has SQL Query: {bool(general_result.query_result.get('sql_query'))}")


if __name__ == "__main__":
    # Set up environment
    # os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key-here") 
    
    print("Enhanced Workflow Test Suite")
    print("Make sure you have set OPENAI_API_KEY environment variable")
    print()
    
    # Run tests
    asyncio.run(test_workflow())
    asyncio.run(test_workflow_routing()) 