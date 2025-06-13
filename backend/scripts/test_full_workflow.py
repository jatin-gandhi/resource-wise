#!/usr/bin/env python3
"""Test script for the complete workflow with database execution."""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.ai.core.config import AIConfig
from app.ai.workflow.graph import AgentWorkflow
from app.services.database import db_service


async def test_database_connection():
    """Test database connection before running workflow tests."""
    print("🔌 Testing Database Connection")
    print("=" * 40)
    
    try:
        # Test database connection
        result = await db_service.test_connection()
        
        if result.get("success", False):
            print("✅ Database connection successful")
            return True
        else:
            print(f"❌ Database connection failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False


async def test_full_workflow():
    """Test the complete workflow with database execution."""
    
    print("\n🚀 Testing Complete Workflow with Database Execution")
    print("=" * 60)
    
    # Initialize configuration
    config = AIConfig()
    
    # Initialize workflow
    workflow = AgentWorkflow(config)
    
    # Test cases for database queries
    test_cases = [
        {
            "name": "Employee Search by Skills",
            "input": "Find all software engineers with Python skills",
            "expected_flow": "intent → query → database → format → end",
            "expected_tables": ["employees", "employee_skills"]
        },
        {
            "name": "Simple Employee Lookup",
            "input": "Show me all employees",
            "expected_flow": "intent → query → database → format → end",
            "expected_tables": ["employees"]
        },
        {
            "name": "Department Search",
            "input": "List all employees in the Engineering department",
            "expected_flow": "intent → query → database → format → end",
            "expected_tables": ["employees", "departments"]
        },
        {
            "name": "General Conversation (No DB)",
            "input": "Hello, how are you?",
            "expected_flow": "intent → end",
            "expected_tables": []
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        print(f"Expected Flow: {test_case['expected_flow']}")
        print("-" * 50)
        
        try:
            # Process the query
            result = await workflow.process(
                user_input=test_case['input'],
                session_id=f"test_session_{i}",
                context={"user_id": "test_user", "test_case": test_case['name']}
            )
            
            # Display results
            print(f"✅ Final Stage: {result.current_stage}")
            print(f"🎯 Intent: {result.query_result.get('intent', 'unknown')}")
            print(f"🔍 Requires Database: {result.query_result.get('requires_database', False)}")
            
            # Check if SQL query was generated
            if result.query_result.get('sql_query'):
                print(f"📊 SQL Query: {result.query_result['sql_query'][:100]}...")
                print(f"🗂️  Tables Used: {result.query_result.get('tables_used', [])}")
                
                # Check database execution
                db_result = result.query_result.get('database_result', {})
                if db_result:
                    print(f"💾 Database Success: {db_result.get('success', False)}")
                    print(f"📈 Rows Retrieved: {db_result.get('row_count', 0)}")
                    print(f"⏱️  Execution Time: {db_result.get('execution_time', 0)}s")
                    
                    if not db_result.get('success', False):
                        print(f"⚠️  Database Error: {db_result.get('error', 'Unknown')}")
                        print(f"🔍 Error Type: {db_result.get('error_type', 'Unknown')}")
                
                # Check response formatting
                formatted_data = result.query_result.get('formatted_data')
                if formatted_data:
                    print(f"🎨 Response Format: {formatted_data.get('type', 'unknown')}")
                    
            else:
                print(f"📊 SQL Query: Not generated (non-database query)")
            
            # Show response preview
            response = result.query_result.get('response', '')
            print(f"💬 Response Preview: {response[:150]}{'...' if len(response) > 150 else ''}")
            
            if result.error:
                print(f"⚠️  Workflow Error: {result.error}")
                
        except Exception as e:
            print(f"❌ Test Error: {str(e)}")
        
        print()
    
    print("🎉 Full workflow testing completed!")


async def test_database_security():
    """Test database security features."""
    
    print("\n🔒 Testing Database Security Features")
    print("=" * 40)
    
    # Test cases for security validation
    security_tests = [
        {
            "name": "Valid SELECT Query",
            "sql": "SELECT id, name FROM employees LIMIT 10;",
            "should_pass": True
        },
        {
            "name": "Dangerous DROP Query",
            "sql": "DROP TABLE employees;",
            "should_pass": False
        },
        {
            "name": "UPDATE Query (Not Allowed)",
            "sql": "UPDATE employees SET name = 'test';",
            "should_pass": False
        },
        {
            "name": "SQL Injection Attempt",
            "sql": "SELECT * FROM employees; DROP TABLE users; --",
            "should_pass": False
        }
    ]
    
    for i, test in enumerate(security_tests, 1):
        print(f"\n{i}. {test['name']}")
        print(f"SQL: {test['sql']}")
        
        try:
            is_safe, error_msg = await db_service.validate_query_safety(test['sql'])
            
            if test['should_pass']:
                if is_safe:
                    print("✅ Correctly allowed safe query")
                else:
                    print(f"❌ Incorrectly blocked safe query: {error_msg}")
            else:
                if not is_safe:
                    print(f"✅ Correctly blocked dangerous query: {error_msg}")
                else:
                    print("❌ Incorrectly allowed dangerous query")
                    
        except Exception as e:
            print(f"❌ Security test error: {str(e)}")


async def test_response_formatting():
    """Test response formatting with sample data."""
    
    print("\n🎨 Testing Response Formatting")
    print("=" * 40)
    
    from app.services.response_formatter import response_formatter
    
    # Sample database results for testing
    sample_results = [
        {
            "name": "Table Format Test",
            "query_result": {
                "success": True,
                "data": [
                    {"id": 1, "name": "John Doe", "email": "john@example.com", "department": "Engineering"},
                    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "department": "Marketing"},
                    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "department": "Engineering"}
                ],
                "columns": ["id", "name", "email", "department"],
                "row_count": 3,
                "execution_time": 0.05
            },
            "query_context": {"query_type": "resource_search"},
            "original_query": "Find all employees"
        },
        {
            "name": "Empty Results Test",
            "query_result": {
                "success": True,
                "data": [],
                "columns": [],
                "row_count": 0,
                "execution_time": 0.02
            },
            "query_context": {"query_type": "skill_search"},
            "original_query": "Find employees with COBOL skills"
        },
        {
            "name": "Error Response Test",
            "query_result": {
                "success": False,
                "error": "Table 'nonexistent' doesn't exist",
                "error_type": "SYNTAX_ERROR",
                "data": [],
                "columns": [],
                "row_count": 0,
                "execution_time": 0
            },
            "query_context": {"query_type": "resource_search"},
            "original_query": "Find data from nonexistent table"
        }
    ]
    
    for i, test in enumerate(sample_results, 1):
        print(f"\n{i}. {test['name']}")
        
        try:
            formatted = await response_formatter.format_database_response(
                query_result=test['query_result'],
                query_context=test['query_context'],
                original_query=test['original_query']
            )
            
            print(f"✅ Format Type: {formatted.get('metadata', {}).get('format', 'unknown')}")
            print(f"📝 Summary: {formatted.get('summary', 'No summary')}")
            print(f"💬 Response: {formatted.get('response', '')[:100]}...")
            
        except Exception as e:
            print(f"❌ Formatting error: {str(e)}")


async def main():
    """Main test function."""
    
    print("🧪 ResourceWise AI - Complete Workflow Test Suite")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some tests may fail.")
    
    if not os.getenv("DATABASE_URL") and not all([
        os.getenv("DATABASE_HOST"),
        os.getenv("DATABASE_NAME"),
        os.getenv("DATABASE_USER"),
        os.getenv("DATABASE_PASSWORD")
    ]):
        print("⚠️  Warning: Database configuration not found. Database tests will fail.")
    
    # Run tests
    try:
        # Test database connection first
        db_connected = await test_database_connection()
        
        # Test response formatting (doesn't need DB)
        await test_response_formatting()
        
        # Test security features
        if db_connected:
            await test_database_security()
            
            # Test full workflow
            await test_full_workflow()
        else:
            print("\n⚠️  Skipping database-dependent tests due to connection issues")
            
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")
    
    finally:
        # Clean up database connections
        try:
            await db_service.close()
        except:
            pass
    
    print("\n🏁 Test suite completed!")


if __name__ == "__main__":
    # Set up environment defaults
    # os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key-here")
    
    # Run the test suite
    asyncio.run(main()) 