#!/usr/bin/env python3
"""
Real-Life Skill Matching Scenarios Test Suite

Tests complex real-world scenarios that challenge the MatchingAgent's
skill prioritization and candidate ranking logic.
"""

import asyncio
import sys
import os
from typing import Dict, Any, List

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.ai.core.config import AIConfig
from app.ai.agents.matching.agent import MatchingAgent


def create_scenario_1_experience_vs_recency():
    """
    SCENARIO 1: Experience Threshold vs Recency
    - Candidate A: 36 months experience, used 12 months ago
    - Candidate B: 6 months experience, used last week
    Expected: B should win (recent usage overcomes experience gap for stale skills)
    """
    return {
        "project_details": {
            "name": "Experience vs Recency Test",
            "duration": 2,  # Short project - should favor recency
            "starting_from": "February",
            "skills_required": ["Python"],
            "resources_required": [
                {"resource_type": "SDE", "resource_count": 1}
            ]
        },
        "available_employees": [
            {
                "employee_id": "sde_exp",
                "name": "Expert Old Usage",
                "email": "expert@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 36, "last_used": "2023-02"},  # 12 months ago
                    {"skill_name": "JavaScript", "experience_months": 24, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_recent",
                "name": "Beginner Recent Usage",
                "email": "recent@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 6, "last_used": "2024-01"},  # Last week
                    {"skill_name": "HTML", "experience_months": 8, "last_used": "Current"}
                ]
            }
        ]
    }


def create_scenario_2_depth_vs_breadth():
    """
    SCENARIO 2: Skill Depth vs Breadth
    - Candidate A: Expert in Python (48mo), no Flask/Django
    - Candidate B: Beginner in Python (6mo), Flask (6mo), Django (3mo)
    Expected: For 3 skills, B should win (breadth over depth)
    """
    return {
        "project_details": {
            "name": "Depth vs Breadth Test",
            "duration": 6,  # Long project
            "starting_from": "March",
            "skills_required": ["Python", "Flask", "Django"],  # 3 skills - should favor breadth
            "resources_required": [
                {"resource_type": "SDE", "resource_count": 1}
            ]
        },
        "available_employees": [
            {
                "employee_id": "sde_depth",
                "name": "Python Expert",
                "email": "depth@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 48, "last_used": "Current"},  # Expert
                    {"skill_name": "JavaScript", "experience_months": 24, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_breadth",
                "name": "Full Stack Beginner",
                "email": "breadth@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 6, "last_used": "Current"},   # Beginner
                    {"skill_name": "Flask", "experience_months": 6, "last_used": "Current"},    # Beginner
                    {"skill_name": "Django", "experience_months": 3, "last_used": "Current"}    # Beginner
                ]
            }
        ]
    }


