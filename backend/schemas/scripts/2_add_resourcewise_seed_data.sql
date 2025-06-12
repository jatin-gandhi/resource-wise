-- =====================================================
-- ResourceWise Database Seed Data - Enhanced Version
-- =====================================================

-- Clear existing data (for fresh start)
TRUNCATE TABLE resourcewise.allocation CASCADE;
TRUNCATE TABLE resourcewise.employee_skill CASCADE;
TRUNCATE TABLE resourcewise.employee_embedding CASCADE;
TRUNCATE TABLE resourcewise.project CASCADE;
TRUNCATE TABLE resourcewise.employee CASCADE;

-- =====================================================
-- EMPLOYEES DATA (50 employees with varied profiles)
-- =====================================================

INSERT INTO resourcewise.employee (id, name, designation, capacity_percent, onboarded_at, is_active) VALUES
-- Architects (2)
('550e8400-e29b-41d4-a716-446655440001', 'Rajesh Tiwari', 'Architect', 100, '2018-03-15', true),
('550e8400-e29b-41d4-a716-446655440002', 'Priya Sharma', 'Architect', 100, '2019-08-22', true),

-- Principal Engineers (2)
('550e8400-e29b-41d4-a716-446655440003', 'Amit Singh', 'PE', 100, '2019-01-10', true),
('550e8400-e29b-41d4-a716-446655440004', 'Sneha Patel', 'PE', 100, '2020-06-01', true),

-- Tech Leads (4)
('550e8400-e29b-41d4-a716-446655440005', 'Vikram Reddy', 'TL', 100, '2020-11-18', true),
('550e8400-e29b-41d4-a716-446655440006', 'Anita Gupta', 'TL', 100, '2021-02-14', true),
('550e8400-e29b-41d4-a716-446655440007', 'Karthik Nair', 'TL', 75, '2021-09-07', true), -- Part-time
('550e8400-e29b-41d4-a716-446655440008', 'Deepika Joshi', 'TL', 100, '2021-05-12', true),

-- Senior Software Engineers (6)
('550e8400-e29b-41d4-a716-446655440009', 'Jatin Gandhi', 'SSE', 100, '2021-07-01', true),
('550e8400-e29b-41d4-a716-446655440010', 'Rohit Mehra', 'SSE', 100, '2021-04-25', true),
('550e8400-e29b-41d4-a716-446655440011', 'Ashutosh Sahay', 'SSE', 100, '2022-01-16', true),
('550e8400-e29b-41d4-a716-446655440012', 'Kavya Iyer', 'SSE', 50, '2021-10-08', true), -- Part-time
('550e8400-e29b-41d4-a716-446655440013', 'Rishav Chakraborty', 'SSE', 100, '2022-03-20', true),
('550e8400-e29b-41d4-a716-446655440014', 'Neha Saxena', 'SSE', 100, '2021-12-05', true),

-- Software Engineers (12)
('550e8400-e29b-41d4-a716-446655440015', 'Manish Verma', 'SE', 100, '2022-02-14', true),
('550e8400-e29b-41d4-a716-446655440016', 'Riya Bansal', 'SE', 100, '2022-06-01', true),
('550e8400-e29b-41d4-a716-446655440017', 'Harsh Jain', 'SE', 100, '2022-04-10', true),
('550e8400-e29b-41d4-a716-446655440018', 'Tanvi Rao', 'SE', 100, '2022-08-30', true),
('550e8400-e29b-41d4-a716-446655440019', 'Aakash Mishra', 'SE', 100, '2022-07-01', true),
('550e8400-e29b-41d4-a716-446655440020', 'Ishita Khanna', 'SE', 100, '2022-08-15', true),
('550e8400-e29b-41d4-a716-446655440021', 'Rohan Sinha', 'SE', 100, '2022-09-01', true),
('550e8400-e29b-41d4-a716-446655440022', 'Sakshi Tiwari', 'SE', 75, '2022-10-12', true), -- Part-time
('550e8400-e29b-41d4-a716-446655440023', 'Gaurav Chopra', 'SE', 100, '2022-04-20', true),
('550e8400-e29b-41d4-a716-446655440024', 'Nidhi Agarwal', 'SE', 100, '2022-11-08', true),
('550e8400-e29b-41d4-a716-446655440025', 'Varun Pandey', 'SE', 100, '2022-12-01', true),
('550e8400-e29b-41d4-a716-446655440026', 'Aditi Kulkarni', 'SE', 100, '2023-01-15', true),

