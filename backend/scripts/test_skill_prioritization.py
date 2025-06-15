#!/usr/bin/env python3
"""
Test script for skill prioritization in MatchingAgent.

Tests the specific case:
- Requirement: 1 TL 50%
- Skills: Python, Flask, Django
- Available TLs: 4 TL who have >=50% availability
  - A: Python(18mo, 6mo ago) + Flask(12mo, 6mo ago) = 2 skills, high exp, old usage
  - B: Python(10mo, 1mo ago) + Flask(10mo, 1mo ago) = 2 skills, med exp, recent usage  
  - C: Python + React = 1 skill match
  - D: React + Node = 0 skill match

Expected ranking: A/B (2 skills) > C (1 skill) > D (0 skills)
Between A/B: B should be preferred (recent usage vs old usage)
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.ai.core.config import AIConfig
from app.ai.agents.matching.agent import MatchingAgent


def create_skill_prioritization_test():
    """Create test case for skill prioritization."""
    return {
        "project_details": {
            "name": "Python Web Application - Skill Prioritization Test",
            "duration": 3,
            "starting_from": "January",
            "skills_required": ["Python", "Flask", "Django"],
            "resources_required": [
                {"resource_type": "TL", "resource_count": 1, "required_allocation_percentage": 50}
            ]
        },
        "available_employees": [
            {
                "employee_id": "tl_a",
                "name": "TL A - High Exp Old Usage",
                "email": "tl.a@company.com",
                "designation": "TL",
                "available_percentage": 75,  # Meets 50% requirement
                "skills": [
                    {"skill_name": "Python", "experience_months": 18, "last_used": "2024-07"},  # 6 months ago
                    {"skill_name": "Flask", "experience_months": 12, "last_used": "2024-07"},   # 6 months ago
                    {"skill_name": "JavaScript", "experience_months": 24, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "tl_b", 
                "name": "TL B - Med Exp Recent Usage",
                "email": "tl.b@company.com",
                "designation": "TL",
                "available_percentage": 80,  # Meets 50% requirement
                "skills": [
                    {"skill_name": "Python", "experience_months": 10, "last_used": "2024-12"},  # 1 month ago
                    {"skill_name": "Flask", "experience_months": 10, "last_used": "2024-12"},   # 1 month ago
                    {"skill_name": "Git", "experience_months": 15, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "tl_c",
                "name": "TL C - One Skill Match",
                "email": "tl.c@company.com", 
                "designation": "TL",
                "available_percentage": 90,  # Meets 50% requirement
                "skills": [
                    {"skill_name": "Python", "experience_months": 15, "last_used": "Current"},
                    {"skill_name": "React", "experience_months": 20, "last_used": "Current"},
                    {"skill_name": "TypeScript", "experience_months": 18, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "tl_d",
                "name": "TL D - No Skill Match",
                "email": "tl.d@company.com",
                "designation": "TL", 
                "available_percentage": 100,  # Meets 50% requirement
                "skills": [
                    {"skill_name": "React", "experience_months": 24, "last_used": "Current"},
                    {"skill_name": "Node.js", "experience_months": 20, "last_used": "Current"},
                    {"skill_name": "MongoDB", "experience_months": 16, "last_used": "Current"}
                ]
            }
        ]
    }


def analyze_results(results, test_data):
    """Analyze and print detailed results."""
    print(f"\n{'='*80}")
    print("SKILL PRIORITIZATION ANALYSIS")
    print(f"{'='*80}")
    
    matching_results = results.get("matching_results", {})
    
    if not matching_results.get("success", False):
        print(f"❌ MATCHING FAILED: {matching_results.get('error_message', 'Unknown error')}")
        return
    
    print(f"✅ MATCHING SUCCESSFUL")
    print(f"Processing Time: {matching_results.get('processing_time_ms', 0)}ms")
    
    # Analyze matched resources
    matched_resources = matching_results.get("matched_resources", {})
    tl_matches = matched_resources.get("TL", [])
    
    print(f"\n📊 MATCHED TL CANDIDATES: {len(tl_matches)}")
    print("-" * 50)
    
    if not tl_matches:
        print("❌ No TL candidates matched!")
        return
    
    # Expected skill counts for validation
    expected_skills = {
        "TL A - High Exp Old Usage": 2,      # Python + Flask
        "TL B - Med Exp Recent Usage": 2,    # Python + Flask  
        "TL C - One Skill Match": 1,         # Python only
        "TL D - No Skill Match": 0           # No matching skills
    }
    
    for i, tl in enumerate(tl_matches, 1):
        name = tl.get("name", "Unknown")
        skills = tl.get("skills", [])
        availability = tl.get("available_percentage", 0)
        
        # Count matching skills
        required_skills = {"python", "flask", "django"}
        matching_skills = [skill for skill in skills if skill.lower() in required_skills]
        skill_count = len(matching_skills)
        
        expected_count = expected_skills.get(name, "Unknown")
        status = "✅" if skill_count == expected_count else "❌"
        
        print(f"{i}. {name}")
        print(f"   Availability: {availability}%")
        print(f"   Matching Skills: {matching_skills} ({skill_count} skills) {status}")
        print(f"   Expected: {expected_count} skills")
        print()
    
    # Analyze team combinations
    team_combinations = matching_results.get("possible_team_combinations", [])
    print(f"🏆 TEAM COMBINATIONS: {len(team_combinations)}")
    print("-" * 50)
    
    if not team_combinations:
        print("❌ No team combinations generated!")
        return
    
    for i, combo in enumerate(team_combinations, 1):
        team_members = combo.get("team_members", [])
        skills_match = combo.get("skills_match", 0)
        skills_matched = combo.get("skills_matched", [])
        skills_missing = combo.get("skills_missing", [])
        
        print(f"Combination {i}:")
        print(f"  Skills Match: {skills_match:.1f}%")
        print(f"  Skills Covered: {skills_matched}")
        print(f"  Skills Missing: {skills_missing}")
        
        for member in team_members:
            name = member.get("name", "Unknown")
            skills = member.get("skills", [])
            print(f"  - {name}: {skills}")
        print()
    
    # Validation
    print(f"🔍 VALIDATION RESULTS")
    print("-" * 50)
    
    # Check if all 4 TLs are included (they all meet availability requirement)
    if len(tl_matches) == 4:
        print("✅ All 4 TLs correctly included (all meet 50% availability requirement)")
    else:
        print(f"❌ Expected 4 TLs, got {len(tl_matches)}")
    
    # Check if team combination includes the best candidate
    if team_combinations:
        best_combo = team_combinations[0]  # Assuming first is best
        best_member = best_combo.get("team_members", [{}])[0]
        best_name = best_member.get("name", "")
        
        print(f"🏅 Best candidate selected: {best_name}")
        
        # Validate selection logic
        if "TL B" in best_name:
            print("✅ EXCELLENT: TL B selected (2 skills + recent usage)")
        elif "TL A" in best_name:
            print("⚠️  ACCEPTABLE: TL A selected (2 skills but old usage)")
        elif "TL C" in best_name:
            print("❌ SUBOPTIMAL: TL C selected (only 1 skill match)")
        elif "TL D" in best_name:
            print("❌ POOR: TL D selected (no skill match)")
        else:
            print(f"❓ UNKNOWN: Unexpected selection - {best_name}")


async def main():
    """Main test function."""
    print("Testing Skill Prioritization in MatchingAgent")
    print("=" * 80)
    print("Test Case:")
    print("- Requirement: 1 TL 50%")
    print("- Skills: Python, Flask, Django")
    print("- Available TLs: 4 candidates with >=50% availability")
    print("  - TL A: Python(18mo, 6mo ago) + Flask(12mo, 6mo ago)")
    print("  - TL B: Python(10mo, 1mo ago) + Flask(10mo, 1mo ago)")  
    print("  - TL C: Python + React")
    print("  - TL D: React + Node")
    print()
    print("Expected Ranking: B > A > C > D")
    print("(Recent usage should outweigh higher experience)")
    print("=" * 80)
    
    # Initialize the agent
    config = AIConfig()
    agent = MatchingAgent(config)
    
    # Create test data
    test_data = create_skill_prioritization_test()
    
    try:
        # Run the matching
        print("🔄 Running matching analysis...")
        results = await agent.process(test_data)
        
        # Analyze results
        analyze_results(results, test_data)
        
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 