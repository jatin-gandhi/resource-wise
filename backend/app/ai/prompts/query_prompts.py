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

STEP 4: ANALYZE RESOLVED TERMS AND SEPARATE BY TYPE

CRITICAL: When resolved terms contain both skills and roles, you must separate them:

ROLE IDENTIFICATION (Job titles/designations):
- Contains words like: "Engineer", "Developer", "Manager", "Lead", "Architect", "Designer", "Analyst", "Officer", "Intern"
- Examples: "Senior Software Engineer", "UX Designer", "Technical Lead", "Project Manager", "Quality Assurance Engineer"

TEAM-RELEVANT ROLE FILTERING:
- For team queries, be HIGHLY SELECTIVE about which roles are actually relevant to the specific team
- DESIGN TEAM: "UX Designer", "UI Designer", "Product Designer", "Graphic Designer"
- QA/TESTING TEAM: "Quality Assurance Engineer", "Senior Quality Assurance Engineer", "Quality Assurance Intern", "Test Engineer"
- BACKEND TEAM: "Backend Developer", "Backend Engineer", "Senior Backend Developer", "API Developer"
- FRONTEND TEAM: "Frontend Developer", "Frontend Engineer", "Senior Frontend Developer", "UI Developer"
- MOBILE TEAM: "Mobile Developer", "iOS Developer", "Android Developer", "Mobile Engineer"
- DEVOPS TEAM: "DevOps Engineer", "Site Reliability Engineer", "Infrastructure Engineer"
- DATA TEAM: "Data Engineer", "Data Scientist", "Data Analyst", "ML Engineer"

GENERIC ROLES TO AVOID FOR TEAM QUERIES:
- Avoid including generic roles like "Software Engineer", "Senior Software Engineer", "Technical Lead", "Software Architect" unless they are specifically mentioned in the team context
- These generic roles could belong to any team, so they dilute the team-specific results

SKILL IDENTIFICATION (Technical abilities/tools):
- Programming languages: "Java", "Python", "JavaScript", "React", "Vue", "Angular"
- Tools/Technologies: "Docker", "AWS", "Figma", "Git", "PostgreSQL", "Jenkins"
- Frameworks: "Spring Boot", "Django", "Express.js", "Next.js"

SEPARATION STRATEGY:
- For TEAM queries: Extract ONLY roles from resolved terms, ignore skills completely
- For SKILL queries: Extract ONLY skills from resolved terms, ignore roles
- For MIXED queries: Use both roles AND skills with appropriate logic

STEP 5: APPLY OPERATION-SPECIFIC PATTERNS

SELECT PATTERNS:
1. TEAM QUERIES (ROLE-FOCUSED):
   - Keywords: "team", "members of", "who's on", "people in", "[role] team"
   - CRITICAL: For team queries, ONLY use job titles/roles from resolved terms, IGNORE skills
   - CRITICAL: Be SELECTIVE about which roles are relevant to the specific team
   - Filter EXCLUSIVELY by d.title using ONLY team-relevant roles from resolved values
   
   TEAM-SPECIFIC ROLE FILTERING:
   - "design team" → ONLY roles related to design: "UX Designer", "UI Designer", "Product Designer"
   - "QA team" → ONLY roles related to testing: "Quality Assurance Engineer", "Senior Quality Assurance Engineer", "Quality Assurance Intern"  
   - "backend team" → ONLY roles related to backend: "Backend Developer", "Senior Backend Developer", "Backend Engineer"
   - "frontend team" → ONLY roles related to frontend: "Frontend Developer", "Senior Frontend Developer", "Frontend Engineer"
   - "mobile team" → ONLY roles related to mobile: "Mobile Developer", "iOS Developer", "Android Developer"
   
   DO NOT include generic roles like "Software Engineer", "Senior Software Engineer", "Technical Lead" unless they are specifically relevant to the team context.
   
   - Example: "Give me members of design team" + resolved_terms: {{"design team": ["Figma", "HTML/CSS", "UX Designer", "Software Architect", "Senior Software Engineer"]}}
     → Extract ONLY design-relevant roles: ["UX Designer"] → WHERE d.title = 'UX Designer'
   - Example: "Show QA team" + resolved_terms: {{"QA team": ["TestNG", "Quality Assurance Engineer", "Senior Quality Assurance Engineer", "Software Engineer"]}}
     → Extract ONLY QA-relevant roles: ["Quality Assurance Engineer", "Senior Quality Assurance Engineer"] → WHERE d.title IN ('Quality Assurance Engineer', 'Senior Quality Assurance Engineer')