-- Software Developers (18)
('550e8400-e29b-41d4-a716-446655440027', 'Nikhil Joshi', 'SD', 100, '2023-03-01', true),
('550e8400-e29b-41d4-a716-446655440028', 'Kriti Sharma', 'SD', 100, '2023-04-15', true),
('550e8400-e29b-41d4-a716-446655440029', 'Abhishek Kumar', 'SD', 100, '2023-05-20', true),
('550e8400-e29b-41d4-a716-446655440030', 'Shreya Gupta', 'SD', 100, '2023-06-10', true),
('550e8400-e29b-41d4-a716-446655440031', 'Rohit Singh', 'SD', 100, '2023-07-01', true),
('550e8400-e29b-41d4-a716-446655440032', 'Divya Patel', 'SD', 50, '2023-08-15', true), -- Part-time
('550e8400-e29b-41d4-a716-446655440033', 'Akshay Reddy', 'SD', 100, '2023-09-01', true),
('550e8400-e29b-41d4-a716-446655440034', 'Priyanka Das', 'SD', 100, '2023-10-12', true),
('550e8400-e29b-41d4-a716-446655440035', 'Sandeep Nair', 'SD', 100, '2023-11-01', true),
('550e8400-e29b-41d4-a716-446655440036', 'Meera Iyer', 'SD', 100, '2023-12-15', true),
('550e8400-e29b-41d4-a716-446655440037', 'Vishal Agarwal', 'SD', 100, '2024-01-10', true),
('550e8400-e29b-41d4-a716-446655440038', 'Pooja Verma', 'SD', 100, '2024-02-01', true),
('550e8400-e29b-41d4-a716-446655440039', 'Kiran Jain', 'SD', 100, '2024-02-20', true),
('550e8400-e29b-41d4-a716-446655440040', 'Swati Khanna', 'SD', 100, '2024-03-05', true),
('550e8400-e29b-41d4-a716-446655440041', 'Deepak Sinha', 'SD', 100, '2024-03-15', true),
('550e8400-e29b-41d4-a716-446655440042', 'Ritika Tiwari', 'SD', 100, '2024-04-01', true),
('550e8400-e29b-41d4-a716-446655440043', 'Aryan Chopra', 'SD', 100, '2024-04-10', true),
('550e8400-e29b-41d4-a716-446655440044', 'Nisha Kulkarni', 'SD', 100, '2024-04-20', true),

-- UX Designers (2)
('550e8400-e29b-41d4-a716-446655440045', 'Aman Desai', 'UX', 100, '2022-03-01', true),
('550e8400-e29b-41d4-a716-446655440046', 'Sonia Malhotra', 'UX', 100, '2023-01-15', true),

-- QA Engineers (2)
('550e8400-e29b-41d4-a716-446655440047', 'Ravi Pandey', 'QA', 100, '2021-12-01', true),
('550e8400-e29b-41d4-a716-446655440048', 'Anjali Mishra', 'QA', 100, '2022-09-15', true),

-- Program Managers (2)
('550e8400-e29b-41d4-a716-446655440049', 'Vikash Bhatia', 'PM', 100, '2020-05-01', true),
('550e8400-e29b-41d4-a716-446655440050', 'Neeti Agarwal', 'PM', 100, '2021-08-10', true);

-- =====================================================
-- EMPLOYEE SKILLS DATA (Diverse technology stack)
-- =====================================================

INSERT INTO resourcewise.employee_skill (id, employee_id, skill_name, summary, experience_months, last_used, source, created_at) VALUES

-- Rajesh Kumar (Architect) - Enterprise Architecture
('650e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'System Architecture', 'Designed microservices for large scale applications', 72, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', 'Java Spring Boot', 'Enterprise application development', 84, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', 'AWS', 'Cloud solution architecture, Well-Architected Framework', 60, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440001', 'Kubernetes', 'Container orchestration at enterprise scale', 48, '2024-03-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440001', 'PostgreSQL', 'Database architecture and optimization', 78, '2024-04-30', 'PAT', NOW()),