def create_scenario_3_critical_vs_secondary():
    """
    SCENARIO 3: Critical vs Non-Critical Skills
    - Required: Python (critical), Flask (nice-to-have), Django (nice-to-have)
    - Candidate A: Python expert, no web frameworks
    - Candidate B: Flask/Django expert, basic Python
    Expected: A should win (critical skill expertise)
    """
    return {
        "project_details": {
            "name": "Critical vs Secondary Skills Test",
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


def create_scenario_4_transferable_skills():
    """
    SCENARIO 4: Skill Transferability
    - Required: React Native
    - Candidate A: React (24mo) - highly transferable
    - Candidate B: Flutter (12mo) - less transferable
    - Candidate C: No mobile experience
    Expected: A should win (transferable skills bonus)
    """
    return {
        "project_details": {
            "name": "Transferable Skills Test",
            "duration": 3,
            "starting_from": "May",
            "skills_required": ["React Native"],
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
                    {"skill_name": "React", "experience_months": 24, "last_used": "Current"},     # Highly transferable
                    {"skill_name": "JavaScript", "experience_months": 30, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_flutter",
                "name": "Flutter Expert",
                "email": "flutter@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Flutter", "experience_months": 12, "last_used": "Current"},  # Less transferable
                    {"skill_name": "Dart", "experience_months": 12, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_backend",
                "name": "Backend Expert",
                "email": "backend@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 36, "last_used": "Current"},   # Not transferable
                    {"skill_name": "Django", "experience_months": 24, "last_used": "Current"}
                ]
            }
        ]
    }


def create_scenario_5_team_composition():
    """
    SCENARIO 5: Team Composition Balance
    - Need: 2 developers for Python + React project
    - Available: 2 Python experts, 2 React experts, 1 full-stack
    Expected: Should prefer balanced team (1 Python + 1 React) or full-stack
    """
    return {
        "project_details": {
            "name": "Team Composition Balance Test",
            "duration": 6,
            "starting_from": "June",
            "skills_required": ["Python", "React"],
            "resources_required": [
                {"resource_type": "SDE", "resource_count": 2}
            ]
        },
        "available_employees": [
            {
                "employee_id": "sde_python1",
                "name": "Python Expert 1",
                "email": "python1@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 36, "last_used": "Current"},
                    {"skill_name": "Django", "experience_months": 24, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_python2",
                "name": "Python Expert 2",
                "email": "python2@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 30, "last_used": "Current"},
                    {"skill_name": "FastAPI", "experience_months": 18, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_react1",
                "name": "React Expert 1",
                "email": "react1@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "React", "experience_months": 30, "last_used": "Current"},
                    {"skill_name": "TypeScript", "experience_months": 24, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_react2",
                "name": "React Expert 2",
                "email": "react2@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "React", "experience_months": 24, "last_used": "Current"},
                    {"skill_name": "JavaScript", "experience_months": 36, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_fullstack",
                "name": "Full Stack Developer",
                "email": "fullstack@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 18, "last_used": "Current"},
                    {"skill_name": "React", "experience_months": 15, "last_used": "Current"},
                    {"skill_name": "JavaScript", "experience_months": 24, "last_used": "Current"}
                ]
            }
        ]
    }


def create_scenario_6_staleness_thresholds():
    """
    SCENARIO 6: Skill Staleness Thresholds
    - Candidate A: Used skill 6 months ago (Moderate)
    - Candidate B: Used skill 18 months ago (Stale)
    - Candidate C: Used skill 3 years ago (Very Stale)
    Expected: A > B > C based on staleness thresholds
    """
    return {
        "project_details": {
            "name": "Skill Staleness Test",
            "duration": 3,
            "starting_from": "July",
            "skills_required": ["Java"],
            "resources_required": [
                {"resource_type": "SDE", "resource_count": 1}
            ]
        },
        "available_employees": [
            {
                "employee_id": "sde_moderate",
                "name": "Moderate Staleness",
                "email": "moderate@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Java", "experience_months": 24, "last_used": "2023-08"},  # 6 months ago
                    {"skill_name": "Spring", "experience_months": 18, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_stale",
                "name": "Stale Skills",
                "email": "stale@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Java", "experience_months": 30, "last_used": "2022-08"},  # 18 months ago
                    {"skill_name": "JavaScript", "experience_months": 12, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_verystale",
                "name": "Very Stale Skills",
                "email": "verystale@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Java", "experience_months": 36, "last_used": "2021-01"},  # 3 years ago
                    {"skill_name": "Python", "experience_months": 6, "last_used": "Current"}
                ]
            }
        ]
    }


def create_scenario_7_project_context():
    """
    SCENARIO 7: Project Context Considerations
    - Short project: Should favor immediate skills
    - Long project: Should consider learning potential
    """
    return {
        "project_details": {
            "name": "Short Project Context Test",
            "duration": 1,  # Very short project
            "starting_from": "August",
            "skills_required": ["Kubernetes"],
            "resources_required": [
                {"resource_type": "PE", "resource_count": 1}  # Platform Engineer
            ]
        },
        "available_employees": [
            {
                "employee_id": "pe_immediate",
                "name": "Immediate Productivity",
                "email": "immediate@company.com",
                "designation": "PE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Kubernetes", "experience_months": 12, "last_used": "Current"},  # Exact match
                    {"skill_name": "Docker", "experience_months": 18, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "pe_potential",
                "name": "Learning Potential",
                "email": "potential@company.com",
                "designation": "PE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Docker", "experience_months": 36, "last_used": "Current"},     # Related skill
                    {"skill_name": "AWS", "experience_months": 24, "last_used": "Current"},        # DevOps background
                    {"skill_name": "Linux", "experience_months": 48, "last_used": "Current"}       # Strong foundation
                ]
            }
        ]
    }


