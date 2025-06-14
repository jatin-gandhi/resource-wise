#!/usr/bin/env python3
"""
Test script for the Matching Agent with comprehensive test data and verification.
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
    """Run a single test scenario with verification."""
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
        # Get expected results for verification
        expected = get_expected_matches_for_scenario(scenario_name, test_data)
        
        # Run the matching
        results = await agent.process(test_data)
        
        # Print results
        print_results(scenario_name, results, test_data)
        
        # Verify results
        verification = verify_matching_results(expected, results, test_data)
        print_verification_results(verification)
        
        return results, verification
    except Exception as e:
        print(f"\nEXECUTION FAILED")
        print(f"Error: {str(e)}")
        print(f"{'='*60}")
        return None, None


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
        result, verification = await run_test_scenario(agent, scenario_name, test_data)
        results.append((scenario_name, result, verification, test_data))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    total_processing_time = 0
    successful_scenarios = 0
    passed_verifications = 0
    total_warnings = 0
    total_errors = 0
    
    for scenario_name, result, verification, test_data in results:
        if result and result.get("matching_results", {}).get("success", False):
            matching_results = result["matching_results"]
            processing_time = matching_results.get("processing_time_ms", 0)
            total_processing_time += processing_time
            successful_scenarios += 1
            
            # Verification metrics
            verification_status = "N/A"
            if verification:
                if verification["overall_pass"]:
                    if not verification["warnings"]:
                        verification_status = "✅ PASSED"
                        passed_verifications += 1
                    else:
                        verification_status = "⚠️  PASSED WITH WARNINGS"
                        passed_verifications += 1
                else:
                    verification_status = "❌ FAILED"
                
                total_warnings += len(verification["warnings"])
                total_errors += len(verification["errors"])
            
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
            print(f"  Verification: {verification_status}")
            if verification and (verification["warnings"] or verification["errors"]):
                print(f"    Warnings: {len(verification['warnings'])}, Errors: {len(verification['errors'])}")
            print()
        else:
            print(f"FAILED - {scenario_name}")
            if verification:
                print(f"  Verification: ❌ FAILED")
            print()
    
    # Overall statistics
    print(f"OVERALL STATISTICS:")
    print(f"  Successful Scenarios: {successful_scenarios}/4")
    print(f"  Passed Verifications: {passed_verifications}/4")
    print(f"  Total Warnings: {total_warnings}")
    print(f"  Total Errors: {total_errors}")
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
    
    # Verification assessment
    if passed_verifications == 4 and total_errors == 0:
        if total_warnings == 0:
            verification_assessment = "PERFECT VERIFICATION"
        else:
            verification_assessment = "GOOD VERIFICATION (with warnings)"
    elif passed_verifications >= 3:
        verification_assessment = "ACCEPTABLE VERIFICATION"
    else:
        verification_assessment = "VERIFICATION ISSUES DETECTED"
    
    print(f"  Overall Performance: {performance}")
    print(f"  Overall Verification: {verification_assessment}")
    
    print(f"\nTest suite completed!")
    print("=" * 60)


# ============================================================================
# VERIFICATION FUNCTIONS
# ============================================================================

def get_expected_matches_for_scenario(scenario_name: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Define expected outcomes for each test scenario based on our known data."""
    
    project_details = test_data["project_details"]
    required_resources = project_details["resources_required"]
    required_skills = set(project_details["skills_required"])
    
    # Analyze available employees to determine expected matches
    employees = test_data["available_employees"]
    
    # Count available employees by designation
    available_by_designation = {}
    employees_with_required_skills = set()
    
    for emp in employees:
        designation = emp["designation"]
        if designation not in available_by_designation:
            available_by_designation[designation] = 0
        available_by_designation[designation] += 1
        
        # Check if employee has any required skills
        emp_skills = {skill["skill_name"].lower() for skill in emp["skills"]}
        required_skills_lower = {skill.lower() for skill in required_skills}
        
        if emp_skills.intersection(required_skills_lower):
            employees_with_required_skills.add(emp["employee_id"])
    
    # Calculate expected resource fulfillment
    expected_resource_fulfillment = {}
    total_required = 0
    total_available = 0
    
    for designation, required_count in required_resources.items():
        available_count = available_by_designation.get(designation, 0)
        fulfilled_count = min(required_count, available_count)
        
        expected_resource_fulfillment[designation] = {
            "required": required_count,
            "available": available_count,
            "fulfilled": fulfilled_count,
            "fulfillment_rate": (fulfilled_count / required_count * 100) if required_count > 0 else 0
        }
        
        total_required += required_count
        total_available += fulfilled_count
    
    overall_fulfillment_rate = (total_available / total_required * 100) if total_required > 0 else 0
    
    # Calculate expected skills coverage
    all_employee_skills = set()
    for emp in employees:
        for skill in emp["skills"]:
            all_employee_skills.add(skill["skill_name"].lower())
    
    required_skills_lower = {skill.lower() for skill in required_skills}
    covered_skills = all_employee_skills.intersection(required_skills_lower)
    missing_skills = required_skills_lower - covered_skills
    
    skills_coverage_rate = (len(covered_skills) / len(required_skills) * 100) if required_skills else 0
    
    # Scenario-specific expectations
    if "Perfect Match" in project_details["name"]:
        expected_assessment = "EXCELLENT"
        min_resource_fulfillment = 100
        min_skills_coverage = 100
    elif "Resource Shortage" in project_details["name"]:
        expected_assessment = "GOOD"
        min_resource_fulfillment = 60
        min_skills_coverage = 80
    elif "Skill Gaps" in project_details["name"]:
        expected_assessment = "CHALLENGING"
        min_resource_fulfillment = 80
        min_skills_coverage = 30
    elif "Critical Shortfall" in project_details["name"]:
        expected_assessment = "CRITICAL"
        min_resource_fulfillment = 40
        min_skills_coverage = 20
    else:
        expected_assessment = "UNKNOWN"
        min_resource_fulfillment = 0
        min_skills_coverage = 0
    
    return {
        "scenario_name": scenario_name,
        "expected_assessment": expected_assessment,
        "resource_fulfillment": expected_resource_fulfillment,
        "overall_fulfillment_rate": overall_fulfillment_rate,
        "skills_coverage_rate": skills_coverage_rate,
        "covered_skills": list(covered_skills),
        "missing_skills": list(missing_skills),
        "employees_with_skills": len(employees_with_required_skills),
        "min_resource_fulfillment": min_resource_fulfillment,
        "min_skills_coverage": min_skills_coverage,
        "should_have_team_combinations": overall_fulfillment_rate > 0 and skills_coverage_rate > 0
    }


