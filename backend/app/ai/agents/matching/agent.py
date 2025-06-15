"""Resource Matching Agent for intelligent resource allocation."""

import time
from typing import Any, Dict, List, Union

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


class ResourceRequirement(BaseModel):
    """Resource requirement details."""

    resource_type: str = Field(..., description="Type of resource (e.g., 'TL', 'SSE', 'SDE')")
    resource_count: int = Field(..., ge=1, description="Number of resources required")
    required_allocation_percentage: int = Field(
        default=None,
        ge=1,
        le=100,
        description="Required allocation percentage (optional - defaults to 100% if not specified)",
    )

    def get_effective_allocation_percentage(self) -> int:
        """Get the effective allocation percentage (100% if not specified)."""
        return (
            self.required_allocation_percentage
            if self.required_allocation_percentage is not None
            else 100
        )


class ProjectDetails(BaseModel):
    """Project details for matching."""

    name: str = Field(..., description="Project name")
    duration: int = Field(..., description="Project duration in months")
    starting_from: str = Field(..., description="Project start date/month")
    skills_required: List[str] = Field(..., description="Required technical skills")
    resources_required: List[ResourceRequirement] = Field(
        ..., description="List of resource requirements with optional allocation percentages"
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
            model="gpt-4o",
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
   - Employee's available_percentage must be >= required allocation percentage
   - If no allocation percentage specified in requirements, assume 100% is required
   - This is the PRIMARY filtering criterion - apply first before other criteria
2. **DESIGNATION MATCH** - Employee designation should align with required role
3. **SKILLS MATCH** - Employee should possess one or more required technical skills
- All matching is case insensitive.

**ALLOCATION MATCHING RULES:**
- ALWAYS apply allocation filtering as the first step
- When allocation percentage IS specified: employee's available_percentage >= required allocation
- When allocation percentage IS NOT specified: employee's available_percentage >= 100% (assume full allocation needed)
- Example: "TL: 1 (required allocation: 50%)" → only include TLs with available_percentage >= 50%
- Example: "SE: 2" → only include SEs with available_percentage >= 100%

**MATCHING PROCESS:**
1. First, filter employees by availability (primary criterion)
2. Then, filter by designation match
3. Finally, consider skills match for team composition

**DESIGNATION MATCHING:**
- Exact match: Senior Software Engineer = Senior Software Engineer
- Level match: Senior Software Engineer can work as Tech Lead but SDE cannot work as Tech Lead

**SKILLS MATCHING & PRIORITIZATION:**
- Calculate percentage of required skills covered by the team
- A team member with ANY of the required skills contributes to the match

**CANDIDATE RANKING WITHIN SAME DESIGNATION:**
When multiple candidates meet availability and designation requirements, rank them by:

1. **Framework-Based Skill Priority**: MANDATORY first-level filtering
   - Identify framework-language relationships in requirements
   - RULE: Framework experience > Base language experience (Django > Python, React > JavaScript)
   - RULE: Framework expertise implies base language competency automatically
   - RULE: Cross-domain frameworks don't imply other languages (Spring Boot ≠ Python knowledge)
   - PRIORITY ORDER: Domain-specific frameworks > Base languages > Unrelated skills
   - When calculating skills match, weight frameworks 3x more than base languages

2. **Skill Count Match**: Among candidates with similar critical skill levels
   - 3+ matching skills > 2 matching skills > 1 matching skill > 0 matching skills

3. **Skill Quality Assessment**: For candidates with same skill count, apply these rules:
   - **Recency Thresholds**:
     * Current/Recent (0-3 months): Excellent
     * Moderate (4-12 months): Good  
     * Stale (13-24 months): Fair
     * Very Stale (25+ months): Poor
   - **Experience Thresholds**:
     * Expert (24+ months): Excellent
     * Experienced (12-23 months): Good
     * Intermediate (6-11 months): Fair
     * Beginner (0-5 months): Poor
   - **Balancing Rules**:
     * Recent + Intermediate > Stale + Expert (for skills used >12 months ago)
     * Expert + Moderate > Intermediate + Recent (for skills used 4-12 months ago)
     * Always prefer Recent over Stale when experience difference is <12 months

4. **Skill Depth vs Breadth**:
   - For 1-2 required skills: Prioritize depth (expert in key skills)
   - For 3+ required skills: Balance depth and breadth
   - ALWAYS ensure critical skills are covered before considering breadth

5. **Framework-Language Relationships & Transferable Skills**:
   - **Implicit Language Skills**: Framework expertise implies base language knowledge
     * Django/Flask expert → Python competency (automatic credit)
     * React/Angular expert → JavaScript competency (automatic credit)
     * Spring Boot expert → Java competency (automatic credit)
   - **Cross-Domain Separation**: Different language ecosystems don't transfer
     * Spring Boot (Java) + Python = separate, unrelated skills
     * .NET (C#) + Python = separate, unrelated skills
   - **Same-Domain Transferability**: Related frameworks get partial credit
     * Django ↔ Flask: 80% transferable (both Python web)
     * React ↔ Angular: 60% transferable (both JavaScript frontend)
   - **Technology Evolution**: Modern versions preferred over legacy

6. **Project Context Considerations**:
   - Short projects (<3 months): Heavily favor recent usage and immediate skills
   - Long projects (6+ months): Consider learning potential and adaptability
   - Complex projects: Prioritize proven experience over recent dabbling

**TEAM COMPOSITION RULES:**
- Start with availability-filtered employees only
- Ensure proper designation distribution
- Maximize skill coverage across the team
- Prioritize combinations that meet allocation requirements
- When selecting from multiple qualified candidates, choose the best-ranked individuals based on skill matching criteria above

**OUTPUT REQUIREMENTS:**
- Group matched employees by their designation (only those meeting availability requirements)
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

**ALLOCATION FILTERING (MANDATORY):**
- Check each resource requirement in the Resources Required section
- ALWAYS apply allocation filtering as the primary criterion
- When allocation requirement is specified, employee must have available_percentage >= required percentage
- When NO allocation requirement is specified, employee must have available_percentage >= 100% (assume full allocation needed)

**SKILL-BASED RANKING (IMPORTANT):**
- For each designation, rank candidates by skill match quality
- Apply the detailed ranking criteria from the system message
- Consider skill count, experience depth, usage recency, and transferable skills
- Account for project duration and complexity when making trade-offs
- Prioritize candidates with the best overall skill profile for the specific project context
- Include the best-ranked candidates in your team combinations

**FRAMEWORK-BASED SKILL PRIORITY (MANDATORY):**
- Analyze skill requirements for framework-language relationships
- PRIORITY HIERARCHY: Frameworks > Base Languages > Unrelated Skills
- FRAMEWORK EXAMPLES: Django/Flask (Python), React/Angular (JavaScript), Spring Boot (Java)
- IMPLICIT SKILLS: Framework expertise automatically grants base language competency
- EXAMPLE ANALYSIS for "Python, Flask, Django":
  * Django expert (24mo) → Gets Python credit automatically → HIGHEST priority
  * Flask expert (18mo) → Gets Python credit automatically → HIGH priority  
  * Python expert (36mo) with no frameworks → MEDIUM priority
  * Unrelated skills only → LOWEST priority
- CROSS-DOMAIN RULE: Spring Boot + Python = separate skills (no automatic credit)

**COMMON RANKING SCENARIOS:**
- High experience + old usage vs Medium experience + recent usage: Favor recent for skills unused >12 months
- Skill specialist vs Generalist: For 1-2 skills favor specialist, for 3+ skills consider generalist
- Exact match vs Transferable skills: Exact match preferred, but give credit to related technologies
- Framework vs Base language: Framework expertise (Django) beats base language only (Python)
- Implicit skills: Django expert automatically gets Python competency credit
- Cross-domain separation: Spring Boot expertise doesn't imply Python knowledge

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

    def _format_resources_required(self, resources: List[ResourceRequirement]) -> str:
        """Format resources required for the prompt."""
        formatted = []
        for requirement in resources:
            resource_type = requirement.resource_type
            count = requirement.resource_count
            effective_allocation = requirement.get_effective_allocation_percentage()

            if requirement.required_allocation_percentage is not None:
                # Explicitly specified allocation
                formatted.append(
                    f"- {resource_type}: {count} (required allocation: {effective_allocation}%)"
                )
            else:
                # Default allocation (100%)
                formatted.append(
                    f"- {resource_type}: {count} (required allocation: {effective_allocation}% - default)"
                )
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
