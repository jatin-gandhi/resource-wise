# Resource Wise - System Architecture

## Overview

Resource Wise is an AI-powered resource allocation system designed to replace manual spreadsheet-based processes with an intelligent, conversational interface. The system combines modern web technologies with advanced AI capabilities to provide real-time resource management and optimization.

## System Architecture

### High-Level Architecture

The system follows a layered architecture pattern with clear separation of concerns:

## Technology Stack

### Backend Technologies
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Runtime** | Python | 3.11+ | Core application runtime |
| **Web Framework** | FastAPI | 0.104+ | High-performance async API |
| **Database** | PostgreSQL | 16 | Primary data storage |
| **Vector Search** | pgvector | 0.5+ | Semantic similarity search |
| **Full-Text Search** | pg_trgm | Built-in | Text search & fuzzy matching |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction layer |
| **Migrations** | Alembic | 1.12+ | Database schema management |
| **Validation** | Pydantic | 2.0+ | Data validation & serialization |
| **AI Integration** | OpenAI | 1.0+ | GPT-4 & embedding models |

### Frontend Technologies
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | React 18+ | User interface framework |
| **Language** | TypeScript | Type-safe JavaScript |
| **Styling** | Tailwind CSS | Utility-first CSS framework |
| **State Management** | React Hooks | Component state management |
| **HTTP Client** | Fetch API | API communication |

### Development & Deployment
| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containerization** | Docker | Development environment |
| **Database Admin** | pgAdmin | Database management |
| **Code Quality** | Ruff | Python linting & formatting |
| **Version Control** | Git | Source code management |

## Database Architecture

### Database Schema Overview

The database schema is designed around core entities with rich search capabilities:

### Key Database Features

#### 1. **Vector Search Capabilities**
- **pgvector Extension**: Enables semantic similarity search using AI embeddings
- **HNSW & IVFFlat Indexes**: Optimized vector search performance
- **Multi-source Embeddings**: Skills, projects, and employee profiles

#### 2. **Full-Text Search with TSVector**
- **Automatic TSVector Updates**: Database triggers maintain search indexes
- **Weighted Search**: Name fields weighted higher than descriptions
- **Fuzzy Matching**: pg_trgm extension for typo tolerance

#### 3. **Hybrid Search Strategy**
- **Combined Results**: Merges semantic and keyword search results
- **Relevance Scoring**: Balances AI similarity with text relevance
- **Performance Optimized**: CTEs and proper indexing for fast queries

## API Architecture

### RESTful Endpoints Structure

```
/api/v1/
├── chat/                    # Chat interface endpoints
│   ├── POST /               # Main chat endpoint
│   └── POST /stream         # Streaming chat responses
├── employees/               # Employee management
│   ├── GET /                # List employees
│   ├── POST /               # Create employee
│   ├── GET /{id}            # Get employee details
│   ├── PUT /{id}            # Update employee
│   └── DELETE /{id}         # Delete employee
├── projects/                # Project management
│   ├── GET /                # List projects
│   ├── POST /               # Create project
│   ├── GET /{id}            # Get project details
│   ├── PUT /{id}            # Update project
│   └── DELETE /{id}         # Delete project
├── allocations/             # Resource allocation
│   ├── GET /                # List allocations
│   ├── POST /               # Create allocation
│   ├── GET /{id}            # Get allocation details
│   ├── PUT /{id}            # Update allocation
│   └── DELETE /{id}         # Delete allocation
└── search/                  # Search endpoints
    ├── GET /employees       # Search employees
    ├── GET /projects        # Search projects
    └── GET /hybrid          # Hybrid AI search
```

### API Design Principles

#### **Chat-First Architecture**
- **Single Endpoint**: `/api/v1/chat` handles all user interactions
- **Natural Language**: Users communicate in plain English
- **Streaming Responses**: Real-time updates for complex queries
- **Context Awareness**: Maintains conversation context

#### **RESTful Fallback**
- **Traditional CRUD**: Available for direct integrations
- **Structured Data**: JSON request/response for programmatic access
- **Validation**: Pydantic models ensure data integrity
- **Error Handling**: Consistent error response format

## AI Integration Architecture

### AI Processing Pipeline

The AI integration follows a multi-stage pipeline for optimal performance:

### AI Integration Components

#### **Intent Analysis**
- **Pattern Matching**: Fast recognition of common queries
- **GPT-4 Analysis**: Complex intent extraction with structured output
- **Function Calling**: Structured data extraction from natural language
- **Confidence Scoring**: Quality assessment of intent recognition

