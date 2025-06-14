"""Test realistic QueryAgent use cases with raw natural language input.

This test validates the new QueryAgent architecture where:
1. Intent Agent just classifies queries as DATABASE_QUERY vs other intents
2. Query Agent receives raw natural language and determines SQL operation type dynamically
3. No pre-processed metadata or operation types are passed to Query Agent
4. Query Agent handles all parameter extraction and query generation internally
"""

import asyncio
import os
import sys
from typing import Any

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import structlog
from app.ai.agents.query.agent import QueryAgent
from app.ai.core.config import AIConfig
from app.core.database import AsyncSessionLocal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class RealisticQueryTester:
    """Test realistic queries with database execution."""

    def __init__(self):
        """Initialize the tester."""

        # Create proper config for QueryAgent
        config = AIConfig(temperature=0.0)  # Deterministic for testing
        self.agent = QueryAgent(config)
        self.test_results = []

    async def execute_query(self, sql: str) -> tuple[list[dict], str | None]:
        """Execute SQL query and return results.

        Args:
            sql: SQL query to execute

        Returns:
            Tuple of (results, error_message)
        """
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(text(sql))

                # Handle different query types
                if sql.strip().upper().startswith("SELECT"):
                    rows = result.fetchall()
                    # Convert to list of dicts
                    columns = result.keys()
                    data = [dict(zip(columns, row)) for row in rows]
                    return data, None
                else:
                    # For INSERT/UPDATE/DELETE, return affected rows count
                    await session.commit()
                    # Get rowcount from the result
                    affected_rows = getattr(result, "rowcount", 0)
                    return [{"affected_rows": affected_rows}], None

        except Exception as e:
            return [], str(e)

    async def test_realistic_case(
        self,
        query_text: str,
        description: str,
        expected_min_results: int = 0,
        expected_max_results: int | None = None,
        should_have_data: bool = True,
        expected_operation: str | None = None,  # Optional - for validation only
    ) -> dict[str, Any]:
        """Test a realistic case with database execution.

        Args:
            query_text: Natural language query
            description: Test description
            expected_min_results: Minimum expected results
            expected_max_results: Maximum expected results (None for unlimited)
            should_have_data: Whether we expect data to be returned
            expected_operation: Expected SQL operation for validation (optional)

        Returns:
            Test result dictionary
        """
        print(f"\n🔍 Testing: {description}")
        print(f"Query: '{query_text}'")
        if expected_operation:
            print(f"Expected Operation: {expected_operation}")
        print("=" * 80)

        test_result = {
            "description": description,
            "query_text": query_text,
            "expected_operation": expected_operation,
            "success": False,
            "agent_result": None,
            "db_results": None,
            "db_error": None,
            "validation_errors": [],
        }

        try:
            # Step 1: Generate SQL with QueryAgent
            test_data = {
                "query": query_text,
                "session_id": "realistic-test",
                "user_id": "test-user",
            }

            agent_result = await self.agent.process(test_data)
            test_result["agent_result"] = agent_result

            print("✅ Generated SQL:")
            print(f"   {agent_result['query']}")
            print(f"\n📊 Query Type: {agent_result.get('query_type', 'N/A')}")
            print(f"📋 Tables: {agent_result.get('tables', [])}")
            print(f"🔗 Joins: {agent_result.get('joins', [])}")
            print(f"🔍 Filters: {agent_result.get('filters', [])}")

            if "error" in agent_result:
                print(f"❌ Agent Error: {agent_result['error']}")
                test_result["validation_errors"].append(f"Agent error: {agent_result['error']}")
                return test_result

            # Step 2: Analyze detected SQL operation type
            sql = agent_result["query"].strip().upper()
            detected_operation = "UNKNOWN"

            if sql.startswith("SELECT"):
                detected_operation = "SELECT"
            elif sql.startswith("INSERT"):
                detected_operation = "INSERT"
            elif sql.startswith("UPDATE"):
                detected_operation = "UPDATE"
            elif sql.startswith("DELETE"):
                detected_operation = "DELETE"

            print(f"\n🎯 Query Agent Operation Analysis:")
            print(f"   🔍 Detected from Natural Language: {detected_operation}")
            print(f"   🧠 Query Agent dynamically determined the SQL operation type")

            # Only validate against expected operation if provided
            operation_match = True  # Default to True
            if expected_operation:
                operation_match = detected_operation == expected_operation
                print(f"   Expected: {expected_operation}")
                print(f"   Match: {'✅ YES' if operation_match else '❌ NO'}")

                if not operation_match:
                    test_result["validation_errors"].append(
                        f"Operation mismatch: expected {expected_operation}, got {detected_operation}"
                    )
            else:
                print(f"   ✅ No expected operation specified - trusting Query Agent's decision")

            # Step 3: Execute SQL against database
            print(f"\n🗄️  Executing SQL against database...")
            db_results, db_error = await self.execute_query(agent_result["query"])
            test_result["db_results"] = db_results
            test_result["db_error"] = db_error

            if db_error:
                print(f"❌ Database Error: {db_error}")
                test_result["validation_errors"].append(f"Database error: {db_error}")
                return test_result

            # Step 4: Validate results
            result_count = len(db_results)
            print(f"📊 Database Results: {result_count} rows returned")

            # Show sample results
            if db_results and detected_operation == "SELECT":
                print("📋 Sample Results:")
                for i, row in enumerate(db_results[:3]):  # Show first 3 rows
                    print(f"   Row {i+1}: {dict(row)}")
                if result_count > 3:
                    print(f"   ... and {result_count - 3} more rows")

            # Validate result count expectations
            count_valid = True
            if result_count < expected_min_results:
                test_result["validation_errors"].append(
                    f"Too few results: got {result_count}, expected at least {expected_min_results}"
                )
                count_valid = False

            if expected_max_results is not None and result_count > expected_max_results:
                test_result["validation_errors"].append(
                    f"Too many results: got {result_count}, expected at most {expected_max_results}"
                )
                count_valid = False

            if should_have_data and result_count == 0:
                test_result["validation_errors"].append("Expected data but got no results")
                count_valid = False

            # Step 5: Overall success evaluation
            test_result["success"] = (
                operation_match
                and db_error is None
                and count_valid
                and len(test_result["validation_errors"]) == 0
            )

            print(f"\n🎯 Test Result: {'✅ PASS' if test_result['success'] else '❌ FAIL'}")
            if test_result["validation_errors"]:
                print("⚠️  Validation Issues:")
                for error in test_result["validation_errors"]:
                    print(f"   - {error}")

            return test_result

        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback

            traceback.print_exc()
            test_result["validation_errors"].append(f"Exception: {str(e)}")
            return test_result

    def _get_mock_sql_for_query(self, query_text: str, expected_operation: str) -> str | None:
        """Generate mock SQL for testing database connectivity.

        Args:
            query_text: Natural language query
            expected_operation: Expected SQL operation

        Returns:
            Mock SQL query or None
        """
        query_lower = query_text.lower()

        if expected_operation == "SELECT":
            # Generate realistic business queries based on content
            if "senior software engineer" in query_lower and "react" in query_lower:
                return """
                SELECT e.id, e.name, e.email, d.title 
                FROM employees e 
                JOIN designations d ON e.designation_id = d.id 
                JOIN employee_skills es ON e.id = es.employee_id 
                WHERE d.title = 'Senior Software Engineer' 
                AND es.skill_name = 'React' 
                AND e.is_active = true 
                LIMIT 3
                """

            elif "less than 75%" in query_lower and "available" in query_lower:
                return """
                SELECT e.id, e.name, e.email, 
                       COALESCE(SUM(a.percent_allocated), 0) as total_allocation
                FROM employees e 
                LEFT JOIN allocations a ON e.id = a.employee_id 
                    AND a.status = 'ACTIVE' 
                    AND a.end_date > CURRENT_DATE
                WHERE e.is_active = true
                GROUP BY e.id, e.name, e.email
                HAVING COALESCE(SUM(a.percent_allocated), 0) < 75
                LIMIT 20
                """

            elif "mobile banking app" in query_lower and "team members" in query_lower:
                return """
                SELECT e.name, e.email, a.percent_allocated, a.start_date, a.end_date
                FROM employees e 
                JOIN allocations a ON e.id = a.employee_id 
                JOIN projects p ON a.project_id = p.id 
                WHERE p.name = 'Mobile Banking App' 
                AND a.status = 'ACTIVE'
                ORDER BY a.percent_allocated DESC
                """

            elif "more than 100%" in query_lower and "allocated" in query_lower:
                return """
                SELECT e.name, e.email, SUM(a.percent_allocated) as total_allocation
                FROM employees e 
                JOIN allocations a ON e.id = a.employee_id 
                WHERE a.status = 'ACTIVE' 
                AND a.end_date > CURRENT_DATE
                GROUP BY e.id, e.name, e.email
                HAVING SUM(a.percent_allocated) > 100
                """

            elif "alex.johnson@techvantage.io" in query_lower and "allocation" in query_lower:
                return """
                SELECT e.name, p.name as project_name, a.percent_allocated, 
                       a.start_date, a.end_date, a.status
                FROM employees e 
                JOIN allocations a ON e.id = a.employee_id 
                JOIN projects p ON a.project_id = p.id 
                WHERE e.email = 'alex.johnson@techvantage.io'
                AND a.status = 'ACTIVE'
                ORDER BY a.start_date DESC
                """

            elif "active customer projects" in query_lower and "team size" in query_lower:
                return """
                SELECT p.name, p.duration_months, 
                       COUNT(a.employee_id) as team_size,
                       SUM(a.percent_allocated) as total_allocation
                FROM projects p 
                LEFT JOIN allocations a ON p.id = a.project_id AND a.status = 'ACTIVE'
                WHERE p.status = 'ACTIVE' 
                AND p.project_type = 'CUSTOMER'
                GROUP BY p.id, p.name, p.duration_months
                ORDER BY total_allocation DESC
                """

            elif "python skills" in query_lower and "less than 50%" in query_lower:
                return """
                SELECT e.name, e.email, es.proficiency_level,
                       COALESCE(SUM(a.percent_allocated), 0) as current_allocation
                FROM employees e 
                JOIN employee_skills es ON e.id = es.employee_id 
                LEFT JOIN allocations a ON e.id = a.employee_id 
                    AND a.status = 'ACTIVE' 
                    AND a.end_date > CURRENT_DATE
                WHERE es.skill_name = 'Python' 
                AND e.is_active = true
                GROUP BY e.id, e.name, e.email, es.proficiency_level
                HAVING COALESCE(SUM(a.percent_allocated), 0) < 50
                """

            elif "average allocation" in query_lower and "senior software engineer" in query_lower:
                return """
                SELECT d.title, 
                       COUNT(DISTINCT e.id) as employee_count,
                       AVG(COALESCE(total_alloc.allocation, 0)) as avg_allocation
                FROM designations d
                JOIN employees e ON d.id = e.designation_id
                LEFT JOIN (
                    SELECT employee_id, SUM(percent_allocated) as allocation
                    FROM allocations 
                    WHERE status = 'ACTIVE' AND end_date > CURRENT_DATE
                    GROUP BY employee_id
                ) total_alloc ON e.id = total_alloc.employee_id
                WHERE d.title = 'Senior Software Engineer'
                AND e.is_active = true
                GROUP BY d.title
                """

            elif "ending in the next 60 days" in query_lower:
                return """
                SELECT p.name, p.duration_months, 
                       e.name as employee_name, e.email,
                       a.percent_allocated, a.end_date
                FROM projects p 
                JOIN allocations a ON p.id = a.project_id 
                JOIN employees e ON a.employee_id = e.id
                WHERE a.end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '60 days'
                AND a.status = 'ACTIVE'
                ORDER BY a.end_date ASC, p.name
                """

            else:
                # Generic employee query
                return "SELECT id, name, email FROM employees WHERE is_active = true LIMIT 5"

        elif expected_operation == "INSERT":
            if "ai chatbot development" in query_lower:
                return """
                INSERT INTO projects (id, name, description, duration_months, project_type, status, created_at, updated_at)
                VALUES (gen_random_uuid(), 'AI Chatbot Development', 'AI-powered customer service chatbot', 8, 'CUSTOMER', 'PLANNING', NOW(), NOW())
                """

        elif expected_operation == "UPDATE":
            if "allocate" in query_lower and "alex.johnson@techvantage.io" in query_lower:
                # Complex allocation with validation
                return """
                WITH employee_check AS (
                    SELECT id, name, email FROM employees 
                    WHERE email = 'alex.johnson@techvantage.io' AND is_active = true
                ),
                project_check AS (
                    SELECT id, name FROM projects 
                    WHERE name = 'Mobile Banking App' AND status = 'ACTIVE'
                ),
                current_allocation AS (
                    SELECT COALESCE(SUM(a.percent_allocated), 0) as total
                    FROM allocations a
                    JOIN employee_check e ON a.employee_id = e.id
                    WHERE a.status = 'ACTIVE' 
                    AND a.end_date > CURRENT_DATE
                ),
                validation AS (
                    SELECT 
                        CASE 
                            WHEN (SELECT total FROM current_allocation) + 50 <= 100 THEN 'VALID'
                            ELSE 'OVERALLOCATED'
                        END as status
                )
                INSERT INTO allocations (id, employee_id, project_id, percent_allocated, start_date, end_date, status, created_at, updated_at)
                SELECT 
                    gen_random_uuid(),
                    e.id,
                    p.id,
                    50,
                    CURRENT_DATE,
                    CURRENT_DATE + INTERVAL '3 months',
                    'ACTIVE',
                    NOW(),
                    NOW()
                FROM employee_check e, project_check p, validation v
                WHERE v.status = 'VALID'
                """

            elif "update" in query_lower and "sarah.chen@techvantage.io" in query_lower:
                return """
                WITH validation AS (
                    SELECT a.id, e.name, p.name as project_name,
                           (SELECT COALESCE(SUM(a2.percent_allocated), 0) 
                            FROM allocations a2 
                            WHERE a2.employee_id = e.id 
                            AND a2.status = 'ACTIVE' 
                            AND a2.id != a.id
                            AND a2.end_date > CURRENT_DATE) as other_allocations
                    FROM allocations a
                    JOIN employees e ON a.employee_id = e.id
                    JOIN projects p ON a.project_id = p.id
                    WHERE e.email = 'sarah.chen@techvantage.io'
                    AND p.name = 'Healthcare Management System'
                    AND a.status = 'ACTIVE'
                )
                UPDATE allocations 
                SET percent_allocated = 75, updated_at = NOW()
                WHERE id IN (
                    SELECT id FROM validation 
                    WHERE other_allocations + 75 <= 100
                )
                """

        return None

    async def run_all_tests(self):
        """Run all realistic test cases."""
        print("🧠 Realistic QueryAgent Testing with Raw Natural Language Input")
        print("Testing Query Agent's ability to determine SQL operations from natural language")
        print("No pre-processed metadata - just raw natural language to SQL conversion")
        print("=" * 80)

        # Test Case 1: Specific employee search by designation and skills
        test1 = await self.test_realistic_case(
            "Find 3 Senior Software Engineers with React experience",
            "Specific Employee Search with Skills Filter",
            expected_min_results=0,  # Might be 0 if no SSEs with React
            expected_max_results=3,
            should_have_data=False,
            expected_operation="SELECT",  # For validation - Query Agent should detect this
        )

        # Test Case 2: Available resources for specific allocation
        test2 = await self.test_realistic_case(
            "Show me developers who are less than 75% allocated and available for a new project",
            "Available Resources for New Project",
            expected_min_results=0,
            expected_max_results=20,
            should_have_data=False,
            expected_operation="SELECT",  # Query Agent should detect this from "Show me"
        )

        # Test Case 3: Specific project team composition
        test3 = await self.test_realistic_case(
            "Who are the current team members working on Mobile Banking App project?",
            "Specific Project Team Composition",
            expected_min_results=0,
            expected_max_results=15,
            should_have_data=False,
            expected_operation="SELECT",  # Query Agent should detect this from "Who are"
        )

        # Test Case 4: Employee overallocation check
        # test4 = await self.test_realistic_case(
        #     "Find employees who are allocated more than 100% across all active projects",
        #     "Overallocation Detection",
        #     expected_min_results=0,
        #     expected_max_results=10,
        #     should_have_data=False,
        #     expected_operation="SELECT",  # Query Agent should detect this from "Find"
        # )

        # Test Case 5: Specific employee current allocation
        # test5 = await self.test_realistic_case(
        #     "What is the current total allocation percentage for employee alex.johnson@techvantage.io?",
        #     "Individual Employee Total Allocation",
        #     expected_min_results=0,
        #     expected_max_results=5,
        #     should_have_data=False,
        #     expected_operation="SELECT",  # Query Agent should detect this from "What is"
        # )

        # Test Case 6: Project capacity analysis
        # test6 = await self.test_realistic_case(
        #     "Show me all active customer projects with their current team size and total allocation",
        #     "Active Customer Projects Capacity",
        #     expected_min_results=0,
        #     expected_max_results=20,
        #     should_have_data=False,
        #     expected_operation="SELECT",  # Query Agent should detect this from "Show me"
        # )

        # Test Case 7: Skills gap for specific technology
        # test7 = await self.test_realistic_case(
        #     "Find all employees with Python skills who are currently allocated less than 50%",
        #     "Python Developers Availability",
        #     expected_min_results=0,
        #     expected_max_results=15,
        #     should_have_data=False,
        #     expected_operation="SELECT",  # Query Agent should detect this from "Find"
        # )

        # Test Case 8: Department utilization analysis
        # test8 = await self.test_realistic_case(
        #     "What is the average allocation percentage for Senior Software Engineers?",
        #     "SSE Utilization Analysis",
        #     expected_min_results=0,
        #     expected_max_results=1,
        #     should_have_data=False,
        #     expected_operation="SELECT",  # Query Agent should detect this from "What is"
        # )

        # Test Case 9: UPDATE - Allocate employee to project with validation
        # test9 = await self.test_realistic_case(
        #     "Allocate alex.johnson@techvantage.io to Mobile Banking App project at 50% for 3 months starting today",
        #     "Employee Project Allocation with Validation",
        #     expected_min_results=0,
        #     expected_max_results=1,
        #     should_have_data=False,
        #     expected_operation="INSERT",  # Query Agent should detect this is creating new allocation
        # )

        # Test Case 10: UPDATE - Change existing allocation
        # test10 = await self.test_realistic_case(
        #     "Update sarah.chen@techvantage.io allocation on Healthcare Management System project to 75%",
        #     "Modify Existing Project Allocation",
        #     expected_min_results=0,
        #     expected_max_results=1,
        #     should_have_data=False,
        #     expected_operation="UPDATE",  # Query Agent should detect this from "Update"
        # )

        # Test Case 11: Complex business query - Project ending soon
        # test11 = await self.test_realistic_case(
        #     "Find all projects ending in the next 60 days with their team members and allocation percentages",
        #     "Projects Ending Soon Analysis",
        #     expected_min_results=0,
        #     expected_max_results=50,
        #     should_have_data=False,
        #     expected_operation="SELECT",  # Query Agent should detect this from "Find"
        # )

        # Test Case 12: INSERT - Create new project allocation
        # test12 = await self.test_realistic_case(
        #     "Create a new project called 'AI Chatbot Development' for 8 months as a customer project",
        #     "New Project Creation",
        #     expected_min_results=0,
        #     expected_max_results=1,
        #     should_have_data=False,
        #     expected_operation="INSERT",  # Query Agent should detect this from "Create"
        # )

        # Store all test results
        self.test_results = [
            test1,
            test2,
            test3,
            # test4,
            # test5,
            # test6,
            # test7,
            # test8,
            # test9,
            # test10,
            # test11,
            # test12,
        ]

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("🎯 REALISTIC QUERY TEST SUMMARY")
        print("=" * 80)

        passed_tests = [t for t in self.test_results if t["success"]]
        failed_tests = [t for t in self.test_results if not t["success"]]

        print(f"📊 Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {len(passed_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"📈 Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")

        if passed_tests:
            print(f"\n✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"   • {test['description']}")

        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['description']}")
                if test["validation_errors"]:
                    for error in test["validation_errors"][:2]:  # Show first 2 errors
                        print(f"     - {error}")

        print(f"\n💡 KEY INSIGHTS:")

        # Analyze operation types
        operations = {}
        for test in self.test_results:
            if test["agent_result"] and "query" in test["agent_result"]:
                sql = test["agent_result"]["query"].strip().upper()
                op = "SELECT" if sql.startswith("SELECT") else "OTHER"
                operations[op] = operations.get(op, 0) + 1

        print(f"   🔍 Query Operations: {operations}")

        # Analyze database connectivity
        db_errors = [t for t in self.test_results if t["db_error"]]
        print(
            f"   🗄️  Database Connectivity: {len(self.test_results) - len(db_errors)}/{len(self.test_results)} successful"
        )

        # Analyze result patterns
        with_data = [t for t in self.test_results if t["db_results"] and len(t["db_results"]) > 0]
        print(f"   📊 Queries with Data: {len(with_data)}/{len(self.test_results)}")

        print(f"\n🚀 NEXT STEPS:")
        if len(passed_tests) == len(self.test_results):
            print("   🎉 Perfect! All realistic queries working correctly!")
            print("   🔧 Consider adding more complex edge cases")
        elif len(passed_tests) >= len(self.test_results) * 0.8:
            print("   👍 Good performance! Focus on fixing remaining issues")
            print("   🔍 Review failed test patterns for improvements")
        else:
            print("   🔧 Needs significant improvement")
            print("   🎯 Focus on core query generation reliability")


async def main():
    """Run realistic query tests."""
    tester = RealisticQueryTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
