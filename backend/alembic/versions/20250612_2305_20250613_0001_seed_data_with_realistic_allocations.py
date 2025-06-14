"""seed data with realistic allocations

Revision ID: 34a648ecedae
Revises: 4c3b1d2fdf93
Create Date: 2025-01-12 23:05:12.345678

"""

import uuid
from datetime import date, datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20250613_0001"
down_revision: Union[str, None] = "34a648ecedae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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

    # Insert designations with DateTime audit fields
    designations_data = [
        # Interns (Level 0)
        ("SDE_INTERN", "Software Development Engineer Intern", "SDE Intern", 0, False),
        ("QA_INTERN", "Quality Assurance Intern", "QA Intern", 0, False),
        # Junior (Level 1-2)
        ("SDE", "Software Development Engineer", "SDE", 1, False),
        ("SE", "Software Engineer", "SE", 2, False),
        ("QA", "Quality Assurance Engineer", "QA", 1, False),
        # Mid-level (Level 3-4)
        ("SSE", "Senior Software Engineer", "SSE", 3, False),
        ("SR_QA", "Senior Quality Assurance Engineer", "Sr. QA", 4, False),
        ("BA", "Business Analyst", "BA", 2, False),
        ("UX", "UX Designer", "UX", 2, False),
        # Senior (Level 5-6)
        ("TL", "Technical Lead", "TL", 5, True),
        ("PM", "Project Manager", "PM", 4, True),
        ("ARCH", "Software Architect", "Architect", 6, True),
        # Principal+ (Level 7+)
        ("PE", "Principal Software Engineer", "Principal Engineer", 8, True),
        ("TDO", "Technical Delivery Officer", "TDO", 10, True),
    ]

    designation_ids = {}
    for code, title, desc, level, is_leadership in designations_data:
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

    # Insert projects with DateTime audit fields and Date business dates
    projects_data = [
        # Customer Projects
        (
            "E-Commerce Platform Modernization",
            "Legacy system migration to microservices",
            8,
            "CUSTOMER",
            "COMPLETED",
            ["React", "Node.js", "PostgreSQL", "Docker", "AWS"],
            ["TL", "SSE", "SDE", "QA"],
            ["React", "Node.js", "PostgreSQL", "Microservices"],
            "2024-04-01",
            "2024-11-30",
        ),
        (
            "Mobile Banking App",
            "iOS and Android banking application",
            12,
            "CUSTOMER",
            "ACTIVE",
            ["React Native", "Node.js", "MongoDB", "AWS"],
            ["TL", "SSE", "SDE", "UX"],
            ["React Native", "Mobile Development", "Banking Domain"],
            "2024-06-15",
            "2025-06-14",
        ),
        (
            "Healthcare Management System",
            "Patient management and scheduling system",
            10,
            "CUSTOMER",
            "ACTIVE",
            ["Angular", "Java", "Spring Boot", "PostgreSQL"],
            ["TL", "SSE", "SDE", "BA", "QA"],
            ["Angular", "Java", "Spring Boot", "Healthcare Domain"],
            "2024-08-01",
            "2025-05-31",
        ),
        (
            "Supply Chain Analytics",
            "Real-time supply chain monitoring dashboard",
            6,
            "CUSTOMER",
            "COMPLETED",
            ["Python", "Django", "PostgreSQL", "Redis", "Celery"],
            ["TL", "SSE", "SDE"],
            ["Python", "Django", "Analytics", "Supply Chain"],
            "2024-05-01",
            "2024-10-31",
        ),
        (
            "Insurance Claims Processing",
            "Automated claims processing system",
            14,
            "CUSTOMER",
            "ACTIVE",
            ["Java", "Spring Boot", "Oracle", "Kafka", "Docker"],
            ["ARCH", "TL", "SSE", "SDE", "QA"],
            ["Java", "Spring Boot", "Insurance Domain", "Kafka"],
            "2024-09-01",
            "2025-10-31",
        ),
        (
            "Retail POS System",
            "Point of sale system for retail chains",
            8,
            "CUSTOMER",
            "ACTIVE",
            ["Vue.js", "Python", "FastAPI", "PostgreSQL"],
            ["TL", "SSE", "SDE", "QA"],
            ["Vue.js", "Python", "FastAPI", "Retail Domain"],
            "2024-10-01",
            "2025-05-31",
        ),
        (
            "Financial Trading Platform",
            "High-frequency trading platform",
            18,
            "CUSTOMER",
            "ACTIVE",
            ["C++", "Python", "Redis", "PostgreSQL", "Kafka"],
            ["ARCH", "PE", "TL", "SSE"],
            ["C++", "Python", "Trading Systems", "Low Latency"],
            "2024-07-01",
            "2026-01-31",
        ),
        (
            "EdTech Learning Platform",
            "Online learning management system",
            10,
            "CUSTOMER",
            "COMPLETED",
            ["React", "Node.js", "MongoDB", "AWS", "Docker"],
            ["TL", "SSE", "SDE", "UX", "QA"],
            ["React", "Node.js", "MongoDB", "EdTech Domain"],
            "2024-03-01",
            "2024-12-31",
        ),
        (
            "Logistics Optimization",
            "Route optimization for delivery services",
            12,
            "CUSTOMER",
            "ACTIVE",
            ["Python", "Django", "PostgreSQL", "Redis", "ML"],
            ["TL", "SSE", "SDE", "BA"],
            ["Python", "Django", "Machine Learning", "Logistics"],
            "2024-11-01",
            "2025-10-31",
        ),
        (
            "CRM Enhancement",
            "Customer relationship management system upgrade",
            6,
            "CUSTOMER",
            "COMPLETED",
            ["Salesforce", "Apex", "Lightning", "JavaScript"],
            ["TL", "SDE", "BA"],
            ["Salesforce", "Apex", "Lightning", "CRM"],
            "2024-06-01",
            "2024-11-30",
        ),
        (
            "IoT Device Management",
            "Industrial IoT device monitoring platform",
            14,
            "CUSTOMER",
            "ACTIVE",
            ["Python", "FastAPI", "InfluxDB", "Grafana", "MQTT"],
            ["ARCH", "TL", "SSE", "SDE"],
            ["Python", "FastAPI", "IoT", "Time Series DB"],
            "2024-12-01",
            "2026-01-31",
        ),
        (
            "Blockchain Wallet",
            "Cryptocurrency wallet application",
            16,
            "CUSTOMER",
            "ACTIVE",
            ["React", "Node.js", "Solidity", "Web3", "PostgreSQL"],
            ["ARCH", "TL", "SSE", "SDE"],
            ["React", "Node.js", "Blockchain", "Solidity"],
            "2024-08-15",
            "2025-12-14",
        ),
        (
            "Video Streaming Platform",
            "Live video streaming and VOD platform",
            20,
            "CUSTOMER",
            "ACTIVE",
            ["React", "Node.js", "FFmpeg", "AWS", "CDN"],
            ["ARCH", "TL", "SSE", "SDE", "QA"],
            ["React", "Node.js", "Video Processing", "CDN"],
            "2024-09-15",
            "2026-05-14",
        ),
        # Internal Projects
        (
            "TechVantage HR Portal",
            "Internal HR management system",
            4,
            "INTERNAL",
            "COMPLETED",
            ["React", "Node.js", "PostgreSQL"],
            ["TL", "SDE", "UX"],
            ["React", "Node.js", "PostgreSQL"],
            "2024-04-15",
            "2024-08-14",
        ),
        (
            "Resource Allocation System",
            "AI-powered resource allocation platform",
            6,
            "INTERNAL",
            "ACTIVE",
            ["React", "FastAPI", "PostgreSQL", "OpenAI"],
            ["TL", "SSE", "SDE"],
            ["React", "FastAPI", "PostgreSQL", "AI"],
            "2024-11-01",
            "2025-04-30",
        ),
        (
            "Knowledge Management",
            "Internal knowledge sharing platform",
            8,
            "INTERNAL",
            "ACTIVE",
            ["Vue.js", "Django", "Elasticsearch", "PostgreSQL"],
            ["TL", "SSE", "SDE"],
            ["Vue.js", "Django", "Elasticsearch"],
            "2024-10-01",
            "2025-05-31",
        ),
        (
            "Performance Analytics",
            "Employee performance tracking system",
            5,
            "INTERNAL",
            "COMPLETED",
            ["Python", "Django", "PostgreSQL", "Chart.js"],
            ["TL", "SDE", "BA"],
            ["Python", "Django", "PostgreSQL"],
            "2024-05-01",
            "2024-09-30",
        ),
        (
            "DevOps Automation",
            "CI/CD pipeline and infrastructure automation",
            12,
            "INTERNAL",
            "ACTIVE",
            ["Python", "Terraform", "Docker", "Kubernetes", "AWS"],
            ["ARCH", "TL", "SSE"],
            ["Python", "Terraform", "Docker", "Kubernetes"],
            "2024-07-01",
            "2025-06-30",
        ),
    ]

    project_ids = {}
    for i, (
        name,
        desc,
        duration,
        proj_type,
        status,
        tech_stack,
        req_roles,
        req_skills,
        start_str,
        end_str,
    ) in enumerate(projects_data):
        project_id = uuid.uuid4()
        project_ids[name] = project_id

        # Convert string arrays to PostgreSQL array format
        tech_stack_str = "{" + ",".join([f'"{tech}"' for tech in tech_stack]) + "}"
        req_roles_str = "{" + ",".join([f'"{role}"' for role in req_roles]) + "}"
        req_skills_str = "{" + ",".join([f'"{skill}"' for skill in req_skills]) + "}"

        op.execute(
            f"""
            INSERT INTO projects (id, name, description, duration_months, project_type, status,
                                tech_stack, required_roles, required_skills,
                                created_at, updated_at, created_by, updated_by)
            VALUES ('{project_id}', '{name}', '{desc}', {duration}, '{proj_type}', '{status}',
                    '{tech_stack_str}', '{req_roles_str}', '{req_skills_str}',
                    NOW(), NOW(), '{system_user_id}', '{system_user_id}');
        """
        )

    # Insert employees with DateTime audit fields and Date business dates
    employees_data = [
        # Interns (15 total: 12 SDE, 3 QA)
        ("alex.johnson@techvantage.io", "Alex Johnson", "SDE_INTERN", 100, "2024-06-01"),
        ("sarah.chen@techvantage.io", "Sarah Chen", "SDE_INTERN", 100, "2024-06-01"),
        ("michael.rodriguez@techvantage.io", "Michael Rodriguez", "SDE_INTERN", 100, "2024-06-15"),
        ("emily.davis@techvantage.io", "Emily Davis", "SDE_INTERN", 100, "2024-07-01"),
        ("james.wilson@techvantage.io", "James Wilson", "SDE_INTERN", 100, "2024-07-01"),
        ("jessica.brown@techvantage.io", "Jessica Brown", "SDE_INTERN", 100, "2024-07-15"),
        ("david.miller@techvantage.io", "David Miller", "SDE_INTERN", 100, "2024-08-01"),
        ("ashley.garcia@techvantage.io", "Ashley Garcia", "SDE_INTERN", 100, "2024-08-01"),
        ("ryan.martinez@techvantage.io", "Ryan Martinez", "SDE_INTERN", 100, "2024-08-15"),
        ("amanda.anderson@techvantage.io", "Amanda Anderson", "SDE_INTERN", 100, "2024-09-01"),
        ("kevin.taylor@techvantage.io", "Kevin Taylor", "SDE_INTERN", 100, "2024-09-01"),
        ("lauren.thomas@techvantage.io", "Lauren Thomas", "SDE_INTERN", 100, "2024-09-15"),
        ("daniel.jackson@techvantage.io", "Daniel Jackson", "QA_INTERN", 100, "2024-06-15"),
        ("natalie.white@techvantage.io", "Natalie White", "QA_INTERN", 100, "2024-07-15"),
        ("brandon.harris@techvantage.io", "Brandon Harris", "QA_INTERN", 100, "2024-08-15"),
        # Junior Level (35 total: 20 SDE, 10 SE, 5 QA)
        ("christopher.martin@techvantage.io", "Christopher Martin", "SDE", 100, "2023-08-01"),
        ("stephanie.thompson@techvantage.io", "Stephanie Thompson", "SDE", 100, "2023-09-01"),
        ("matthew.garcia@techvantage.io", "Matthew Garcia", "SDE", 100, "2023-10-01"),
        ("rachel.martinez@techvantage.io", "Rachel Martinez", "SDE", 100, "2023-11-01"),
        ("joshua.robinson@techvantage.io", "Joshua Robinson", "SDE", 100, "2023-12-01"),
        ("megan.clark@techvantage.io", "Megan Clark", "SDE", 100, "2024-01-01"),
        ("andrew.rodriguez@techvantage.io", "Andrew Rodriguez", "SDE", 100, "2024-02-01"),
        ("samantha.lewis@techvantage.io", "Samantha Lewis", "SDE", 100, "2024-03-01"),
        ("nicholas.lee@techvantage.io", "Nicholas Lee", "SDE", 100, "2024-04-01"),
        ("brittany.walker@techvantage.io", "Brittany Walker", "SDE", 100, "2024-05-01"),
        ("tyler.hall@techvantage.io", "Tyler Hall", "SDE", 100, "2024-06-01"),
        ("kayla.allen@techvantage.io", "Kayla Allen", "SDE", 100, "2024-07-01"),
        ("justin.young@techvantage.io", "Justin Young", "SDE", 100, "2024-08-01"),
        ("courtney.hernandez@techvantage.io", "Courtney Hernandez", "SDE", 100, "2024-09-01"),
        ("austin.king@techvantage.io", "Austin King", "SDE", 100, "2024-10-01"),
        ("chelsea.wright@techvantage.io", "Chelsea Wright", "SDE", 100, "2024-11-01"),
        ("jordan.lopez@techvantage.io", "Jordan Lopez", "SDE", 100, "2023-07-01"),
        ("taylor.hill@techvantage.io", "Taylor Hill", "SDE", 100, "2023-06-01"),
        ("morgan.scott@techvantage.io", "Morgan Scott", "SDE", 100, "2023-05-01"),
        ("cameron.green@techvantage.io", "Cameron Green", "SDE", 100, "2023-04-01"),
        ("derek.adams@techvantage.io", "Derek Adams", "SE", 100, "2022-08-01"),
        ("lindsay.baker@techvantage.io", "Lindsay Baker", "SE", 100, "2022-09-01"),
        ("travis.gonzalez@techvantage.io", "Travis Gonzalez", "SE", 100, "2022-10-01"),
        ("brooke.nelson@techvantage.io", "Brooke Nelson", "SE", 100, "2022-11-01"),
        ("sean.carter@techvantage.io", "Sean Carter", "SE", 100, "2022-12-01"),
        ("paige.mitchell@techvantage.io", "Paige Mitchell", "SE", 100, "2023-01-01"),
        ("blake.perez@techvantage.io", "Blake Perez", "SE", 100, "2023-02-01"),
        ("sierra.roberts@techvantage.io", "Sierra Roberts", "SE", 100, "2023-03-01"),
        ("cole.turner@techvantage.io", "Cole Turner", "SE", 100, "2023-04-01"),
        ("maya.phillips@techvantage.io", "Maya Phillips", "SE", 100, "2023-05-01"),
        ("logan.campbell@techvantage.io", "Logan Campbell", "QA", 100, "2023-06-01"),
        ("alexis.parker@techvantage.io", "Alexis Parker", "QA", 100, "2023-07-01"),
        ("hunter.evans@techvantage.io", "Hunter Evans", "QA", 100, "2023-08-01"),
        ("sydney.edwards@techvantage.io", "Sydney Edwards", "QA", 100, "2023-09-01"),
        ("connor.collins@techvantage.io", "Connor Collins", "QA", 100, "2023-10-01"),
        # Mid-level (30 total: 20 SSE, 3 Sr. QA, 4 BA, 3 UX)
        ("ethan.stewart@techvantage.io", "Ethan Stewart", "SSE", 100, "2021-01-01"),
        ("olivia.sanchez@techvantage.io", "Olivia Sanchez", "SSE", 100, "2021-02-01"),
        ("caleb.morris@techvantage.io", "Caleb Morris", "SSE", 100, "2021-03-01"),
        ("grace.rogers@techvantage.io", "Grace Rogers", "SSE", 100, "2021-04-01"),
        ("noah.reed@techvantage.io", "Noah Reed", "SSE", 100, "2021-05-01"),
        ("sophia.cook@techvantage.io", "Sophia Cook", "SSE", 100, "2021-06-01"),
        ("lucas.bailey@techvantage.io", "Lucas Bailey", "SSE", 100, "2021-07-01"),
        ("isabella.rivera@techvantage.io", "Isabella Rivera", "SSE", 100, "2021-08-01"),
        ("mason.cooper@techvantage.io", "Mason Cooper", "SSE", 100, "2021-09-01"),
        ("ava.richardson@techvantage.io", "Ava Richardson", "SSE", 100, "2021-10-01"),
        ("jackson.cox@techvantage.io", "Jackson Cox", "SSE", 100, "2021-11-01"),
        ("emma.ward@techvantage.io", "Emma Ward", "SSE", 100, "2021-12-01"),
        ("aiden.torres@techvantage.io", "Aiden Torres", "SSE", 100, "2022-01-01"),
        ("mia.peterson@techvantage.io", "Mia Peterson", "SSE", 100, "2022-02-01"),
        ("carter.gray@techvantage.io", "Carter Gray", "SSE", 100, "2022-03-01"),
        ("chloe.ramirez@techvantage.io", "Chloe Ramirez", "SSE", 100, "2022-04-01"),
        ("owen.james@techvantage.io", "Owen James", "SSE", 100, "2022-05-01"),
        ("lily.watson@techvantage.io", "Lily Watson", "SSE", 100, "2022-06-01"),
        ("wyatt.brooks@techvantage.io", "Wyatt Brooks", "SSE", 100, "2022-07-01"),
        ("zoe.kelly@techvantage.io", "Zoe Kelly", "SSE", 100, "2022-08-01"),
        ("gabriel.sanders@techvantage.io", "Gabriel Sanders", "SR_QA", 100, "2020-06-01"),
        ("natasha.price@techvantage.io", "Natasha Price", "SR_QA", 100, "2020-08-01"),
        ("marcus.bennett@techvantage.io", "Marcus Bennett", "SR_QA", 100, "2020-10-01"),
        ("victoria.wood@techvantage.io", "Victoria Wood", "BA", 100, "2022-01-01"),
        ("adrian.barnes@techvantage.io", "Adrian Barnes", "BA", 100, "2022-03-01"),
        ("elena.ross@techvantage.io", "Elena Ross", "BA", 100, "2022-05-01"),
        ("trevor.henderson@techvantage.io", "Trevor Henderson", "BA", 100, "2022-07-01"),
        ("jasmine.coleman@techvantage.io", "Jasmine Coleman", "UX", 100, "2022-02-01"),
        ("bryce.jenkins@techvantage.io", "Bryce Jenkins", "UX", 100, "2022-04-01"),
        ("ruby.perry@techvantage.io", "Ruby Perry", "UX", 100, "2022-06-01"),
        # Senior Level (15 total: 8 TL, 4 PM, 3 Architect)
        ("alexander.powell@techvantage.io", "Alexander Powell", "TL", 100, "2019-01-01"),
        ("samantha.long@techvantage.io", "Samantha Long", "TL", 100, "2019-03-01"),
        ("benjamin.patterson@techvantage.io", "Benjamin Patterson", "TL", 100, "2019-05-01"),
        ("rebecca.hughes@techvantage.io", "Rebecca Hughes", "TL", 100, "2019-07-01"),
        ("jonathan.flores@techvantage.io", "Jonathan Flores", "TL", 100, "2019-09-01"),
        ("michelle.washington@techvantage.io", "Michelle Washington", "TL", 100, "2019-11-01"),
        ("anthony.butler@techvantage.io", "Anthony Butler", "TL", 100, "2020-01-01"),
        ("jennifer.simmons@techvantage.io", "Jennifer Simmons", "TL", 100, "2020-03-01"),
        ("robert.foster@techvantage.io", "Robert Foster", "PM", 100, "2020-01-01"),
        ("elizabeth.gonzales@techvantage.io", "Elizabeth Gonzales", "PM", 100, "2020-04-01"),
        ("william.bryant@techvantage.io", "William Bryant", "PM", 100, "2020-07-01"),
        ("stephanie.alexander@techvantage.io", "Stephanie Alexander", "PM", 100, "2020-10-01"),
        ("thomas.russell@techvantage.io", "Thomas Russell", "ARCH", 100, "2018-01-01"),
        ("patricia.griffin@techvantage.io", "Patricia Griffin", "ARCH", 100, "2018-06-01"),
        ("charles.diaz@techvantage.io", "Charles Diaz", "ARCH", 100, "2019-01-01"),
        # Principal+ Level (5 total: 3 PE, 2 TDO) - 2 get 50% capacity
        ("richard.hayes@techvantage.io", "Richard Hayes", "PE", 100, "2017-01-01"),
        ("linda.myers@techvantage.io", "Linda Myers", "PE", 50, "2017-06-01"),  # 50% capacity
        ("steven.ford@techvantage.io", "Steven Ford", "PE", 100, "2018-01-01"),
        (
            "karen.hamilton@techvantage.io",
            "Karen Hamilton",
            "TDO",
            50,
            "2016-01-01",
        ),  # 50% capacity
        ("mark.graham@techvantage.io", "Mark Graham", "TDO", 100, "2016-06-01"),
    ]

    employee_ids = {}
    for email, name, designation_code, capacity, onboarded_str in employees_data:
        employee_id = uuid.uuid4()
        employee_ids[email] = employee_id
        designation_id = designation_ids[designation_code]

        op.execute(
            f"""
            INSERT INTO employees (id, email, name, designation_id, capacity_percent, onboarded_at, is_active,
                                 created_at, updated_at, created_by, updated_by)
            VALUES ('{employee_id}', '{email}', '{name}', '{designation_id}', {capacity}, '{onboarded_str}', true,
                    NOW(), NOW(), '{system_user_id}', '{system_user_id}');
        """
        )

    # Create realistic allocations
    import random
    from datetime import timedelta

    # Categorize employees by level for allocation logic
    junior_employees = []
    mid_employees = []
    senior_employees = []
    excluded_senior = None  # One 50% capacity senior remains unallocated

    pe_tdo_50_capacity_count = 0
    for email, name, designation_code, capacity, onboarded_str in employees_data:
        if designation_code in ["SDE_INTERN", "QA_INTERN", "SDE", "SE", "QA"]:
            junior_employees.append(email)
        elif designation_code in ["SSE", "SR_QA", "BA", "UX"]:
            mid_employees.append(email)
        elif designation_code in ["TL", "PM", "ARCH", "PE", "TDO"]:
            # Keep one 50% capacity senior unallocated (available)
            if designation_code in ["PE", "TDO"] and capacity == 50:
                if pe_tdo_50_capacity_count == 0:
                    excluded_senior = email  # First 50% capacity senior stays unallocated
                    pe_tdo_50_capacity_count += 1
                    continue
                else:
                    pe_tdo_50_capacity_count += 1
            senior_employees.append(email)

    # Create allocations for active projects
    active_projects = [
        ("Mobile Banking App", 12),
        ("Healthcare Management System", 10),
        ("Insurance Claims Processing", 14),
        ("Retail POS System", 8),
        ("Financial Trading Platform", 18),
        ("Logistics Optimization", 12),
        ("IoT Device Management", 14),
        ("Blockchain Wallet", 16),
        ("Video Streaming Platform", 20),
        ("Resource Allocation System", 6),
        ("Knowledge Management", 8),
        ("DevOps Automation", 12),
    ]

    allocation_count = 0
    for project_name, duration_months in active_projects:
        if project_name not in project_ids:
            continue

        project_id = project_ids[project_name]

        # Calculate project dates
        start_days_ago = random.randint(60, 365)  # Started 2-12 months ago
        start_date = (datetime.now() - timedelta(days=start_days_ago)).date()
        end_date = start_date + timedelta(days=duration_months * 30)

        # Allocate 4-8 employees per project
        num_employees = random.randint(4, 8)

        # Mix of employee levels
        selected_employees = []

        # Add 2-3 junior employees
        if junior_employees:
            selected_employees.extend(
                random.sample(junior_employees, min(3, len(junior_employees)))
            )

        # Add 2-3 mid-level employees
        if mid_employees:
            selected_employees.extend(random.sample(mid_employees, min(3, len(mid_employees))))

        # Add 1-2 senior employees
        if senior_employees:
            selected_employees.extend(
                random.sample(senior_employees, min(2, len(senior_employees)))
            )

        # Trim to desired number
        selected_employees = selected_employees[:num_employees]

        for employee_email in selected_employees:
            if employee_email == excluded_senior:
                continue  # Skip the unallocated senior

            employee_id = employee_ids[employee_email]

            # Find employee designation for allocation logic
            employee_data = next((emp for emp in employees_data if emp[0] == employee_email), None)
            if not employee_data:
                continue

            _, _, designation_code, capacity, _ = employee_data

            # Determine allocation percentage based on employee level
            if designation_code in ["SDE_INTERN", "QA_INTERN", "SDE", "SE", "QA"]:
                # Juniors: Either 0% (bench) or 100% (single project focus)
                percent_allocated = random.choice([100, 100, 100, 0])  # 75% chance of 100%
            elif designation_code in ["SSE", "SR_QA", "BA", "UX"]:
                # Mid-level: Various splits across 1-2 projects
                percent_allocated = random.choice([50, 75, 100])
            else:
                # Senior: Lighter individual allocations across 2-3 projects
                percent_allocated = random.choice([25, 50, 75])

            # Skip 0% allocations
            if percent_allocated == 0:
                continue

            allocation_id = uuid.uuid4()
            op.execute(
                f"""
                INSERT INTO allocations (id, project_id, employee_id, percent_allocated, start_date, end_date, status,
                                       created_at, updated_at, created_by, updated_by)
                VALUES ('{allocation_id}', '{project_id}', '{employee_id}', '{percent_allocated}', 
                        '{start_date}', '{end_date}', 'ACTIVE',
                        NOW(), NOW(), '{system_user_id}', '{system_user_id}');
            """
            )
            allocation_count += 1

    # Create some completed allocations for historical projects
    completed_projects = [
        ("E-Commerce Platform Modernization", 8),
        ("Supply Chain Analytics", 6),
        ("EdTech Learning Platform", 10),
        ("CRM Enhancement", 6),
        ("TechVantage HR Portal", 4),
        ("Performance Analytics", 5),
    ]

    for project_name, duration_months in completed_projects:
        if project_name not in project_ids:
            continue

        project_id = project_ids[project_name]

        # Calculate completed project dates
        end_days_ago = random.randint(30, 180)  # Ended 1-6 months ago
        end_date = (datetime.now() - timedelta(days=end_days_ago)).date()
        start_date = end_date - timedelta(days=duration_months * 30)

        # Allocate 3-6 employees per completed project
        num_employees = random.randint(3, 6)

        # Mix of employee levels
        selected_employees = []
        if junior_employees:
            selected_employees.extend(
                random.sample(junior_employees, min(2, len(junior_employees)))
            )
        if mid_employees:
            selected_employees.extend(random.sample(mid_employees, min(2, len(mid_employees))))
        if senior_employees:
            selected_employees.extend(
                random.sample(senior_employees, min(1, len(senior_employees)))
            )

        selected_employees = selected_employees[:num_employees]

        for employee_email in selected_employees:
            if employee_email == excluded_senior:
                continue

            employee_id = employee_ids[employee_email]

            # Similar allocation logic for completed projects
            employee_data = next((emp for emp in employees_data if emp[0] == employee_email), None)
            if not employee_data:
                continue

            _, _, designation_code, capacity, _ = employee_data

            if designation_code in ["SDE_INTERN", "QA_INTERN", "SDE", "SE", "QA"]:
                percent_allocated = random.choice([75, 100])
            elif designation_code in ["SSE", "SR_QA", "BA", "UX"]:
                percent_allocated = random.choice([50, 75, 100])
            else:
                percent_allocated = random.choice([25, 50, 75])

            allocation_id = uuid.uuid4()
            op.execute(
                f"""
                INSERT INTO allocations (id, project_id, employee_id, percent_allocated, start_date, end_date, status,
                                       created_at, updated_at, created_by, updated_by)
                VALUES ('{allocation_id}', '{project_id}', '{employee_id}', '{percent_allocated}', 
                        '{start_date}', '{end_date}', 'COMPLETED',
                        NOW(), NOW(), '{system_user_id}', '{system_user_id}');
            """
            )
            allocation_count += 1


def downgrade() -> None:
    # Delete in reverse order due to foreign key constraints
    op.execute("DELETE FROM allocations;")
    op.execute("DELETE FROM employee_skills;")
    op.execute("DELETE FROM employee_embeddings;")
    op.execute("DELETE FROM employees;")
    op.execute("DELETE FROM projects;")
    op.execute("DELETE FROM designations;")
    op.execute("DELETE FROM users WHERE email = 'system@techvantage.io';")
