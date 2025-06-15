#!/usr/bin/env python3
"""
Test the fix for Critical vs Secondary Skills scenario.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.ai.core.config import AIConfig
from app.ai.agents.matching.agent import MatchingAgent


def create_critical_vs_secondary_test():
    """
    SCENARIO: Critical vs Non-Critical Skills
    - Required: Python (critical), Flask (nice-to-have), Django (nice-to-have)
    - Candidate A: Python expert, no web frameworks
    - Candidate B: Flask/Django expert, basic Python
    Expected: A should win (critical skill expertise)
    """
    return {
        "project_details": {
            "name": "Critical vs Secondary Skills Test - FIXED",
            "duration": 4,
            "starting_from": "April",
            "skills_required": ["Python", "Flask", "Django"],  # Python is first = critical
            "resources_required": [
                {"resource_type": "SDE", "resource_count": 1}
            ]
        },
        "available_employees": [
            {
                "employee_id": "sde_critical",
                "name": "Python Expert",
                "email": "critical@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 36, "last_used": "Current"},  # Expert in critical skill
                    {"skill_name": "JavaScript", "experience_months": 18, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_secondary",
                "name": "Web Framework Expert",
                "email": "secondary@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 3, "last_used": "Current"},   # Beginner in critical
                    {"skill_name": "Flask", "experience_months": 24, "last_used": "Current"},   # Expert in secondary
                    {"skill_name": "Django", "experience_months": 18, "last_used": "Current"}   # Expert in secondary
                ]
            }
        ]
    }


async def main():
    """Test the critical vs secondary fix."""
    print("🔧 TESTING CRITICAL vs SECONDARY SKILLS FIX")
    print("=" * 60)
    print("Expected: Python Expert should win over Web Framework Expert")
    print("Reason: Critical skill (Python) should beat secondary skills")
    print("=" * 60)
    
    # Initialize the agent
    config = AIConfig()
    agent = MatchingAgent(config)
    
    # Create test data
    test_data = create_critical_vs_secondary_test()
    
    try:
        # Run the matching
        print("🔄 Running matching analysis...")
        results = await agent.process(test_data)
        
        matching_results = results.get("matching_results", {})
        
        if not matching_results.get("success", False):
            print(f"❌ MATCHING FAILED: {matching_results.get('error_message', 'Unknown error')}")
            return
        
        # Analyze team combinations
        team_combinations = matching_results.get("possible_team_combinations", [])
        
        if not team_combinations:
            print("❌ No team combinations generated!")
            return
        
        # Get the best combination (first one)
        best_combo = team_combinations[0]
        team_members = best_combo.get("team_members", [])
        
        if not team_members:
            print("❌ No team members in best combination!")
            return
        
        selected_candidate = team_members[0].get("name", "Unknown")
        skills_match = best_combo.get("skills_match", 0)
        skills_matched = best_combo.get("skills_matched", [])
        
        print(f"\n🏅 SELECTED CANDIDATE: {selected_candidate}")
        print(f"📊 Skills Match: {skills_match:.1f}%")
        print(f"🎯 Skills Matched: {skills_matched}")
        
        # Check if it matches expected winner
        if "Python Expert" in selected_candidate:
            print(f"✅ SUCCESS: Critical skill priority is working!")
            print(f"💡 The fix correctly prioritized Python expertise over Flask/Django")
        else:
            print(f"❌ STILL FAILING: Expected Python Expert, got {selected_candidate}")
            print(f"💡 Need further prompt refinement for critical skills priority")
        
        # Show all combinations for analysis
        print(f"\n📋 ALL TEAM COMBINATIONS:")
        for i, combo in enumerate(team_combinations, 1):
            member = combo.get("team_members", [{}])[0]
            name = member.get("name", "Unknown")
            match = combo.get("skills_match", 0)
            matched = combo.get("skills_matched", [])
            print(f"  {i}. {name} - {match:.1f}% match - Skills: {matched}")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 