2. SKILL QUERIES (SKILL-FOCUSED):
   - Keywords: "with skills", "expertise in", "who knows", "experienced in"
   - Filter by es.skill_name using skill-related resolved values
   - Example: "Find React experts" + resolved_terms: {{"react": ["React"]}}
     → WHERE es.skill_name = 'React'
   - Example: "Developers with frontend skills" + resolved_terms: {{"frontend": ["React", "Vue", "Angular"]}}
     → WHERE es.skill_name IN ('React', 'Vue', 'Angular')

3. MIXED QUERIES (BOTH ROLES AND SKILLS):
   - When multiple fuzzy terms are resolved, combine conditions appropriately
   - Example: "Find senior frontend developers" + resolved_terms: {{"senior": ["Senior Software Engineer"], "frontend": ["React", "Vue"]}}
     → WHERE d.title = 'Senior Software Engineer' AND es.skill_name IN ('React', 'Vue')

4. ALLOCATION QUERIES:
   - For allocation analysis, join employees, allocations, and projects tables
   - AllocationPercentage is an ENUM that needs to be cast to integer for calculations
   - CRITICAL: Use CAST(a.percent_allocated AS INTEGER) for SUM operations
   - For overallocation queries: SUM(CAST(a.percent_allocated AS INTEGER)) > 100
   - For available employees: SUM(CAST(a.percent_allocated AS INTEGER)) < 100

5. AVAILABILITY QUERIES:
   - "available", "who is available", "free" → Filter employees with total allocation < 100%
   
   PARTIAL AVAILABILITY LOGIC:
   - "available at least X%" means "allocated at most (100-X)%"
   - "available at least 25%" → allocated ≤ 75% → HAVING SUM(percent_allocated) <= 75
   - "available at least 50%" → allocated ≤ 50% → HAVING SUM(percent_allocated) <= 50
   - "available 100%" → allocated = 0% → completely unallocated
   
   - CURRENT AVAILABILITY: Use subquery to calculate total allocation per employee:
     ```sql
     WHERE e.id NOT IN (
       SELECT a.employee_id 
       FROM allocations a 
       WHERE a.status = 'active' 
       GROUP BY a.employee_id 
       HAVING SUM(CAST(a.percent_allocated AS INTEGER)) >= 100
     )
     ```
   - FUTURE AVAILABILITY: For "next month", "next week", etc., check if employee has NO allocations during that future period:
     ```sql
     WHERE e.id NOT IN (
       SELECT a.employee_id 
       FROM allocations a 
       WHERE a.status = 'active' 
       AND a.start_date <= (CURRENT_DATE + INTERVAL '1 month')
       AND a.end_date >= CURRENT_DATE + INTERVAL '1 month'
     )
     ```
   - For "available 100%" queries, check if employee is completely unallocated during the period
   - For partial availability like "available at least 25%", use HAVING SUM(percent_allocated) <= (100 - 25) = 75
   - "Available at least X%" means "allocated at most (100-X)%"
   - When showing current allocations, use SUM(percent_allocated) to get total allocation per employee
   
   ALLOCATION DISPLAY QUERIES:
   - "with their current allocation", "show allocation" → Use LEFT JOIN and GROUP BY with SUM()
   - Use COALESCE(SUM(percent_allocated), 0) to handle employees with no allocations
   - Always GROUP BY employee fields when using SUM() for allocations
   - Use LEFT JOIN allocations (not INNER JOIN) to include unallocated employees
   
   - CRITICAL: Never use aggregate functions like SUM() in WHERE clause - always use HAVING with GROUP BY
   - Always include `e.is_active = TRUE` for active employees only

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
   - CRITICAL: Always use SELECT DISTINCT when joining with employee_skills to avoid duplicate employees
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

Example 1 - Team Query (Role-focused):
User Query: "Give me members of design team"
Resolved Terms: {{"design team": ["Figma", "HTML/CSS", "UX Designer", "Software Architect", "Technical Lead", "Senior Software Engineer"]}}
Analysis: TEAM query → Extract ONLY design-relevant roles: ["UX Designer"] (ignore generic roles like "Software Architect", "Technical Lead", "Senior Software Engineer")
SQL: SELECT e.name, d.title FROM employees e JOIN designations d ON e.designation_id = d.id WHERE d.title = 'UX Designer';

Example 2 - Skill Query (Skill-focused):
User Query: "Find developers with React experience"
Resolved Terms: {{"developers": ["React", "JavaScript", "Senior Software Engineer", "Software Engineer"]}}
Analysis: SKILL query → Extract ONLY skills: ["React", "JavaScript"]
SQL: SELECT DISTINCT e.name, d.title FROM employees e JOIN designations d ON e.designation_id = d.id JOIN employee_skills es ON e.id = es.employee_id WHERE es.skill_name IN ('React', 'JavaScript');

