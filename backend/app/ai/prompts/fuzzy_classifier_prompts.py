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

FUZZY indicators (need resolution):
1. SKILL CATEGORIES: "frontend", "backend", "mobile", "cloud", "data", "web", "design", "analytics", "devops", "security", "testing"
2. EXPERIENCE LEVELS: "senior", "junior", "experienced", "lead", "management", "expert", "specialist"
3. TEAM REFERENCES: "design team", "QA team", "backend team", "frontend team" (team names need role resolution)
4. SKILL EXPERIENCE QUERIES: "developers with [skill] experience", "who knows [skill]", "experts in [skill]"
5. ROLE ABBREVIATIONS: "SSE", "TL", "PM", "QA", "SE", "SDE", "BA", "UX" (need expansion to full titles)
6. VAGUE DESCRIPTORS: "good at", "skilled in", "familiar with", "proficient in"

PRECISE indicators (no resolution needed):
1. SPECIFIC SKILLS: "React", "Java", "Python", "PostgreSQL", "AWS", "Docker", "Kubernetes"
2. FULL ROLE TITLES: "Senior Software Engineer", "Technical Lead", "Project Manager", "Quality Assurance Engineer"
3. PROJECT STATUS QUERIES: "working on active projects", "working on customer projects", "assigned to projects"
4. ALLOCATION QUERIES: "overallocated", "underutilized", "available", "allocated to"
5. SPECIFIC NAMES: "John Smith", "Mobile Banking App", "Healthcare System"
6. PRECISE OPERATIONS: "list all", "show employees", "find employees"

CONTEXT-AWARE CLASSIFICATION:
- "working on" + project context (active/customer/internal) → PRECISE
- "working on" + vague context → FUZZY
- "developers with [specific skill]" → PRECISE if skill is specific (React, Java)
- "developers with [category] experience" → FUZZY if category is broad (frontend, backend)
- "who knows [specific skill]" → PRECISE (should check all employees)

Examples:
FUZZY:
- "Find SSE with React skills" → fuzzy terms: ["SSE"]
- "Find senior frontend developers" → fuzzy terms: ["senior", "frontend"]
- "List experienced backend engineers" → fuzzy terms: ["experienced", "backend"]
- "Find developers with cloud experience" → fuzzy terms: ["developers", "cloud"]
- "Who knows Python and machine learning?" → fuzzy terms: ["machine learning"]
- "Show me cloud experts" → fuzzy terms: ["cloud", "experts"]
- "Give me members of design team" → fuzzy terms: ["design"]
- "Find developers with React experience" → fuzzy terms: ["developers"]

PRECISE:
- "Show employees working on active projects" → fuzzy terms: []
- "Who's working on customer projects?" → fuzzy terms: []
- "List all employees with React skills" → fuzzy terms: []
- "Find overallocated employees" → fuzzy terms: []
- "Show employees with Java and Spring Boot skills" → fuzzy terms: []

Query: "{query}"

Respond in this exact format:
Classification: [fuzzy/precise]
Fuzzy Terms: [comma-separated list of fuzzy terms, or "none" if no fuzzy terms]

Example responses:
Classification: fuzzy
Fuzzy Terms: SSE, frontend

Classification: precise
Fuzzy Terms: none
""",
        )
