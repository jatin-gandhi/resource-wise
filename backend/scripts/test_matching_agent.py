#!/usr/bin/env python3
"""
Test script for the Matching Agent with comprehensive test data.
"""

import asyncio
from typing import Dict, Any
import sys
from pathlib import Path

# Add the backend app to the Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.ai.agents.matching.agent import MatchingAgent
from app.ai.core.config import AIConfig


def create_test_employees():
    """Create 20 diverse test employees with varied skills and availability."""
    return [
        {
            "employee_id": "emp_001",
            "name": "Alex Chen",
            "email": "alex.chen@company.com",
            "designation": "TL",
            "available_percentage": 75,
            "skills": [
                {"skill_name": "React Native", "experience_months": 36, "last_used": "Current"},
                {"skill_name": "TypeScript", "experience_months": 42, "last_used": "Current"},
                {"skill_name": "Node.js", "experience_months": 48, "last_used": "2024-01"},
                {"skill_name": "Team Leadership", "experience_months": 24, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_002",
            "name": "Sarah Johnson",
            "email": "sarah.johnson@company.com",
            "designation": "SSE",
            "available_percentage": 100,
            "skills": [
                {"skill_name": "React Native", "experience_months": 30, "last_used": "Current"},
                {"skill_name": "JavaScript", "experience_months": 54, "last_used": "Current"},
                {"skill_name": "Redux", "experience_months": 24, "last_used": "2024-02"},
                {"skill_name": "Mobile UI/UX", "experience_months": 18, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_003",
            "name": "Michael Rodriguez",
            "email": "michael.rodriguez@company.com",
            "designation": "SSE",
            "available_percentage": 50,
            "skills": [
                {"skill_name": "TypeScript", "experience_months": 36, "last_used": "Current"},
                {"skill_name": "Node.js", "experience_months": 42, "last_used": "Current"},
                {"skill_name": "Express.js", "experience_months": 30, "last_used": "2024-01"},
                {"skill_name": "MongoDB", "experience_months": 24, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_004",
            "name": "Emily Davis",
            "email": "emily.davis@company.com",
            "designation": "SDE",
            "available_percentage": 100,
            "skills": [
                {"skill_name": "React Native", "experience_months": 18, "last_used": "Current"},
                {"skill_name": "JavaScript", "experience_months": 24, "last_used": "Current"},
                {"skill_name": "CSS", "experience_months": 30, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_005",
            "name": "David Kim",
            "email": "david.kim@company.com",
            "designation": "SDE",
            "available_percentage": 75,
            "skills": [
                {"skill_name": "TypeScript", "experience_months": 20, "last_used": "Current"},
                {"skill_name": "React", "experience_months": 22, "last_used": "2024-01"},
                {"skill_name": "Git", "experience_months": 26, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_006",
            "name": "Lisa Wang",
            "email": "lisa.wang@company.com",
            "designation": "SDE",
            "available_percentage": 50,
            "skills": [
                {"skill_name": "JavaScript", "experience_months": 16, "last_used": "Current"},
                {"skill_name": "HTML", "experience_months": 20, "last_used": "Current"},
                {"skill_name": "CSS", "experience_months": 18, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_007",
            "name": "James Wilson",
            "email": "james.wilson@company.com",
            "designation": "QA",
            "available_percentage": 100,
            "skills": [
                {"skill_name": "Mobile Testing", "experience_months": 30, "last_used": "Current"},
                {"skill_name": "Automation Testing", "experience_months": 24, "last_used": "Current"},
                {"skill_name": "Selenium", "experience_months": 18, "last_used": "2024-02"}
            ]
        },
        {
            "employee_id": "emp_008",
            "name": "Maria Garcia",
            "email": "maria.garcia@company.com",
            "designation": "QA",
            "available_percentage": 75,
            "skills": [
                {"skill_name": "Manual Testing", "experience_months": 36, "last_used": "Current"},
                {"skill_name": "Test Planning", "experience_months": 30, "last_used": "Current"},
                {"skill_name": "Bug Tracking", "experience_months": 42, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_009",
            "name": "Robert Brown",
            "email": "robert.brown@company.com",
            "designation": "SE",
            "available_percentage": 100,
            "skills": [
                {"skill_name": "React Native", "experience_months": 12, "last_used": "Current"},
                {"skill_name": "JavaScript", "experience_months": 18, "last_used": "Current"},
                {"skill_name": "API Integration", "experience_months": 14, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_010",
            "name": "Jennifer Lee",
            "email": "jennifer.lee@company.com",
            "designation": "SE",
            "available_percentage": 50,
            "skills": [
                {"skill_name": "TypeScript", "experience_months": 15, "last_used": "Current"},
                {"skill_name": "React", "experience_months": 16, "last_used": "2024-01"},
                {"skill_name": "State Management", "experience_months": 12, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_011",
            "name": "Kevin Martinez",
            "email": "kevin.martinez@company.com",
            "designation": "ARCH",
            "available_percentage": 25,
            "skills": [
                {"skill_name": "System Architecture", "experience_months": 60, "last_used": "Current"},
                {"skill_name": "Microservices", "experience_months": 48, "last_used": "Current"},
                {"skill_name": "Cloud Architecture", "experience_months": 36, "last_used": "Current"},
                {"skill_name": "Technical Leadership", "experience_months": 54, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_012",
            "name": "Amanda Taylor",
            "email": "amanda.taylor@company.com",
            "designation": "PM",
            "available_percentage": 50,
            "skills": [
                {"skill_name": "Project Management", "experience_months": 48, "last_used": "Current"},
                {"skill_name": "Agile", "experience_months": 42, "last_used": "Current"},
                {"skill_name": "Stakeholder Management", "experience_months": 36, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_013",
            "name": "Daniel Anderson",
            "email": "daniel.anderson@company.com",
            "designation": "TDO",
            "available_percentage": 75,
            "skills": [
                {"skill_name": "Technical Documentation", "experience_months": 30, "last_used": "Current"},
                {"skill_name": "API Documentation", "experience_months": 24, "last_used": "Current"},
                {"skill_name": "User Guides", "experience_months": 36, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_014",
            "name": "Rachel Thompson",
            "email": "rachel.thompson@company.com",
            "designation": "PE",
            "available_percentage": 100,
            "skills": [
                {"skill_name": "Performance Testing", "experience_months": 30, "last_used": "Current"},
                {"skill_name": "Load Testing", "experience_months": 24, "last_used": "Current"},
                {"skill_name": "Performance Optimization", "experience_months": 18, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_015",
            "name": "Christopher White",
            "email": "christopher.white@company.com",
            "designation": "SSE",
            "available_percentage": 75,
            "skills": [
                {"skill_name": "Flutter", "experience_months": 24, "last_used": "2024-01"},
                {"skill_name": "Dart", "experience_months": 24, "last_used": "2024-01"},
                {"skill_name": "Mobile Development", "experience_months": 36, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_016",
            "name": "Nicole Harris",
            "email": "nicole.harris@company.com",
            "designation": "SDE",
            "available_percentage": 100,
            "skills": [
                {"skill_name": "Python", "experience_months": 20, "last_used": "Current"},
                {"skill_name": "Django", "experience_months": 16, "last_used": "2024-02"},
                {"skill_name": "REST APIs", "experience_months": 18, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_017",
            "name": "Matthew Clark",
            "email": "matthew.clark@company.com",
            "designation": "SE",
            "available_percentage": 50,
            "skills": [
                {"skill_name": "Java", "experience_months": 30, "last_used": "2024-01"},
                {"skill_name": "Spring Boot", "experience_months": 24, "last_used": "2024-01"},
                {"skill_name": "Database Design", "experience_months": 28, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_018",
            "name": "Stephanie Lewis",
            "email": "stephanie.lewis@company.com",
            "designation": "QA",
            "available_percentage": 75,
            "skills": [
                {"skill_name": "API Testing", "experience_months": 22, "last_used": "Current"},
                {"skill_name": "Postman", "experience_months": 18, "last_used": "Current"},
                {"skill_name": "Test Automation", "experience_months": 20, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_019",
            "name": "Andrew Walker",
            "email": "andrew.walker@company.com",
            "designation": "SDE",
            "available_percentage": 25,
            "skills": [
                {"skill_name": "C#", "experience_months": 24, "last_used": "2024-02"},
                {"skill_name": ".NET", "experience_months": 22, "last_used": "2024-02"},
                {"skill_name": "SQL Server", "experience_months": 26, "last_used": "Current"}
            ]
        },
        {
            "employee_id": "emp_020",
            "name": "Megan Hall",
            "email": "megan.hall@company.com",
            "designation": "TL",
            "available_percentage": 50,
            "skills": [
                {"skill_name": "Angular", "experience_months": 36, "last_used": "2024-01"},
                {"skill_name": "TypeScript", "experience_months": 40, "last_used": "Current"},
                {"skill_name": "Team Management", "experience_months": 18, "last_used": "Current"},
                {"skill_name": "Code Review", "experience_months": 30, "last_used": "Current"}
            ]
        }
    ]


def create_test_scenario_1():
    """Test Scenario 1: All resources fulfilled with all skill requirements covered."""
    return {
        "project_details": {
            "name": "Mobile Banking App - Perfect Match",
            "duration": 3,
            "starting_from": "July",
            "skills_required": ["React Native", "TypeScript", "JavaScript", "Mobile Testing"],
            "resources_required": {
                "TL": 1,
                "SSE": 2,
                "SDE": 2,
                "QA": 1
            }
        },
        "available_employees": create_test_employees()
    }


def create_test_scenario_2():
    """Test Scenario 2: Partial resources fulfilled with all skill requirements covered."""
    return {
        "project_details": {
            "name": "E-commerce Platform - Resource Shortage",
            "duration": 4,
            "starting_from": "August",
            "skills_required": ["React Native", "TypeScript", "Node.js", "MongoDB"],
            "resources_required": {
                "TL": 3,  # Need 3 but only have 2 available
                "SSE": 5,  # Need 5 but only have 3 available
                "SDE": 4,  # Should be achievable
                "QA": 2   # Should be achievable
            }
        },
        "available_employees": create_test_employees()
    }


def create_test_scenario_3():
    """Test Scenario 3: All resources fulfilled with partial skill requirements covered."""
    return {
        "project_details": {
            "name": "AI-Powered Analytics Dashboard",
            "duration": 5,
            "starting_from": "September",
            "skills_required": ["Python", "Machine Learning", "TensorFlow", "Kubernetes", "Docker", "GraphQL"],
            "resources_required": {
                "TL": 1,   # Available
                "SSE": 2,  # Available
                "SDE": 3   # Available
            }
        },
        "available_employees": create_test_employees()
    }


def create_test_scenario_4():
    """Test Scenario 4: Partial resources fulfilled with partial skill requirements covered."""
    return {
        "project_details": {
            "name": "Enterprise Blockchain Platform",
            "duration": 8,
            "starting_from": "October",
            "skills_required": ["Solidity", "Web3", "Ethereum", "Rust", "Go", "Microservices", "Redis"],
            "resources_required": {
                "ARCH": 2,  # Need 2 but only have 1 available
                "TL": 3,    # Need 3 but only have 2 available
                "SSE": 6,   # Need 6 but only have 3 available
                "SDE": 8,   # Need 8 but only have 5 available
                "PE": 2     # Need 2 but only have 1 available
            }
        },
        "available_employees": create_test_employees()
    }


def print_results(scenario_name: str, results: Dict[str, Any], test_data: Dict[str, Any]):
    """Print simplified test results without icons."""
    print(f"\n{'='*60}")
    print(f"{scenario_name}")
    print(f"{'='*60}")
    
    matching_results = results.get("matching_results", {})
    project_details = test_data.get("project_details", {})
    
    if not matching_results.get("success", False):
        print(f"FAILED: {matching_results.get('error_message', 'Unknown error')}")
        return
    
    # Basic metrics
    processing_time = matching_results.get('processing_time_ms', 0)
    print(f"Status: SUCCESS")
    print(f"Processing Time: {processing_time}ms")
    print(f"Project: {project_details.get('name', 'Unknown')}")
    
    # Resource analysis
    required_resources = project_details.get("resources_required", {})
    matched_resources = matching_results.get("matched_resources", {})
    
    total_required = sum(required_resources.values())
    total_matched = sum(len(employees) for employees in matched_resources.values())
    fulfillment_rate = (total_matched/total_required*100) if total_required > 0 else 0
    
    print(f"\nResource Fulfillment: {total_matched}/{total_required} ({fulfillment_rate:.1f}%)")
    
    # Resource breakdown
    print(f"Resource Breakdown:")
    for designation, count in required_resources.items():
        matched_count = len(matched_resources.get(designation, []))
        fulfillment = (matched_count / count * 100) if count > 0 else 0
        
        if matched_count >= count:
            status = "FULFILLED"
        elif matched_count > 0:
            status = "PARTIAL"
        else:
            status = "MISSING"
            
        print(f"  {designation}: {matched_count}/{count} ({fulfillment:.0f}%) - {status}")
    
    # Skills analysis
    team_combinations = matching_results.get("possible_team_combinations", [])
    
    if team_combinations:
        best_combo = max(team_combinations, key=lambda x: x.get('skills_match', 0))
        covered_skills = set(best_combo.get('skills_matched', []))
        missing_skills = set(best_combo.get('skills_missing', []))
        skills_match = best_combo.get('skills_match', 0)
        
        print(f"\nSkills Coverage:")
        print(f"Best Team Skills Match: {skills_match:.1f}%")
        
        if covered_skills:
            print(f"Skills Covered: {', '.join(sorted(covered_skills))}")
        
        if missing_skills:
            print(f"Skills Missing: {', '.join(sorted(missing_skills))}")
        else:
            print(f"All required skills are covered")
    
    # Matched employees by designation
    print(f"\nMatched Employees by Designation:")
    if matched_resources:
        for designation, employees in matched_resources.items():
            print(f"  {designation} ({len(employees)} available):")
            for emp in employees:
                availability = emp.get('available_percentage', 0)
                skills_text = ", ".join(emp.get("skills", []))
                print(f"    {emp.get('name', 'Unknown')} - {availability}% available")
                if skills_text:
                    print(f"      Skills: {skills_text}")
                else:
                    print(f"      Skills: None listed")
            print()
    else:
        print("  No employees matched for any designation")
    
    # Team combinations
    print(f"Team Combinations: {len(team_combinations)} options found")
    
    if team_combinations:
        for i, combo in enumerate(team_combinations, 1):
            skills_match = combo.get('skills_match', 0)
            team_size = len(combo.get('team_members', []))
            
            if skills_match >= 80:
                match_rating = "EXCELLENT"
            elif skills_match >= 60:
                match_rating = "GOOD"
            else:
                match_rating = "POOR"
            
            print(f"  Option {i}: {team_size} members, {skills_match:.1f}% skills match ({match_rating})")
            
            # Group team members by designation
            members_by_designation = {}
            for member in combo.get("team_members", []):
                designation = member.get('designation', 'Unknown')
                if designation not in members_by_designation:
                    members_by_designation[designation] = []
                members_by_designation[designation].append(member)
            
            for designation, members in members_by_designation.items():
                print(f"    {designation}:")
                for member in members:
                    availability = member.get('available_percentage', 0)
                    print(f"      {member.get('name', 'Unknown')} ({availability}%)")
    else:
        print("  No viable team combinations found")
    
    # Overall assessment
    print(f"\nOverall Assessment:")
    resource_fulfillment = (total_matched/total_required*100) if total_required > 0 else 0
    skill_coverage = best_combo.get('skills_match', 0) if team_combinations else 0
    
    if resource_fulfillment >= 100 and skill_coverage >= 80:
        assessment = "EXCELLENT - All requirements can be fully met"
    elif resource_fulfillment >= 80 and skill_coverage >= 60:
        assessment = "GOOD - Most requirements can be met with minor compromises"
    elif resource_fulfillment >= 50 or skill_coverage >= 40:
        assessment = "CHALLENGING - Significant gaps in resources or skills"
    else:
        assessment = "CRITICAL - Major shortfalls in both resources and skills"
    
    print(f"Rating: {assessment}")
    print(f"Resource Fulfillment: {resource_fulfillment:.1f}%")
    print(f"Best Skills Coverage: {skill_coverage:.1f}%")


async def run_test_scenario(agent: MatchingAgent, scenario_name: str, test_data: Dict[str, Any]):
    """Run a single test scenario."""
    print(f"\n{'-'*60}")
    print(f"EXECUTING {scenario_name}")
    print(f"{'-'*60}")
    
    project_details = test_data['project_details']
    print(f"Project: {project_details['name']}")
    print(f"Duration: {project_details['duration']} months")
    print(f"Skills: {', '.join(project_details['skills_required'])}")
    print(f"Resources: {dict(project_details['resources_required'])}")
    print(f"Employee Pool: {len(test_data['available_employees'])} candidates")
    print(f"\nProcessing...")
    
    try:
        results = await agent.process(test_data)
        print_results(scenario_name, results, test_data)
        return results
    except Exception as e:
        print(f"\nEXECUTION FAILED")
        print(f"Error: {str(e)}")
        print(f"{'='*60}")
        return None


async def main():
    """Main test function."""
    print("Initializing Matching Agent Test Suite")
    print("=" * 60)
    print("Testing 4 comprehensive scenarios to evaluate matching capabilities:")
    print("1. All resources fulfilled + All skills covered")
    print("2. Partial resources fulfilled + All skills covered") 
    print("3. All resources fulfilled + Partial skills covered")
    print("4. Partial resources fulfilled + Partial skills covered")
    print("=" * 60)
    
    # Initialize the agent
    config = AIConfig()
    agent = MatchingAgent(config)
    
    # Test scenarios
    scenarios = [
        ("SCENARIO 1: PERFECT MATCH", create_test_scenario_1()),
        ("SCENARIO 2: RESOURCE SHORTAGE", create_test_scenario_2()),
        ("SCENARIO 3: SKILL GAPS", create_test_scenario_3()),
        ("SCENARIO 4: CRITICAL SHORTFALL", create_test_scenario_4())
    ]
    
    results = []
    
    for scenario_name, test_data in scenarios:
        result = await run_test_scenario(agent, scenario_name, test_data)
        results.append((scenario_name, result, test_data))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    total_processing_time = 0
    successful_scenarios = 0
    
    for scenario_name, result, test_data in results:
        if result and result.get("matching_results", {}).get("success", False):
            matching_results = result["matching_results"]
            processing_time = matching_results.get("processing_time_ms", 0)
            total_processing_time += processing_time
            successful_scenarios += 1
            
            # Calculate metrics
            project_details = test_data.get("project_details", {})
            required_resources = project_details.get("resources_required", {})
            matched_resources = matching_results.get("matched_resources", {})
            
            total_required = sum(required_resources.values())
            total_matched = sum(len(employees) for employees in matched_resources.values())
            resource_fulfillment = (total_matched/total_required*100) if total_required > 0 else 0
            
            team_combinations = matching_results.get("possible_team_combinations", [])
            best_skills_match = max([combo.get('skills_match', 0) for combo in team_combinations]) if team_combinations else 0
            
            # Status indicator
            if resource_fulfillment >= 100 and best_skills_match >= 80:
                status = "EXCELLENT"
            elif resource_fulfillment >= 80 and best_skills_match >= 60:
                status = "GOOD"
            elif resource_fulfillment >= 50 or best_skills_match >= 40:
                status = "CHALLENGING"
            else:
                status = "CRITICAL"
            
            print(f"{status} - {scenario_name}:")
            print(f"  Processing Time: {processing_time}ms")
            print(f"  Resource Fulfillment: {resource_fulfillment:.1f}% ({total_matched}/{total_required})")
            print(f"  Best Skills Match: {best_skills_match:.1f}%")
            print(f"  Team Combinations: {len(team_combinations)}")
            print()
        else:
            print(f"FAILED - {scenario_name}")
            print()
    
    # Overall statistics
    print(f"OVERALL STATISTICS:")
    print(f"  Successful Scenarios: {successful_scenarios}/4")
    print(f"  Total Processing Time: {total_processing_time}ms")
    print(f"  Average Processing Time: {total_processing_time/successful_scenarios if successful_scenarios > 0 else 0:.1f}ms")
    
    # Performance assessment
    if successful_scenarios == 4:
        if total_processing_time < 10000:  # Less than 10 seconds total
            performance = "EXCELLENT PERFORMANCE"
        elif total_processing_time < 20000:  # Less than 20 seconds total
            performance = "GOOD PERFORMANCE"
        else:
            performance = "ACCEPTABLE PERFORMANCE"
    else:
        performance = "PERFORMANCE ISSUES DETECTED"
    
    print(f"  Overall Performance: {performance}")
    
    print(f"\nTest suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 