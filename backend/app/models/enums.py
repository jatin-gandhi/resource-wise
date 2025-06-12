"""Database enums for predefined values"""

from enum import Enum


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


class AllocationPercentage(int, Enum):
    """Standard allocation percentages"""

    QUARTER = 25
    HALF = 50
    THREE_QUARTER = 75
    FULL = 100


class SkillProficiencyLevel(int, Enum):
    """Skill proficiency levels"""

    BEGINNER = 1
    NOVICE = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5


class SkillSource(str, Enum):
    """Source of skill assessment"""

    PAT = "PAT"  # Performance Assessment Tool
    MANUAL = "manual"
    SEED = "seed"  # For seeded data
    SELF_ASSESSMENT = "self_assessment"
    MANAGER_ASSESSMENT = "manager_assessment"
