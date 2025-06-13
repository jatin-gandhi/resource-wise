"""Database service for secure query execution."""

import asyncio
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import asyncpg
import structlog
from app.core.config import settings

logger = structlog.get_logger()


class DatabaseService:
    """Service for secure database operations."""

    def __init__(self):
        """Initialize database service."""
        self._connection_pool: Optional[asyncpg.Pool] = None
        self._max_rows = 1000  # Maximum rows to return
        self._query_timeout = 30  # Query timeout in seconds
        self._db_host = 'localhost'
        self._db_port = 5433
        self._db_user = 'admin'
        self._db_password = 'admin'
        self._db_name = 'resourcewise'
        self._db_driver = 'postgresql+asyncpg'
        
        # Allowed SQL operations (security whitelist)
        self._allowed_operations = {
            "SELECT", "WITH"  # Only read operations allowed
        }
        
        # Dangerous SQL patterns to block
        # self._dangerous_patterns = [
        #     r'\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE)\b',
        #     r'\b(EXEC|EXECUTE|xp_|sp_)\b',
        #     r'--',  # SQL comments
        #     r'/\*.*\*/',  # Multi-line comments
        #     r'\b(UNION|UNION\s+ALL)\b(?!.*FROM)',  # Suspicious UNION usage
        # ]
        self._dangerous_patterns = [
            r'\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE)\b',
            r'\b(EXEC|EXECUTE|xp_|sp_)\b',
        ]

    async def initialize(self) -> None:
        """Initialize database connection pool."""
        try:
            if self._connection_pool is None:
                self._connection_pool = await asyncpg.create_pool(
                    host=self._db_host,
                    port=self._db_port,
                    user=self._db_user,
                    password=self._db_password,
                    database=self._db_name,
                    min_size=2,
                    max_size=10,
                    command_timeout=self._query_timeout,
                    server_settings={
                        'application_name': 'ResourceWise-AI-Agent',
                    }
                )
                logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error("Failed to initialize database connection pool", error=str(e))
            raise

    async def close(self) -> None:
        """Close database connection pool."""
        if self._connection_pool:
            await self._connection_pool.close()
            self._connection_pool = None
            logger.info("Database connection pool closed")

    async def execute_query(
        self, 
        sql: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a SQL query safely.

        Args:
            sql: SQL query string
            params: Query parameters (not used for security, but kept for interface)

        Returns:
            Dictionary containing query results and metadata
        """
        start_time = time.time()
        
        try:
            # Ensure connection pool is initialized
            if self._connection_pool is None:
                await self.initialize()

            # Validate query safety
            is_safe, safety_error = await self.validate_query_safety(sql)
            if not is_safe:
                return {
                    "success": False,
                    "error": f"Query validation failed: {safety_error}",
                    "error_type": "SECURITY_VIOLATION",
                    "data": [],
                    "columns": [],
                    "row_count": 0,
                    "execution_time": 0
                }

            # Execute query with timeout
            async with self._connection_pool.acquire() as connection:
                try:
                    # Set query timeout
                    await connection.execute(f"SET statement_timeout = '{self._query_timeout}s'")
                    
                    # Execute the query
                    rows = await connection.fetch(sql)
                    
                    # Process results
                    data = []
                    columns = []
                    
                    if rows:
                        # Get column names from first row
                        columns = list(rows[0].keys())
                        
                        # Convert rows to dictionaries, limiting results
                        limited_rows = rows[:self._max_rows]
                        data = [dict(row) for row in limited_rows]
                        
                        # Log if results were truncated
                        if len(rows) > self._max_rows:
                            logger.warning(
                                "Query results truncated",
                                total_rows=len(rows),
                                returned_rows=self._max_rows
                            )

                    execution_time = time.time() - start_time
                    
                    result = {
                        "success": True,
                        "data": data,
                        "columns": columns,
                        "row_count": len(data),
                        "total_rows": len(rows),
                        "execution_time": round(execution_time, 3),
                        "truncated": len(rows) > self._max_rows if rows else False
                    }
                    
                    logger.info(
                        "Query executed successfully",
                        row_count=len(data),
                        execution_time=execution_time,
                        truncated=result["truncated"]
                    )
                    
                    return result

                except asyncio.TimeoutError:
                    return {
                        "success": False,
                        "error": f"Query timeout after {self._query_timeout} seconds",
                        "error_type": "TIMEOUT",
                        "data": [],
                        "columns": [],
                        "row_count": 0,
                        "execution_time": self._query_timeout
                    }

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(
                "Database query execution failed",
                error=error_msg,
                sql=sql[:200] + "..." if len(sql) > 200 else sql,
                execution_time=execution_time
            )
            
            # Categorize error types
            error_type = "DATABASE_ERROR"
            if "connection" in error_msg.lower():
                error_type = "CONNECTION_ERROR"
            elif "syntax" in error_msg.lower():
                error_type = "SYNTAX_ERROR"
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                error_type = "PERMISSION_ERROR"
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": error_type,
                "data": [],
                "columns": [],
                "row_count": 0,
                "execution_time": round(execution_time, 3)
            }

    async def validate_query_safety(self, sql: str) -> Tuple[bool, Optional[str]]:
        """Validate that a SQL query is safe to execute.

        Args:
            sql: SQL query string

        Returns:
            Tuple of (is_safe, error_message)
        """
        try:
            # Normalize SQL for analysis
            normalized_sql = sql.strip().upper()
            
            # Check if query is empty
            if not normalized_sql:
                return False, "Empty query"
            
            # Check for allowed operations
            first_word = normalized_sql.split()[0]
            if first_word not in self._allowed_operations:
                return False, f"Operation '{first_word}' is not allowed. Only SELECT queries are permitted."
            
            # Check for dangerous patterns
            for pattern in self._dangerous_patterns:
                if re.search(pattern, normalized_sql, re.IGNORECASE):
                    return False, f"Query contains potentially dangerous pattern: {pattern}"
            
            # Additional safety checks
            
            # Check for excessive complexity (basic heuristic)
            if normalized_sql.count('(') > 10 or normalized_sql.count('JOIN') > 5:
                return False, "Query is too complex"
            
            # Check for suspicious functions
            suspicious_functions = ['PG_SLEEP', 'DBMS_LOCK', 'WAITFOR']
            for func in suspicious_functions:
                if func in normalized_sql:
                    return False, f"Function '{func}' is not allowed"
            
            return True, None
            
        except Exception as e:
            logger.error("Error validating query safety", error=str(e), sql=sql[:100])
            return False, f"Query validation error: {str(e)}"

    async def test_connection(self) -> Dict[str, Any]:
        """Test database connection.

        Returns:
            Connection test results
        """
        try:
            if self._connection_pool is None:
                await self.initialize()
            
            async with self._connection_pool.acquire() as connection:
                result = await connection.fetchval("SELECT 1")
                
                return {
                    "success": True,
                    "message": "Database connection successful",
                    "result": result
                }
                
        except Exception as e:
            logger.error("Database connection test failed", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }

    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a specific table.

        Args:
            table_name: Name of the table

        Returns:
            Table information including columns and types
        """
        try:
            # Validate table name (basic security check)
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
                return {
                    "success": False,
                    "error": "Invalid table name format"
                }
            
            query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = $1 
                ORDER BY ordinal_position
            """
            
            if self._connection_pool is None:
                await self.initialize()
            
            async with self._connection_pool.acquire() as connection:
                rows = await connection.fetch(query, table_name)
                
                columns = [dict(row) for row in rows]
                
                return {
                    "success": True,
                    "table_name": table_name,
                    "columns": columns,
                    "column_count": len(columns)
                }
                
        except Exception as e:
            logger.error("Failed to get table info", table_name=table_name, error=str(e))
            return {
                "success": False,
                "error": str(e)
            }


# Global database service instance
db_service = DatabaseService() 