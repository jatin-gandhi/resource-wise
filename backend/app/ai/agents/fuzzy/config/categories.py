"""Skill category configuration for fuzzy resolution."""

from datetime import datetime
from typing import Dict, List


class SkillCategoryConfig:
    """Centralized configuration for skill categories and mappings."""

    # Version for tracking updates
    VERSION = "1.0.0"
    LAST_UPDATED = "2024-06-14"

    # Core skill categories with their mappings
    SKILL_CATEGORIES = {
        "frontend": {
            "skills": [
                "React",
                "Angular",
                "Vue.js",
                "JavaScript",
                "TypeScript",
                "HTML/CSS",
                "Redux",
                "Material-UI",
                "Tailwind CSS",
                "Next.js",
            ],
            "roles": [
                "Frontend Developer",
                "UI Developer",
                "UX Designer",
                "Software Engineer",
                "Senior Software Engineer",
            ],
            "aliases": ["front-end", "ui", "ux", "client-side", "web development"],
        },
        "backend": {
            "skills": [
                "Java",
                "Python",
                "Node.js",
                "Spring Boot",
                "Django",
                "FastAPI",
                "PostgreSQL",
                "MySQL",
                "MongoDB",
                "Redis",
                "Express.js",
                "OpenAI API",
                "SQL Server",
                ".NET",
                "Laravel",
                "PHP",
            ],
            "roles": [
                "Backend Developer",
                "API Developer",
                "Database Developer",
                "Software Engineer",
                "Senior Software Engineer",
                "Technical Lead",
            ],
            "aliases": ["back-end", "server-side", "api", "database", "server"],
        },
        "mobile": {
            "skills": [
                "React Native",
                "Flutter",
                "Swift",
                "Kotlin",
                "iOS Development",
                "Android Development",
                "Ionic",
                "Xamarin",
            ],
            "roles": [
                "Mobile Developer",
                "iOS Developer",
                "Android Developer",
                "Software Engineer",
                "Senior Software Engineer",
            ],
            "aliases": ["app development", "ios", "android", "mobile app"],
        },
        "cloud": {
            "skills": [
                "AWS",
                "Azure",
                "GCP",
                "Docker",
                "Kubernetes",
                "Terraform",
                "AWS Lambda",
                "Azure Functions",
                "Google Cloud Functions",
                "CloudFormation",
                "AWS CDK",
                "EC2",
                "S3",
                "RDS",
                "DynamoDB",
            ],
            "roles": [
                "Cloud Engineer",
                "DevOps Engineer",
                "Cloud Architect",
                "Software Engineer",
                "Senior Software Engineer",
                "Technical Lead",
            ],
            "aliases": ["aws", "azure", "gcp", "infrastructure"],
        },
        "data": {
            "skills": [
                "Python",
                "Machine Learning",
                "Deep Learning",
                "NumPy",
                "Pandas",
                "PyTorch",
                "TensorFlow",
                "Scikit-learn",
                "Computer Vision",
                "NLP",
                "PostgreSQL",
                "MySQL",
                "SQL Server",
            ],
            "roles": [
                "Data Scientist",
                "Data Analyst",
                "ML Engineer",
                "Data Engineer",
                "Software Engineer",
                "Senior Software Engineer",
            ],
            "aliases": ["data science", "machine learning", "ml", "ai", "analytics"],
        },
        "testing": {
            "skills": [
                "Selenium",
                "Jest",
                "JUnit",
                "Cypress",
                "TestNG",
                "Playwright",
                "PyTest",
                "Mocha",
                "Chai",
                "Postman",
            ],
            "roles": [
                "QA Engineer",
                "Test Automation Engineer",
                "Quality Assurance Engineer",
                "Senior Quality Assurance Engineer",
                "Software Engineer",
            ],
            "aliases": ["qa", "quality assurance", "automation", "test"],
        },
        "devops": {
            "skills": [
                "Docker",
                "Kubernetes",
                "Jenkins",
                "GitLab CI",
                "Terraform",
                "Ansible",
                "Prometheus",
                "Grafana",
                "Helm",
                "AWS",
                "Azure",
                "GCP",
            ],
            "roles": [
                "DevOps Engineer",
                "Cloud Engineer",
                "Site Reliability Engineer",
                "Technical Lead",
                "Software Engineer",
            ],
            "aliases": ["deployment", "ci/cd", "infrastructure", "automation"],
        },
    }

    # Configuration settings
    SETTINGS = {
        "max_results_per_category": 10,
        "enable_vector_fallback": True,
        "vector_similarity_threshold": 0.2,
    }

    @classmethod
    def get_category_data(cls, category: str) -> Dict:
        """Get data for a specific category."""
        return cls.SKILL_CATEGORIES.get(category.lower(), {})

    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get list of all available categories."""
        return list(cls.SKILL_CATEGORIES.keys())

    @classmethod
    def get_all_aliases(cls) -> Dict[str, str]:
        """Get mapping of all aliases to their categories."""
        alias_map = {}
        for category, data in cls.SKILL_CATEGORIES.items():
            for alias in data.get("aliases", []):
                alias_map[alias.lower()] = category
        return alias_map

    @classmethod
    def is_known_category(cls, term: str) -> bool:
        """Check if term is a known category or alias."""
        term_lower = term.lower().strip()

        # Check direct category match
        if term_lower in cls.SKILL_CATEGORIES:
            return True

        # Check aliases
        alias_map = cls.get_all_aliases()
        return term_lower in alias_map

    @classmethod
    def resolve_category(cls, term: str) -> str:
        """Resolve term to its canonical category name."""
        term_lower = term.lower().strip()

        # Direct match
        if term_lower in cls.SKILL_CATEGORIES:
            return term_lower

        # Alias match
        alias_map = cls.get_all_aliases()
        return alias_map.get(term_lower, term_lower)

    @classmethod
    def get_setting(cls, key: str, default=None):
        """Get a configuration setting."""
        return cls.SETTINGS.get(key, default)
