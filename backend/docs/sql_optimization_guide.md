# SQL Query Optimization Guide

## Overview
This guide documents best practices for writing optimized SQL queries in the ResourceWise system, with special focus on avoiding common performance pitfalls.

## 🚨 Critical Issue: JOIN Multiplication with employee_skills

### The Problem
When joining `employees` with `employee_skills`, each employee appears **multiple times** in the result set (once per skill they have). This causes:

- **Incorrect result counts**: 370 results instead of 200 employees
- **Performance degradation**: Unnecessary data processing
- **Memory waste**: Duplicate employee information

### ❌ Problematic Pattern
```sql
-- BAD: Causes join multiplication
SELECT DISTINCT e.name, d.title 
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
JOIN employee_skills es ON e.id = es.employee_id 
WHERE es.skill_name IN ('React', 'JavaScript', 'Python');
```

**Result**: Employee with React, JavaScript, and Python skills appears 3 times!

### ✅ Optimized Solutions

#### Solution 1: EXISTS Subquery (For Employee Filtering Only)
```sql
-- GOOD: One row per employee, optimal performance
-- Use when you DON'T need skill details in the result
SELECT e.name, d.title 
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
WHERE e.is_active = TRUE 
AND EXISTS (
    SELECT 1 FROM employee_skills es 
    WHERE es.employee_id = e.id 
    AND es.skill_name IN ('React', 'JavaScript', 'Python')
);
```

#### Solution 2: JOIN + GROUP BY (When You Need Skill Details)
```sql
-- GOOD: When you need skill details in the result
-- Prevents duplicates with proper GROUP BY
SELECT e.name, d.title, 
       STRING_AGG(es.skill_name, ', ') as skills,
       STRING_AGG(es.experience_months::text, ', ') as experience_months
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
JOIN employee_skills es ON e.id = es.employee_id 
WHERE e.is_active = TRUE 
AND es.skill_name IN ('React', 'JavaScript', 'Python')
GROUP BY e.id, e.name, d.title;
```

#### ❌ Common Mistake: Mixing EXISTS with Skill Details
```sql
-- BAD: Can't reference es.skill_name when es is only in EXISTS subquery
SELECT e.name, d.title, es.skill_name  -- ❌ ERROR: es not available here
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
WHERE EXISTS (
    SELECT 1 FROM employee_skills es 
    WHERE es.employee_id = e.id 
    AND es.skill_name IN ('React', 'JavaScript')
);
```

## 🎯 Query Optimization Patterns

### 1. Employee Skill Queries
```sql
-- Find employees with specific skills
SELECT e.name, d.title 
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
WHERE e.is_active = TRUE 
AND EXISTS (
    SELECT 1 FROM employee_skills es 
    WHERE es.employee_id = e.id 
    AND es.skill_name IN ('React', 'Vue', 'Angular')
);
```

### 2. Mixed Role + Skill Queries
```sql
-- Find specific roles with specific skills
SELECT e.name, d.title 
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
WHERE d.title = 'Senior Software Engineer' 
AND e.is_active = TRUE 
AND EXISTS (
    SELECT 1 FROM employee_skills es 
    WHERE es.employee_id = e.id 
    AND es.skill_name IN ('Java', 'Python', 'Node.js')
);
```

### 3. Availability Queries

#### ✅ Simple Availability Check (No Skill Details)
```sql
-- Find available employees with skills (no skill details needed)
SELECT e.name, d.title 
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
WHERE e.is_active = TRUE 
AND EXISTS (
    SELECT 1 FROM employee_skills es 
    WHERE es.employee_id = e.id 
    AND es.skill_name IN ('React', 'JavaScript')
)
AND e.id NOT IN (
    SELECT a.employee_id 
    FROM allocations a 
    WHERE a.status = 'ACTIVE' 
    GROUP BY a.employee_id 
    HAVING SUM(CAST(a.percent_allocated AS INTEGER)) >= 100
);
```

#### ✅ Detailed Availability Query (With Skill Details)
```sql
-- Find available employees with skill details
SELECT e.name, d.title, 
       STRING_AGG(es.skill_name, ', ') as skills,
       (100 - COALESCE(SUM(CAST(a.percent_allocated AS INTEGER)), 0)) AS available_percentage
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
JOIN employee_skills es ON e.id = es.employee_id 
LEFT JOIN allocations a ON e.id = a.employee_id AND a.status = 'ACTIVE'
WHERE e.is_active = TRUE 
AND es.skill_name IN ('React', 'JavaScript')
GROUP BY e.id, e.name, d.title
HAVING COALESCE(SUM(CAST(a.percent_allocated AS INTEGER)), 0) < 100;
```

