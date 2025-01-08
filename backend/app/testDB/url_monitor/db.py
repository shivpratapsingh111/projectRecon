# url_monitor/db.py
import psycopg2
import psycopg2.extras
import json
import hashlib
from datetime import datetime
from typing import Optional, Tuple, Dict, List
from .queries import QueryManager
import logging

class Database:
    def __init__(self, config: dict):
        self.db_config = config
        self.logger = logging.getLogger("url_monitor")
        self._initialize_database()
        self.conn = self._connect()
    
    def _connect(self) -> psycopg2.extensions.connection:
        """Establish database connection"""
        return psycopg2.connect(**self.db_config)

    def _initialize_database(self):
        """Create database if it doesn't exist and initialize tables"""
        # First connect to default postgres database to create our database if needed
        temp_config = self.db_config.copy()
        target_db = temp_config.pop('dbname')
        temp_config['dbname'] = 'postgres'
        
        conn = None
        try:
            conn = psycopg2.connect(**temp_config)
            conn.autocommit = True  # Required for database creation
            cur = conn.cursor()
            
            # Check if database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            if not cur.fetchone():
                self.logger.info(f"Creating database {target_db}")
                # Close existing connections
                cur.execute(f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = %s
                    AND pid <> pg_backend_pid()
                """, (target_db,))
                # Create database
                cur.execute(f"CREATE DATABASE {target_db}")
            
        except Exception as e:
            self.logger.error(f"Failed to create database: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
        
        # Now connect to our database and create tables
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # Create tables
            self.logger.info("Initializing database tables")
            cur.execute(QueryManager.CREATE_ENDPOINTS_TABLE)
            cur.execute(QueryManager.CREATE_CHANGES_TABLE)
            
            conn.commit()
            self.logger.info("Database initialization completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize tables: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def add_url(self, url: str) -> int:
        """Add a new URL to monitor"""
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(QueryManager.INSERT_ENDPOINT, (url,))
                return cur.fetchone()[0]

    def get_url_data(self, url: str) -> Optional[Tuple]:
        """Get the latest data for a URL"""
        with self.conn.cursor() as cur:
            cur.execute(QueryManager.SELECT_ENDPOINT_DATA, (url,))
            return cur.fetchone()

    def get_all_urls(self) -> List[Tuple[int, str]]:
        """Get all monitored URLs"""
        with self.conn.cursor() as cur:
            cur.execute(QueryManager.SELECT_ALL_ENDPOINTS)
            return cur.fetchall()

    def update_url_data(self, endpoint_id: int, status_code: int, 
                       response_size: int, body_hash: str, 
                       response_body: str, headers: Dict, 
                       response_time: float):
        """Update the latest data for a URL"""
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(QueryManager.UPDATE_ENDPOINT_DATA, 
                          (status_code, response_size, body_hash, 
                           response_body, json.dumps(headers), 
                           response_time, endpoint_id))

    def record_change(self, endpoint_id: int, old_data: Dict, new_data: Dict, 
                     change_types: List[str]):
        """Record a change in URL monitoring data"""
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(QueryManager.INSERT_CHANGE,
                          (endpoint_id, 
                           old_data.get('status_code'), new_data.get('status_code'),
                           old_data.get('size'), new_data.get('size'),
                           old_data.get('body_hash'), new_data.get('body_hash'),
                           old_data.get('response_body'), new_data.get('response_body'),
                           json.dumps(old_data.get('headers', {})), 
                           json.dumps(new_data.get('headers', {})),
                           old_data.get('response_time'), new_data.get('response_time'),
                           change_types))

    def delete_url(self, endpoint_id: int):
        """Delete a URL and its associated changes"""
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(QueryManager.DELETE_CHANGES_FOR_ENDPOINT, (endpoint_id,))
                cur.execute(QueryManager.DELETE_ENDPOINT, (endpoint_id,))

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()