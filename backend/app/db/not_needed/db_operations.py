# db_operations.py
from typing import Dict, List, Optional, Any, Tuple
from psycopg2 import extensions
from psycopg2.extras import Json
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import Json

from backend.app.testDB.not_needed.db_queries import QueryManager
from backend.app.testDB.not_needed.db_manager import DatabaseManager

# from db_manager import DatabaseManager
# from db_queries import QueryManager

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

    # --- Endpoint Monitor ---
    def insert_endpoint(self, endpoint_data: Dict):
        """Record a change in endpoint response"""
        try:
            params = (
                endpoint_data['url'],
                endpoint_data['old_status_code'],
                endpoint_data['new_status_code'],
                endpoint_data['old_response_size'],
                endpoint_data['new_response_size'],
                endpoint_data['old_body_hash'],
                endpoint_data['new_body_hash'],
                endpoint_data['old_body_file_path'],
                endpoint_data['new_body_file_path'],
                endpoint_data['change_detected_at']
            )
            self.db.execute_query(QueryManager.INSERT_ENDPOINT, params)
            self.logger.info(f"Endpoint Data inserted successfully - [{str(endpoint_data['url'])}]")
            
        except Exception as e:
            self.logger.error(f"Failed to insert endpoint data [{str(endpoint_data['url'])}]: {str(e)}")
            raise

    # --- Report ---
    def insert_program(self, program_data: Dict):
        try:
            params = (
                program_data['program_name'],
                program_data['program_url'],
                program_data['acquisitions'],
                program_data['email'],
                program_data['report_form']
            )
            result = self.db.execute_query(QueryManager.INSERT_PROGRAM, params)
            self.logger.info(f"New program created with id {result[0]}")
            return result[0]
        except Exception as e:
            self.logger.error(f"Failed to insert program data {str(program_data['program_name'])}: {str(e)}")
            raise
    def insert_web_target(self, web_target_data: Dict):
        try:
            params = (
                web_target_data['program_id'],
                web_target_data['target_domain'],
                web_target_data['technology'],
                web_target_data['status_code'],
                web_target_data['port'],
                web_target_data['host'],
                web_target_data['ipv4'],
                web_target_data['ipv6'],
                web_target_data['response_time'],
                web_target_data['webserver'],
                web_target_data['vulnerability_reported']
            )
            result = self.db.execute_query(QueryManager.INSERT_WEB_TARGET, params)
            self.logger.info(f"New web-target created with id {result[0]}")
            return result[0]
        except Exception as e:
            self.logger.error(f"Failed to insert web target data {str(web_target_data['target_domain'])} : {str(e)}")
            raise
    def insert_mobile_target(self, mobile_target_data: Dict):
        try:
            params = (
                mobile_target_data['program_id'],
                mobile_target_data['target_package'],
                mobile_target_data['target_apk'],
                extensions.adapt(mobile_target_data['technology']),
                mobile_target_data['download_url'],
                extensions.adapt(mobile_target_data['vulnerability_reported'])
            )
            result = self.db.execute_query(QueryManager.INSERT_MOBILE_TARGET, params)
            self.logger.info(f"New mobile-target created with id {result[0]}")
            
            return result[0]
        except Exception as e:
            self.logger.error(f"Failed to insert mobile target data {str(mobile_target_data['target_package'])} : {str(e)}")
            raise


class EndpointUpdateOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    # --- Endpoint Monitor ---
    def update_endpoint_data(self, id: int, endpoint_data: Dict):
        """Update endpoint data"""
        try:
            params = (
                endpoint_data['old_status_code'],
                endpoint_data['new_status_code'],
                endpoint_data['old_response_size'],
                endpoint_data['new_response_size'],
                endpoint_data['old_body_hash'],
                endpoint_data['new_body_hash'],
                endpoint_data['old_body_file_path'],
                endpoint_data['new_body_file_path'],
                endpoint_data['change_detected_at'],
                id
            )
            # self.logger.info(f"Query: {QueryManager.INSERT_ENDPOINT}, Parameters: {params}")
            self.db.execute_query(QueryManager.UPDATE_ENDPOINT_DATA, params)
        except Exception as e:
            self.logger.error(f"Failed to update endpoint {id}: {str(e)}")
            raise
    def update_endpoint_timestamp(self, id: int):
        try:
            self.db.execute_query(QueryManager.UPDATE_ENDPOINT_TIMESTAMP, (id,))
        except Exception as e:
            self.logger.error(f"Failed to update timestamp for endpoint {id}: {str(e)}")
            raise

    # --- Report ---
    def update_mobile_target_vuln(self, id, vulnerability_reported: Dict):
        """Update mobile target vulnerability"""
        try:
            params = (
                vulnerability_reported['vulnerability_reported'],
                id
            )
            self.db.execute_query(QueryManager.UPDATE_MOBILE_TARGET_DATA, params)
        except Exception as e:
            self.logger.error(f"Failed to update mobile target vulnerability {id}: {str(e)}")
            raise


class EndpointDeleteOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    # --- Endpoint Monitor ---
    def delete_endpoint(self, id: int):
        """Delete an endpoint and its associated changes"""
        try:
            # First delete associated changes due to foreign key constraint
            self.db.execute_query(QueryManager.DELETE_ENDPOINT, (id,))
        except Exception as e:
            self.logger.error(f"Failed to delete endpoint {id}: {str(e)}")
            raise

class EndpointQueryOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)

    # --- Endpoint Monitor ---
    def get_endpoint_data_by_url(self, url: str) -> Optional[Dict]:
        """Get current endpoint data from url"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ENDPOINT_DATA_BY_URL, (url,))
            if result:
                row = result[0]
                return {
                    'id': row[0],
                    'url': row[1],
                    'old_status_code': row[2],
                    'new_status_code': row[3],
                    'old_response_size': row[4],
                    'new_response_size': row[5],
                    'old_body_hash': row[6],
                    'new_body_hash': row[7],
                    'old_body_file_path': row[8],
                    'new_body_file_path': row[9],
                    'change_detected_at': row[10],
                    'last_check': row[11]
                }
            return None
        except Exception as e:
            self.logger.error(f"Failed to get endpoint data for {url}: {str(e)}")
            raise
    def get_endpoint_data_by_id(self, id: str) -> Optional[Dict]:
        """Get current endpoint data from id"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ENDPOINT_DATA_BY_ID, (id,))
            if result:
                row = result[0]
                return {
                    'id': row[0],
                    'url': row[1],
                    'old_status_code': row[2],
                    'new_status_code': row[3],
                    'old_response_size': row[4],
                    'new_response_size': row[5],
                    'old_body_hash': row[6],
                    'new_body_hash': row[7],
                    'old_body_file_path': row[8],
                    'new_body_file_path': row[9],
                    'change_detected_at': row[10],
                    'last_check': row[11]
                }
            return None
        except Exception as e:
            self.logger.error(f"Failed to get endpoint data for {id}: {str(e)}")
            raise
    def get_all_endpoints(self) -> List[Dict]:
        """Get all monitored endpoints"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ALL_ENDPOINTS)
            return [{'id': row[0], 'url': row[1]} for row in result]
        except Exception as e:
            self.logger.error(f"Failed to get endpoints: {str(e)}")
            raise
    
    # --- Report ---
    def get_program_details(self, program_id=None, program_name=None) -> List[Dict]:
        """Returns program details from program_id or program_name"""
        try:
            if program_id is not None: 
                results = self.db.execute_query(QueryManager.GET_PROGRAM_DATA_BY_ID, (program_id,))
                return results
            
            elif program_name is not None: 
                results = self.db.execute_query(QueryManager.GET_PROGRAM_DATA_BY_NAME, (program_name,))
                return results
            else:
                return None
        except Exception as e:
            self.logger.error(f"Failed to get program details [{str(program_name)}]: {str(e)}")
            raise

    def check_program_exists(self, program_name) -> List[Dict]:
        """Check if program exists"""
        try:
            result = self.db.execute_query(QueryManager.CHECK_PROGRAM_EXISTS, (program_name,))
            return result[0][0]
        except Exception as e:
            self.logger.error(f"Failed to check if program exists: {str(e)}")
            raise
    def check_mobile_target_exists(self, target_package) -> List[Dict]:
        """Check if mobile target exists"""
        try:
            result = self.db.execute_query(QueryManager.CHECK_MOBILE_TARGET_EXISTS, (target_package,))
            return result[0][0]
        except Exception as e:
            self.logger.error(f"Failed to check if mobile target exists: {str(e)}")
            raise
    def check_web_target_exists(self, target_domain) -> List[Dict]:
        """Check if web target exists"""
        try:
            result = self.db.execute_query(QueryManager.CHECK_WEB_TARGET_EXISTS, (target_domain,))
            return result[0][0]
        except Exception as e:
            self.logger.error(f"Failed to check if web target exists: {str(e)}")
            raise
    def check_mobile_target_vuln_exists(self, vulnerability_reported, target_package) -> List[Dict]:
        """Check if mobile target vulnerability already exists"""
        try:
            result = self.db.execute_query(QueryManager.CHECK_MOBILE_TARGET_VULN_EXISTS, (vulnerability_reported, target_package))
            return result[0][0]
        except Exception as e:
            logging.exception("An error occurred")
            self.logger.error(f"Failed to check if mobile target vulnerability already exists: {str(e)}")
            raise
    def get_mobile_target_data(self, target_id=None, target_package=None) -> List[Dict]:
        """Returns mobile target data from target_package name or target_id"""
        try:
            if target_id is not None:
                result = self.db.execute_query(QueryManager.GET_MOBILE_TARGET_BY_ID, (target_id,))
                return result
            if target_package is not None:
                result = self.db.execute_query(QueryManager.GET_MOBILE_TARGET_BY_NAME, (target_package,))
                return result
            else:
                return None
        except Exception as e:
            self.logger.error(f"Failed to get mobile target data: {str(e)}")
            raise

    