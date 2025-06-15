# ResourceWise AI - Complete Workflow Documentation

## 🏗️ Architecture Overview

The ResourceWise AI system now implements a complete multi-agent workflow that can handle both conversational queries and database operations with intelligent routing, secure execution, and user-friendly response formatting.

## 🔄 Workflow Flow

```
User Input → Intent Classification → [Database Required?]
                                   ↓                    ↓
                            Query Generation      Direct Response
                                   ↓                    ↓
                            Database Execution          ↓
                                   ↓                    ↓
                            Response Formatting         ↓
                                   ↓                    ↓
                            Final Response ←----------→ End
```

## 🎯 Workflow Nodes

### 1. **Intent Classification Node**
- **Agent**: `IntentAgent`
- **Purpose**: Analyze user input and determine intent type
- **Outputs**:
  - Intent type (database_query, general_conversation, greeting, help_request)
  - Extracted parameters for database queries
  - Routing decision (`requires_database` flag)

### 2. **Query Generation Node** *(Database queries only)*
- **Agent**: `QueryAgent`
- **Purpose**: Generate SQL queries from natural language
- **Features**:
  - Schema-aware query generation
  - Query validation and optimization
  - Parameter extraction and mapping
- **Outputs**:
  - Valid SQL query
  - Query metadata (tables, parameters, type)

### 3. **Database Execution Node** *(Database queries only)*
- **Service**: `DatabaseService`
- **Purpose**: Securely execute SQL queries
- **Security Features**:
  - Query safety validation (only SELECT allowed)
  - SQL injection prevention
  - Query timeout and resource limits
  - Connection pooling
- **Outputs**:
  - Query results (data, columns, metadata)
  - Execution statistics
  - Error handling

### 4. **Response Formatting Node** *(Database queries only)*
- **Service**: `ResponseFormatter`
- **Purpose**: Format raw data into user-friendly responses
- **Formats**:
  - **Table**: Markdown tables for structured data
  - **List**: Bullet points for simple listings
  - **Summary**: Analytics with insights and statistics
  - **JSON**: Fallback format for complex data
- **Features**:
  - Intelligent format selection
  - Data truncation for large results
  - Natural language summaries

## 🔒 Security Features

### Database Security
- **Whitelist Approach**: Only SELECT and WITH operations allowed
- **Pattern Blocking**: Dangerous SQL patterns automatically blocked
- **Query Validation**: Multi-layer validation before execution
- **Resource Limits**: Query timeout, row limits, connection pooling
- **Error Sanitization**: Safe error messages without exposing internals

### Blocked Operations
```sql
-- ❌ These are automatically blocked:
DROP TABLE users;
UPDATE employees SET salary = 100000;
DELETE FROM projects;
INSERT INTO logs VALUES ('malicious');
EXEC xp_cmdshell('rm -rf /');
SELECT * FROM users; DROP TABLE logs; --
```

### Allowed Operations
```sql
-- ✅ These are allowed:
SELECT name, email FROM employees WHERE department = 'Engineering';
SELECT COUNT(*) FROM projects WHERE status = 'active';
WITH active_projects AS (SELECT * FROM projects WHERE status = 'active') 
SELECT * FROM active_projects;
```

## 📊 Response Formats

### Table Format
Used for structured data with multiple columns and moderate row count.

```markdown
| Name | Email | Department |
|------|-------|------------|
| John Doe | john@example.com | Engineering |
| Jane Smith | jane@example.com | Marketing |
```

### List Format
Used for simple data or when focusing on key fields.

```markdown
Found 3 employees matching your criteria:

1. **Name:** John Doe **Email:** john@example.com **Department:** Engineering
2. **Name:** Jane Smith **Email:** jane@example.com **Department:** Marketing
3. **Name:** Bob Johnson **Email:** bob@example.com **Department:** Engineering
```

### Summary Format
Used for analytics queries or large datasets.

```markdown
Analysis of 150 records:
- Most common department: Engineering (75 employees)
- Average allocation: 85%
- Active projects: 12

**Key Statistics:**
- Total records: 150
- Data fields: 8
- Execution time: 0.05s
```

