#!/usr/bin/env python3
"""Simple demonstration of the Intent Agent with standardized output format."""

import asyncio
import sys
from pathlib import Path

# Add the backend app to the Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.ai.agents.intent.agent import IntentAgent, IntentType
from app.ai.core.config import AIConfig


async def demo_intent_agent():
    """Demonstrate Intent Agent functionality with key examples."""
    
    print("🚀 ResourceWise Intent Agent Demo")
    print("=" * 50)
    print("This demo shows how the Intent Agent classifies user queries")
    print("and provides standardized output format for seamless integration.")
    print("=" * 50)
    
    # Initialize Intent Agent
    try:
        intent_agent = IntentAgent()
        print("✅ Intent Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Intent Agent: {e}")
        print("💡 Make sure OPENAI_API_KEY is set in your environment")
        return
    
    # Demo queries
    demo_queries = [
        {
            "name": "Database Query - Employee Search",
            "query": "Find all Software Engineers with Python skills",
            "expected": "DATABASE_QUERY with SQL generation"
        },
        {
            "name": "Database Query - Specific Allocation",
            "query": "Show me the allocation of james.wilson@techvantage.io",
            "expected": "DATABASE_QUERY with employee-specific SQL"
        },
        {
            "name": "Greeting", 
            "query": "Hello! Good morning",
            "expected": "GREETING with welcome response"
        },
        {
            "name": "Help Request",
            "query": "What can you help me with?",
            "expected": "HELP_REQUEST with capability explanation"
        },
        {
            "name": "General Conversation",
            "query": "How does resource allocation work?",
            "expected": "GENERAL_CONVERSATION with informative response"
        }
    ]
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"\n{'🔍' if 'Database' in demo['name'] else '💬'} Demo {i}: {demo['name']}")
        print(f"Query: \"{demo['query']}\"")
        print(f"Expected: {demo['expected']}")
        print("-" * 50)
        
        try:
            # Prepare input
            input_data = {
                "query": demo["query"],
                "session_id": f"demo-session-{i}",
                "user_id": "demo-user",
                "metadata": {}
            }
            
            # Process through Intent Agent
            response = await intent_agent.process(input_data)
            
            # Display standardized response
            print("📋 Standardized Response:")
            print(f"   Intent: {response.get('intent', 'Unknown')}")
            print(f"   Success: {response.get('success', 'Unknown')}")
            print(f"   Requires Database: {response.get('requires_database', 'Unknown')}")
            print(f"   Response: {response.get('response', 'No response')[:100]}...")
            
            # Show database-specific details
            if response.get('requires_database'):
                print(f"\n🗄️  Database Query Details:")
                print(f"   Query Type: {response.get('query_type', 'Unknown')}")
                print(f"   SQL Generated: {response.get('sql_query', 'None')[:80]}...")
                print(f"   Tables: {response.get('tables', 'None')}")
                
                query_result = response.get('query_result', {})
                if query_result:
                    print(f"   Query Agent Result: Available ✅")
                else:
                    print(f"   Query Agent Result: Not available ❌")
            
            # Show error if any
            if response.get('error'):
                print(f"\n❌ Error: {response.get('error')}")
                
            print("✅ Demo completed successfully")
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
        
        print()  # Add spacing
    
    print("=" * 50)
    print("🎯 Key Features Demonstrated:")
    print("   ✅ Intent classification (DATABASE_QUERY, GREETING, HELP_REQUEST, etc.)")
    print("   ✅ Standardized response format with success/error indicators")
    print("   ✅ Seamless Query Agent integration for database queries")
    print("   ✅ Enhanced parameter extraction with fallback logic")
    print("   ✅ Proper error handling and informative responses")
    print("\n🎉 Intent Agent is ready for integration!")


if __name__ == "__main__":
    asyncio.run(demo_intent_agent()) 