def verify_matching_results(expected: Dict[str, Any], actual_results: Dict[str, Any], test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Verify actual results against expected outcomes."""
    
    verification_results = {
        "scenario_name": expected["scenario_name"],
        "overall_pass": True,
        "checks": [],
        "errors": [],
        "warnings": []
    }
    
    matching_results = actual_results.get("matching_results", {})
    
    if not matching_results.get("success", False):
        verification_results["overall_pass"] = False
        verification_results["errors"].append(f"Matching failed: {matching_results.get('error_message', 'Unknown error')}")
        return verification_results
    
    # Check 1: Resource fulfillment verification
    matched_resources = matching_results.get("matched_resources", {})
    project_details = test_data["project_details"]
    required_resources = project_details["resources_required"]
    
    total_required = sum(required_resources.values())
    total_matched = sum(len(employees) for employees in matched_resources.values())
    actual_fulfillment_rate = (total_matched / total_required * 100) if total_required > 0 else 0
    
    # Verify resource counts by designation
    for designation, expected_info in expected["resource_fulfillment"].items():
        actual_matched = len(matched_resources.get(designation, []))
        expected_max = expected_info["available"]
        required_count = expected_info["required"]
        
        if actual_matched > expected_max:
            verification_results["errors"].append(
                f"Too many {designation} matched: got {actual_matched}, max available {expected_max}"
            )
            verification_results["overall_pass"] = False
        
        if actual_matched < min(required_count, expected_max) * 0.8:  # Allow 20% tolerance
            verification_results["warnings"].append(
                f"Low {designation} matching: got {actual_matched}, expected ~{min(required_count, expected_max)}"
            )
    
    # Check 2: Skills coverage verification
    team_combinations = matching_results.get("possible_team_combinations", [])
    
    if expected["should_have_team_combinations"] and not team_combinations:
        verification_results["errors"].append("Expected team combinations but none were provided")
        verification_results["overall_pass"] = False
    
    if team_combinations:
        best_combo = max(team_combinations, key=lambda x: x.get('skills_match', 0))
        actual_skills_coverage = best_combo.get('skills_match', 0)
        
        if actual_skills_coverage < expected["min_skills_coverage"]:
            verification_results["warnings"].append(
                f"Skills coverage below expected minimum: {actual_skills_coverage:.1f}% < {expected['min_skills_coverage']}%"
            )
    
    # Check 3: Employee skill validation
    required_skills_lower = {skill.lower() for skill in project_details["skills_required"]}
    
    for designation, employees in matched_resources.items():
        for emp in employees:
            emp_skills_lower = {skill.lower() for skill in emp.get("skills", [])}
            
            if not emp_skills_lower.intersection(required_skills_lower):
                verification_results["warnings"].append(
                    f"Employee {emp.get('name', 'Unknown')} matched but has no required skills"
                )
    
    # Check 4: Availability validation
    for designation, employees in matched_resources.items():
        for emp in employees:
            availability = emp.get("available_percentage", 0)
            if availability < 25:  # Very low availability
                verification_results["warnings"].append(
                    f"Employee {emp.get('name', 'Unknown')} has very low availability: {availability}%"
                )
    
    # Check 5: Overall assessment validation
    if actual_fulfillment_rate >= expected["min_resource_fulfillment"]:
        verification_results["checks"].append(f"✓ Resource fulfillment meets minimum: {actual_fulfillment_rate:.1f}% >= {expected['min_resource_fulfillment']}%")
    else:
        verification_results["warnings"].append(f"Resource fulfillment below minimum: {actual_fulfillment_rate:.1f}% < {expected['min_resource_fulfillment']}%")
    
    if team_combinations:
        best_skills = max(combo.get('skills_match', 0) for combo in team_combinations)
        if best_skills >= expected["min_skills_coverage"]:
            verification_results["checks"].append(f"✓ Skills coverage meets minimum: {best_skills:.1f}% >= {expected['min_skills_coverage']}%")
        else:
            verification_results["warnings"].append(f"Skills coverage below minimum: {best_skills:.1f}% < {expected['min_skills_coverage']}%")
    
    # Check 6: Team combination quality
    if team_combinations:
        high_quality_combos = [combo for combo in team_combinations if combo.get('skills_match', 0) >= 60]
        if high_quality_combos:
            verification_results["checks"].append(f"✓ Found {len(high_quality_combos)} high-quality team combinations (≥60% skills match)")
        else:
            verification_results["warnings"].append("No high-quality team combinations found (≥60% skills match)")
    
    return verification_results


def print_verification_results(verification: Dict[str, Any]):
    """Print verification results in a clear format."""
    
    print(f"\n{'='*60}")
    print(f"VERIFICATION RESULTS: {verification['scenario_name']}")
    print(f"{'='*60}")
    
    # Overall status
    if verification["overall_pass"]:
        if not verification["warnings"]:
            print("✅ VERIFICATION PASSED - All checks successful")
        else:
            print("⚠️  VERIFICATION PASSED WITH WARNINGS")
    else:
        print("❌ VERIFICATION FAILED")
    
    # Successful checks
    if verification["checks"]:
        print(f"\n✅ SUCCESSFUL CHECKS:")
        for check in verification["checks"]:
            print(f"  {check}")
    
    # Warnings
    if verification["warnings"]:
        print(f"\n⚠️  WARNINGS:")
        for warning in verification["warnings"]:
            print(f"  • {warning}")
    
    # Errors
    if verification["errors"]:
        print(f"\n❌ ERRORS:")
        for error in verification["errors"]:
            print(f"  • {error}")
    
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main()) 