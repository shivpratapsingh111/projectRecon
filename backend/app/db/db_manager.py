# External imports
from typing import Dict, List, Optional, Any, Tuple
import psycopg2

# Internal imports
from app.db.db_queries import QueryManager
from app.interface.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Initialization
logger = setup_logger(
    __name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG
)

# Logic
class DatabaseManager:

    def __init__(self, DB_CONFIG: Dict):
        self.DB_CONFIG = DB_CONFIG

        # Initialize database and tables
        self._initialize_database()

# ---

    def _initialize_database(self):
        """Create database if it doesn't exist and initialize tables"""
        # First connect to default postgres database to create our database if needed
        temp_config = self.DB_CONFIG.copy()
        target_db = temp_config.pop('dbname')
        temp_config['dbname'] = 'postgres'
        
        conn = None
        try:
            conn = psycopg2.connect(**temp_config)
            conn.autocommit = True  # Required for database creation
            cur = conn.cursor()
            
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            db_exists =  cur.fetchone()
            
            if db_exists:
                logger.info(f"DB already exists {target_db} - Proceeding...")
                
            if not db_exists:
                logger.info(f"Creating database {target_db}")
                # Close existing connections to avoid "database is being accessed by other users"
                cur.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s
                    AND pid <> pg_backend_pid()
                """, (target_db,))
                cur.execute(f"CREATE DATABASE {target_db}")
            
        except Exception as e:
            logger.exception(f"Failed to create database: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
        
        try:
            conn = psycopg2.connect(**self.DB_CONFIG)
            conn.autocommit = True        
            cur = conn.cursor()
            
            # Set extension for uuid_generate_v4()
            cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            
            logger.info("Initializing database tables")
            
            # Create all tables from a list
            for QueryManager.tables in QueryManager.CREATE_TABLE_LIST:
                cur.execute(QueryManager.tables)
            conn.commit()
            logger.info("Database initialization completed successfully")
            
        except Exception as e:
            logger.exception(f"Failed to initialize tables: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

# ---

    def execute_query(self, query: str, params: Tuple) -> Optional[Any]:
        """Execute a query and return results if any"""
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(**self.DB_CONFIG)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(query, params)
            result = None

            if (query.strip().upper().startswith('SELECT')):
                result = cur.fetchall()
            elif ("RETURNING id" in query):
                result = cur.fetchone()
            else:
                result = None

            conn.commit()
            return result

        except Exception as e:
            if conn:
                conn.rollback()
            logger.exception(f"Database error: {str(e)}")
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

# ---

    def execute_many(self, query: str, params_list: List[Tuple]) -> None:
        """Execute the same query with multiple parameter sets"""
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(**self.DB_CONFIG)
            conn.autocommit = True
            cur = conn.cursor()
            cur.executemany(query, params_list)
            conn.commit()
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.exception(f"Database error in batch operation: {str(e)}")
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