#### **Response Generation**
- **Context-Aware**: Considers conversation history and user context
- **Natural Language**: Converts structured data to conversational responses
- **Personalization**: Adapts tone and detail level to user preferences
- **Error Handling**: Graceful degradation when AI services are unavailable

## Performance & Scalability

### Performance Optimization Strategies

#### 1. Database Optimization
- **Indexes**: Comprehensive indexing strategy for all search patterns
- **Connection Pooling**: Async connection pool for database operations
- **Query Optimization**: Optimized queries with proper JOINs and CTEs

#### 2. Caching Strategy
- **Application Cache**: In-memory caching for frequent queries
- **Database Cache**: PostgreSQL query result caching
- **AI Response Cache**: Cache AI-generated responses for similar queries

#### 3. API Performance
- **Async Operations**: Full async/await pattern throughout the application
- **Streaming Responses**: Real-time streaming for long-running operations
- **Request Validation**: Fast Pydantic validation with early error detection

### Scalability Considerations

#### Horizontal Scaling
```yaml
# Future scaling architecture
services:
  api:
    replicas: 3
    load_balancer: nginx
    
  database:
    primary: postgresql-master
    replicas: 
      - postgresql-read-1
      - postgresql-read-2
    
  cache:
    service: redis-cluster
    nodes: 3
    
  ai_service:
    queue: celery
    workers: 5
```

#### Monitoring & Observability
```python
# Metrics collection
class MetricsCollector:
    def __init__(self):
        self.response_times = []
        self.error_rates = {}
        self.cache_hit_rates = {}
    
    def track_response_time(self, endpoint: str, duration: float):
        self.response_times.append({
            'endpoint': endpoint,
            'duration': duration,
            'timestamp': time.time()
        })
    
    def track_error(self, endpoint: str, error_type: str):
        key = f"{endpoint}:{error_type}"
        self.error_rates[key] = self.error_rates.get(key, 0) + 1
```

## Security Architecture

### Authentication & Authorization
```python
# Future implementation
class SecurityManager:
    def __init__(self):
        self.jwt_secret = settings.JWT_SECRET
        self.token_expiry = timedelta(hours=24)
    
    async def authenticate_user(self, token: str) -> User:
        """Validate JWT token and return user"""
        payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
        return await self.get_user_by_id(payload["user_id"])
    
    def authorize_action(self, user: User, action: str, resource: str) -> bool:
        """Check if user has permission for action on resource"""
        return user.has_permission(action, resource)
```

### Data Protection
- **Input Validation**: Comprehensive Pydantic validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **CORS Configuration**: Proper cross-origin resource sharing setup
- **Environment Variables**: Secure configuration management

## Development Workflow

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality
```bash
# Linting and formatting
ruff check .
ruff format .

# Type checking (future)
mypy app/
```

### Testing Strategy
```python
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# API tests
pytest tests/api/
```

## Deployment Architecture

### Development Environment
```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: resourcewise
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
    ports:
      - "5432:5432"
    volumes:
      - ./docker/init-db.sql:/docker-entrypoint-initdb.d/init.sql
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql+asyncpg://admin:admin@db:5432/resourcewise
      - OPENAI_API_KEY=${OPENAI_API_KEY}

volumes:
  postgres_data:
```

### Production Considerations
- **Container Orchestration**: Kubernetes or Docker Swarm
- **Load Balancing**: NGINX or cloud load balancer
- **Database**: Managed PostgreSQL service (AWS RDS, Google Cloud SQL)
- **Monitoring**: Prometheus + Grafana
- **Logging**: Centralized logging with ELK stack

## Future Enhancements

### Phase 2 Features
- **Real-time Notifications**: WebSocket integration for live updates
- **Advanced Analytics**: Machine learning for resource optimization
- **Mobile App**: React Native mobile application
- **Integrations**: Slack, Microsoft Teams, JIRA integrations

### Phase 3 Features
- **Multi-tenancy**: Support for multiple organizations
- **Advanced AI**: Custom fine-tuned models for domain-specific tasks
- **Workflow Automation**: Automated resource allocation based on rules
- **Advanced Reporting**: Interactive dashboards and reports

## Conclusion

Resource Wise is architected as a modern, scalable, and intelligent resource allocation system. The hybrid approach combining traditional database operations with AI-powered natural language processing provides both performance and flexibility. The system is designed to grow from a hackathon prototype to a production-ready enterprise solution.

Key architectural strengths:
- **🚀 Performance**: Multi-tier caching and optimized queries
- **🧠 Intelligence**: AI-powered natural language interface
- **📈 Scalability**: Async architecture with horizontal scaling support
- **🔒 Security**: Comprehensive security measures and best practices
- **🛠️ Maintainability**: Clean code architecture with proper separation of concerns 