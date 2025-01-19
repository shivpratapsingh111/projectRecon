# db_operations.py

# ===[Imports]===
from typing import Dict, List, Optional
from psycopg2 import extensions

# ===[Local Imports]===
from app.services.monitor_endpoints.db.db_queries import QueryManager
from app.services.monitor_endpoints.db.db_manager import DatabaseManager
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


class EndpointUpdateOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
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
                endpoint_data['need_review'],
                id
            )
            self.db.execute_query(QueryManager.UPDATE_ENDPOINT_DATA, params)
        except Exception as e:
            logger.exception(f"Failed to update endpoint {id}: {str(e)}")
            raise
    def update_endpoint_timestamp(self, id):
        try:
            self.db.execute_query(QueryManager.UPDATE_ENDPOINT_TIMESTAMP, (id,))
        except Exception as e:
            logger.exception(f"Failed to update timestamp for endpoint {id}: {str(e)}")
            raise
    def update_need_review_endpoint(self, endpoint_id):
        try:
            self.db.execute_query(QueryManager.UPDATE_NEED_REVIEW_ENDPOINT, (endpoint_id,))
        except Exception as e:
            logger.exception(f"Failed to update need review endpoint {endpoint_id}: {str(e)}")
            raise
    def update_endpoint_status(self, endpoint_id, status):
        try:
            self.db.execute_query(QueryManager.UPDATE_ENDPOINT_STATUS, (status, endpoint_id,))
        except Exception as e:
            logger.exception(f"Failed to update status of endpoint {endpoint_id}: {str(e)}")
            raise
    def update_endpoint_interval(self, endpoint_id, interval):
        try:
            self.db.execute_query(QueryManager.UPDATE_ENDPOINT_SCAN_INTERVAL, (interval, endpoint_id,))
        except Exception as e:
            logger.exception(f"Failed to update scan interval for endpoint {endpoint_id}: {str(e)}")
            raise


class EndpointDeleteOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    # --- Endpoint Monitor ---
    def delete_endpoint(self, id: int):
        """Delete an endpoint and its associated changes"""
        try:
            # First delete associated changes due to foreign key constraint
            self.db.execute_query(QueryManager.DELETE_ENDPOINT, (id,))
        except Exception as e:
            logger.exception(f"Failed to delete endpoint {id}: {str(e)}")
            raise

class EndpointQueryOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    # --- Endpoint Monitor ---
    def get_endpoint_data_by_url(self, url: str) -> Optional[Dict]:
        """Get current endpoint data from url"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ENDPOINT_DATA_BY_URL, (url,))
            if result:
                row = result[0]
                return {
                    'id': row[0],
                    'program_id': row[1],
                    'target_id': row[2],
                    'scan_name': row[3],
                    'url': row[4],
                    'old_status_code': row[5],
                    'new_status_code': row[6],
                    'old_response_size': row[7],
                    'new_response_size': row[8],
                    'old_body_hash': row[9],
                    'new_body_hash': row[10],
                    'old_body_file_path': row[11],
                    'new_body_file_path': row[12],
                    'change_detected_at': row[13],
                    'need_review': row[14],
                    'last_check': row[15]
                }
            return None
        except Exception as e:
            logger.exception(f"Failed to get endpoint data for {url}: {str(e)}")
            raise
    def get_endpoint_data_by_id(self, id: str) -> Optional[Dict]:
        """Get current endpoint data from id"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ENDPOINT_DATA_BY_ID, (id,))
            if result:
                row = result[0]
                return {
                    'id': row[0],
                    'program_id': row[1],
                    'target_id': row[2],
                    'scan_name': row[3],
                    'url': row[4],
                    'old_status_code': row[5],
                    'new_status_code': row[6],
                    'old_response_size': row[7],
                    'new_response_size': row[8],
                    'old_body_hash': row[9],
                    'new_body_hash': row[10],
                    'old_body_file_path': row[11],
                    'new_body_file_path': row[12],
                    'change_detected_at': row[13],
                    'need_review': row[14],
                    'last_check': row[15]
                }
            return None
        except Exception as e:
            logger.exception(f"Failed to get endpoint data for {id}: {str(e)}")
            raise
    def get_all_endpoints(self) -> List[Dict]:
        """Get all monitored endpoints"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ALL_ENDPOINTS)
            return [{'id': row[0], 'url': row[1]} for row in result]
        except Exception as e:
            logger.exception(f"Failed to get endpoints: {str(e)}")
            raise
    def get_all_programs(self) -> List[Dict]:
        """Get all monitored endpoints"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ALL_PROGRAMS, None)
            return result
        except Exception as e:
            logger.exception(f"Failed to get endpoints: {str(e)}")
            raise
    def get_target_and_program_id(self, target_domain) -> List[Dict]:
        """Get target and program id for the endpoint"""
        try:
            result = self.db.execute_query(QueryManager.GET_TARGET_AND_PROGRAM_ID, (target_domain,))
            if result != []:
                return result[0]
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get target_id and program_id for endpoint: {str(e)}")
            raise
    def get_need_review_endpoints(self) -> List[Dict]:
        """Get all endpoints that are left to review"""
        try:
            result = self.db.execute_query(QueryManager.GET_NEED_REVIEW_ENDPOINTS, (None,))
            if result != []:
                return result
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get endpoints that need review: {str(e)}")
            raise
    def get_endpoint_response_body_filepaths(self, endpoint_id) -> List[Dict]:
        """Get all endpoints that are left to review
            Query Returns: [('/file/path1', '/file/path2', ...more)]
            Function Returns (return result[0]): ('/file/path1', '/file/path2', ...more)
        """
        try:
            result = self.db.execute_query(QueryManager.GET_ENDPOINT_RESPONSE_BODY_FILEPATHS, (endpoint_id,))
            if result != []:
                return result[0]
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get response body endpoints that need review: {str(e)}")
            raise
    def get_endpoints_data_by_status(self, status: str) -> List[Dict]:
        """Get data for all endpoints with provided status
            returns:- 
            [('abcd1', 'abcd2', 'Test-Scan', 4, 'active', 'http://accounts.google.com/', 200, '108KB', '/file/path1', datetime.datetime(2025, 1, 16, 11, 58, 15, 166147)), ('abcd3', 'abcd4', 'Test-Scan', 4, 'active', 'http://studio.youtube.com/', 200, '10KB', '/file/path2', datetime.datetime(2025, 1, 16, 11, 58, 15, 208807))]
        """
        try:
            result = self.db.execute_query(QueryManager.GET_ENDPOINTS_DATA_BY_STATUS, (status,))
            if result != []:
                return result
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get endpoints data with Status [{status}]: {str(e)}")
            raise
    def get_program_name(self, program_id) -> List[Dict]:
        """Get program name from program id
            Returns: [('Google',)]
            To get exact name use: result[0][0]
        """
        try:
            result = self.db.execute_query(QueryManager.GET_PROGRAM_NAME, (program_id,))
            if result != []:
                return result
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get program name for [{program_id}]: {str(e)}")
            raise