def create_scenario_8_skill_combinations():
    """
    SCENARIO 8: Skill Combination Synergies
    - Required: Python, Machine Learning, AWS
    - Test different combinations of these skills
    Expected: Should prefer combinations with synergy
    """
    return {
        "project_details": {
            "name": "Skill Combination Synergies Test",
            "duration": 8,
            "starting_from": "September",
            "skills_required": ["Python", "Machine Learning", "AWS"],
            "resources_required": [
                {"resource_type": "SDE", "resource_count": 1}
            ]
        },
        "available_employees": [
            {
                "employee_id": "sde_py_ml",
                "name": "Python ML Expert",
                "email": "pyml@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 36, "last_used": "Current"},
                    {"skill_name": "Machine Learning", "experience_months": 24, "last_used": "Current"},
                    {"skill_name": "TensorFlow", "experience_months": 18, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_py_aws",
                "name": "Python Cloud Expert",
                "email": "pyaws@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Python", "experience_months": 30, "last_used": "Current"},
                    {"skill_name": "AWS", "experience_months": 24, "last_used": "Current"},
                    {"skill_name": "Docker", "experience_months": 18, "last_used": "Current"}
                ]
            },
            {
                "employee_id": "sde_ml_aws",
                "name": "ML Cloud Expert",
                "email": "mlaws@company.com",
                "designation": "SDE",
                "available_percentage": 100,
                "skills": [
                    {"skill_name": "Machine Learning", "experience_months": 30, "last_used": "Current"},
                    {"skill_name": "AWS", "experience_months": 36, "last_used": "Current"},
                    {"skill_name": "R", "experience_months": 24, "last_used": "Current"}  # Basic Python alternative
                ]
            }
        ]
    }


def analyze_scenario_results(scenario_name: str, results: Dict[str, Any], expected_winner: str, reasoning: str):
    """Analyze results for a specific scenario."""
    print(f"\n{'='*80}")
    print(f"SCENARIO ANALYSIS: {scenario_name}")
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
    
    # Get the best combination (first one)
    best_combo = team_combinations[0]
    team_members = best_combo.get("team_members", [])
    
    if not team_members:
        print("❌ No team members in best combination!")
        return False
    
    # For single-person scenarios, check the selected candidate
    if len(team_members) == 1:
        selected_candidate = team_members[0].get("name", "Unknown")
        skills_match = best_combo.get("skills_match", 0)
        
        print(f"🏅 SELECTED CANDIDATE: {selected_candidate}")
        print(f"📊 Skills Match: {skills_match:.1f}%")
        
        # Check if it matches expected winner
        if expected_winner.lower() in selected_candidate.lower():
            print(f"✅ CORRECT: Expected winner selected!")
            return True
        else:
            print(f"❌ INCORRECT: Expected {expected_winner}, got {selected_candidate}")
            return False
    
    # For multi-person scenarios, analyze team composition
    else:
        print(f"👥 SELECTED TEAM ({len(team_members)} members):")
        for member in team_members:
            name = member.get("name", "Unknown")
            skills = member.get("skills", [])
            print(f"  - {name}: {skills}")
        
        skills_match = best_combo.get("skills_match", 0)
        print(f"📊 Team Skills Match: {skills_match:.1f}%")
        
        # For team scenarios, we'll consider it successful if skills match is high
        if skills_match >= 80:
            print(f"✅ GOOD TEAM COMPOSITION: High skills coverage")
            return True
        else:
            print(f"⚠️  SUBOPTIMAL TEAM: Low skills coverage")
            return False


