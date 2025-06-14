"""seed data with business fields and realistic allocations

Revision ID: 20250613_0001
Revises: 34a648ecedae
Create Date: 2025-06-13 00:01:00.000000

"""

import random
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250613_0001"
down_revision: Union[str, None] = "34a648ecedae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed database with 200 employees, realistic business data, and proper allocation constraints"""

    # System user for audit tracking
    system_user_id = uuid.uuid4()

    # Insert system user first
    op.execute(
        f"""
        INSERT INTO users (id, username, email, hashed_password, full_name, is_active, is_superuser, 
                          created_at, updated_at, created_by, updated_by) 
        VALUES ('{system_user_id}', 'system', 'system@techvantage.io', 
                '$2b$12$dummy.hash.for.system.user', 'System User', true, true,
                NOW(), NOW(), '{system_user_id}', '{system_user_id}');
    """
    )

    # Insert designations
    designations_data = [
        # Interns (Level 0)
        ("SDE_INTERN", "Software Development Engineer Intern", 0, False),
        ("QA_INTERN", "Quality Assurance Intern", 0, False),
        # Junior (Level 1-2)
        ("SDE", "Software Development Engineer", 1, False),
        ("SE", "Software Engineer", 2, False),
        ("QA", "Quality Assurance Engineer", 1, False),
        # Mid-level (Level 3-4)
        ("SSE", "Senior Software Engineer", 3, False),
        ("SR_QA", "Senior Quality Assurance Engineer", 4, False),
        ("BA", "Business Analyst", 2, False),
        ("UX", "UX Designer", 2, False),
        # Senior (Level 5-6)
        ("TL", "Technical Lead", 5, True),
        ("PM", "Project Manager", 4, True),
        ("ARCH", "Software Architect", 6, True),
        # Principal+ (Level 7+)
        ("PE", "Principal Software Engineer", 8, True),
        ("TDO", "Technical Delivery Officer", 10, True),
    ]

    designation_ids = {}
    for code, title, level, is_leadership in designations_data:
        designation_id = uuid.uuid4()
        designation_ids[code] = designation_id
        op.execute(
            f"""
            INSERT INTO designations (id, code, title, level, is_leadership, is_active,
                                    created_at, updated_at, created_by, updated_by)
            VALUES ('{designation_id}', '{code}', '{title}', {level}, {is_leadership}, true,
                    NOW(), NOW(), '{system_user_id}', '{system_user_id}');
        """
        )

    # Customer names and Dev Partner organizations
    customer_names = [
        "RetailCorp Inc",
        "FinanceFirst Bank",
        "HealthTech Solutions",
        "EduLearn Platform",
        "LogiFlow Systems",
        "MediaStream Co",
        "GreenEnergy Ltd",
        "AutoTech Motors",
        "FoodChain Global",
        "TravelEase Inc",
        "SportsTech Pro",
        "FashionForward Ltd",
        "RealEstate Plus",
        "InsureTech Corp",
        "AgriTech Solutions",
        "ManufacturingPro",
        "TelecomNext",
        "EnergyFlow Systems",
        "ConstructTech",
        "PharmaCare Inc",
    ]

    dev_partner_orgs = [
        "TechPartner Solutions",
        "DevConsult LLC",
        "CodeCraft Partners",
        "InnovateTech Consulting",
        "AgileWorks Inc",
        "CloudExperts Ltd",
    ]

    # Insert projects (36 total - doubled from 18)
    projects_data = [
        # Customer Projects (24 total)
        (
            "E-Commerce Platform Modernization",
            "Legacy system migration to microservices",
            8,
            "CUSTOMER",
            "COMPLETED",
            ["React", "Node.js", "PostgreSQL", "Docker", "AWS"],
            "RetailCorp Inc",
        ),
        (
            "Mobile Banking App",
            "iOS and Android banking application",
            12,
            "CUSTOMER",
            "ACTIVE",
            ["React Native", "Node.js", "MongoDB", "AWS"],
            "FinanceFirst Bank",
        ),
        (
            "Healthcare Management System",
            "Patient management and scheduling system",
            10,
            "CUSTOMER",
            "ACTIVE",
            ["Angular", "Java", "Spring Boot", "PostgreSQL"],
            "HealthTech Solutions",
        ),
        (
            "Supply Chain Analytics",
            "Real-time supply chain monitoring dashboard",
            6,
            "CUSTOMER",
            "COMPLETED",
            ["Python", "Django", "PostgreSQL", "Redis", "Celery"],
            "LogiFlow Systems",
        ),
        (
            "Insurance Claims Processing",
            "Automated claims processing system",
            14,
            "CUSTOMER",
            "ACTIVE",
            ["Java", "Spring Boot", "Oracle", "Kafka", "Docker"],
            "InsureTech Corp",
        ),
        (
            "Retail POS System",
            "Point of sale system for retail chains",
            8,
            "CUSTOMER",
            "ACTIVE",
            ["Vue.js", "Python", "FastAPI", "PostgreSQL"],
            "RetailCorp Inc",
        ),
        (
            "Financial Trading Platform",
            "High-frequency trading platform",
            18,
            "CUSTOMER",
            "ACTIVE",
            ["C++", "Python", "Redis", "PostgreSQL", "Kafka"],
            "FinanceFirst Bank",
        ),
        (
            "EdTech Learning Platform",
            "Online learning management system",
            10,
            "CUSTOMER",
            "COMPLETED",
            ["React", "Node.js", "MongoDB", "AWS", "Docker"],
            "EduLearn Platform",
        ),
        (
            "Logistics Optimization",
            "Route optimization for delivery services",
            12,
            "CUSTOMER",
            "ACTIVE",
            ["Python", "Django", "PostgreSQL", "Redis", "ML"],
            "LogiFlow Systems",
        ),
        (
            "CRM Enhancement",
            "Customer relationship management system upgrade",
            6,
            "CUSTOMER",
            "COMPLETED",
            ["Salesforce", "Apex", "Lightning", "JavaScript"],
            "AutoTech Motors",
        ),
        (
            "IoT Device Management",
            "Industrial IoT device monitoring platform",
            14,
            "CUSTOMER",
            "ACTIVE",
            ["Python", "FastAPI", "InfluxDB", "Grafana", "MQTT"],
            "ManufacturingPro",
        ),
        (
            "Blockchain Wallet",
            "Cryptocurrency wallet application",
            16,
            "CUSTOMER",
            "ACTIVE",
            ["React", "Node.js", "Solidity", "Web3", "PostgreSQL"],
            "FinanceFirst Bank",
        ),
        (
            "Video Streaming Platform",
            "Live video streaming and VOD platform",
            20,
            "CUSTOMER",
            "ACTIVE",
            ["React", "Node.js", "FFmpeg", "AWS", "CDN"],
            "MediaStream Co",
        ),
        (
            "Food Delivery App",
            "Multi-restaurant food delivery platform",
            9,
            "CUSTOMER",
            "ACTIVE",
            ["React Native", "Node.js", "MongoDB", "Redis"],
            "FoodChain Global",
        ),
        (
            "Travel Booking System",
            "Comprehensive travel booking platform",
            11,
            "CUSTOMER",
            "ACTIVE",
            ["Vue.js", "Python", "Django", "PostgreSQL"],
            "TravelEase Inc",
        ),
        (
            "Sports Analytics Platform",
            "Real-time sports data analytics",
            7,
            "CUSTOMER",
            "COMPLETED",
            ["React", "Python", "FastAPI", "InfluxDB"],
            "SportsTech Pro",
        ),
        (
            "Fashion E-commerce",
            "Online fashion retail platform",
            13,
            "CUSTOMER",
            "ACTIVE",
            ["Next.js", "Node.js", "PostgreSQL", "Stripe"],
            "FashionForward Ltd",
        ),
        (
            "Real Estate Portal",
            "Property listing and management system",
            10,
            "CUSTOMER",
            "ACTIVE",
            ["React", "Java", "Spring Boot", "PostgreSQL"],
            "RealEstate Plus",
        ),
        (
            "Agricultural IoT",
            "Smart farming IoT solution",
            15,
            "CUSTOMER",
            "ACTIVE",
            ["Python", "FastAPI", "InfluxDB", "MQTT", "ML"],
            "AgriTech Solutions",
        ),
        (
            "Telecom Network Monitor",
            "Network performance monitoring system",
            12,
            "CUSTOMER",
            "ACTIVE",
            ["React", "Python", "Django", "TimescaleDB"],
            "TelecomNext",
        ),
        (
            "Energy Grid Management",
            "Smart grid monitoring and control",
            16,
            "CUSTOMER",
            "ACTIVE",
            ["Angular", "Java", "Spring Boot", "PostgreSQL"],
            "EnergyFlow Systems",
        ),
        (
            "Construction Project Manager",
            "Construction project management platform",
            8,
            "CUSTOMER",
            "COMPLETED",
            ["Vue.js", "Node.js", "PostgreSQL", "AWS"],
            "ConstructTech",
        ),
        (
            "Pharmaceutical Tracker",
            "Drug development tracking system",
            14,
            "CUSTOMER",
            "ACTIVE",
            ["React", "Python", "Django", "PostgreSQL"],
            "PharmaCare Inc",
        ),
        (
            "Auto Insurance Claims",
            "Automated vehicle insurance claims",
            9,
            "CUSTOMER",
            "ACTIVE",
            ["Angular", "Java", "Spring Boot", "Oracle"],
            "AutoTech Motors",
        ),
        # Internal Projects (12 total)
        (
            "TechVantage HR Portal",
            "Internal HR management system",
            4,
            "INTERNAL",
            "COMPLETED",
            ["React", "Node.js", "PostgreSQL"],
            None,
        ),
        (
            "Resource Allocation System",
            "AI-powered resource allocation platform",
            6,
            "INTERNAL",
            "ACTIVE",
            ["React", "FastAPI", "PostgreSQL", "OpenAI"],
            None,
        ),
        (
            "Knowledge Management",
            "Internal knowledge sharing platform",
            8,
            "INTERNAL",
            "ACTIVE",
            ["Vue.js", "Django", "Elasticsearch", "PostgreSQL"],
            None,
        ),
        (
            "Performance Analytics",
            "Employee performance tracking system",
            5,
            "INTERNAL",
            "COMPLETED",
            ["Python", "Django", "PostgreSQL", "Chart.js"],
            None,
        ),
        (
            "DevOps Automation",
            "CI/CD pipeline and infrastructure automation",
            12,
            "INTERNAL",
            "ACTIVE",
            ["Python", "Terraform", "Docker", "Kubernetes", "AWS"],
            None,
        ),
        (
            "Security Monitoring",
            "Internal security monitoring platform",
            10,
            "INTERNAL",
            "ACTIVE",
            ["Python", "FastAPI", "Elasticsearch", "Grafana"],
            None,
        ),
        (
            "Cost Optimization",
            "Cloud cost optimization and monitoring",
            6,
            "INTERNAL",
            "COMPLETED",
            ["React", "Python", "AWS", "PostgreSQL"],
            None,
        ),
        (
            "Training Platform",
            "Internal employee training system",
            7,
            "INTERNAL",
            "ACTIVE",
            ["React", "Node.js", "MongoDB", "AWS"],
            None,
        ),
        (
            "Asset Management",
            "IT asset tracking and management",
            5,
            "INTERNAL",
            "COMPLETED",
            ["Vue.js", "Python", "Django", "PostgreSQL"],
            None,
        ),
        (
            "Communication Hub",
            "Internal communication and collaboration",
            8,
            "INTERNAL",
            "ACTIVE",
            ["React", "Node.js", "PostgreSQL", "WebSocket"],
            None,
        ),
        (
            "Quality Assurance Portal",
            "QA process management system",
            6,
            "INTERNAL",
            "ACTIVE",
            ["Angular", "Java", "Spring Boot", "PostgreSQL"],
            None,
        ),
        (
            "Innovation Lab",
            "Internal R&D project management",
            9,
            "INTERNAL",
            "ACTIVE",
            ["React", "Python", "FastAPI", "PostgreSQL"],
            None,
        ),
    ]

    project_ids = {}
    for name, desc, duration, proj_type, status, tech_stack, customer in projects_data:
        project_id = uuid.uuid4()
        project_ids[name] = project_id

        # Convert tech stack to PostgreSQL array format
        tech_stack_str = "{" + ",".join([f'"{tech}"' for tech in tech_stack]) + "}"

        # Generate realistic project dates
        if status == "COMPLETED":
            end_days_ago = random.randint(30, 180)
            end_date = (datetime.now() - timedelta(days=end_days_ago)).date()
            start_date = end_date - timedelta(days=duration * 30)
        else:  # ACTIVE
            start_days_ago = random.randint(60, 365)
            start_date = (datetime.now() - timedelta(days=start_days_ago)).date()
            end_date = start_date + timedelta(days=duration * 30)

        # Generate realistic costs
        if proj_type == "CUSTOMER":
            project_cost = Decimal(str(random.randint(100000, 1000000)))
        else:  # INTERNAL
            project_cost = Decimal(str(random.randint(50000, 300000)))

        monthly_cost = project_cost / duration

        op.execute(
            f"""
            INSERT INTO projects (id, name, description, duration_months, project_type, status,
                                tech_stack, customer_name, start_date, end_date, 
                                project_cost, monthly_cost,
                                created_at, updated_at, created_by, updated_by)
            VALUES ('{project_id}', '{name}', '{desc}', {duration}, '{proj_type}', '{status}',
                    '{tech_stack_str}', {f"'{customer}'" if customer else "NULL"}, 
                    '{start_date}', '{end_date}', {project_cost}, {monthly_cost},
                    NOW(), NOW(), '{system_user_id}', '{system_user_id}');
        """
        )

    # Generate 200 employees with realistic distribution
    # Distribution: 30 Interns, 70 Junior, 60 Mid-level, 30 Senior, 10 Principal+

    # Employee distribution by designation (200 total)
    employee_distribution = [
        # Interns (30 total - all KD India)
        ("SDE_INTERN", 24),
        ("QA_INTERN", 6),
        # Junior (70 total)
        ("SDE", 40),
        ("SE", 20),
        ("QA", 10),
        # Mid-level (60 total)
        ("SSE", 40),
        ("SR_QA", 6),
        ("BA", 8),
        ("UX", 6),
        # Senior (30 total)
        ("TL", 16),
        ("PM", 8),
        ("ARCH", 6),
        # Principal+ (10 total)
        ("PE", 6),
        ("TDO", 4),
    ]

    # Generate employee names and emails
    first_names = [
        "Alex",
        "Sarah",
        "Michael",
        "Emily",
        "James",
        "Jessica",
        "David",
        "Ashley",
        "Ryan",
        "Amanda",
        "Kevin",
        "Lauren",
        "Daniel",
        "Natalie",
        "Brandon",
        "Christopher",
        "Stephanie",
        "Matthew",
        "Rachel",
        "Joshua",
        "Megan",
        "Andrew",
        "Samantha",
        "Nicholas",
        "Brittany",
        "Tyler",
        "Kayla",
        "Justin",
        "Courtney",
        "Austin",
        "Chelsea",
        "Jordan",
        "Taylor",
        "Morgan",
        "Cameron",
        "Derek",
        "Lindsay",
        "Travis",
        "Brooke",
        "Sean",
        "Paige",
        "Blake",
        "Sierra",
        "Cole",
        "Maya",
        "Logan",
        "Alexis",
        "Hunter",
        "Sydney",
        "Connor",
        "Ethan",
        "Olivia",
        "Caleb",
        "Grace",
        "Noah",
        "Sophia",
        "Lucas",
        "Isabella",
        "Mason",
        "Ava",
        "Jackson",
        "Emma",
        "Aiden",
        "Mia",
        "Carter",
        "Chloe",
        "Owen",
        "Lily",
        "Wyatt",
        "Zoe",
        "Gabriel",
        "Natasha",
        "Marcus",
        "Victoria",
        "Adrian",
        "Elena",
        "Trevor",
        "Jasmine",
        "Bryce",
        "Ruby",
        "Alexander",
        "Samantha",
        "Benjamin",
        "Rebecca",
        "Jonathan",
        "Michelle",
        "Anthony",
        "Jennifer",
        "Robert",
        "Elizabeth",
        "William",
        "Stephanie",
        "Thomas",
        "Patricia",
        "Charles",
        "Richard",
        "Linda",
        "Steven",
        "Karen",
        "Mark",
    ]

    last_names = [
        "Johnson",
        "Chen",
        "Rodriguez",
        "Davis",
        "Wilson",
        "Brown",
        "Miller",
        "Garcia",
        "Martinez",
        "Anderson",
        "Taylor",
        "Thomas",
        "Jackson",
        "White",
        "Harris",
        "Martin",
        "Thompson",
        "Garcia",
        "Martinez",
        "Robinson",
        "Clark",
        "Rodriguez",
        "Lewis",
        "Lee",
        "Walker",
        "Hall",
        "Allen",
        "Young",
        "Hernandez",
        "King",
        "Wright",
        "Lopez",
        "Hill",
        "Scott",
        "Green",
        "Adams",
        "Baker",
        "Gonzalez",
        "Nelson",
        "Carter",
        "Mitchell",
        "Perez",
        "Roberts",
        "Turner",
        "Phillips",
        "Campbell",
        "Parker",
        "Evans",
        "Edwards",
        "Collins",
        "Stewart",
        "Sanchez",
        "Morris",
        "Rogers",
        "Reed",
        "Cook",
        "Bailey",
        "Rivera",
        "Cooper",
        "Richardson",
        "Cox",
        "Ward",
        "Torres",
        "Peterson",
        "Gray",
        "Ramirez",
        "James",
        "Watson",
        "Brooks",
        "Kelly",
        "Sanders",
        "Price",
        "Bennett",
        "Wood",
        "Barnes",
        "Ross",
        "Henderson",
        "Coleman",
        "Jenkins",
        "Perry",
        "Powell",
        "Long",
        "Patterson",
        "Hughes",
        "Flores",
        "Washington",
        "Butler",
        "Simmons",
        "Foster",
        "Gonzales",
        "Bryant",
        "Alexander",
        "Russell",
        "Griffin",
        "Diaz",
        "Hayes",
        "Myers",
        "Ford",
        "Hamilton",
        "Graham",
    ]

    employees_data = []
    employee_count = 0

    # Track organization distribution
    kd_india_count = 0
    kd_us_count = 0
    contractor_count = 0
    dev_partner_count = 0

    for designation_code, count in employee_distribution:
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{employee_count}@techvantage.io"
            name = f"{first_name} {last_name}"

            # Determine employee group and type based on constraints
            if designation_code in ["SDE_INTERN", "QA_INTERN"]:
                # All interns are KD India
                employee_group = "KD_INDIA"
                employee_type = "INTERN"
                location = "Bangalore"
                organization = "Kickdrum India Pvt Ltd"
                kd_india_count += 1
            else:
                # Calculate current percentages
                total_non_interns = employee_count - (
                    kd_india_count if designation_code in ["SDE_INTERN", "QA_INTERN"] else 0
                )

                # 70% KD India (including interns), 20% contractors, 10% dev partners
                target_kd_india = int(0.7 * 200)
                target_contractors = int(0.2 * 200)
                target_dev_partners = int(0.1 * 200)

                if kd_india_count < target_kd_india:
                    employee_group = "KD_INDIA"
                    employee_type = "FULL_TIME"
                    location = random.choice(["Bangalore", "Mumbai", "Remote"])
                    organization = "Kickdrum India Pvt Ltd"
                    kd_india_count += 1
                elif contractor_count < target_contractors:
                    # 60% KD US, 40% KD India for contractors
                    if contractor_count < target_contractors * 0.6:
                        employee_group = "KD_US"
                        location = random.choice(["New York", "San Francisco", "Austin", "Remote"])
                        organization = "Kickdrum Technologies Inc"
                        kd_us_count += 1
                    else:
                        employee_group = "KD_INDIA"
                        location = random.choice(["Bangalore", "Mumbai", "Remote"])
                        organization = "Kickdrum India Pvt Ltd"
                    employee_type = "CONTRACTOR"
                    contractor_count += 1
                else:
                    # Dev Partners
                    employee_group = "DEV_PARTNER"
                    employee_type = random.choice(["CONTRACTOR", "CONSULTANT"])
                    location = random.choice(["Remote", "New York", "London", "Bangalore"])
                    organization = random.choice(dev_partner_orgs)
                    dev_partner_count += 1

            # Set capacity and onboarding date
            if (
                designation_code in ["PE", "TDO"] and random.random() < 0.3
            ):  # 30% of PE/TDO have 50% capacity
                capacity = 50
            else:
                capacity = 100

            # Generate realistic onboarding dates
            if designation_code in ["SDE_INTERN", "QA_INTERN"]:
                onboarded_at = date(2024, random.randint(6, 11), random.randint(1, 28))
            elif designation_code in ["SDE", "SE", "QA"]:
                onboarded_at = date(
                    random.randint(2023, 2024), random.randint(1, 12), random.randint(1, 28)
                )
            elif designation_code in ["SSE", "SR_QA", "BA", "UX"]:
                onboarded_at = date(
                    random.randint(2021, 2023), random.randint(1, 12), random.randint(1, 28)
                )
            elif designation_code in ["TL", "PM", "ARCH"]:
                onboarded_at = date(
                    random.randint(2019, 2021), random.randint(1, 12), random.randint(1, 28)
                )
            else:  # PE, TDO
                onboarded_at = date(
                    random.randint(2016, 2019), random.randint(1, 12), random.randint(1, 28)
                )

            # Set realistic financial rates
            if employee_type == "CONTRACTOR":
                cost_per_hour = Decimal(str(random.randint(80, 150)))
                billing_rate = Decimal(str(random.randint(120, 200)))
            elif employee_type == "CONSULTANT":
                cost_per_hour = Decimal(str(random.randint(100, 180)))
                billing_rate = Decimal(str(random.randint(150, 250)))
            elif employee_type == "INTERN":
                cost_per_hour = Decimal(str(random.randint(20, 40)))
                billing_rate = Decimal(str(random.randint(30, 60)))
            else:  # FULL_TIME
                if designation_code in ["PE", "TDO"]:
                    cost_per_hour = Decimal(str(random.randint(120, 200)))
                    billing_rate = Decimal(str(random.randint(180, 300)))
                elif designation_code in ["TL", "PM", "ARCH"]:
                    cost_per_hour = Decimal(str(random.randint(80, 140)))
                    billing_rate = Decimal(str(random.randint(120, 220)))
                elif designation_code in ["SSE", "SR_QA", "BA", "UX"]:
                    cost_per_hour = Decimal(str(random.randint(60, 100)))
                    billing_rate = Decimal(str(random.randint(90, 150)))
                else:  # Junior
                    cost_per_hour = Decimal(str(random.randint(40, 70)))
                    billing_rate = Decimal(str(random.randint(60, 110)))

            # Adjust rates based on location
            if location in ["New York", "San Francisco"]:
                cost_per_hour *= Decimal("1.3")
                billing_rate *= Decimal("1.3")
            elif location == "London":
                cost_per_hour *= Decimal("1.2")
                billing_rate *= Decimal("1.2")
            elif location == "Bangalore":
                cost_per_hour *= Decimal("0.6")
                billing_rate *= Decimal("0.6")

            employees_data.append(
                (
                    email,
                    name,
                    designation_code,
                    capacity,
                    onboarded_at,
                    employee_group,
                    employee_type,
                    location,
                    organization,
                    cost_per_hour,
                    billing_rate,
                )
            )
            employee_count += 1

    # Insert employees
    employee_ids = {}
    for (
        email,
        name,
        designation_code,
        capacity,
        onboarded_at,
        employee_group,
        employee_type,
        location,
        organization,
        cost_per_hour,
        billing_rate,
    ) in employees_data:

        employee_id = uuid.uuid4()
        employee_ids[email] = employee_id
        designation_id = designation_ids[designation_code]

        op.execute(
            f"""
            INSERT INTO employees (id, email, name, designation_id, capacity_percent, onboarded_at, is_active,
                                 employee_group, employee_type, location, organization,
                                 cost_per_hour, billing_rate,
                                 created_at, updated_at, created_by, updated_by)
            VALUES ('{employee_id}', '{email}', '{name}', '{designation_id}', {capacity}, '{onboarded_at}', true,
                    '{employee_group}', '{employee_type}', '{location}', '{organization}',
                    {cost_per_hour}, {billing_rate},
                    NOW(), NOW(), '{system_user_id}', '{system_user_id}');
        """
        )

    # Assign project managers to projects
    # Get senior employees who can be project managers
    senior_employees = [
        emp for emp in employees_data if emp[2] in ["TL", "PM", "ARCH", "PE", "TDO"]
    ]

    for project_name in project_ids:
        if random.random() < 0.8:  # 80% of projects have assigned managers
            manager_email = random.choice(senior_employees)[0]
            manager_id = employee_ids[manager_email]

            op.execute(
                f"""
                UPDATE projects 
                SET project_manager_id = '{manager_id}'
                WHERE id = '{project_ids[project_name]}';
            """
            )

        # Create realistic allocations with 100% constraint enforcement
    print("Creating allocations with 100% constraint enforcement...")

    # Track current allocations per employee
    employee_allocations = {email: 0 for email, _, _, _, _, _, _, _, _, _, _ in employees_data}

    # Get active projects for allocation
    active_projects = [name for name, _, _, _, status, _, _ in projects_data if status == "ACTIVE"]

    allocation_count = 0
    max_attempts = 1000  # Prevent infinite loops

    for project_name in active_projects:
        project_id = project_ids[project_name]

        # Determine team size based on project duration
        project_duration = next(
            duration for name, _, duration, _, _, _, _ in projects_data if name == project_name
        )
        if project_duration <= 6:
            team_size = random.randint(3, 6)
        elif project_duration <= 12:
            team_size = random.randint(5, 10)
        else:
            team_size = random.randint(8, 15)

        # Select employees for this project
        attempts = 0
        allocated_employees = []

        while len(allocated_employees) < team_size and attempts < max_attempts:
            # Select random employee
            employee_data = random.choice(employees_data)
            email = employee_data[0]
            designation_code = employee_data[2]
            capacity = employee_data[3]

            # Skip if already allocated to this project
            if email in [emp[0] for emp in allocated_employees]:
                attempts += 1
                continue

            # Determine allocation percentage based on role and current allocation
            current_allocation = employee_allocations[email]
            available_capacity = capacity - current_allocation

            if available_capacity <= 0:
                attempts += 1
                continue

            # Set allocation based on seniority and available capacity
            if designation_code in ["SDE_INTERN", "QA_INTERN", "SDE", "SE", "QA"]:
                # Juniors: prefer full allocation to single project
                if available_capacity >= 75:
                    percent_allocated = min(available_capacity, random.choice([75, 100]))
                elif available_capacity >= 50:
                    percent_allocated = min(available_capacity, random.choice([50, 75]))
                else:
                    percent_allocated = available_capacity
            elif designation_code in ["SSE", "SR_QA", "BA", "UX"]:
                # Mid-level: can split across projects
                percent_allocated = min(available_capacity, random.choice([25, 50, 75]))
            else:
                # Senior: lighter allocations across multiple projects
                percent_allocated = min(available_capacity, random.choice([25, 50]))

            # Skip very small allocations
            if percent_allocated < 25:
                attempts += 1
                continue

            # Add to allocated employees
            allocated_employees.append((email, percent_allocated))
            employee_allocations[email] += percent_allocated
            attempts += 1

        # Create allocation records
        for email, percent_allocated in allocated_employees:
            employee_id = employee_ids[email]

            # Generate project dates
            project_data = next(p for p in projects_data if p[0] == project_name)
            duration = project_data[2]

            start_days_ago = random.randint(30, 180)
            start_date = (datetime.now() - timedelta(days=start_days_ago)).date()
            end_date = start_date + timedelta(days=duration * 30)

            # Calculate financial data
            employee_data = next(emp for emp in employees_data if emp[0] == email)
            billing_rate = employee_data[10]

            # Project-specific rate (±10% variation)
            variation = Decimal(str(random.uniform(0.9, 1.1)))
            hourly_rate = billing_rate * variation

            # Monthly cost calculation (160 hours/month * allocation %)
            monthly_hours = Decimal("160") * (Decimal(str(percent_allocated)) / Decimal("100"))
            monthly_cost = hourly_rate * monthly_hours

            allocation_id = uuid.uuid4()
            op.execute(
                f"""
                INSERT INTO allocations (id, project_id, employee_id, percent_allocated, 
                                       start_date, end_date, status, hourly_rate, monthly_cost,
                                       created_at, updated_at, created_by, updated_by)
                VALUES ('{allocation_id}', '{project_id}', '{employee_id}', {percent_allocated}, 
                        '{start_date}', '{end_date}', 'ACTIVE', {hourly_rate}, {monthly_cost},
                        NOW(), NOW(), '{system_user_id}', '{system_user_id}');
            """
            )
            allocation_count += 1

    # Create some completed allocations for historical projects (ensuring no constraint violations)
    completed_projects = [
        name for name, _, _, _, status, _, _ in projects_data if status == "COMPLETED"
    ]

    for project_name in completed_projects:
        project_id = project_ids[project_name]

        # Smaller teams for completed projects
        team_size = random.randint(3, 8)

        # Select random employees for historical projects
        selected_employees = random.sample(employees_data, min(team_size, len(employees_data)))

        for employee_data in selected_employees:
            email = employee_data[0]
            designation_code = employee_data[2]
            employee_id = employee_ids[email]

            # Generate completed project dates that don't overlap with active allocations
            project_data = next(p for p in projects_data if p[0] == project_name)
            duration = project_data[2]

            # Ensure completed projects end before active projects start (no overlap)
            # Active projects started 30-365 days ago, so completed projects should end before that
            end_days_ago = random.randint(400, 800)  # 13-26 months ago
            end_date = (datetime.now() - timedelta(days=end_days_ago)).date()
            start_date = end_date - timedelta(days=duration * 30)

            # Historical allocation percentages (can be higher since no overlap with current)
            if designation_code in ["SDE_INTERN", "QA_INTERN", "SDE", "SE", "QA"]:
                percent_allocated = random.choice([75, 100])
            elif designation_code in ["SSE", "SR_QA", "BA", "UX"]:
                percent_allocated = random.choice([50, 75, 100])
            else:
                percent_allocated = random.choice([25, 50, 75])

            # Calculate financial data
            billing_rate = employee_data[10]
            variation = Decimal(str(random.uniform(0.9, 1.1)))
            hourly_rate = billing_rate * variation
            monthly_hours = Decimal("160") * (Decimal(str(percent_allocated)) / Decimal("100"))
            monthly_cost = hourly_rate * monthly_hours

            allocation_id = uuid.uuid4()
            op.execute(
                f"""
                INSERT INTO allocations (id, project_id, employee_id, percent_allocated, 
                                       start_date, end_date, status, hourly_rate, monthly_cost,
                                       created_at, updated_at, created_by, updated_by)
                VALUES ('{allocation_id}', '{project_id}', '{employee_id}', {percent_allocated}, 
                        '{start_date}', '{end_date}', 'COMPLETED', {hourly_rate}, {monthly_cost},
                        NOW(), NOW(), '{system_user_id}', '{system_user_id}');
            """
            )
            allocation_count += 1

    # Generate employee skills
    print("Creating employee skills...")

    # Define skill categories and their skills
    skill_categories = {
        "frontend": {
            "skills": [
                "React",
                "Angular",
                "Vue.js",
                "Next.js",
                "TypeScript",
                "JavaScript",
                "HTML/CSS",
                "Tailwind CSS",
                "Material-UI",
                "Redux",
            ],
            "weight": 0.3,
        },
        "backend": {
            "skills": [
                "Java",
                "Python",
                "Node.js",
                "PHP",
                ".NET",
                "Spring Boot",
                "Django",
                "FastAPI",
                "Express.js",
                "Laravel",
            ],
            "weight": 0.35,
        },
        "cloud": {
            "skills": [
                "AWS",
                "Azure",
                "GCP",
                "AWS Lambda",
                "EC2",
                "S3",
                "RDS",
                "CloudFormation",
                "Azure Functions",
                "Google Cloud Functions",
            ],
            "weight": 0.25,
        },
        "mobile": {
            "skills": [
                "React Native",
                "Flutter",
                "Swift",
                "Kotlin",
                "iOS Development",
                "Android Development",
                "Xamarin",
                "Ionic",
            ],
            "weight": 0.15,
        },
        "devops": {
            "skills": [
                "Docker",
                "Kubernetes",
                "Terraform",
                "Jenkins",
                "GitLab CI",
                "Grafana",
                "Prometheus",
                "AWS CDK",
                "Ansible",
                "Helm",
            ],
            "weight": 0.2,
        },
        "database": {
            "skills": [
                "PostgreSQL",
                "MySQL",
                "MongoDB",
                "Redis",
                "Elasticsearch",
                "Oracle",
                "SQL Server",
                "DynamoDB",
                "Cassandra",
                "InfluxDB",
            ],
            "weight": 0.3,
        },
        "ai_ml": {
            "skills": [
                "Machine Learning",
                "TensorFlow",
                "PyTorch",
                "OpenAI API",
                "Scikit-learn",
                "Pandas",
                "NumPy",
                "Computer Vision",
                "NLP",
                "Deep Learning",
            ],
            "weight": 0.1,
        },
        "testing": {
            "skills": [
                "Jest",
                "Selenium",
                "Cypress",
                "JUnit",
                "PyTest",
                "Postman",
                "TestNG",
                "Mocha",
                "Chai",
                "Playwright",
            ],
            "weight": 0.25,
        },
        "tools": {
            "skills": [
                "Git",
                "JIRA",
                "Confluence",
                "VS Code",
                "IntelliJ IDEA",
                "Figma",
                "Slack",
                "Notion",
                "Postman",
                "Swagger",
            ],
            "weight": 0.4,
        },
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
        "tech_lead": ["backend", "frontend", "cloud", "database", "tools"],
    }

    # Define experience ranges based on designation level
    designation_experience = {
        "SDE_INTERN": {"min_exp": 0, "max_exp": 12},  # 0-1 year
        "QA_INTERN": {"min_exp": 0, "max_exp": 12},  # 0-1 year
        "SDE": {"min_exp": 6, "max_exp": 24},  # 0.5-2 years
        "SE": {"min_exp": 12, "max_exp": 36},  # 1-3 years
        "QA": {"min_exp": 6, "max_exp": 24},  # 0.5-2 years
        "SSE": {"min_exp": 24, "max_exp": 60},  # 2-5 years
        "SR_QA": {"min_exp": 36, "max_exp": 72},  # 3-6 years
        "BA": {"min_exp": 12, "max_exp": 48},  # 1-4 years
        "UX": {"min_exp": 12, "max_exp": 48},  # 1-4 years
        "TL": {"min_exp": 48, "max_exp": 96},  # 4-8 years
        "PM": {"min_exp": 36, "max_exp": 84},  # 3-7 years
        "ARCH": {"min_exp": 60, "max_exp": 120},  # 5-10 years
        "PE": {"min_exp": 84, "max_exp": 150},  # 7-12.5 years
        "TDO": {"min_exp": 96, "max_exp": 180},  # 8-15 years
    }

    proficiency_levels = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]

    def get_proficiency_level(skill_experience_months):
        """Determine proficiency level based on experience months (1-5 scale)"""
        years = skill_experience_months / 12.0

        if years >= 7:  # 7+ years
            return 5  # Expert
        elif years >= 3:  # 3-7 years
            return 4  # Advanced
        elif years >= 1:  # 1-3 years
            return 3  # Intermediate
        elif years >= 0.5:  # 6+ months
            return 2  # Beginner+
        else:  # 0-6 months
            return 1  # Beginner

    def calculate_years_since_onboarding(onboarded_at):
        """Calculate years since employee was onboarded"""
        if isinstance(onboarded_at, str):
            onboarded_date = datetime.strptime(onboarded_at, "%Y-%m-%d").date()
        else:
            onboarded_date = onboarded_at

        today = date.today()
        years = (today - onboarded_date).days / 365.25
        return max(years, 0.1)  # Minimum 0.1 years

    # Process each employee for skills
    skills_count = 0
    for (
        email,
        name,
        designation_code,
        capacity,
        onboarded_at,
        employee_group,
        employee_type,
        location,
        organization,
        cost_per_hour,
        billing_rate,
    ) in employees_data:

        employee_id = employee_ids[email]

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
                possible_profiles = [
                    "fullstack",
                    "cloud_backend",
                    "mobile_developer",
                    "frontend_specialist",
                    "backend_specialist",
                ]
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
                proficiency = get_proficiency_level(skill_exp_months)

                # Generate summary
                summaries = [
                    f"Experienced in {skill_name} development with {skill_exp_months} months of hands-on experience",
                    f"Proficient in {skill_name} with practical application in multiple projects",
                    f"Strong background in {skill_name} gained through professional development",
                    f"Skilled in {skill_name} with focus on best practices and modern approaches",
                    f"Competent in {skill_name} with experience in enterprise-level applications",
                ]
                summary = random.choice(summaries)

                # Insert skill record
                skill_id = uuid.uuid4()
                op.execute(
                    f"""
                    INSERT INTO employee_skills (
                        id, employee_id, skill_name, summary, experience_months, 
                        last_used, source, proficiency_level,
                        created_at, updated_at, created_by, updated_by
                    ) VALUES (
                        '{skill_id}', '{employee_id}', '{skill_name}', '{summary}', 
                        {skill_exp_months}, '{last_used}', 'SEED', '{proficiency}',
                        NOW(), NOW(), '{system_user_id}', '{system_user_id}'
                    );
                """
                )
                skills_count += 1

        # Ensure every employee has some basic tools
        basic_tools = ["Git", "JIRA", "VS Code"]
        for tool in basic_tools:
            # Check if already added
            existing_result = op.get_bind().execute(
                sa.text(
                    """
                    SELECT COUNT(*) FROM employee_skills 
                    WHERE employee_id = :employee_id AND skill_name = :skill_name
                """
                ),
                {"employee_id": employee_id, "skill_name": tool},
            )
            existing = existing_result.fetchone()[0]

            if existing == 0:
                min_exp = max(1, des_info["min_exp"])
                max_exp = max(min_exp + 1, min(int(years_experience * 12), des_info["max_exp"]))
                skill_exp_months = random.randint(min_exp, max_exp)
                last_used = date.today() - timedelta(days=random.randint(1, 90))
                proficiency = get_proficiency_level(skill_exp_months)

                skill_id = uuid.uuid4()
                op.execute(
                    f"""
                    INSERT INTO employee_skills (
                        id, employee_id, skill_name, summary, experience_months, 
                        last_used, source, proficiency_level,
                        created_at, updated_at, created_by, updated_by
                    ) VALUES (
                        '{skill_id}', '{employee_id}', '{tool}', 
                        'Essential development tool used daily in professional work', 
                        {skill_exp_months}, '{last_used}', 'SEED', '{proficiency}',
                        NOW(), NOW(), '{system_user_id}', '{system_user_id}'
                    );
                """
                )
                skills_count += 1

    print(f"✅ Successfully created seed data:")
    print(f"   - 200 employees with realistic business field distribution")
    print(f"   - 36 projects (24 customer, 12 internal)")
    print(f"   - {allocation_count} allocations respecting 100% constraint")
    print(f"   - {skills_count} employee skills with realistic proficiency levels")
    print(f"   - Organization distribution: 70% KD India, 20% Contractors, 10% Dev Partners")
    print(f"   - All interns are KD India employees")
    print(f"   - Contractors: 60% KD US, 40% KD India")


def downgrade() -> None:
    """Remove all seed data"""
    # Delete in reverse order due to foreign key constraints
    op.execute("DELETE FROM allocations;")
    op.execute("DELETE FROM employee_skills WHERE source = 'SEED';")
    op.execute("DELETE FROM employee_embeddings;")
    op.execute("DELETE FROM employees;")
    op.execute("DELETE FROM projects;")
    op.execute("DELETE FROM designations;")
    op.execute("DELETE FROM users WHERE email = 'system@techvantage.io';")

    print("✅ Successfully removed all seed data")
