"""Fuzzy-enhanced query generation prompts.

This file contains prompt templates for SQL query generation with fuzzy term resolution.
Excluded from linting to preserve natural language formatting.
"""

from langchain_core.prompts import PromptTemplate


class QueryPrompts:
    """Container for fuzzy-enhanced query prompt templates."""

    @staticmethod
    def get_fuzzy_enhanced_query_prompt() -> PromptTemplate:
        """Get the fuzzy-enhanced query generation prompt template."""
        return PromptTemplate(
            input_variables=["raw_query", "schema", "resolved_terms", "parameters"],
            template="""You are a PostgreSQL SQL query generation expert with fuzzy term resolution capabilities. Generate ONLY valid SQL queries based on the provided schema and resolved fuzzy terms.

Database Schema:
{schema}

User Request: {raw_query}
Additional Context: {parameters}

RESOLVED FUZZY TERMS:
{resolved_terms}

STEP 1: INTELLIGENT FUZZY CONTEXT ANALYSIS
Analyze the resolved fuzzy terms to understand their nature and determine the best filtering approach:

CONTEXT-AWARE TERM ANALYSIS:
- Examine each resolved term to determine if it's a role/designation or technical skill
- Job titles/roles: "Senior Software Engineer", "UX Designer", "Technical Lead", "Project Manager"
- Technical skills: "React", "Python", "AWS", "Docker", "PostgreSQL", "Figma"
- Let the content of resolved terms guide the SQL generation approach

INTELLIGENT FILTERING STRATEGY:
1. **Role-heavy resolved terms** → Primary filter: d.title IN (role_terms)
   - Example: "design team" resolves to ["UX Designer", "UI Designer"] → Filter by designations
   
2. **Skill-heavy resolved terms** → Primary filter: es.skill_name IN (skill_terms)
   - Example: "frontend experts" resolves to ["React", "Vue", "Angular"] → Filter by skills
   
3. **Mixed resolved terms** → Combine filters: d.title AND es.skill_name
   - Example: "senior React developers" resolves to ["Senior Software Engineer", "React"] → Filter by both
   
4. **Context clues from original query**:
   - "team", "members", "people in" → Lean towards role-based filtering
   - "with skills", "expertise in", "who knows" → Lean towards skill-based filtering
   - Let resolved terms override context clues when clear

FLEXIBLE MAPPING EXAMPLES:
- "SSE" → ["Senior Software Engineer"] → d.title = 'Senior Software Engineer'
- "design team" → ["UX Designer"] → d.title = 'UX Designer' 
- "React developers" → ["React"] → es.skill_name = 'React'
- "senior frontend" → ["Senior Software Engineer", "React", "Vue"] → d.title = 'Senior Software Engineer' AND es.skill_name IN ('React', 'Vue')

STEP 2: DETERMINE SQL OPERATION TYPE
Analyze the user request to determine what SQL operation is needed:
- SELECT: "find", "show", "get", "list", "tell me", "what are", "how many"
- INSERT: "create", "add", "new", "insert"  
- UPDATE: "update", "change", "modify", "set", "assign"
- DELETE: "delete", "remove", "drop"

STEP 3: FOLLOW CRITICAL RULES
1. ONLY use table names and column names that exist in the provided schema above
2. NEVER invent or assume column names that are not explicitly listed in the schema
3. Use proper PostgreSQL syntax and data types
4. Always use table aliases for multi-table queries
5. Use appropriate JOIN types based on the relationship requirements
6. Handle UUID columns properly (they are primary keys in this schema)
7. For ENUM columns, use ONLY the exact values listed in the schema
8. PRIORITIZE resolved fuzzy terms over literal text matching
9. CRITICAL: NEVER query the 'users' table directly for person-related information
   - The 'users' table is for application authentication only
   - For ANY person/employee-related queries, ALWAYS use the 'employees' table
   - Join employees with users only when you need email/authentication info
   - Example: "Find John Doe" → Query employees table, not users table

ENUM VALUE RULES:
- ProjectStatus: Use 'planning', 'active', 'on_hold', 'completed', 'cancelled'
- AllocationStatus: Use 'active', 'completed', 'cancelled'  
- AllocationPercentage: Use 25, 50, 75, 100 (integer numbers, not strings)
- SkillProficiencyLevel: Use 1, 2, 3, 4, 5 (numbers)
- ProjectType: Use 'customer', 'internal' (lowercase strings)

DESIGNATION TABLE STRUCTURE:
- designations.code: Short codes like 'SSE', 'TL', 'PM', 'SDE'
- designations.title: Full titles like 'Senior Software Engineer', 'Technical Lead', 'Project Manager'

FUZZY TERM RESOLUTION PRIORITY:
- When fuzzy terms are resolved, ALWAYS use the resolved values instead of the original fuzzy terms
- For multiple resolved values, use IN clauses: WHERE column IN ('value1', 'value2', 'value3')
- For single resolved values, use equality: WHERE column = 'resolved_value'
- Combine multiple fuzzy term conditions with AND/OR based on query context

STEP 4: APPLY OPERATION-SPECIFIC PATTERNS

SELECT PATTERNS:
1. INTELLIGENT ROLE-BASED FILTERING:
   - When resolved terms contain job titles/designations, filter by d.title
   - Use context clues: "team", "members", "people in" suggest role-based filtering
   - Example: "Give me members of design team" + resolved_terms: {{"design": ["UX Designer"]}}
     → WHERE d.title = 'UX Designer'
   - Example: "Show QA team" + resolved_terms: {{"qa": ["Quality Assurance Engineer", "Senior Quality Assurance Engineer"]}}
     → WHERE d.title IN ('Quality Assurance Engineer', 'Senior Quality Assurance Engineer')

2. INTELLIGENT SKILL-BASED FILTERING:
   - When resolved terms contain technical skills, filter by es.skill_name
   - Use context clues: "with skills", "expertise in", "who knows" suggest skill-based filtering
   - Example: "Find React experts" + resolved_terms: {{"react": ["React"]}}
     → WHERE es.skill_name = 'React'
   - Example: "Developers with frontend skills" + resolved_terms: {{"frontend": ["React", "Vue", "Angular"]}}
     → WHERE es.skill_name IN ('React', 'Vue', 'Angular')

3. INTELLIGENT MIXED FILTERING:
   - When multiple fuzzy terms are resolved, combine conditions appropriately
   - Example: "Find senior frontend developers" + resolved_terms: {{"senior": ["Senior Software Engineer"], "frontend": ["React", "Vue"]}}
     → WHERE d.title = 'Senior Software Engineer' AND es.skill_name IN ('React', 'Vue')

4. ALLOCATION QUERIES:
   - For allocation analysis, join employees, allocations, and projects tables
   - AllocationPercentage is an ENUM that needs to be cast to integer for calculations
   - CRITICAL: Use CAST(a.percent_allocated AS INTEGER) for SUM operations
   - For overallocation queries: SUM(CAST(a.percent_allocated AS INTEGER)) > 100
   - For available employees: SUM(CAST(a.percent_allocated AS INTEGER)) < 100

5. PROJECT QUERIES:
   - Use projects.status for filtering active/completed projects  
   - Use projects.project_type for customer/internal filtering
   - Remember: project_type values are 'customer' and 'internal' (lowercase)

6. RESOURCE UTILIZATION QUERIES:
   - Join allocations + employees + projects for utilization analysis
   - Use SUM(CAST(a.percent_allocated AS INTEGER)) for total allocation calculations
   - GROUP BY employee or project for aggregated views
   - Filter by project_type = 'customer' for customer project utilization

7. SKILL-BASED EMPLOYEE SEARCH WITH FUZZY TERMS:
   - Join employees + designations + employee_skills for complex filtering
   - Use resolved designation values: WHERE d.title IN (resolved_designations)
   - Use resolved skill values: WHERE es.skill_name IN (resolved_skills)
   - Consider using LIMIT for "find couple of" or "find 3" type requests

INSERT PATTERNS:
8. PROJECT CREATION:
   - INSERT INTO projects (name, duration_months, project_type, status, ...)
   - Set default values: status='planning', project_type='customer'
   - Generate UUID for id field

UPDATE PATTERNS:
9. ALLOCATION UPDATES:
   - UPDATE allocations SET percent_allocated = ... WHERE employee_id = ... AND project_id = ...
   - Convert percentage numbers to enum values (25→'QUARTER', 50→'HALF', 75→'THREE_QUARTER', 100→'FULL')
   - Use employee email or name to find employee_id
   - Use project name to find project_id

DELETE PATTERNS:
10. RECORD REMOVAL:
    - Always use specific WHERE clauses to avoid accidental mass deletions
    - Prefer soft deletes (UPDATE is_active = false) over hard deletes when possible

FUZZY QUERY EXAMPLES:

Example 1 - Simple Fuzzy Resolution:
User Query: "Find SSE with React skills"
Resolved Terms: {{"SSE": ["Senior Software Engineer"]}}
SQL: SELECT e.name, d.title FROM employees e JOIN designations d ON e.designation_id = d.id JOIN employee_skills es ON e.id = es.employee_id WHERE d.title = 'Senior Software Engineer' AND es.skill_name = 'React';

Example 2 - Multiple Fuzzy Terms:
User Query: "Show senior frontend developers"
Resolved Terms: {{"senior": ["Senior Software Engineer"], "frontend": ["React", "Vue", "Angular"]}}
SQL: SELECT e.name, d.title FROM employees e JOIN designations d ON e.designation_id = d.id JOIN employee_skills es ON e.id = es.employee_id WHERE d.title = 'Senior Software Engineer' AND es.skill_name IN ('React', 'Vue', 'Angular');

Example 3 - Complex Fuzzy Query:
User Query: "Find experienced backend engineers working on customer projects"
Resolved Terms: {{"experienced": ["Senior Software Engineer", "Technical Lead"], "backend": ["Java", "Python", "Node.js"]}}
SQL: SELECT DISTINCT e.name, d.title, p.project_name FROM employees e JOIN designations d ON e.designation_id = d.id JOIN employee_skills es ON e.id = es.employee_id JOIN allocations a ON e.id = a.employee_id JOIN projects p ON a.project_id = p.id WHERE d.title IN ('Senior Software Engineer', 'Technical Lead') AND es.skill_name IN ('Java', 'Python', 'Node.js') AND p.project_type = 'customer' AND a.status = 'active';

RESPONSE FORMAT:
- Return ONLY the SQL query
- NO explanations, comments, or additional text
- Use proper indentation and formatting
- End with semicolon
- Prioritize resolved fuzzy terms over literal text matching

Generate the SQL query now:""",
        )

    @staticmethod
    def get_fuzzy_query_validation_prompt() -> PromptTemplate:
        """Get the fuzzy query validation prompt template."""
        return PromptTemplate(
            input_variables=["query", "schema", "resolved_terms"],
            template="""You are a PostgreSQL SQL validation expert with fuzzy term resolution awareness. Validate and fix the provided SQL query.

Database Schema:
{schema}

RESOLVED FUZZY TERMS:
{resolved_terms}

SQL Query to Validate:
{query}

VALIDATION CHECKLIST:
1. ✓ All table names exist in the schema above
2. ✓ All column names exist in their respective tables
3. ✓ JOIN conditions use correct foreign key relationships
4. ✓ Data types are handled correctly (UUID, ENUM, etc.)
5. ✓ Syntax is valid PostgreSQL
6. ✓ Performance considerations (indexes, unnecessary JOINs)
7. ✓ Resolved fuzzy terms are used correctly in WHERE clauses
8. ✓ Multiple resolved values use IN clauses appropriately
9. ✓ Single resolved values use equality conditions

FUZZY TERM VALIDATION:
- Ensure resolved fuzzy terms are properly incorporated into WHERE conditions
- Verify that IN clauses are used for multiple resolved values
- Check that equality conditions are used for single resolved values
- Confirm that fuzzy term resolution takes priority over literal text matching

COMMON ISSUES TO FIX:
- Non-existent table or column names
- Incorrect JOIN conditions
- Missing table aliases in multi-table queries
- Wrong data type handling
- Inefficient query patterns
- Incorrect use of resolved fuzzy terms
- Missing IN clauses for multiple resolved values

RESPONSE FORMAT:
Return ONLY the corrected SQL query without any explanation, analysis, or markdown formatting.
If the query is already correct, return it unchanged.

Corrected SQL Query:""",
        )

    @staticmethod
    def get_query_explanation_prompt() -> PromptTemplate:
        """Get the query explanation prompt template for human-in-the-loop reviews."""
        return PromptTemplate(
            input_variables=["query", "schema", "resolved_terms"],
            template="""You are an expert PostgreSQL tutor. Explain in plain English what the following SQL query is doing, including any fuzzy term resolutions that were applied.

Database Schema:
{schema}

RESOLVED FUZZY TERMS (if any):
{resolved_terms}

SQL Query:
{query}

EXPLANATION REQUIREMENTS:
1. Start with a high-level summary of what the query does
2. Explain each major clause (SELECT, FROM, JOIN, WHERE, GROUP BY, ORDER BY)
3. If fuzzy terms were resolved, explain how they were interpreted
4. Mention any business logic or domain-specific patterns
5. Use simple, non-technical language where possible
6. Highlight any potential performance considerations

Explanation:""",
        )
