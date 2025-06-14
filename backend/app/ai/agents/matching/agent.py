"""Resource Matching Agent for intelligent resource allocation."""

import time
from typing import Any, Dict, List

import structlog
from pydantic import BaseModel, Field, validator

from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda

from app.ai.agents.base import BaseAgent
from app.ai.core.config import AIConfig

logger = structlog.get_logger()


# ============================================================================
# INPUT SCHEMAS
# ============================================================================


class ProjectDetails(BaseModel):
    """Project details for matching."""

    name: str = Field(..., description="Project name")
    duration: int = Field(..., description="Project duration in months")
    starting_from: str = Field(..., description="Project start date/month")
    skills_required: List[str] = Field(..., description="Required technical skills")
    resources_required: Dict[str, int] = Field(
        ...,
        description="Number and type of resources required (e.g., {'Tech Lead': 1, 'Senior Software Engineer': 2})",
    )


class EmployeeSkill(BaseModel):
    """Employee skill detail."""

    skill_name: str = Field(..., description="Skill name")
    experience_months: int = Field(..., description="Experience in months")
    last_used: str = Field(..., description="When last used (e.g., '2024-01', 'Current')")


class EmployeeDetail(BaseModel):
    """Employee detail information."""

    employee_id: str = Field(..., description="Employee ID")
    name: str = Field(..., description="Employee name")
    email: str = Field(..., description="Employee email")
    designation: str = Field(..., description="Current designation")
    available_percentage: int = Field(
        ..., ge=0, le=100, description="Available capacity percentage"
    )
    skills: List[EmployeeSkill] = Field(default_factory=list, description="Employee skills list")


class MatchingInput(BaseModel):
    """Input for the matching engine."""

    project_details: ProjectDetails = Field(..., description="Project details")
    available_employees: List[EmployeeDetail] = Field(..., description="Available employees")

    @validator("available_employees")
    def validate_employees_not_empty(cls, v):
        if not v:
            raise ValueError("Available employees list cannot be empty")
        return v


# ============================================================================
# OUTPUT SCHEMAS
# ============================================================================


class MatchedEmployeeDetail(BaseModel):
    """Simplified employee detail for matching output."""

    name: str = Field(..., description="Employee name")
    designation: str = Field(..., description="Employee designation")
    available_percentage: int = Field(
        ..., ge=0, le=100, description="Available capacity percentage"
    )
    skills: List[str] = Field(
        default_factory=list, description="Employee skills as list of strings"
    )


class TeamCombination(BaseModel):
    """Team combination with skills analysis."""

    team_members: List[MatchedEmployeeDetail] = Field(..., description="List of team members")
    skills_match: float = Field(..., description="Skills match percentage")
    skills_matched: List[str] = Field(
        default_factory=list, description="Skills that are covered by the team"
    )
    skills_missing: List[str] = Field(
        default_factory=list, description="Skills that are missing from the team"
    )


class MatchingOutput(BaseModel):
    """Simplified output from the matching engine."""

    matched_resources: Dict[str, List[MatchedEmployeeDetail]] = Field(
        ..., description="Resources matched by designation"
    )
    possible_team_combinations: List[TeamCombination] = Field(
        default_factory=list, description="Possible team combinations"
    )


# ============================================================================
# MATCHING AGENT
# ============================================================================