Example 3 - Mixed Query (Both roles and skills):
User Query: "Find senior frontend developers"
Resolved Terms: {{"senior": ["Senior Software Engineer"], "frontend": ["React", "Vue", "Angular"]}}
Analysis: MIXED query → Use roles: ["Senior Software Engineer"] AND skills: ["React", "Vue", "Angular"]
SQL: SELECT DISTINCT e.name, d.title FROM employees e JOIN designations d ON e.designation_id = d.id JOIN employee_skills es ON e.id = es.employee_id WHERE d.title = 'Senior Software Engineer' AND es.skill_name IN ('React', 'Vue', 'Angular');

Example 4 - Current Availability Query:
User Query: "Give me SSE who is available with backend skills"
Resolved Terms: {{"SSE": ["Senior Software Engineer"], "backend": ["Java", "Python", "Node.js"]}}
Analysis: MIXED query with CURRENT AVAILABILITY → Use roles + skills + current availability check
SQL: SELECT DISTINCT e.name, d.title FROM employees e JOIN designations d ON e.designation_id = d.id JOIN employee_skills es ON e.id = es.employee_id WHERE d.title = 'Senior Software Engineer' AND es.skill_name IN ('Java', 'Python', 'Node.js') AND e.is_active = TRUE AND e.id NOT IN (SELECT a.employee_id FROM allocations a WHERE a.status = 'active' GROUP BY a.employee_id HAVING SUM(CAST(a.percent_allocated AS INTEGER)) >= 100);

Example 5 - Future 100% Availability Query:
User Query: "Is Tyler available 100% for next month?"
Analysis: FUTURE AVAILABILITY query → Check if Tyler has NO allocations during next month period
SQL: SELECT e.name, e.email FROM employees e WHERE e.name = 'Tyler' AND e.is_active = TRUE AND e.id NOT IN (SELECT a.employee_id FROM allocations a WHERE a.status = 'active' AND a.start_date <= (CURRENT_DATE + INTERVAL '1 month') AND a.end_date >= (CURRENT_DATE + INTERVAL '1 month'));

Example 6 - Current Partial Availability with Allocation Display:
User Query: "Give me TLs who are available at least 25% along with their current allocation"
Analysis: PARTIAL AVAILABILITY + ALLOCATION DISPLAY → Show TLs allocated ≤ 75% with their total allocation
SQL: SELECT e.name, d.title, COALESCE(SUM(CAST(a.percent_allocated AS INTEGER)), 0) as total_allocation FROM employees e JOIN designations d ON e.designation_id = d.id LEFT JOIN allocations a ON e.id = a.employee_id AND a.status = 'active' WHERE d.title = 'Technical Lead' AND e.is_active = TRUE GROUP BY e.id, e.name, d.title HAVING COALESCE(SUM(CAST(a.percent_allocated AS INTEGER)), 0) <= 75;

Example 7 - Future Partial Availability Query:
User Query: "Who is available at least 50% next week?"
Analysis: FUTURE PARTIAL AVAILABILITY → Check employees with ≤ 50% allocation next week
SQL: SELECT e.name, e.email FROM employees e WHERE e.is_active = TRUE AND e.id NOT IN (SELECT a.employee_id FROM allocations a WHERE a.status = 'active' AND a.start_date <= (CURRENT_DATE + INTERVAL '1 week') AND a.end_date >= (CURRENT_DATE + INTERVAL '1 week') GROUP BY a.employee_id HAVING SUM(CAST(a.percent_allocated AS INTEGER)) > 50);

Example 8 - Complex Project Query:
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

CRITICAL TEAM QUERY VALIDATION:
- For TEAM queries (containing "team", "members of", "who's on"), validate that ONLY team-relevant roles are used
- DESIGN TEAM: Only "UX Designer", "UI Designer", "Product Designer" - NOT generic roles
- QA TEAM: Only "Quality Assurance Engineer", "Senior Quality Assurance Engineer", "Quality Assurance Intern"
- BACKEND TEAM: Only "Backend Developer", "Backend Engineer", "Senior Backend Developer" - NOT skills like "Java", "Python"
- DO NOT "correct" team queries by adding generic roles like "Software Engineer", "Senior Software Engineer", "Technical Lead"
- DO NOT use skills (programming languages, tools) as job titles in d.title conditions
- If the original query correctly filters by specific team roles, DO NOT expand it to include all resolved terms

COMMON ISSUES TO FIX:
- Non-existent table or column names
- Incorrect JOIN conditions
- Missing table aliases in multi-table queries
- Wrong data type handling
- Inefficient query patterns
- Incorrect use of resolved fuzzy terms
- Missing IN clauses for multiple resolved values
- Missing DISTINCT when joining with employee_skills (causes duplicate employees)
- Incorrect availability logic (should be simple allocation < 100% check)
- Using skills as job titles in d.title conditions
- CRITICAL: Aggregate functions (SUM, COUNT, etc.) in WHERE clause - must use HAVING with GROUP BY instead
- Future availability queries with incorrect date logic

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
