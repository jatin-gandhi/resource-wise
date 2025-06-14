"""Fuzzy classification prompts for the FuzzyClassifier.

This file contains all prompt templates used for fuzzy query classification.
Excluded from linting to preserve natural language formatting.
"""

from langchain_core.prompts import PromptTemplate


class FuzzyClassifierPrompts:
    """Container for all fuzzy classification prompt templates."""

    @staticmethod
    def get_fuzzy_classification_prompt() -> PromptTemplate:
        """Get the fuzzy classification prompt template."""
        return PromptTemplate(
            input_variables=["query"],
            template="""You are a query classifier. Analyze the query and identify any vague/fuzzy terms that need semantic resolution.

FUZZY TERMS TO IDENTIFY:
1. **Job Titles/Roles** (vague designations):
   - "SSE", "TL", "PM", "SDE", "QA", "BA", "UI/UX"
   - "senior", "junior", "lead", "manager", "architect"
   - "developer", "engineer", "designer", "analyst"

2. **Technical Skills** (broad categories):
   - "frontend", "backend", "fullstack", "mobile", "devops"
   - "database", "cloud", "testing", "design tools"
   - "programming languages", "frameworks", "tools"

3. **Team/Department Names** (organizational units):
   - "design team", "QA team", "backend team", "mobile team"
   - "development team", "testing team", "UI team"

4. **Experience Levels** (subjective qualifiers):
   - "experienced", "expert", "skilled", "proficient"
   - "beginner", "novice", "intermediate", "advanced"

5. **Availability Terms** (resource status):
   - "available", "free", "unallocated", "partially allocated"
   - "overallocated", "busy", "fully booked"

6. **Project Types** (business categories):
   - "customer projects", "internal projects", "client work"
   - "active projects", "completed projects", "ongoing"

7. **Financial Terms** (subjective/relative):
   - "expensive", "cheap", "high cost", "low cost"
   - "cost-effective", "premium", "affordable"

8. **Project Management Terms** (vague roles/concepts):
   - "who manages", "project manager" (when not specific)
   - "timeline", "deadline", "duration" (when vague)
   - "deliverables", "milestones", "phases"

9. **Time-based Terms** (relative time):
   - "next month", "this quarter", "soon", "recently"
   - "current", "upcoming", "past", "future"

PRECISE TERMS (NOT fuzzy - direct database mappings):
- **Exact names**: "John Doe", "Mobile Banking App", "React"
- **Specific numbers**: "25%", "100%", "3 months"
- **Exact dates**: "2024-01-15", "January 2024"
- **Boolean values**: "active", "inactive", "true", "false"
- **Employee Groups** (direct enum mappings): "KD India", "KD US", "Dev Partner", "Independent"
- **Employee Types** (direct enum mappings): "contractors", "full-time", "consultants", "interns"
- **Specific locations**: "Bangalore", "New York", "Remote", "San Francisco"
- **Specific skills**: "React", "Java", "Python", "PostgreSQL", "AWS", "Docker"
- **Full role titles**: "Senior Software Engineer", "Technical Lead", "Project Manager"
- **Specific financial values**: "billing rate > 100", "cost = 150"
- **Specific project names**: "Mobile Banking App", "Healthcare Management System"

CLASSIFICATION RULES:
1. If the query contains ANY fuzzy terms → Classify as "FUZZY"
2. If the query contains ONLY precise terms → Classify as "PRECISE"
3. Mixed queries with both fuzzy and precise terms → Classify as "FUZZY"

EXAMPLES:

Query: "Find SSE with React skills"
Analysis: "SSE" is fuzzy (needs expansion to full title)
Classification: FUZZY

Query: "Show me John Doe's current allocation"
Analysis: "John Doe" is precise name, "current allocation" is precise
Classification: PRECISE

Query: "List experienced frontend developers"
Analysis: "experienced" and "frontend" are both fuzzy terms
Classification: FUZZY

Query: "Find employees in design team"
Analysis: "design team" is fuzzy (could include various design roles)
Classification: FUZZY

Query: "Show KD India contractors in Bangalore"
Analysis: "KD India" = precise employee_group, "contractors" = precise employee_type, "Bangalore" = precise location
Classification: PRECISE

Query: "What's the cost of Mobile Banking App project?"
Analysis: "Mobile Banking App" is precise project name, "cost" is precise field
Classification: PRECISE

Query: "Find expensive resources for customer projects"
Analysis: "expensive" and "customer projects" are fuzzy terms
Classification: FUZZY

Query: "Who manages the Healthcare Management System?"
Analysis: "manages" is fuzzy, "Healthcare Management System" is precise
Classification: FUZZY

Query: "Show headcount by organization"
Analysis: "headcount" and "organization" are fuzzy business terms
Classification: FUZZY

Query: "List all employees with email addresses"
Analysis: All terms are precise and specific
Classification: PRECISE

Query: "Find full-time employees in Remote location"
Analysis: "full-time" = precise employee_type, "Remote" = precise location
Classification: PRECISE

Query: "Show contractors with React skills"
Analysis: "contractors" = precise employee_type, "React" = precise skill
Classification: PRECISE

Query: "List Dev Partner consultants"
Analysis: "Dev Partner" = precise employee_group, "consultants" = precise employee_type
Classification: PRECISE

RESPONSE FORMAT:
Return only one word: "FUZZY" or "PRECISE"

Query to classify: {query}

Classification:""",
        )