async def run_scenario(agent: MatchingAgent, scenario_name: str, test_data: Dict[str, Any], expected_winner: str, reasoning: str):
    """Run a single scenario test."""
    try:
        results = await agent.process(test_data)
        return analyze_scenario_results(scenario_name, results, expected_winner, reasoning)
    except Exception as e:
        print(f"❌ SCENARIO FAILED: {str(e)}")
        return False


async def main():
    """Main test function for real-life scenarios."""
    print("🧪 REAL-LIFE SKILL MATCHING SCENARIOS TEST SUITE")
    print("=" * 80)
    print("Testing complex real-world scenarios that challenge skill prioritization logic")
    print("=" * 80)
    
    # Initialize the agent
    config = AIConfig()
    agent = MatchingAgent(config)
    
    # Define test scenarios
    scenarios = [
        (
            "EXPERIENCE vs RECENCY",
            create_scenario_1_experience_vs_recency(),
            "Beginner Recent Usage",
            "Recent usage (1 week) should beat old usage (12 months) for short projects"
        ),
        (
            "DEPTH vs BREADTH",
            create_scenario_2_depth_vs_breadth(),
            "Full Stack Beginner",
            "For 3+ skills, breadth should beat depth"
        ),
        (
            "CRITICAL vs SECONDARY",
            create_scenario_3_critical_vs_secondary(),
            "Python Expert",
            "Critical skill (Python) expertise should beat secondary skills (Flask/Django)"
        ),
        (
            "TRANSFERABLE SKILLS",
            create_scenario_4_transferable_skills(),
            "React Expert",
            "React experience should transfer well to React Native"
        ),
        (
            "TEAM COMPOSITION",
            create_scenario_5_team_composition(),
            "Balanced Team",
            "Should prefer skill diversity or full-stack developers"
        ),
        (
            "STALENESS THRESHOLDS",
            create_scenario_6_staleness_thresholds(),
            "Moderate Staleness",
            "6 months ago should beat 18 months and 3 years"
        ),
        (
            "PROJECT CONTEXT",
            create_scenario_7_project_context(),
            "Immediate Productivity",
            "Short projects should favor immediate skills over learning potential"
        ),
        (
            "SKILL SYNERGIES",
            create_scenario_8_skill_combinations(),
            "Python ML Expert",
            "Python+ML combination should have strong synergy"
        )
    ]
    
    # Run all scenarios
    results = []
    successful_scenarios = 0
    
    for scenario_name, test_data, expected_winner, reasoning in scenarios:
        print(f"\n🔄 Running {scenario_name}...")
        success = await run_scenario(agent, scenario_name, test_data, expected_winner, reasoning)
        results.append((scenario_name, success))
        if success:
            successful_scenarios += 1
    
    # Summary
    print(f"\n{'='*80}")
    print("🏆 REAL-LIFE SCENARIOS TEST SUMMARY")
    print(f"{'='*80}")
    
    total_scenarios = len(scenarios)
    success_rate = (successful_scenarios / total_scenarios) * 100
    
    print(f"📊 Overall Results: {successful_scenarios}/{total_scenarios} scenarios passed ({success_rate:.1f}%)")
    print()
    
    for scenario_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {scenario_name}")
    
    print()
    
    # Assessment
    if success_rate >= 90:
        assessment = "🌟 EXCELLENT - Prompt handles real-life scenarios very well"
    elif success_rate >= 75:
        assessment = "✅ GOOD - Prompt handles most scenarios correctly"
    elif success_rate >= 60:
        assessment = "⚠️  ACCEPTABLE - Some scenarios need improvement"
    else:
        assessment = "❌ POOR - Significant prompt improvements needed"
    
    print(f"🎯 Assessment: {assessment}")
    print(f"💡 Confidence Level: {success_rate:.0f}%")
    
    if success_rate < 100:
        print(f"\n🔧 Recommendations:")
        print(f"- Review failed scenarios for prompt improvements")
        print(f"- Consider adding more specific rules for edge cases")
        print(f"- Test with additional real-world data")
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main()) 