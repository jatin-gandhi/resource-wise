-- Enable the vector extension for the current database
CREATE EXTENSION IF NOT EXISTS vector;

--Create schema
CREATE SCHEMA IF NOT EXISTS resourcewise;

--Employee
CREATE TABLE IF NOT EXISTS resourcewise.employee (
  id UUID PRIMARY KEY,
  name TEXT,
  designation TEXT,  -- TL, SSE, SD, etc.
  capacity_percent INT, -- e.g. 100, 70, 50
  onboarded_at DATE,
  is_active BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
--PAT Skill Record
CREATE TABLE IF NOT EXISTS resourcewise.employee_skill (
  id UUID PRIMARY KEY,
  employee_id UUID ,
  skill_name TEXT,
  summary TEXT,
  experience_months INT,
  last_used DATE,
  source TEXT,  -- 'PAT', etc.
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (employee_id) REFERENCES resourcewise.employee(id)
);
--Skill Embeddings
CREATE TABLE resourcewise.employee_embedding (
  employee_id UUID,
  source TEXT,
  summary TEXT,
  embedding VECTOR(1536),
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  PRIMARY KEY (employee_id, source),
  FOREIGN KEY (employee_id) REFERENCES resourcewise.employee(id)
);
--Project
CREATE TABLE resourcewise.project (
  id UUID PRIMARY KEY,
  name TEXT,
  description TEXT,
  duration_months INT,
  tech_stack TEXT[],
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
--Allocation
CREATE TABLE resourcewise.allocation (
  id UUID PRIMARY KEY,
  project_id UUID,
  employee_id UUID,
  percent_allocated INT,
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (employee_id) REFERENCES resourcewise.employee(id),
  FOREIGN KEY (project_id) REFERENCES resourcewise.project(id)
);
