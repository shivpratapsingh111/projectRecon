# db_operations.py

# ===[Imports]===
from typing import Dict, List, Optional
from psycopg2 import extensions

# ===[Local Imports]===
from app.services.scans.db.db_queries import QueryManager
from app.services.scans.db.db_manager import DatabaseManager
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='monitor_endpoints', enable_debug = False)


class DatabaseOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

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
    # --- Endpoint Monitor ---
    def insert_endpoint(self, endpoint_data: Dict):
        """Record a change in endpoint response"""
        try:
            params = (
                endpoint_data['program_id'],
                endpoint_data['target_id'],
                endpoint_data['scan_name'],
                endpoint_data['status'],
                endpoint_data['url'],
                endpoint_data['old_status_code'],
                endpoint_data['new_status_code'],
                endpoint_data['old_response_size'],
                endpoint_data['new_response_size'],
                endpoint_data['old_body_hash'],
                endpoint_data['new_body_hash'],
                endpoint_data['old_body_file_path'],
                endpoint_data['new_body_file_path'],
                endpoint_data['change_detected_at'],
                endpoint_data['need_review']
            )
            self.db.execute_query(QueryManager.INSERT_ENDPOINT, params)
            logger.info(f"Endpoint Data inserted successfully - [{str(endpoint_data['url'])}]")
            
        except Exception as e:
            logger.exception(f"Failed to insert endpoint data [{str(endpoint_data['url'])}]: {str(e)}")
            raise


    def insert_web_target(self, program_id, target_name):
        """Insert web target"""
        try:
            self.db.execute_query(QueryManager.INSERT_WEB_TARGETS, (program_id, target_name))
            logger.info(f"Web Target inserted successfully - [{target_name}]")
            
        except Exception as e:
            logger.exception(f"Failed to insert web target [{target_name}] in program [{program_id}]: {str(e)}")
            raise

class EndpointUpdateOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    # --- Endpoint Monitor ---

class EndpointDeleteOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    # --- Endpoint Monitor ---

class EndpointQueryOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    # --- Endpoint Monitor ---
    def get_all_programnames(self) -> List[Dict]:
        """Get all scan names"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ALL_PROGRAMNAMES, None)
            return result
        except Exception as e:
            logger.exception(f"Failed to get scan names: {str(e)}")
            raise

    def get_web_target_id(self, target_domain) -> List[Dict]:
        """Returns web target ID by searching from target domain
           Returns: id
           Example: 8bc2d48a-e09a-4800-ab80-580cc62063b2
        """
        try:
            result = self.db.execute_query(QueryManager.GET_WEB_TARGET_ID, (target_domain,))
            return result[0][0]
        except Exception as e:
            logger.exception(f"Failed to web target id [{target_domain}]: {str(e)}")
            raise
