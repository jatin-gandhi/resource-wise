#!/usr/bin/env python3
"""
Test Framework-Based Skill Priority Logic

Tests the enhanced logic where:
1. Framework experience > Base language experience
2. Framework expertise implies base language competency
3. Cross-domain frameworks are treated separately
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.ai.core.config import AIConfig
from app.ai.agents.matching.agent import MatchingAgent


def create_framework_priority_test():
    """
    SCENARIO: Framework vs Base Language Priority
    Requirements: Python, Flask, Django
    
    Expected Priority:
    1. Django Expert (framework implies Python) - HIGHEST
    2. Flask Expert (framework implies Python) - HIGH  
    3. Python Expert (base language only) - MEDIUM
    4. Spring Boot + Python (cross-domain) - MEDIUM (Python credit only)
    5. Unrelated skills - LOWEST
    """
    return {
        "project_details": {
            "name": "Framework Priority Test - Python Web Stack",
            "duration": 4,
            "starting_from": "April",
            "skills_required": ["Python", "Flask", "Django"],
            "resources_required": [
                {"resource_type": "SDE", "resource_count": 1}
            ]
        },
        "available_employees": [
            {
                "employee_id": "sde_django",
                "name": "Django Expert",
                "email": "django@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Django", "experience_months": 24, "last_used": "Current"},  # Framework expert
                    {"skill_name": "PostgreSQL", "experience_months": 18, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_flask",
                "name": "Flask Expert",
                "email": "flask@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Flask", "experience_months": 18, "last_used": "Current"},   # Framework expert
                    {"skill_name": "Redis", "experience_months": 12, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_python",
                "name": "Python Expert",
                "email": "python@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 36, "last_used": "Current"},  # Base language only
                    {"skill_name": "Data Science", "experience_months": 24, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_crossdomain",
                "name": "Cross Domain Developer",
                "email": "crossdomain@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Spring Boot", "experience_months": 30, "last_used": "Current"}, # Java framework
                    {"skill_name": "Python", "experience_months": 12, "last_used": "Current"}       # Separate Python
                ]
            },
            {
                "employee_id": "sde_unrelated",
                "name": "Frontend Developer",
                "email": "frontend@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "React", "experience_months": 24, "last_used": "Current"},       # Unrelated
                    {"skill_name": "TypeScript", "experience_months": 18, "last_used": "Current"}   # Unrelated
                ]
            }
        ]
    }


def create_implicit_skills_test():
    """
    SCENARIO: Implicit Skills Recognition
    Requirements: JavaScript, React
    
    Expected: React expert should get JavaScript credit automatically
    """
    return {
        "project_details": {
            "name": "Implicit Skills Test - React/JavaScript",
            "duration": 3,
            "starting_from": "May",
            "skills_required": ["JavaScript", "React"],
            "resources_required": [
                {"resource_type": "SDE", "resource_count": 1}
            ]
        },
        "available_employees": [
            {
                "employee_id": "sde_react",
                "name": "React Expert",
                "email": "react@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "React", "experience_months": 30, "last_used": "Current"},       # Framework (implies JS)
                    {"skill_name": "CSS", "experience_months": 24, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_js",
                "name": "JavaScript Expert",
                "email": "javascript@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "JavaScript", "experience_months": 36, "last_used": "Current"},  # Base language only
                    {"skill_name": "Node.js", "experience_months": 18, "last_used": "Current"}
                ]
            }
        ]
    }


def create_cross_domain_test():
    """
    SCENARIO: Cross-Domain Framework Separation
    Requirements: Python, Django
    
    Expected: Spring Boot expertise should NOT imply Python knowledge
    """
    return {
        "project_details": {
            "name": "Cross Domain Test - No Implicit Transfer",
            "duration": 4,
            "starting_from": "June",
            "skills_required": ["Python", "Django"],
            "resources_required": [
                {"resource_type": "SDE", "resource_count": 1}
            ]
        },
        "available_employees": [
            {
                "employee_id": "sde_django",
                "name": "Django Expert",
                "email": "django@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Django", "experience_months": 24, "last_used": "Current"}       # Should get Python credit
                ]
            },
            {
                "employee_id": "sde_spring",
                "name": "Spring Boot Expert",
                "email": "spring@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Spring Boot", "experience_months": 36, "last_used": "Current"}, # Should NOT get Python credit
                    {"skill_name": "Java", "experience_months": 48, "last_used": "Current"}
                ]
            }
        ]
    }


async def analyze_framework_test(test_name: str, results: dict, expected_winner: str, reasoning: str):
    """Analyze framework priority test results."""
    print(f"\n{'='*80}")
    print(f"FRAMEWORK TEST ANALYSIS: {test_name}")
    print(f"{'='*80}")
    print(f"Expected Winner: {expected_winner}")
    print(f"Reasoning: {reasoning}")
    print("-" * 80)
    
    matching_results = results.get("matching_results", {})
    
    if not matching_results.get("success", False):
        print(f"❌ MATCHING FAILED: {matching_results.get('error_message', 'Unknown error')}")
        return False
    
    # Analyze team combinations
    team_combinations = matching_results.get("possible_team_combinations", [])
    
    if not team_combinations:
        print("❌ No team combinations generated!")
        return False
    
    # Show all combinations for analysis
    print(f"📋 ALL TEAM COMBINATIONS:")
    for i, combo in enumerate(team_combinations, 1):
        team_members = combo.get("team_members", [])
        skills_match = combo.get("skills_match", 0)
        skills_matched = combo.get("skills_matched", [])
        skills_missing = combo.get("skills_missing", [])
        
        if team_members:
            member = team_members[0]
            name = member.get("name", "Unknown")
            member_skills = member.get("skills", [])
            
            print(f"  {i}. {name}")
            print(f"     Skills Match: {skills_match:.1f}%")
            print(f"     Skills Matched: {skills_matched}")
            print(f"     Skills Missing: {skills_missing}")
            print(f"     Candidate Skills: {member_skills}")
            print()
    
    # Get the best combination (first one)
    best_combo = team_combinations[0]
    team_members = best_combo.get("team_members", [])
    
    if team_members:
        selected_candidate = team_members[0].get("name", "Unknown")
        skills_match = best_combo.get("skills_match", 0)
        
        print(f"🏅 SELECTED CANDIDATE: {selected_candidate}")
        print(f"📊 Skills Match: {skills_match:.1f}%")
        
        # Check if it matches expected winner
        if expected_winner.lower() in selected_candidate.lower():
            print(f"✅ CORRECT: Framework priority logic working!")
            return True
        else:
            print(f"❌ INCORRECT: Expected {expected_winner}, got {selected_candidate}")
            return False
    
    return False


async def main():
    """Main test function for framework-based priority."""
    print("🧪 FRAMEWORK-BASED SKILL PRIORITY TEST SUITE")
    print("=" * 80)
    print("Testing enhanced framework > base language priority logic")
    print("Key Concepts:")
    print("1. Framework expertise > Base language expertise")
    print("2. Framework expertise implies base language competency")
    print("3. Cross-domain frameworks don't transfer (Spring Boot ≠ Python)")
    print("=" * 80)
    
    # Initialize the agent
    config = AIConfig()
    agent = MatchingAgent(config)
    
    # Define test scenarios
    scenarios = [
        (
            "FRAMEWORK PRIORITY",
            create_framework_priority_test(),
            "Django Expert",
            "Django framework expertise should beat Python-only expertise"
        ),
        (
            "IMPLICIT SKILLS",
            create_implicit_skills_test(),
            "React Expert",
            "React expertise should imply JavaScript competency automatically"
        ),
        (
            "CROSS-DOMAIN SEPARATION",
            create_cross_domain_test(),
            "Django Expert",
            "Spring Boot should NOT imply Python knowledge"
        )
    ]
    
    # Run all scenarios
    results = []
    successful_scenarios = 0
    
    for test_name, test_data, expected_winner, reasoning in scenarios:
        print(f"\n🔄 Running {test_name}...")
        try:
            result = await agent.process(test_data)
            success = await analyze_framework_test(test_name, result, expected_winner, reasoning)
            results.append((test_name, success))
            if success:
                successful_scenarios += 1
        except Exception as e:
            print(f"❌ TEST FAILED: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*80}")
    print("🏆 FRAMEWORK PRIORITY TEST SUMMARY")
    print(f"{'='*80}")
    
    total_scenarios = len(scenarios)
    success_rate = (successful_scenarios / total_scenarios) * 100
    
    print(f"📊 Overall Results: {successful_scenarios}/{total_scenarios} scenarios passed ({success_rate:.1f}%)")
    print()
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print()
    
    # Assessment
    if success_rate >= 90:
        assessment = "🌟 EXCELLENT - Framework priority logic working perfectly"
    elif success_rate >= 75:
        assessment = "✅ GOOD - Framework logic mostly working"
    elif success_rate >= 50:
        assessment = "⚠️  ACCEPTABLE - Some framework logic issues"
    else:
        assessment = "❌ POOR - Framework priority logic needs major fixes"
    
    print(f"🎯 Assessment: {assessment}")
    print(f"💡 Framework Logic Confidence: {success_rate:.0f}%")
    
    if success_rate < 100:
        print(f"\n🔧 Next Steps:")
        print(f"- Review failed scenarios for prompt improvements")
        print(f"- Consider more explicit framework-language mappings")
        print(f"- Test with additional framework combinations")
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main()) 