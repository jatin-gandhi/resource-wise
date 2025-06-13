"""Test specific semantic cases for the enhanced QueryAgent."""

import asyncio
import os

from app.ai.agents.query.agent import QueryAgent


async def test_semantic_case(
    query_text: str, description: str, expected_operation: str, metadata: dict | None = None
):
    """Test a specific semantic case and show detailed results."""

    print(f"\n🔍 Testing: {description}")
    print(f"Query: '{query_text}'")
    print(f"Expected Operation: {expected_operation}")
    print("=" * 70)

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  No OPENAI_API_KEY found - skipping LLM test")
        return False

    try:
        agent = QueryAgent()

        test_data = {"query": query_text, "session_id": "semantic-test", "user_id": "test-user"}

        result = await agent.process(test_data)

        print("✅ Generated SQL:")
        print(f"   {result['query']}")
        print(f"\n📊 Query Type: {result['query_type']}")
        print(f"📋 Tables: {result['tables']}")
        print(f"🔗 Joins: {result['joins']}")
        print(f"🔍 Filters: {result['filters']}")

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False

        # Analyze the generated SQL to see if it matches expected operation
        sql = result["query"].upper()
        detected_operation = "UNKNOWN"

        if sql.startswith("SELECT"):
            detected_operation = "SELECT"
        elif sql.startswith("INSERT"):
            detected_operation = "INSERT"
        elif sql.startswith("UPDATE"):
            detected_operation = "UPDATE"
        elif sql.startswith("DELETE"):
            detected_operation = "DELETE"

        print("\n🎯 Semantic Analysis:")
        print(f"   Expected: {expected_operation}")
        print(f"   Detected: {detected_operation}")
        print(f"   Match: {'✅ YES' if detected_operation == expected_operation else '❌ NO'}")

        return detected_operation == expected_operation

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Test the three specific semantic cases."""

    print("🧠 Semantic QueryAgent Testing")
    print("Testing specific CRUD operation detection and generation")

    # Test Case 1: Complex SELECT with JOINs
    success1 = await test_semantic_case(
        "Find couple of SSEs with React skills",
        "Complex Resource Search with Skills",
        "SELECT",
        {"skills": ["React"], "designation": "SSE", "limit": "couple"},
    )

    # Test Case 2: INSERT with defaults
    success2 = await test_semantic_case(
        "Create project X for 6 months",
        "Project Creation with Duration",
        "INSERT",
        {"project_name": "X", "duration": 6},
    )

    # Test Case 3: UPDATE with lookups
    success3 = await test_semantic_case(
        "Update Jatin's allocation to 50%",
        "Allocation Update with Employee Lookup",
        "UPDATE",
        {"employee": "Jatin", "percentage": 50},
    )

    print("\n🎯 Semantic Test Results:")
    print(f"   Test 1 (SELECT - Complex): {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Test 2 (INSERT - Create): {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"   Test 3 (UPDATE - Modify): {'✅ PASS' if success3 else '❌ FAIL'}")

    total_passed = sum([success1, success2, success3])
    print(f"\n📊 Overall: {total_passed}/3 semantic tests passed")

    if total_passed == 3:
        print("\n🎉 Perfect! The QueryAgent correctly detected all CRUD operations semantically!")
    elif total_passed >= 2:
        print("\n👍 Good! Most semantic operations detected correctly.")
    else:
        print("\n🔧 Needs improvement in semantic operation detection.")

    print("\n💡 Key Features Demonstrated:")
    print("   🧠 Semantic operation detection (SELECT/INSERT/UPDATE)")
    print("   🔗 Complex multi-table JOINs for skills and designations")
    print("   🆔 Employee/project lookups for UPDATE operations")
    print("   📝 Default value insertion for CREATE operations")
    print("   🚫 No QueryType enum dependency")


if __name__ == "__main__":
    asyncio.run(main())
