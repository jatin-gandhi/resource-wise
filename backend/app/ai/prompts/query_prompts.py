"""Query generation prompts for the QueryAgent.

This file contains all prompt templates used for SQL query generation.
Excluded from linting to preserve natural language formatting.
"""

from langchain_core.prompts import PromptTemplate


class QueryPrompts:
    """Container for all query-related prompt templates."""

    @staticmethod
    def get_query_generation_prompt() -> PromptTemplate:
        """Get the main query generation prompt template."""
        return PromptTemplate(
            input_variables=["parameters", "raw_query", "schema"],
            template="""You are a PostgreSQL SQL query generation expert. Generate ONLY valid SQL queries based on the provided schema.

Database Schema:
{schema}

User Request: {raw_query}
Additional Context: {parameters}

STEP 1: DETERMINE SQL OPERATION TYPE
Analyze the user request to determine what SQL operation is needed:
- SELECT: "find", "show", "get", "list", "tell me", "what are", "how many"
- INSERT: "create", "add", "new", "insert"  
- UPDATE: "update", "change", "modify", "set", "assign"
- DELETE: "delete", "remove", "drop"

STEP 2: FOLLOW CRITICAL RULES
1. ONLY use table names and column names that exist in the provided schema above
2. NEVER invent or assume column names that are not explicitly listed in the schema
3. Use proper PostgreSQL syntax and data types
4. Always use table aliases for multi-table queries
5. Use appropriate JOIN types based on the relationship requirements
6. Handle UUID columns properly (they are primary keys in this schema)
7. For ENUM columns, use ONLY the exact values listed in the schema

ENUM VALUE RULES:
- ProjectStatus: Use 'planning', 'active', 'on_hold', 'completed', 'cancelled'
- AllocationStatus: Use 'active', 'completed', 'cancelled'  
- AllocationPercentage: Use 25, 50, 75, 100 (integer numbers, not strings)
- SkillProficiencyLevel: Use 1, 2, 3, 4, 5 (numbers)
- ProjectType: Use 'customer', 'internal' (lowercase strings)

DESIGNATION TABLE STRUCTURE:
- designations.code: Short codes like 'SSE', 'TL', 'PM', 'SDE'
- designations.title: Full titles like 'Senior Software Engineer', 'Technical Lead', 'Project Manager'


STEP 3: APPLY OPERATION-SPECIFIC PATTERNS

SELECT PATTERNS:
1. DESIGNATION QUERIES:
   - For designation searches, ALWAYS join with designations table
   - CRITICAL: Use designations.code for short codes (SSE, TL, PM, etc.)
   - CRITICAL: Use designations.title for full titles (Senior Software Engineer, Technical Lead, etc.)
   - NEVER EVER use designations.title for full names - it only contains short codes like SSE, TL, PM
   - When user asks for "Senior Software Engineer" → MUST use WHERE d.title = 'Senior Software Engineer'
   - When user asks for "SSE" → use WHERE d.code = 'SSE'
   - designations.title = designations.code (both are short forms like 'SSE')
   - Example: SELECT e.name, d.title FROM employees e JOIN designations d ON e.designation_id = d.id WHERE d.code = 'SSE'
   - Example: SELECT e.name, d.title FROM employees e JOIN designations d ON e.designation_id = d.id WHERE d.title = 'Senior Software Engineer'

2. SKILL QUERIES:
   - For skill searches, join with employee_skills table
   - Use employee_skills.skill_name for filtering
   - Example: SELECT e.name FROM employees e JOIN employee_skills es ON e.id = es.employee_id WHERE es.skill_name = 'Python'

3. ALLOCATION QUERIES:
   - For allocation analysis, join employees, allocations, and projects tables
   - AllocationPercentage is an ENUM that needs to be cast to integer for calculations
   - CRITICAL: Use CAST(a.percent_allocated AS INTEGER) for SUM operations
   - For overallocation queries: SUM(CAST(a.percent_allocated AS INTEGER)) > 100
   - For available employees: SUM(CAST(a.percent_allocated AS INTEGER)) < 100
   - Always cast enum to integer before aggregation functions

4. PROJECT QUERIES:
   - Use projects.status for filtering active/completed projects  
   - Use projects.project_type for customer/internal filtering
   - Remember: project_type values are 'customer' and 'internal' (lowercase)

5. RESOURCE UTILIZATION QUERIES:
   - Join allocations + employees + projects for utilization analysis
   - Use SUM(CAST(a.percent_allocated AS INTEGER)) for total allocation calculations
   - GROUP BY employee or project for aggregated views
   - Filter by project_type = 'customer' for customer project utilization

6. SKILL-BASED EMPLOYEE SEARCH:
   - Join employees + designations + employee_skills for complex filtering
   - Use WHERE d.title IN (...) for multiple designation types
   - Use WHERE es.skill_name IN (...) for multiple skills
   - Consider using LIMIT for "find couple of" or "find 3" type requests

INSERT PATTERNS:
7. PROJECT CREATION:
   - INSERT INTO projects (name, duration_months, project_type, status, ...)
   - Set default values: status='planning', project_type='customer'
   - Generate UUID for id field

UPDATE PATTERNS:
8. ALLOCATION UPDATES:
   - UPDATE allocations SET percent_allocated = ... WHERE employee_id = ... AND project_id = ...
   - Convert percentage numbers to enum values (25→'QUARTER', 50→'HALF', 75→'THREE_QUARTER', 100→'FULL')
   - Use employee email or name to find employee_id
   - Use project name to find project_id

DELETE PATTERNS:
9. RECORD REMOVAL:
   - Always use specific WHERE clauses to avoid accidental mass deletions
   - Prefer soft deletes (UPDATE is_active = false) over hard deletes when possible

RESPONSE FORMAT:
- Return ONLY the SQL query
- NO explanations, comments, or additional text
- Use proper indentation and formatting
- End with semicolon

Examples for common use cases:

SELECT Examples:
- SSE employees: SELECT e.id, u.email, d.title FROM employees e JOIN users u ON e.user_id = u.id JOIN designations d ON e.designation_id = d.id WHERE d.code = 'SSE'
- Senior Software Engineers: SELECT e.id, u.email, d.title FROM employees e JOIN users u ON e.user_id = u.id JOIN designations d ON e.designation_id = d.id WHERE d.title = 'Senior Software Engineer'
- Find 3 SSEs with React skills: SELECT e.id, u.email, d.title FROM employees e JOIN users u ON e.user_id = u.id JOIN designations d ON e.designation_id = d.id JOIN employee_skills es ON e.id = es.employee_id WHERE d.title = 'Senior Software Engineer' AND es.skill_name = 'React' LIMIT 3
- Resource utilization for customer projects: SELECT e.name, SUM(CAST(a.percent_allocated AS INTEGER)) as total_utilization FROM employees e JOIN allocations a ON e.id = a.employee_id JOIN projects p ON a.project_id = p.id WHERE p.project_type = 'customer' AND a.status = 'active' GROUP BY e.id, e.name

INSERT Examples:
- Create project: INSERT INTO projects (id, name, duration_months, project_type, status, created_at, updated_at) VALUES (gen_random_uuid(), 'Project X', 6, 'customer', 'planning', NOW(), NOW())

UPDATE Examples:
- Update allocation: UPDATE allocations SET percent_allocated = 'HALF' WHERE employee_id = (SELECT id FROM employees WHERE name = 'Jatin Gandhi') AND project_id = (SELECT id FROM projects WHERE name = 'ABC')

Generate the SQL query now:""",
        )

    @staticmethod
    def get_query_validation_prompt() -> PromptTemplate:
        """Get the query validation prompt template."""
        return PromptTemplate(
            input_variables=["query", "schema"],
            template="""You are a PostgreSQL SQL validation expert. Validate and fix the provided SQL query.

Database Schema:
{schema}

SQL Query to Validate:
{query}

VALIDATION CHECKLIST:
1. ✓ All table names exist in the schema above
2. ✓ All column names exist in their respective tables
3. ✓ JOIN conditions use correct foreign key relationships
4. ✓ Data types are handled correctly (UUID, ENUM, etc.)
5. ✓ Syntax is valid PostgreSQL
6. ✓ Performance considerations (indexes, unnecessary JOINs)

COMMON ISSUES TO FIX:
- Non-existent table or column names
- Incorrect JOIN conditions
- Missing table aliases in multi-table queries
- Wrong data type handling
- Inefficient query patterns

RESPONSE FORMAT:
Return ONLY the corrected SQL query without any explanation, analysis, or markdown formatting.
If the query is already correct, return it unchanged.

Corrected SQL Query:""",
        )

    @staticmethod
    def get_schema_validation_rules() -> str:
        """Get the schema validation rules as a string."""
        return """
SCHEMA VALIDATION RULES:
1. Table names must exist in the schema
2. Column names must exist in their respective tables
3. JOIN conditions must use valid foreign key relationships
4. ENUM values must match exactly as defined
5. UUID columns are used for primary keys and foreign keys
6. Use proper PostgreSQL syntax for all operations
"""
