"""Data seeding script for Resource Wise backend"""

import asyncio
import os
import sys
from datetime import date

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, create_tables
from app.models import Allocation, Employee, EmployeeSkill, Project

logger = structlog.get_logger()


async def create_sample_employees(db: AsyncSession) -> list[Employee]:
    """Create sample employees"""
    employees = [
        Employee(
            name="Alice Johnson",
            email="alice.johnson@company.com",
            designation="TL",
            capacity_percent=100,
            onboarded_at=date(2020, 1, 15),
            is_active=True,
        ),
        Employee(
            name="Bob Smith",
            email="bob.smith@company.com",
            designation="SSE",
            capacity_percent=100,
            onboarded_at=date(2021, 3, 10),
            is_active=True,
        ),
        Employee(
            name="Carol Davis",
            email="carol.davis@company.com",
            designation="SSE",
            capacity_percent=80,
            onboarded_at=date(2021, 6, 20),
            is_active=True,
        ),
        Employee(
            name="David Wilson",
            email="david.wilson@company.com",
            designation="SD",
            capacity_percent=100,
            onboarded_at=date(2022, 2, 5),
            is_active=True,
        ),
        Employee(
            name="Eva Martinez",
            email="eva.martinez@company.com",
            designation="SD",
            capacity_percent=100,
            onboarded_at=date(2023, 1, 10),
            is_active=True,
        ),
    ]

    for employee in employees:
        db.add(employee)

    await db.commit()
    await db.refresh(employees[0])  # Refresh to get IDs

    logger.info(f"Created {len(employees)} sample employees")
    return employees


async def create_sample_skills(db: AsyncSession, employees: list[Employee]):
    """Create sample skills for employees"""
    skills_data = [
        # Alice Johnson (TL) - Full-stack with leadership
        (employees[0], "React", "5 years of React development experience", 60, 5),
        (employees[0], "Node.js", "Backend development with Node.js", 48, 4),
        (employees[0], "Team Leadership", "Leading development teams", 36, 5),
        (employees[0], "Python", "Backend development and automation", 24, 4),
        # Bob Smith (SSE) - Mobile specialist
        (employees[1], "React Native", "Cross-platform mobile development", 42, 5),
        (employees[1], "Flutter", "Native mobile app development", 36, 4),
        (employees[1], "iOS", "Native iOS development with Swift", 48, 4),
        (employees[1], "Android", "Native Android development", 30, 3),
        # Carol Davis (SSE) - Backend specialist
        (employees[2], "Python", "FastAPI and Django development", 60, 5),
        (employees[2], "PostgreSQL", "Database design and optimization", 48, 4),
        (employees[2], "AWS", "Cloud infrastructure and deployment", 36, 4),
        (employees[2], "Docker", "Containerization and orchestration", 30, 3),
        # David Wilson (SD) - Frontend focused
        (employees[3], "React", "Frontend development with React", 36, 4),
        (employees[3], "TypeScript", "Type-safe JavaScript development", 30, 4),
        (employees[3], "CSS", "Modern CSS and responsive design", 42, 4),
        (employees[3], "Next.js", "Full-stack React framework", 18, 3),
        # Eva Martinez (SD) - AI/ML interested
        (employees[4], "Python", "General Python development", 24, 3),
        (employees[4], "Machine Learning", "ML model development", 12, 2),
        (employees[4], "Data Analysis", "Data processing and visualization", 18, 3),
        (employees[4], "OpenAI API", "AI integration and chatbots", 6, 2),
    ]

    skills = []
    for employee, skill_name, summary, experience_months, proficiency in skills_data:
        skill = EmployeeSkill(
            employee_id=employee.id,
            skill_name=skill_name,
            summary=summary,
            experience_months=experience_months,
            proficiency_level=proficiency,
            last_used=date(2024, 1, 1),
            source="SEED",
        )
        skills.append(skill)
        db.add(skill)

    await db.commit()
    logger.info(f"Created {len(skills)} sample skills")


async def create_sample_projects(db: AsyncSession) -> list[Project]:
    """Create sample projects"""
    projects = [
        Project(
            name="Mobile Banking App",
            description="Cross-platform mobile app for banking services",
            duration_months=6,
            tech_stack=["React Native", "Node.js", "PostgreSQL", "AWS"],
            required_roles=["TL", "SSE", "SD"],
            required_skills=["React Native", "Mobile Development", "API Integration"],
            status="active",
        ),
        Project(
            name="AI Chatbot Platform",
            description="Internal AI chatbot for customer support",
            duration_months=4,
            tech_stack=["Python", "FastAPI", "OpenAI", "React"],
            required_roles=["SSE", "SD"],
            required_skills=["Python", "AI/ML", "OpenAI API", "React"],
            status="planning",
        ),
        Project(
            name="Data Analytics Dashboard",
            description="Real-time analytics dashboard for business metrics",
            duration_months=3,
            tech_stack=["React", "Python", "PostgreSQL", "Docker"],
            required_roles=["SSE", "SD"],
            required_skills=["React", "Data Visualization", "Python", "PostgreSQL"],
            status="planning",
        ),
    ]

    for project in projects:
        db.add(project)

    await db.commit()
    await db.refresh(projects[0])  # Refresh to get IDs

    logger.info(f"Created {len(projects)} sample projects")
    return projects


async def create_sample_allocations(
    db: AsyncSession, employees: list[Employee], projects: list[Project]
):
    """Create sample allocations"""
    allocations = [
        # Mobile Banking App - Active project
        Allocation(
            project_id=projects[0].id,
            employee_id=employees[0].id,  # Alice (TL)
            percent_allocated=100,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            status="active",
        ),
        Allocation(
            project_id=projects[0].id,
            employee_id=employees[1].id,  # Bob (Mobile specialist)
            percent_allocated=100,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            status="active",
        ),
        Allocation(
            project_id=projects[0].id,
            employee_id=employees[3].id,  # David (Frontend)
            percent_allocated=80,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 6, 30),
            status="active",
        ),
    ]

    for allocation in allocations:
        db.add(allocation)

    await db.commit()
    logger.info(f"Created {len(allocations)} sample allocations")


async def seed_database():
    """Main seeding function"""
    logger.info("Starting database seeding...")

    # Ensure tables exist
    await create_tables()

    async with AsyncSessionLocal() as db:
        try:
            # Create sample data
            employees = await create_sample_employees(db)
            await create_sample_skills(db, employees)
            projects = await create_sample_projects(db)
            await create_sample_allocations(db, employees, projects)

            logger.info("Database seeding completed successfully!")

        except Exception as e:
            logger.error("Database seeding failed", error=str(e))
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
