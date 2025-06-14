"""Database enums for predefined values"""

from enum import Enum


class ProjectType(str, Enum):
    """Project type enum"""

    CUSTOMER = "customer"
    INTERNAL = "internal"


class ProjectStatus(str, Enum):
    """Project status enum"""

    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AllocationStatus(str, Enum):
    """Allocation status enum"""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AllocationPercentage(Enum):
    """Common allocation percentages"""

    QUARTER = 25
    HALF = 50
    THREE_QUARTER = 75
    FULL = 100


class SkillSource(str, Enum):
    """Source of skill information"""

    PAT = "PAT"  # Performance Assessment Tool
    MANUAL = "MANUAL"  # Manually entered
    SEED = "SEED"  # Seeded data
    SELF_ASSESSMENT = "SELF_ASSESSMENT"
    MANAGER_ASSESSMENT = "MANAGER_ASSESSMENT"


class SkillProficiencyLevel(str, Enum):
    """Skill proficiency levels"""

    BEGINNER = "BEGINNER"  # 0-6 months
    NOVICE = "NOVICE"  # 6-12 months
    INTERMEDIATE = "INTERMEDIATE"  # 1-3 years
    ADVANCED = "ADVANCED"  # 3-5 years
    EXPERT = "EXPERT"  # 5+ years


class EmployeeGroup(str, Enum):
    """Employee organization group"""

    KD_INDIA = "KD_INDIA"
    KD_US = "KD_US"
    DEV_PARTNER = "DEV_PARTNER"
    INDEPENDENT = "INDEPENDENT"


class EmployeeType(str, Enum):
    """Employee type classification"""

    FULL_TIME = "FULL_TIME"
    CONTRACTOR = "CONTRACTOR"
    CONSULTANT = "CONSULTANT"
    INTERN = "INTERN"
