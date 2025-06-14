"""populate employee skills

Revision ID: a1b2c3d4e5f6
Revises: 34a648ecedae
Create Date: 2025-01-12 23:06:30.123456

"""

import uuid
import random
from datetime import date, datetime, timedelta
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "20250613_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get system user ID for audit tracking
    result = op.get_bind().execute(
        sa.text("SELECT id FROM users WHERE email = 'system@techvantage.io' LIMIT 1")
    )
    system_user_id = result.fetchone()[0]

    # Define skill categories and their skills
    skill_categories = {
        "frontend": {
            "skills": ["React", "Angular", "Vue.js", "Next.js", "TypeScript", "JavaScript", "HTML/CSS", "Tailwind CSS", "Material-UI", "Redux"],
            "weight": 0.3
        },
        "backend": {
            "skills": ["Java", "Python", "Node.js", "PHP", ".NET", "Spring Boot", "Django", "FastAPI", "Express.js", "Laravel"],
            "weight": 0.35
        },
        "cloud": {
            "skills": ["AWS", "Azure", "GCP", "AWS Lambda", "EC2", "S3", "RDS", "CloudFormation", "Azure Functions", "Google Cloud Functions"],
            "weight": 0.25
        },
        "mobile": {
            "skills": ["React Native", "Flutter", "Swift", "Kotlin", "iOS Development", "Android Development", "Xamarin", "Ionic"],
            "weight": 0.15
        },
        "devops": {
            "skills": ["Docker", "Kubernetes", "Terraform", "Jenkins", "GitLab CI", "Grafana", "Prometheus", "AWS CDK", "Ansible", "Helm"],
            "weight": 0.2
        },
        "database": {
            "skills": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Oracle", "SQL Server", "DynamoDB", "Cassandra", "InfluxDB"],
            "weight": 0.3
        },
        "ai_ml": {
            "skills": ["Machine Learning", "TensorFlow", "PyTorch", "OpenAI API", "Scikit-learn", "Pandas", "NumPy", "Computer Vision", "NLP", "Deep Learning"],
            "weight": 0.1
        },
        "testing": {
            "skills": ["Jest", "Selenium", "Cypress", "JUnit", "PyTest", "Postman", "TestNG", "Mocha", "Chai", "Playwright"],
            "weight": 0.25
        },
        "tools": {
            "skills": ["Git", "JIRA", "Confluence", "VS Code", "IntelliJ IDEA", "Figma", "Slack", "Notion", "Postman", "Swagger"],
            "weight": 0.4
        }
    }

    # Define skill combinations for different employee types
    skill_profiles = {
        "fullstack": ["frontend", "backend", "database", "tools"],
        "frontend_specialist": ["frontend", "tools", "testing"],
        "backend_specialist": ["backend", "database", "tools", "testing"],
        "cloud_backend": ["backend", "cloud", "devops", "database"],
        "mobile_developer": ["mobile", "backend", "database", "tools"],
        "devops_engineer": ["devops", "cloud", "backend", "tools"],
        "ai_engineer": ["ai_ml", "backend", "database", "tools"],
        "qa_specialist": ["testing", "tools", "frontend", "backend"],
        "architect": ["backend", "cloud", "devops", "database", "frontend"],
        "tech_lead": ["backend", "frontend", "cloud", "database", "tools"]
    }

    # Get all employees with their designations
    employees_result = op.get_bind().execute(
        sa.text("""
            SELECT e.id, e.email, e.name, d.code, e.onboarded_at
            FROM employees e
            JOIN designations d ON e.designation_id = d.id
            ORDER BY e.email
        """)
    )
    employees = employees_result.fetchall()

    # Define experience ranges based on designation level
    designation_experience = {
        "SDE_INTERN": {"min_exp": 0, "max_exp": 12},      # 0-1 year
        "QA_INTERN": {"min_exp": 0, "max_exp": 12},       # 0-1 year
        "SDE": {"min_exp": 6, "max_exp": 24},             # 0.5-2 years
        "SE": {"min_exp": 12, "max_exp": 36},             # 1-3 years
        "QA": {"min_exp": 6, "max_exp": 24},              # 0.5-2 years
        "SSE": {"min_exp": 24, "max_exp": 60},            # 2-5 years
        "SR_QA": {"min_exp": 36, "max_exp": 72},          # 3-6 years
        "BA": {"min_exp": 12, "max_exp": 48},             # 1-4 years
        "UX": {"min_exp": 12, "max_exp": 48},             # 1-4 years
        "TL": {"min_exp": 48, "max_exp": 96},             # 4-8 years
        "PM": {"min_exp": 36, "max_exp": 84},             # 3-7 years
        "ARCH": {"min_exp": 60, "max_exp": 120},          # 5-10 years
        "PE": {"min_exp": 84, "max_exp": 150},            # 7-12.5 years
        "TDO": {"min_exp": 96, "max_exp": 180}            # 8-15 years
    }

    proficiency_levels = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]

    def get_proficiency_level(base_proficiency, skill_experience_months):
        """Determine proficiency level based on experience months"""
        # Convert months to years for easier calculation
        years = skill_experience_months / 12.0
        
        # Apply the new proficiency mapping
        # Note: Using existing enum values, mapping your requirements to available levels
        if years >= 7:  # 7+ years
            return "EXPERT"
        elif years >= 3:  # 3-7 years  
            return "ADVANCED"
        elif years >= 1:  # 1-3 years
            return "INTERMEDIATE"
        else:  # 0-1 year
            return "BEGINNER"

    def calculate_years_since_onboarding(onboarded_at):
        """Calculate years since employee was onboarded"""
        if isinstance(onboarded_at, str):
            onboarded_date = datetime.strptime(onboarded_at, "%Y-%m-%d").date()
        else:
            onboarded_date = onboarded_at
        
        today = date.today()
        years = (today - onboarded_date).days / 365.25
        return max(years, 0.1)  # Minimum 0.1 years

    # Process each employee
    for employee in employees:
        employee_id, email, name, designation_code, onboarded_at = employee
        
        # Get designation info
        des_info = designation_experience.get(designation_code, designation_experience["SDE"])
        years_experience = calculate_years_since_onboarding(onboarded_at)
        
        # Determine employee profile based on designation and randomness
        if designation_code in ["SDE_INTERN", "QA_INTERN"]:
            # Interns: Basic skills in 1-2 areas
            possible_profiles = ["frontend_specialist", "backend_specialist", "qa_specialist"]
            profile = random.choice(possible_profiles)
            num_skills_per_category = random.randint(2, 4)
        elif designation_code in ["SDE", "SE", "QA"]:
            # Junior: Focused on 1-2 specializations
            if designation_code == "QA":
                profile = "qa_specialist"
            else:
                possible_profiles = ["frontend_specialist", "backend_specialist", "fullstack"]
                profile = random.choice(possible_profiles)
            num_skills_per_category = random.randint(3, 5)
        elif designation_code in ["SSE", "SR_QA"]:
            # Mid-level: More diverse skills
            if designation_code == "SR_QA":
                profile = "qa_specialist"
            else:
                possible_profiles = ["fullstack", "cloud_backend", "mobile_developer", "frontend_specialist", "backend_specialist"]
                profile = random.choice(possible_profiles)
            num_skills_per_category = random.randint(4, 6)
        elif designation_code in ["BA", "UX"]:
            # Business/UX: Specialized skills
            if designation_code == "UX":
                profile = "frontend_specialist"
            else:
                profile = "frontend_specialist"  # BA often works with frontend teams
            num_skills_per_category = random.randint(3, 5)
        elif designation_code in ["TL", "PM"]:
            # Leadership: Broad technical knowledge
            possible_profiles = ["tech_lead", "fullstack", "architect"]
            profile = random.choice(possible_profiles)
            num_skills_per_category = random.randint(5, 7)
        else:  # ARCH, PE, TDO
            # Senior: Very broad and deep skills
            possible_profiles = ["architect", "tech_lead"]
            profile = random.choice(possible_profiles)
            num_skills_per_category = random.randint(6, 8)

        # Get skill categories for this profile
        categories = skill_profiles.get(profile, ["backend", "tools"])
        
        # Add some randomness - occasionally add extra categories
        if random.random() < 0.3:  # 30% chance
            extra_categories = [cat for cat in skill_categories.keys() if cat not in categories]
            if extra_categories:
                categories.append(random.choice(extra_categories))

        # Generate skills for each category
        for category in categories:
            category_skills = skill_categories[category]["skills"]
            num_skills = min(num_skills_per_category, len(category_skills))
            selected_skills = random.sample(category_skills, random.randint(2, num_skills))
            
            for skill_name in selected_skills:
                # Calculate experience months for this skill
                max_skill_exp = int(years_experience * 12 * random.uniform(0.6, 1.0))
                min_exp = max(1, des_info["min_exp"])
                max_exp = max(min_exp + 1, min(max_skill_exp, des_info["max_exp"]))
                skill_exp_months = random.randint(min_exp, max_exp)
                
                # Calculate last used (within last 2 years for active skills)
                days_since_used = random.randint(1, 730)  # 0-2 years
                last_used = date.today() - timedelta(days=days_since_used)
                
                # Determine proficiency based on experience months
                proficiency = get_proficiency_level(None, skill_exp_months)
                
                # Generate summary
                summaries = [
                    f"Experienced in {skill_name} development with {skill_exp_months} months of hands-on experience",
                    f"Proficient in {skill_name} with practical application in multiple projects",
                    f"Strong background in {skill_name} gained through professional development",
                    f"Skilled in {skill_name} with focus on best practices and modern approaches",
                    f"Competent in {skill_name} with experience in enterprise-level applications"
                ]
                summary = random.choice(summaries)
                
                # Insert skill record
                skill_id = uuid.uuid4()
                op.get_bind().execute(
                    sa.text("""
                        INSERT INTO employee_skills (
                            id, employee_id, skill_name, summary, experience_months, 
                            last_used, source, proficiency_level,
                            created_at, updated_at, created_by, updated_by
                        ) VALUES (
                            :skill_id, :employee_id, :skill_name, :summary, 
                            :skill_exp_months, :last_used, 'SEED', :proficiency,
                            NOW(), NOW(), :system_user_id, :system_user_id
                        )
                    """),
                    {
                        'skill_id': skill_id,
                        'employee_id': employee_id,
                        'skill_name': skill_name,
                        'summary': summary,
                        'skill_exp_months': skill_exp_months,
                        'last_used': last_used,
                        'proficiency': proficiency,
                        'system_user_id': system_user_id
                    }
                )

        # Ensure every employee has some basic tools
        basic_tools = ["Git", "JIRA", "VS Code"]
        for tool in basic_tools:
            # Check if already added
            existing = op.get_bind().execute(
                sa.text("""
                    SELECT COUNT(*) FROM employee_skills 
                    WHERE employee_id = :employee_id AND skill_name = :skill_name
                """),
                {'employee_id': employee_id, 'skill_name': tool}
            ).fetchone()[0]
            
            if existing == 0:
                min_exp = max(1, des_info["min_exp"])
                max_exp = max(min_exp + 1, min(int(years_experience * 12), des_info["max_exp"]))
                skill_exp_months = random.randint(min_exp, max_exp)
                last_used = date.today() - timedelta(days=random.randint(1, 90))
                proficiency = get_proficiency_level(None, skill_exp_months)
                
                skill_id = uuid.uuid4()
                op.get_bind().execute(
                    sa.text("""
                        INSERT INTO employee_skills (
                            id, employee_id, skill_name, summary, experience_months, 
                            last_used, source, proficiency_level,
                            created_at, updated_at, created_by, updated_by
                        ) VALUES (
                            :skill_id, :employee_id, :skill_name, :summary, 
                            :skill_exp_months, :last_used, 'SEED', :proficiency,
                            NOW(), NOW(), :system_user_id, :system_user_id
                        )
                    """),
                    {
                        'skill_id': skill_id,
                        'employee_id': employee_id,
                        'skill_name': tool,
                        'summary': 'Essential development tool used daily in professional work',
                        'skill_exp_months': skill_exp_months,
                        'last_used': last_used,
                        'proficiency': proficiency,
                        'system_user_id': system_user_id
                    }
                )


def downgrade() -> None:
    # Remove all seeded skills
    op.get_bind().execute(sa.text("DELETE FROM employee_skills WHERE source = 'SEED'")) 