## 🚀 Usage Examples

### Employee Search
```
User: "Find all software engineers with Python skills"

Flow: Intent → Query → Database → Format
Result: Table format with employee details
```

### Analytics Query
```
User: "Show me overallocated employees"

Flow: Intent → Query → Database → Format  
Result: Summary format with insights and statistics
```

### General Conversation
```
User: "Hello, how are you?"

Flow: Intent → Direct Response
Result: Conversational response without database access
```

## 🛠️ Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=resourcewise
DATABASE_USER=your_user
DATABASE_PASSWORD=your_password

# AI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o

# LangSmith (Optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
```

### Service Configuration
```python
# Database Service Settings
MAX_ROWS = 1000          # Maximum rows returned
QUERY_TIMEOUT = 30       # Query timeout in seconds
CONNECTION_POOL_SIZE = 10 # Max database connections

# Response Formatter Settings
MAX_TABLE_ROWS = 20      # Max rows in table format
MAX_LIST_ITEMS = 50      # Max items in list format
```

## 🧪 Testing

### Run Complete Test Suite
```bash
cd backend
python scripts/test_full_workflow.py
```

### Test Components
- **Database Connection**: Verify database connectivity
- **Security Validation**: Test SQL injection prevention
- **Response Formatting**: Test different output formats
- **Full Workflow**: End-to-end testing with real queries

### Sample Test Cases
1. **Employee Search**: "Find Python developers"
2. **Department Query**: "List Engineering team members"
3. **Analytics**: "Show project allocation summary"
4. **Security Test**: Attempt dangerous SQL operations
5. **Error Handling**: Invalid queries and connection issues

## 📈 Performance Considerations

### Database Optimization
- Connection pooling for efficient resource usage
- Query timeout to prevent long-running operations
- Result pagination for large datasets
- Index-aware query generation

### Response Optimization
- Intelligent format selection based on data size
- Data truncation for large results
- Streaming support for real-time responses
- Caching for frequently accessed data

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check environment variables
   - Verify database is running
   - Confirm network connectivity

2. **Query Generation Errors**
   - Verify OpenAI API key
   - Check schema service configuration
   - Review query complexity

3. **Security Violations**
   - Review blocked SQL patterns
   - Ensure only SELECT operations
   - Check for SQL injection attempts

4. **Formatting Errors**
   - Verify data structure
   - Check column mappings
   - Review format selection logic

### Debug Mode
```python
# Enable debug logging
import structlog
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
)
```

## 🚀 Future Enhancements

### Planned Features
1. **Query Caching**: Cache frequent query results
2. **Advanced Analytics**: Statistical insights and trends
3. **Chart Generation**: Visual data representation
4. **Query Optimization**: Automatic query performance tuning
5. **Multi-Database Support**: Support for multiple data sources
6. **Real-time Streaming**: Live data updates
7. **Natural Language Insights**: AI-generated data insights

### Extensibility
The workflow is designed for easy extension:
- Add new node types for specialized processing
- Implement custom response formatters
- Integrate additional security layers
- Support new database types
- Add custom validation rules

## 📚 API Reference

### Workflow Usage
```python
from app.ai.workflow.graph import AgentWorkflow
from app.ai.core.config import AIConfig

# Initialize workflow
config = AIConfig()
workflow = AgentWorkflow(config)

# Process query
result = await workflow.process(
    user_input="Find Python developers",
    session_id="user_123",
    context={"user_id": "user_123"}
)

# Access results
print(result.query_result["response"])
```

### Direct Service Usage
```python
from app.services.database import db_service
from app.services.response_formatter import response_formatter

# Execute query directly
db_result = await db_service.execute_query("SELECT * FROM employees LIMIT 5")

# Format response
formatted = await response_formatter.format_database_response(
    query_result=db_result,
    query_context={"query_type": "resource_search"},
    original_query="Show me employees"
)
```

---

This complete workflow provides a robust, secure, and user-friendly system for natural language database interactions with intelligent response formatting and comprehensive error handling. 