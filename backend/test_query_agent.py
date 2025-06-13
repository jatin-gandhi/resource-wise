#!/usr/bin/env python3
"""Test script for QueryAgent to verify it works correctly and doesn't hallucinate."""

import asyncio

from sqlalchemy import text

from app.ai.agents.query.agent import QueryAgent, QueryType
from app.core.database import get_async_session


async def execute_query(query: str):
    """Execute a query against the database and return results."""
    try:
        async for session in get_async_session():
            result = await session.execute(text(query))
            rows = result.fetchall()
            columns = list(result.keys())

            # Convert to list of dictionaries
            results = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                results.append(row_dict)

            return results, None
    except Exception as e:
        return [], str(e)


async def test_specific_use_cases():
    """Test specific use cases requested by the user."""
    print("🧪 Testing QueryAgent with specific use cases...")
    print("🔑 Make sure OPENAI_API_KEY is set in your environment")

    # Initialize the agent
    try:
        agent = QueryAgent()
        print("✅ QueryAgent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize QueryAgent: {e}")
        print("💡 Make sure OPENAI_API_KEY is set in your .env file")
        return

    # Specific test cases requested
    test_cases = [
        {
            "name": "Find All Available Resources",
            "input": {
                "query": "Find all available resources",
                "session_id": "test-session-1",
                "user_id": "test-user",
                "metadata": {"query_type": QueryType.RESOURCE_SEARCH, "limit": 50},
            },
            "description": "Should find all active employees who are available for allocation",
        },
        {
            "name": "Find Allocation of Specific Employee",
            "input": {
                "query": "Find the allocation of james.wilson@techvantage.io",
                "session_id": "test-session-2",
                "user_id": "test-user",
                "metadata": {
                    "query_type": QueryType.ANALYTICS,
                    "filters": {"email": "james.wilson@techvantage.io"},
                },
            },
            "description": "Should find current project allocations for the specific employee",
        },
        {
            "name": "Get Project List for Specific Employee",
            "input": {
                "query": "Give me the list of projects of james.wilson@techvantage.io. Provide me the project name, start date, end date, status, and allocated percentage in output.",
                "session_id": "test-session-3",
                "user_id": "test-user",
                "metadata": {
                    "query_type": QueryType.ANALYTICS,
                    "filters": {"email": "james.wilson@techvantage.io"},
                    "columns": [
                        "project_name",
                        "start_date",
                        "end_date",
                        "status",
                        "allocated_percentage",
                    ],
                },
            },
            "description": "Should return detailed project information with specific columns for the employee",
        },
        {
            "name": "Get All SSE Projects with Complete Information",
            "input": {
                "query": "Give me projects of all Senior Software Engineers with complete information including employee name, project details, and allocation status",
                "session_id": "test-session-4",
                "user_id": "test-user",
                "metadata": {
                    "query_type": QueryType.ANALYTICS,
                    "filters": {"designation": "Senior Software Engineer"},
                    "include_details": True,
                },
            },
            "description": "Should return comprehensive project information for all SSEs including employee details, project info, and allocation status",
        },
        {
            "name": "Find Overallocated Employees",
            "input": {
                "query": "Show me all employees who are allocated more than 100% across active projects",
                "session_id": "test-session-5",
                "user_id": "test-user",
                "metadata": {
                    "query_type": QueryType.ANALYTICS,
                    "analysis_type": "overallocation",
                    "threshold": 100,
                },
            },
            "description": "Should identify employees with total active allocations exceeding 100% capacity",
        },
        {
            "name": "Get Project Team Composition",
            "input": {
                "query": "Show me the team composition for all active projects with employee names, designations, and their allocation percentages",
                "session_id": "test-session-6",
                "user_id": "test-user",
                "metadata": {
                    "query_type": QueryType.ANALYTICS,
                    "analysis_type": "team_composition",
                    "project_status": "active",
                },
            },
            "description": "Should show detailed team structure for active projects with employee roles and allocation levels",
        },
        {
            "name": "Find Employees Available for New Projects",
            "input": {
                "query": "Find all employees who have less than 75% allocation and are available for new project assignments",
                "session_id": "test-session-7",
                "user_id": "test-user",
                "metadata": {
                    "query_type": QueryType.RESOURCE_SEARCH,
                    "availability_threshold": 75,
                    "status": "available",
                },
            },
            "description": "Should identify employees with capacity for additional project work",
        },
        {
            "name": "Get Project Timeline and Resource Summary",
            "input": {
                "query": "Show me all projects with their timelines, total team size, and resource allocation summary ordered by start date",
                "session_id": "test-session-8",
                "user_id": "test-user",
                "metadata": {
                    "query_type": QueryType.ANALYTICS,
                    "analysis_type": "project_summary",
                    "order_by": "start_date",
                },
            },
            "description": "Should provide comprehensive project overview with timeline and resource metrics",
        },
        {
            "name": "Find Employees by Designation and Availability",
            "input": {
                "query": "Get all Software Engineers and Senior Software Engineers who are currently active and show their current project assignments",
                "session_id": "test-session-9",
                "user_id": "test-user",
                "metadata": {
                    "query_type": QueryType.RESOURCE_SEARCH,
                    "designations": ["Software Engineer", "Senior Software Engineer"],
                    "include_assignments": True,
                },
            },
            "description": "Should filter employees by specific designations and show their current project status",
        },
    ]

    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"🔍 Test {i}: {test_case['name']}")
        print(f"Query: '{test_case['input']['query']}'")
        print(f"Description: {test_case['description']}")

        try:
            # Generate SQL query using QueryAgent
            print("\n🤖 Generating SQL with QueryAgent...")
            result = await agent.process(test_case["input"])

            if "error" in result and result["error"]:
                print(f"❌ QueryAgent Error: {result['error']}")
                continue

            generated_sql = result["query"]
            print("\n✅ Generated SQL:")
            print(f"   {generated_sql}")

            print("\n📊 Query Analysis:")
            print(f"   - Type: {result['query_type']}")
            print(f"   - Tables used: {result['tables']}")
            print(f"   - Joins: {result['joins']}")
            print(f"   - Filters: {result['filters']}")

            # Execute the query against the database
            print("\n🗄️  Executing query against database...")
            db_results, db_error = await execute_query(generated_sql)

            if db_error:
                print(f"❌ Database Error: {db_error}")
                print("💡 This indicates the generated SQL has issues")

                # Try to suggest fixes
                if "does not exist" in db_error.lower():
                    print("🔧 Suggestion: Check table/column names in the schema")
                elif "syntax error" in db_error.lower():
                    print("🔧 Suggestion: Check SQL syntax")

            else:
                print("✅ Query executed successfully!")
                results_count = len(db_results)
                print(f"📈 Results: {results_count} rows returned")

                if db_results and len(db_results) > 0:
                    print("\n📋 Sample Results (first 5 rows):")
                    for j, row in enumerate(db_results[:5], 1):
                        print(f"   Row {j}:")
                        for key, value in row.items():
                            # Truncate long values for readability
                            display_value = str(value)
                            if len(display_value) > 50:
                                display_value = display_value[:47] + "..."
                            print(f"     {key}: {display_value}")
                        print()

                    if len(db_results) > 5:
                        print(f"   ... and {len(db_results) - 5} more rows")
                else:
                    print("   No results found (empty result set)")

            # Validation checks
            query_lower = generated_sql.lower()
            issues = []

            # Check for hallucinated tables (common mistakes)
            hallucination_patterns = [
                (
                    "department" in query_lower and "departments" not in query_lower,
                    "❌ Uses 'department' table (doesn't exist, should be 'designations')",
                ),
                (
                    "skill" in query_lower
                    and "skills" not in query_lower
                    and "employee_skills" not in query_lower,
                    "❌ Uses 'skill' table (doesn't exist, should be 'employee_skills')",
                ),
                (
                    "user" in query_lower and "users" not in query_lower,
                    "❌ Incorrect 'user' table reference",
                ),
                (
                    "employee" in query_lower
                    and "employees" not in query_lower
                    and "employee_" not in query_lower,
                    "❌ Uses 'employee' table (should be 'employees')",
                ),
            ]

            for check, message in hallucination_patterns:
                if check:
                    issues.append(message)

            # Check for good practices
            good_practices = []
            if "select" in query_lower:
                good_practices.append("✅ Has SELECT clause")
            if "from" in query_lower:
                good_practices.append("✅ Has FROM clause")
            if any(alias in query_lower for alias in [" e.", " d.", " p.", " a.", " es.", " u."]):
                good_practices.append("✅ Uses table aliases")
            if "where" in query_lower:
                good_practices.append("✅ Has filtering conditions")
            if "join" in query_lower:
                good_practices.append("✅ Uses JOINs for multi-table queries")
            if generated_sql.rstrip().endswith(";"):
                good_practices.append("✅ Properly terminated with semicolon")

            print("\n🔍 Validation Results:")
            if issues:
                print("   Issues found:")
                for issue in issues:
                    print(f"     {issue}")
            else:
                print("   ✅ No hallucination issues detected!")

            print("   Good practices:")
            for practice in good_practices:
                print(f"     {practice}")

            # Overall assessment
            if not issues and not db_error:
                print(f"\n🎉 Test {i} PASSED - Query is accurate and executes successfully!")
            elif not db_error:
                print(f"\n⚠️  Test {i} executes but has style issues")
            else:
                print(f"\n❌ Test {i} FAILED - Query has errors")

        except Exception as e:
            print(f"❌ Test {i} failed with exception: {str(e)}")
            import traceback

            traceback.print_exc()

    print(f"\n{'=' * 80}")
    print("🎯 Test Summary:")
    print("💡 Key improvements implemented:")
    print("   ✅ Strict schema validation to prevent hallucination")
    print("   ✅ Clear, specific prompts with PostgreSQL syntax")
    print("   ✅ Retry logic for better accuracy")
    print("   ✅ Real database schema integration")
    print("   ✅ Database execution validation")


if __name__ == "__main__":
    asyncio.run(test_specific_use_cases())
