# db_operations.py
from db_manager import DatabaseManager
from typing import Dict, List, Optional, Any, Tuple
import psycopg2
from psycopg2.extras import Json
import logging
from datetime import datetime
from db_queries import QueryManager
import psycopg2
from psycopg2.extras import Json


class DatabaseOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

        logging.basicConfig(
            level=logging.DEBUG,  # Set logging level to DEBUG
            format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            handlers=[
                logging.FileHandler('endpoint_monitor.log', mode='a'),  # Append mode for the log file
                logging.StreamHandler()  # Print logs to the terminal
            ]
        )
        
        # Create a logger for the class
        self.logger = logging.getLogger(self.__class__.__name__)  # Use the class name for better context
        self.logger.setLevel(logging.DEBUG)  # Ensure the logger level is set to DEBUG

    def insert_operations(self):
        return EndpointInsertOperations(self.db)

    def update_operations(self):
        return EndpointUpdateOperations(self.db)

    def delete_operations(self):
        return EndpointDeleteOperations(self.db)

    def query_operations(self):
        return EndpointQueryOperations(self.db)


class EndpointInsertOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    def add_endpoint(self, url: str) -> int:
        """Add a new endpoint and return its ID"""
        try:
            result = self.db.execute_query(QueryManager.INSERT_ENDPOINT, (url,))
            return result[0][0]
        except Exception as e:
            self.logger.error(f"Failed to add endpoint {url}: {str(e)}")
            raise

    def record_change(self, change_data: Dict):
        """Record a change in endpoint response"""
        try:
            params = (
                change_data['endpoint_id'],
                change_data['old_status_code'],
                change_data['new_status_code'],
                change_data['old_size'],
                change_data['new_size'],
                change_data['old_body_hash'],
                change_data['new_body_hash'],
                change_data['old_response_body'],
                change_data['new_response_body'],
                Json(change_data['old_headers']),
                Json(change_data['new_headers']),
                change_data['old_response_time'],
                change_data['new_response_time'],
                change_data['change_type']
            )
            self.db.execute_query(QueryManager.INSERT_CHANGE, params)
        except Exception as e:
            self.logger.error(f"Failed to record change: {str(e)}")
            raise

class EndpointUpdateOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    def update_endpoint_data(self, endpoint_id: int, data: Dict):
        """Update endpoint data"""
        try:
            params = (
                data['status_code'],
                data['response_size'],
                data['body_hash'],
                data['response_body'],
                data['headers'],
                data['response_time'],
                endpoint_id
            )
            # self.logger.info(f"Query: {QueryManager.INSERT_ENDPOINT}, Parameters: {params}")
            self.db.execute_query(QueryManager.UPDATE_ENDPOINT_DATA, params)
        except Exception as e:
            self.logger.error(f"Failed to update endpoint {endpoint_id}: {str(e)}")
            raise

class EndpointDeleteOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    def delete_endpoint(self, endpoint_id: int):
        """Delete an endpoint and its associated changes"""
        try:
            # First delete associated changes due to foreign key constraint
            self.db.execute_query(QueryManager.DELETE_CHANGES_FOR_ENDPOINT, (endpoint_id,))
            self.db.execute_query(QueryManager.DELETE_ENDPOINT, (endpoint_id,))
        except Exception as e:
            self.logger.error(f"Failed to delete endpoint {endpoint_id}: {str(e)}")
            raise

class EndpointQueryOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    def get_endpoint_data(self, url: str) -> Optional[Dict]:
        """Get current endpoint data"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ENDPOINT_DATA, (url,))
            if result:
                row = result[0]
                return {
                    'status_code': row[0],
                    'response_size': row[1],
                    'body_hash': row[2],
                    'response_body': row[3],
                    'headers': row[4],
                    'response_time': row[5],
                    'id': row[6]
                }
            return None
        except Exception as e:
            self.logger.error(f"Failed to get endpoint data for {url}: {str(e)}")
            raise

    def get_all_endpoints(self) -> List[Dict]:
        """Get all monitored endpoints"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ALL_ENDPOINTS)
            return [{'id': row[0], 'url': row[1]} for row in result]
        except Exception as e:
            self.logger.error(f"Failed to get endpoints: {str(e)}")
            raise