-- Priya Sharma (Architect) - Frontend Architecture
('650e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440002', 'React', 'Architected component libraries and design systems', 66, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440002', 'TypeScript', 'Type-safe architecture patterns', 54, '2024-04-25', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440002', 'Node.js', 'Full-stack JavaScript architecture', 60, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440009', '550e8400-e29b-41d4-a716-446655440002', 'Azure', 'Frontend deployment and CDN optimization', 42, '2024-03-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440002', 'GraphQL', 'API design and federation', 36, '2024-02-15', 'PAT', NOW()),

-- Amit Singh (PE) - Cloud & DevOps
('650e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440003', 'Python', 'Advanced backend development and automation', 72, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440012', '550e8400-e29b-41d4-a716-446655440003', 'GCP', 'Google Cloud Platform, BigQuery, Dataflow', 48, '2024-04-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440013', '550e8400-e29b-41d4-a716-446655440003', 'Docker', 'Containerization strategies', 54, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440014', '550e8400-e29b-41d4-a716-446655440003', 'Terraform', 'Infrastructure as Code', 36, '2024-04-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440015', '550e8400-e29b-41d4-a716-446655440003', 'MongoDB', 'NoSQL database design', 42, '2024-03-15', 'PAT', NOW()),

-- Sneha Patel (PE) - Mobile & Cross-platform
('650e8400-e29b-41d4-a716-446655440016', '550e8400-e29b-41d4-a716-446655440004', 'React Native', 'Cross-platform mobile architecture', 60, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440017', '550e8400-e29b-41d4-a716-446655440004', 'Flutter', 'Dart and Flutter development', 48, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440018', '550e8400-e29b-41d4-a716-446655440004', 'iOS Swift', 'Native iOS development', 54, '2024-03-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440019', '550e8400-e29b-41d4-a716-446655440004', 'Android Kotlin', 'Native Android development', 50, '2024-03-25', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440004', 'Firebase', 'Mobile backend services', 36, '2024-02-10', 'PAT', NOW()),

-- Tech Leads Skills
-- Vikram Reddy (TL) - Backend focused
('650e8400-e29b-41d4-a716-446655440021', '550e8400-e29b-41d4-a716-446655440005', 'Java Spring Boot', 'Microservices and REST APIs', 48, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440022', '550e8400-e29b-41d4-a716-446655440005', 'PostgreSQL', 'Advanced database operations', 42, '2024-04-25', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440023', '550e8400-e29b-41d4-a716-446655440005', 'AWS', 'EC2, RDS, Lambda, API Gateway', 36, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440024', '550e8400-e29b-41d4-a716-446655440005', 'Redis', 'Caching and session management', 30, '2024-03-30', 'PAT', NOW()),

-- Anita Gupta (TL) - Full Stack
('650e8400-e29b-41d4-a716-446655440025', '550e8400-e29b-41d4-a716-446655440006', 'React', 'Component-based development', 44, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440026', '550e8400-e29b-41d4-a716-446655440006', 'Node.js', 'Express.js and backend APIs', 40, '2024-04-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440027', '550e8400-e29b-41d4-a716-446655440006', 'MongoDB', 'Document database design', 38, '2024-04-10', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440028', '550e8400-e29b-41d4-a716-446655440006', 'Azure', 'App Services and Functions', 32, '2024-03-15', 'PAT', NOW()),

-- Karthik Nair (TL) - .NET Stack
('650e8400-e29b-41d4-a716-446655440029', '550e8400-e29b-41d4-a716-446655440007', '.NET Core', 'Enterprise applications', 50, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440030', '550e8400-e29b-41d4-a716-446655440007', 'C#', 'Object-oriented programming', 52, '2024-04-25', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440031', '550e8400-e29b-41d4-a716-446655440007', 'SQL Server', 'T-SQL and stored procedures', 48, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440032', '550e8400-e29b-41d4-a716-446655440007', 'Angular', 'Frontend framework', 34, '2024-03-20', 'PAT', NOW()),

-- Deepika Joshi (TL) - Python Stack
('650e8400-e29b-41d4-a716-446655440033', '550e8400-e29b-41d4-a716-446655440008', 'Python', 'FastAPI and Django development', 46, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440034', '550e8400-e29b-41d4-a716-446655440008', 'Django', 'Web framework and ORM', 42, '2024-04-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440035', '550e8400-e29b-41d4-a716-446655440008', 'PostgreSQL', 'Database design and queries', 40, '2024-04-10', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440036', '550e8400-e29b-41d4-a716-446655440008', 'GCP', 'Google Cloud services', 28, '2024-03-25', 'PAT', NOW()),

-- Senior Software Engineers (sample skills for key ones)
-- Rahul Agarwal (SSE) - Frontend
('650e8400-e29b-41d4-a716-446655440037', '550e8400-e29b-41d4-a716-446655440009', 'React', 'Advanced React patterns and hooks', 36, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440038', '550e8400-e29b-41d4-a716-446655440009', 'TypeScript', 'Type-safe frontend development', 30, '2024-04-25', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440039', '550e8400-e29b-41d4-a716-446655440009', 'Next.js', 'Server-side rendering', 24, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440040', '550e8400-e29b-41d4-a716-446655440009', 'CSS', 'Modern CSS and animations', 40, '2024-05-01', 'PAT', NOW()),

-- Pooja Mehta (SSE) - Backend
('650e8400-e29b-41d4-a716-446655440041', '550e8400-e29b-41d4-a716-446655440010', 'Java Spring Boot', 'RESTful services', 34, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440042', '550e8400-e29b-41d4-a716-446655440010', 'MySQL', 'Database optimization', 32, '2024-04-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440043', '550e8400-e29b-41d4-a716-446655440010', 'AWS', 'Cloud deployment', 28, '2024-04-10', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440044', '550e8400-e29b-41d4-a716-446655440010', 'Docker', 'Containerization', 26, '2024-03-30', 'PAT', NOW()),

-- Continue with more skills for other employees (adding key skills for demonstration)
-- Software Engineers and Developers (sample skills)

-- SE/SD Frontend Skills
('650e8400-e29b-41d4-a716-446655440045', '550e8400-e29b-41d4-a716-446655440015', 'React', 'Component development', 28, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440046', '550e8400-e29b-41d4-a716-446655440016', 'Vue.js', 'Progressive web apps', 24, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440047', '550e8400-e29b-41d4-a716-446655440017', 'Angular', 'Enterprise applications', 22, '2024-04-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440048', '550e8400-e29b-41d4-a716-446655440018', 'React', 'State management with Redux', 26, '2024-04-25', 'PAT', NOW()),

-- SE/SD Backend Skills
('650e8400-e29b-41d4-a716-446655440049', '550e8400-e29b-41d4-a716-446655440019', 'Node.js', 'Express.js APIs', 20, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440020', 'Python', 'Flask development', 18, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440051', '550e8400-e29b-41d4-a716-446655440021', 'Java Spring Boot', 'Microservices', 22, '2024-04-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440052', '550e8400-e29b-41d4-a716-446655440023', '.NET Core', 'Web APIs', 20, '2024-04-10', 'PAT', NOW()),

-- Mobile Development Skills
('650e8400-e29b-41d4-a716-446655440053', '550e8400-e29b-41d4-a716-446655440027', 'React Native', 'Cross-platform development', 15, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440054', '550e8400-e29b-41d4-a716-446655440028', 'Flutter', 'Mobile UI development', 12, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440055', '550e8400-e29b-41d4-a716-446655440029', 'Android Kotlin', 'Native Android', 18, '2024-04-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440056', '550e8400-e29b-41d4-a716-446655440030', 'iOS Swift', 'Native iOS', 16, '2024-04-25', 'PAT', NOW()),

-- Cloud Skills Distribution
('650e8400-e29b-41d4-a716-446655440057', '550e8400-e29b-41d4-a716-446655440031', 'AWS', 'EC2, S3, Lambda', 14, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440058', '550e8400-e29b-41d4-a716-446655440033', 'Azure', 'App Services, Functions', 12, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440059', '550e8400-e29b-41d4-a716-446655440035', 'GCP', 'Compute Engine, Cloud Functions', 10, '2024-04-20', 'PAT', NOW()),

-- Database Skills
('650e8400-e29b-41d4-a716-446655440060', '550e8400-e29b-41d4-a716-446655440037', 'PostgreSQL', 'Query optimization', 16, '2024-04-25', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440061', '550e8400-e29b-41d4-a716-446655440039', 'MongoDB', 'Document databases', 14, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440062', '550e8400-e29b-41d4-a716-446655440041', 'MySQL', 'Relational databases', 18, '2024-04-15', 'PAT', NOW()),

-- UX Designer Skills
('650e8400-e29b-41d4-a716-446655440063', '550e8400-e29b-41d4-a716-446655440045', 'Figma', 'UI/UX design and prototyping', 30, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440064', '550e8400-e29b-41d4-a716-446655440045', 'Adobe XD', 'Design systems', 24, '2024-04-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440065', '550e8400-e29b-41d4-a716-446655440045', 'Sketch', 'Interface design', 36, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440066', '550e8400-e29b-41d4-a716-446655440045', 'User Research', 'Usability testing and research', 28, '2024-04-30', 'PAT', NOW()),

('650e8400-e29b-41d4-a716-446655440067', '550e8400-e29b-41d4-a716-446655440046', 'Figma', 'Collaborative design', 18, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440068', '550e8400-e29b-41d4-a716-446655440046', 'Adobe Creative Suite', 'Photoshop, Illustrator', 22, '2024-04-25', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440069', '550e8400-e29b-41d4-a716-446655440046', 'Prototyping', 'Interactive prototypes', 16, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440046', 'User Experience', 'UX research and design', 20, '2024-04-30', 'PAT', NOW()),

-- QA Engineer Skills
('650e8400-e29b-41d4-a716-446655440071', '550e8400-e29b-41d4-a716-446655440047', 'Selenium', 'Web automation testing', 32, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440072', '550e8400-e29b-41d4-a716-446655440047', 'Cypress', 'End-to-end testing', 18, '2024-04-25', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440073', '550e8400-e29b-41d4-a716-446655440047', 'Postman', 'API testing', 28, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440074', '550e8400-e29b-41d4-a716-446655440047', 'TestNG', 'Test framework', 24, '2024-04-15', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440075', '550e8400-e29b-41d4-a716-446655440047', 'JIRA', 'Test management', 30, '2024-05-01', 'PAT', NOW()),

('650e8400-e29b-41d4-a716-446655440076', '550e8400-e29b-41d4-a716-446655440048', 'Playwright', 'Modern web testing', 12, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440077', '550e8400-e29b-41d4-a716-446655440048', 'Jest', 'Unit testing', 16, '2024-04-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440078', '550e8400-e29b-41d4-a716-446655440048', 'Appium', 'Mobile testing', 14, '2024-04-10', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440079', '550e8400-e29b-41d4-a716-446655440048', 'Performance Testing', 'Load and stress testing', 18, '2024-04-25', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440080', '550e8400-e29b-41d4-a716-446655440048', 'TestRail', 'Test case management', 20, '2024-04-30', 'PAT', NOW()),

-- Program Manager Skills
('650e8400-e29b-41d4-a716-446655440081', '550e8400-e29b-41d4-a716-446655440049', 'Project Management', 'Agile and Scrum methodologies', 48, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440082', '550e8400-e29b-41d4-a716-446655440049', 'JIRA', 'Project tracking and management', 42, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440083', '550e8400-e29b-41d4-a716-446655440049', 'Stakeholder Management', 'Cross-functional coordination', 54, '2024-04-30', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440084', '550e8400-e29b-41d4-a716-446655440049', 'Risk Management', 'Project risk assessment', 36, '2024-04-15', 'PAT', NOW()),

('650e8400-e29b-41d4-a716-446655440085', '550e8400-e29b-41d4-a716-446655440050', 'Agile Coaching', 'Scrum Master certification', 30, '2024-05-01', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440086', '550e8400-e29b-41d4-a716-446655440050', 'Product Management', 'Product roadmap and strategy', 36, '2024-04-25', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440087', '550e8400-e29b-41d4-a716-446655440050', 'Confluence', 'Documentation and knowledge management', 32, '2024-04-20', 'PAT', NOW()),
('650e8400-e29b-41d4-a716-446655440088', '550e8400-e29b-41d4-a716-446655440050', 'Budget Management', 'Resource planning and allocation', 28, '2024-04-10', 'PAT', NOW());

-- =====================================================
-- PROJECTS DATA (Color-coded project names)
-- =====================================================

INSERT INTO resourcewise.project (id, name, description, duration_months, tech_stack, created_at) VALUES
('750e8400-e29b-41d4-a716-446655440001', 'Project-Red', 'Enterprise e-commerce platform with advanced analytics', 12, ARRAY['React', 'Node.js', 'PostgreSQL', 'AWS', 'Redis'], '2024-01-15'),
('750e8400-e29b-41d4-a716-446655440002', 'Project-Blue', 'Cross-platform mobile banking application', 10, ARRAY['React Native', 'Java Spring Boot', 'MySQL', 'Azure', 'Docker'], '2024-02-01'),
('750e8400-e29b-41d4-a716-446655440003', 'Project-Green', 'Healthcare management system with telemedicine', 14, ARRAY['.NET Core', 'Angular', 'SQL Server', 'Azure', 'SignalR'], '2024-01-10'),
('750e8400-e29b-41d4-a716-446655440004', 'Project-Purple', 'Real-time data analytics and visualization platform', 8, ARRAY['Python', 'React', 'PostgreSQL', 'GCP', 'Kafka'], '2024-02-20'),
('750e8400-e29b-41d4-a716-446655440005', 'Project-Orange', 'IoT device management and monitoring system', 9, ARRAY['Node.js', 'Vue.js', 'MongoDB', 'AWS', 'MQTT'], '2024-03-01'),
('750e8400-e29b-41d4-a716-446655440006', 'Project-Yellow', 'Social media content management platform', 6, ARRAY['React', 'Python FastAPI', 'PostgreSQL', 'AWS', 'Elasticsearch'], '2024-03-15'),
('750e8400-e29b-41d4-a716-446655440007', 'Project-Cyan', 'Financial trading and portfolio management app', 11, ARRAY['Flutter', 'Java Spring Boot', 'MySQL', 'GCP', 'WebSocket'], '2024-04-01'),
('750e8400-e29b-41d4-a716-446655440008', 'Project-Magenta', 'Educational learning management system', 7, ARRAY['Angular', '.NET Core', 'SQL Server', 'Azure', 'SignalR'], '2024-04-10');

-- =====================================================
-- ALLOCATIONS DATA (35 employees allocated, 15 available)
-- =====================================================

INSERT INTO resourcewise.allocation (id, project_id, employee_id, percent_allocated, start_date, end_date) VALUES

-- Project-Red Team (E-commerce Platform) - 6 members
('850e8400-e29b-41d4-a716-446655440001', '750e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 50, '2024-01-15', '2025-01-15'), -- Rajesh (Architect)
('850e8400-e29b-41d4-a716-446655440002', '750e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440005', 100, '2024-01-15', '2025-01-15'), -- Vikram (TL)
('850e8400-e29b-41d4-a716-446655440003', '750e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440009', 100, '2024-01-20', '2025-01-15'), -- Rahul (SSE)
('850e8400-e29b-41d4-a716-446655440004', '750e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440015', 100, '2024-01-25', '2025-01-15'), -- Manish (SE)
('850e8400-e29b-41d4-a716-446655440005', '750e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440027', 100, '2024-02-01', '2025-01-15'), -- Nikhil (SD)
('850e8400-e29b-41d4-a716-446655440006', '750e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440045', 100, '2024-01-20', '2025-01-15'), -- Aman (UX)

-- Project-Blue Team (Mobile Banking) - 5 members
('850e8400-e29b-41d4-a716-446655440007', '750e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440004', 100, '2024-02-01', '2024-12-01'), -- Sneha (PE)
('850e8400-e29b-41d4-a716-446655440008', '750e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440010', 100, '2024-02-05', '2024-12-01'), -- Pooja (SSE)
('850e8400-e29b-41d4-a716-446655440009', '750e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440016', 100, '2024-02-10', '2024-12-01'), -- Riya (SE)
('850e8400-e29b-41d4-a716-446655440010', '750e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440028', 100, '2024-02-15', '2024-12-01'), -- Kriti (SD)
('850e8400-e29b-41d4-a716-446655440011', '750e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440047', 50, '2024-02-20', '2024-12-01'), -- Ravi (QA)

-- Project-Green Team (Healthcare System) - 6 members
('850e8400-e29b-41d4-a716-446655440012', '750e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440007', 75, '2024-01-10', '2025-03-10'), -- Karthik (TL)
('850e8400-e29b-41d4-a716-446655440013', '750e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440011', 100, '2024-01-15', '2025-03-10'), -- Arjun (SSE)
('850e8400-e29b-41d4-a716-446655440014', '750e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440017', 100, '2024-01-20', '2025-03-10'), -- Harsh (SE)
('850e8400-e29b-41d4-a716-446655440015', '750e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440022', 75, '2024-01-25', '2025-03-10'), -- Sakshi (SE)
('850e8400-e29b-41d4-a716-446655440016', '750e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440029', 100, '2024-02-01', '2025-03-10'), -- Abhishek (SD)
('850e8400-e29b-41d4-a716-446655440017', '750e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440049', 100, '2024-01-15', '2025-03-10'), -- Vikash (PM)

-- Project-Purple Team (Data Analytics) - 4 members
('850e8400-e29b-41d4-a716-446655440018', '750e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440008', 100, '2024-02-20', '2024-10-20'), -- Deepika (TL)
('850e8400-e29b-41d4-a716-446655440019', '750e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440013', 100, '2024-02-25', '2024-10-20'), -- Siddharth (SSE)
('850e8400-e29b-41d4-a716-446655440020', '750e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440018', 100, '2024-03-01', '2024-10-20'), -- Tanvi (SE)
('850e8400-e29b-41d4-a716-446655440021', '750e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440030', 100, '2024-03-05', '2024-10-20'), -- Shreya (SD)

-- Project-Orange Team (IoT Management) - 5 members
('850e8400-e29b-41d4-a716-446655440022', '750e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440006', 100, '2024-03-01', '2024-12-01'), -- Anita (TL)
('850e8400-e29b-41d4-a716-446655440023', '750e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440014', 100, '2024-03-05', '2024-12-01'), -- Neha (SSE)
('850e8400-e29b-41d4-a716-446655440024', '750e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440019', 100, '2024-03-10', '2024-12-01'), -- Aakash (SE)
('850e8400-e29b-41d4-a716-446655440025', '750e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440031', 100, '2024-03-15', '2024-12-01'), -- Rohit (SD)
('850e8400-e29b-41d4-a716-446655440026', '750e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440033', 100, '2024-03-20', '2024-12-01'), -- Akshay (SD)

-- Project-Yellow Team (Social Media Platform) - 4 members
('850e8400-e29b-41d4-a716-446655440027', '750e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440012', 50, '2024-03-15', '2024-09-15'), -- Kavya (SSE) - Part-time
('850e8400-e29b-41d4-a716-446655440028', '750e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440020', 100, '2024-03-20', '2024-09-15'), -- Ishita (SE)
('850e8400-e29b-41d4-a716-446655440029', '750e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440034', 100, '2024-03-25', '2024-09-15'), -- Priyanka (SD)
('850e8400-e29b-41d4-a716-446655440030', '750e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440046', 100, '2024-03-20', '2024-09-15'), -- Sonia (UX)

-- Project-Cyan Team (Trading Platform) - 3 members
('850e8400-e29b-41d4-a716-446655440031', '750e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440021', 100, '2024-04-01', '2025-03-01'), -- Rohan (SE)
('850e8400-e29b-41d4-a716-446655440032', '750e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440032', 50, '2024-04-05', '2025-03-01'), -- Divya (SD) - Part-time
('850e8400-e29b-41d4-a716-446655440033', '750e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440035', 100, '2024-04-10', '2025-03-01'), -- Sandeep (SD)

-- Project-Magenta Team (Learning Management) - 4 members
('850e8400-e29b-41d4-a716-446655440034', '750e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440023', 100, '2024-04-10', '2024-11-10'), -- Gaurav (SE)
('850e8400-e29b-41d4-a716-446655440035', '750e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440036', 100, '2024-04-15', '2024-11-10'), -- Meera (SD)
('850e8400-e29b-41d4-a716-446655440036', '750e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440037', 100, '2024-04-20', '2024-11-10'), -- Vishal (SD)
('850e8400-e29b-41d4-a716-446655440037', '750e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440048', 50, '2024-04-25', '2024-11-10'), -- Anjali (QA)

-- Additional allocations for architecture and PM oversight
('850e8400-e29b-41d4-a716-446655440038', '750e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 30, '2024-02-01', '2024-12-01'), -- Priya (Architect) - Blue
('850e8400-e29b-41d4-a716-446655440039', '750e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440003', 50, '2024-02-20', '2024-10-20'), -- Amit (PE) - Purple
('850e8400-e29b-41d4-a716-446655440040', '750e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440050', 100, '2024-03-15', '2024-09-15'); -- Neeti (PM) - Yellow

-- =====================================================
-- AVAILABLE EMPLOYEES (15 employees not fully allocated)
-- =====================================================
-- The following employees are available for new projects:
-- 1. Manish Verma (SE) - Available
-- 2. Harsh Jain (SE) - Available  
-- 3. Sakshi Tiwari (SE) - 25% available (75% allocated)
-- 4. Nidhi Agarwal (SE) - Available
-- 5. Varun Pandey (SE) - Available
-- 6. Aditi Kulkarni (SE) - Available
-- 7. Kriti Sharma (SD) - Available (after Project-Blue)
-- 8. Abhishek Kumar (SD) - Available (after Project-Green)
-- 9. Shreya Gupta (SD) - Available (after Project-Purple)
-- 10. Rohit Singh (SD) - Available (after Project-Orange)
-- 11. Divya Patel (SD) - 50% available (50% allocated)
-- 12. Akshay Reddy (SD) - Available (after Project-Orange)
-- 13. Priyanka Das (SD) - Available (after Project-Yellow)
-- 14. Sandeep Nair (SD) - Available (after Project-Cyan)
-- 15. Pooja Verma (SD) - Available
-- Plus several more SDs: Kiran Jain, Swati Khanna, Deepak Sinha, Ritika Tiwari, Aryan Chopra, Nisha Kulkarni

-- =====================================================
-- SUMMARY QUERIES FOR VERIFICATION
-- =====================================================

-- Check employee distribution by designation
-- SELECT designation, COUNT(*) as count FROM employees GROUP BY designation ORDER BY count DESC;

-- Check allocation utilization
-- SELECT 
--     e.name, 
--     e.designation,
--     e.capacity_percent,
--     COALESCE(SUM(a.percent_allocated), 0) as allocated_percent,
--     (e.capacity_percent - COALESCE(SUM(a.percent_allocated), 0)) as available_percent
-- FROM employees e
-- LEFT JOIN allocations a ON e.id = a.employee_id 
--     AND a.end_date > CURRENT_DATE
-- GROUP BY e.id, e.name, e.designation, e.capacity_percent
-- ORDER BY designation, available_percent DESC;

-- Check skills distribution
-- SELECT skill_name, COUNT(*) as employee_count 
-- FROM employee_skills 
-- GROUP BY skill_name 
-- ORDER BY employee_count DESC;

-- Check project team compositions
-- SELECT 
--     p.name as project_name,
--     COUNT(a.employee_id) as team_size,
--     STRING_AGG(e.designation, ', ' ORDER BY e.designation) as team_composition
-- FROM projects p
-- JOIN allocations a ON p.id = a.project_id
-- JOIN employees e ON a.employee_id = e.id
-- WHERE a.end_date > CURRENT_DATE
-- GROUP BY p.id, p.name
-- ORDER BY p.name;