class MatchingAgent(BaseAgent):
    """Resource matching agent for intelligent resource allocation."""

    def __init__(self, config: AIConfig):
        """Initialize the matching agent.

        Args:
            config: AI configuration settings. Required - contains API keys and model settings.
        """
        super().__init__(config)

        # Initialize LLM for resource matching
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,  # Low temperature for consistent matching
            max_tokens=3000,
            api_key=self.config.api_key,
        )

        # Create output parser
        self.output_parser = PydanticOutputParser(pydantic_object=MatchingOutput)

        # Create the matching prompt
        self.matching_prompt = self._create_matching_prompt()

        # Create the matching chain
        self.matching_chain = (
            RunnableLambda(self._prepare_prompt_variables)
            | self.matching_prompt
            | self.llm
            | self.output_parser
        )

        logger.info("[MATCHING-AGENT] Initialized")

    def _create_matching_prompt(self) -> ChatPromptTemplate:
        """Create the matching prompt template."""

        system_message = """You are ResourceWise AI, an expert resource matching specialist. Your job is to analyze project requirements and available employees to provide optimal resource allocation recommendations.

**MATCHING CRITERIA (in order of importance):**

1. **AVAILABILITY** - Employee must have sufficient available allocation percentage
2. **DESIGNATION MATCH** - Employee designation should align with required role
3. **SKILLS MATCH** - Employee should possess one or more required technical skills
- All matching is case insensitive.

**SCORING METHODOLOGY:**
- Skills Match Percentage: Calculate based on how many required skills the team covers
- Consider employee availability and designation fit
- Prioritize combinations that maximize skill coverage

**DESIGNATION MATCHING:**
- Exact match: Senior Software Engineer = Senior Software Engineer
- Level match: Senior Software Engineer can work as Tech Lead but SDE cannot work as Tech Lead

**SKILLS MATCHING:**
- Calculate percentage of required skills covered by the team
- A team member with ANY of the required skills contributes to the match

**TEAM COMPOSITION RULES:**
- Ensure proper availability of employees
- Ensure skill coverage across the team 

**OUTPUT REQUIREMENTS:**
- Group matched employees by their designation
- Provide 2-3 possible team combinations
- Calculate accurate skills match percentages
- List specific skills matched and missing for each combination"""

        human_template = """
**PROJECT DETAILS:**
Project Name: {project_name}
Duration: {duration} months
Starting From: {starting_from}
Skills Required: {skills_required}
Resources Required: {resources_required}

**AVAILABLE EMPLOYEES:**
{available_employees}

**ANALYSIS REQUEST:**
Please analyze the available employees and provide:

1. **Matched Resources**: Group suitable employees by designation
2. **Team Combinations**: Suggest 2-3 optimal team combinations with skills analysis

**OUTPUT FORMAT REQUIREMENTS:**
- For matched employees, include only: name, designation, available_percentage, skills (as simple list of skill names only)
- For team combinations, include: team_members, skills_match (percentage), skills_matched, skills_missing
- Extract only skill names from employee skills (ignore experience/dates)
- Calculate skills_match as percentage of required skills covered by the team

{format_instructions}
"""

        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_message),
                HumanMessagePromptTemplate.from_template(human_template),
            ]
        )

    def _format_resources_required(self, resources: Dict[str, int]) -> str:
        """Format resources required for the prompt."""
        formatted = []
        for designation, count in resources.items():
            formatted.append(f"- {designation}: {count}")
        return "\n".join(formatted)

    def _format_available_employees(self, employees: List[EmployeeDetail]) -> str:
        """Format available employees for the prompt."""
        formatted = []

        for i, emp in enumerate(employees, 1):
            if emp.skills:
                skills_text = ", ".join(
                    [
                        f"{skill.skill_name} ({skill.experience_months}mo, last: {skill.last_used})"
                        for skill in emp.skills
                    ]
                )
            else:
                skills_text = "No skills listed"

            emp_text = f"""**Employee {i}: {emp.name}**
- ID: {emp.employee_id}
- Email: {emp.email}
- Designation: {emp.designation}
- Available Capacity: {emp.available_percentage}%
- Skills: {skills_text}"""
            formatted.append(emp_text)

        return "\n\n".join(formatted)

    def _prepare_prompt_variables(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare prompt variables for the matching chain."""
        # Validate and parse input
        matching_input = MatchingInput(**input_data)
        project = matching_input.project_details

        return {
            "project_name": project.name,
            "duration": project.duration,
            "starting_from": project.starting_from,
            "skills_required": ", ".join(project.skills_required),
            "resources_required": self._format_resources_required(project.resources_required),
            "available_employees": self._format_available_employees(
                matching_input.available_employees
            ),
            "format_instructions": self.output_parser.get_format_instructions(),
        }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process matching request.

        Args:
            input_data: Matching input data
                Expected format:
                {
                    "project_details": {
                        "name": "Mobile Banking App",
                        "duration": 3,
                        "starting_from": "July",
                        "skills_required": ["React Native", "TypeScript"],
                        "resources_required": {"Tech Lead": 1, "Senior Software Engineer": 2}
                    },
                    "available_employees": [
                        {
                            "employee_id": "emp_001",
                            "name": "John Doe",
                            "email": "john@company.com",
                            "designation": "Tech Lead",
                            "available_percentage": 80,
                            "skills": ["React Native", "JavaScript"]
                        }
                    ]
                }

        Returns:
            Matching results in the specified format
        """
        start_time = time.time()

        try:
            logger.info("[MATCHING-AGENT] Processing matching request")

            # Log input details for debugging
            matching_input = MatchingInput(**input_data)
            project = matching_input.project_details
            logger.info(
                "[MATCHING-AGENT] Input received for matching",
                project=project,
                available_employees_count=len(matching_input.available_employees),
            )

            # Invoke the matching chain
            result = await self.matching_chain.ainvoke(input_data)

            processing_time = round((time.time() - start_time) * 1000, 1)

            logger.info(
                "[MATCHING-AGENT] Matching completed successfully",
                processing_time_ms=processing_time,
                matched_designations=len(result.matched_resources),
                team_combinations=len(result.possible_team_combinations),
            )

            # Convert to dict and add metadata
            output = result.model_dump()
            output["processing_time_ms"] = processing_time
            output["success"] = True

            return {"matching_results": output}

        except Exception as e:
            processing_time = round((time.time() - start_time) * 1000, 1)

            logger.error(
                "[MATCHING-AGENT] Error in matching process",
                error=str(e),
                processing_time_ms=processing_time,
            )

            # Return error response
            return {
                "matching_results": {
                    "matched_resources": {},
                    "possible_team_combinations": [],
                    "processing_time_ms": processing_time,
                    "success": False,
                    "error_message": str(e),
                }
            }