#### ❌ Common Availability Mistakes
```sql
-- BAD: Wrong HAVING logic (shows 100% allocated employees!)
HAVING (100 - SUM(allocation)) > 0

-- BAD: Wrong enum case
WHERE a.status = 'active'  -- Should be 'ACTIVE'

-- BAD: Missing CAST for integer math
SUM(a.percent_allocated)  -- Should be SUM(CAST(a.percent_allocated AS INTEGER))
```

### 4. Complex Project Queries
```sql
-- Find employees working on projects with specific skills
SELECT e.name, d.title, p.name 
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
JOIN allocations a ON e.id = a.employee_id 
JOIN projects p ON a.project_id = p.id 
WHERE d.title IN ('Senior Software Engineer', 'Technical Lead') 
AND p.project_type = 'customer' 
AND a.status = 'active' 
AND e.is_active = TRUE 
AND EXISTS (
    SELECT 1 FROM employee_skills es 
    WHERE es.employee_id = e.id 
    AND es.skill_name IN ('Java', 'Python', 'Node.js')
)
GROUP BY e.id, e.name, d.title, p.id, p.name;
```

## 📊 Performance Best Practices

### 1. Always Filter Active Records
```sql
-- Always include active filters
WHERE e.is_active = TRUE 
AND a.status = 'active'  -- for allocations
AND p.status = 'active'  -- for projects
```

### 2. Use Proper Indexes
The system has optimized indexes for:
- `employee_skills(employee_id, skill_name)`
- `employees(is_active)`
- `allocations(employee_id, status)`
- `designations(title)`

### 3. Avoid SELECT *
```sql
-- BAD: Retrieves unnecessary data
SELECT * FROM employees e JOIN employee_skills es ON ...

-- GOOD: Select only needed columns
SELECT e.name, e.email, d.title FROM employees e ...
```

### 4. Use LIMIT for Large Results
```sql
-- Add LIMIT for user-facing queries
SELECT e.name, d.title 
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
WHERE e.is_active = TRUE 
LIMIT 100;
```

## 🔍 Common Anti-Patterns to Avoid

### 1. ❌ Cartesian Products
```sql
-- BAD: Missing JOIN condition
SELECT e.name, es.skill_name 
FROM employees e, employee_skills es;
```

### 2. ❌ N+1 Query Pattern
```sql
-- BAD: Multiple queries in application code
SELECT * FROM employees WHERE is_active = TRUE;
-- Then for each employee:
SELECT * FROM employee_skills WHERE employee_id = ?;
```

### 3. ❌ Inefficient Subqueries
```sql
-- BAD: Correlated subquery in SELECT
SELECT e.name, 
       (SELECT COUNT(*) FROM employee_skills es WHERE es.employee_id = e.id) as skill_count
FROM employees e;

-- GOOD: Use JOIN with GROUP BY
SELECT e.name, COUNT(es.skill_name) as skill_count
FROM employees e 
LEFT JOIN employee_skills es ON e.id = es.employee_id 
GROUP BY e.id, e.name;
```

## 🧪 Testing Query Performance

### 1. Use EXPLAIN ANALYZE
```sql
EXPLAIN ANALYZE 
SELECT e.name, d.title 
FROM employees e 
JOIN designations d ON e.designation_id = d.id 
WHERE EXISTS (
    SELECT 1 FROM employee_skills es 
    WHERE es.employee_id = e.id 
    AND es.skill_name IN ('React', 'JavaScript')
);
```

### 2. Monitor Query Execution Time
- Target: < 100ms for simple queries
- Target: < 500ms for complex queries
- Alert: > 1000ms indicates optimization needed

### 3. Check Result Count Accuracy
```sql
-- Verify employee count matches expectation
SELECT COUNT(DISTINCT e.id) as unique_employees,
       COUNT(*) as total_rows
FROM employees e 
JOIN employee_skills es ON e.id = es.employee_id 
WHERE es.skill_name IN ('React', 'JavaScript');
```

## 📈 Monitoring and Alerts

### Key Metrics to Track
1. **Query execution time** > 1000ms
2. **Result count anomalies** (e.g., 370 results for 200 employees)
3. **Memory usage** during query execution
4. **Index usage** efficiency

### Performance Regression Detection
- Compare result counts before/after changes
- Monitor query execution plans
- Track database connection pool usage

## 🛠️ Tools and Resources

### Database Analysis Tools
- `EXPLAIN ANALYZE` for query plans
- `pg_stat_statements` for query statistics
- Database monitoring dashboards

### Code Review Checklist
- [ ] No `JOIN employee_skills` without proper GROUP BY
- [ ] EXISTS subqueries used for skill filtering
- [ ] Active record filters included
- [ ] Proper indexes utilized
- [ ] Result count validation performed

---

**Remember**: The goal is **one row per employee** in employee-centric queries. Use EXISTS subqueries to avoid join multiplication! 