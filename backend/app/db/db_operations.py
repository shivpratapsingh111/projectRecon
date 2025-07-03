# External imports
from typing import Dict, List, Optional
from psycopg2 import extensions

# Internal imports
from app.db.db_queries import QueryManager
from app.interface.logger_manager import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Intialization
logger = setup_logger(
    __name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG
)

# Logic
class DatabaseOperations:
    def __init__(self, db_manager):
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
    def __init__(self, db_manager):
        self.db = db_manager

    # --- Endpoint Monitor ---
    def insert_endpoint(self, endpoint_data: Dict):
        """Record a change in endpoint response"""
        try:
            params = (
                endpoint_data["program_uuid"],
                endpoint_data["target_id"],
                endpoint_data["scan_name"],
                endpoint_data["status"],
                endpoint_data["url"],
                endpoint_data["old_status_code"],
                endpoint_data["new_status_code"],
                endpoint_data["old_response_size"],
                endpoint_data["new_response_size"],
                endpoint_data["old_body_hash"],
                endpoint_data["new_body_hash"],
                endpoint_data["old_body_file_path"],
                endpoint_data["new_body_file_path"],
                endpoint_data["change_detected_at"],
                endpoint_data["need_review"],
            )
            self.db.execute_query(QueryManager.INSERT_ENDPOINT, params)
            logger.info(
                f"Endpoint Data inserted successfully - [{str(endpoint_data['url'])}]"
            )

        except Exception as e:
            logger.exception(
                f"Failed to insert endpoint data [{str(endpoint_data['url'])}]: {str(e)}"
            )
            raise

    # --- Report ---
    def insert_program(self, program_data: Dict):
        try:
            params = (
                program_data["program_name"],
                program_data["program_url"],
                program_data["acquisitions"],
                program_data["email"],
                program_data["report_form"],
            )
            result = self.db.execute_query(QueryManager.INSERT_PROGRAM, params)
            logger.info(f"New program created with id {result[0]}")
            return result[0]
        except Exception as e:
            logger.exception(
                f"Failed to insert program data {str(program_data['program_name'])}: {str(e)}"
            )
            raise

    def insert_web_target(self, web_target_data: Dict):
        try:
            params = (
                web_target_data["program_uuid"],
                web_target_data["target_domain"],
                web_target_data["technology"],
                web_target_data["status_code"],
                web_target_data["port"],
                web_target_data["host"],
                web_target_data["ipv4"],
                web_target_data["ipv6"],
                web_target_data["response_time"],
                web_target_data["webserver"],
                web_target_data["vulnerability_reported"],
            )
            result = self.db.execute_query(QueryManager.INSERT_WEB_TARGET, params)
            logger.info(f"New web-target created with id {result[0]}")
            return result[0]
        except Exception as e:
            logger.exception(
                f"Failed to insert web target data {str(web_target_data['target_domain'])} : {str(e)}"
            )
            raise

    def insert_web_target_new(self, program_uuid, target_name):
        """
        Insert web target
        Returns id
        Example: 10499b38-3036-4d21-b693-3f1e74dea425
        """
        try:
            target_id = self.db.execute_query(
                QueryManager.INSERT_WEB_TARGET_NEW, (program_uuid, target_name)
            )
            logger.info(f"Web Target inserted successfully - [{target_name}]")
            return target_id[0]

        except Exception as e:
            logger.exception(
                f"Failed to insert web target [{target_name}] in program [{program_uuid}]: {str(e)}"
            )
            raise

    def insert_mobile_target(self, mobile_target_data: Dict):
        try:
            params = (
                mobile_target_data["program_uuid"],
                mobile_target_data["target_package"],
                mobile_target_data["target_apk"],
                extensions.adapt(mobile_target_data["technology"]),
                mobile_target_data["download_url"],
                extensions.adapt(mobile_target_data["vulnerability_reported"]),
            )
            result = self.db.execute_query(QueryManager.INSERT_MOBILE_TARGET, params)
            logger.info(f"New mobile-target created with id {result[0]}")

            return result[0]
        except Exception as e:
            logger.exception(
                f"Failed to insert mobile target data {str(mobile_target_data['target_package'])} : {str(e)}"
            )
            raise


class EndpointUpdateOperations:
    def __init__(self, db_manager):
        self.db = db_manager

    # --- Endpoint Monitor ---
    def update_endpoint_data(self, id: int, endpoint_data: Dict):
        """Update endpoint data"""
        try:
            params = (
                endpoint_data["old_status_code"],
                endpoint_data["new_status_code"],
                endpoint_data["old_response_size"],
                endpoint_data["new_response_size"],
                endpoint_data["old_body_hash"],
                endpoint_data["new_body_hash"],
                endpoint_data["old_body_file_path"],
                endpoint_data["new_body_file_path"],
                endpoint_data["change_detected_at"],
                endpoint_data["need_review"],
                id,
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
            self.db.execute_query(
                QueryManager.UPDATE_NEED_REVIEW_ENDPOINT, (endpoint_id,)
            )
        except Exception as e:
            logger.exception(
                f"Failed to update need review endpoint {endpoint_id}: {str(e)}"
            )
            raise

    def update_endpoint_status(self, endpoint_id, status):
        try:
            self.db.execute_query(
                QueryManager.UPDATE_ENDPOINT_STATUS,
                (
                    status,
                    endpoint_id,
                ),
            )
        except Exception as e:
            logger.exception(
                f"Failed to update status of endpoint {endpoint_id}: {str(e)}"
            )
            raise

    def update_endpoint_interval(self, endpoint_id, interval):
        try:
            self.db.execute_query(
                QueryManager.UPDATE_ENDPOINT_SCAN_INTERVAL,
                (
                    interval,
                    endpoint_id,
                ),
            )
        except Exception as e:
            logger.exception(
                f"Failed to update scan interval for endpoint {endpoint_id}: {str(e)}"
            )
            raise


    # --- Report ---
    def update_mobile_target_vuln(self, id, vulnerability_reported: Dict):
        """Update mobile target vulnerability"""
        try:
            params = (vulnerability_reported["vulnerability_reported"], id)
            self.db.execute_query(QueryManager.UPDATE_MOBILE_TARGET_DATA, params)
        except Exception as e:
            logger.exception(
                f"Failed to update mobile target vulnerability {id}: {str(e)}"
            )
            raise

    def update_web_targets_data(self, values: Dict):
        """Update web targets data"""
        try:
            self.db.execute_query(QueryManager.UPDATE_WEB_TARGETS_DATA, values)
        except Exception as e:
            logger.exception(f"Failed to update web targets data {id}: {str(e)}")
            raise


class EndpointDeleteOperations:
    def __init__(self, db_manager):
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
    def __init__(self, db_manager):
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
    def get_endpoint_data_by_url(self, url: str) -> Optional[Dict]:
        """Get current endpoint data from url"""
        try:
            result = self.db.execute_query(
                QueryManager.SELECT_ENDPOINT_DATA_BY_URL, (url,)
            )
            if result:
                row = result[0]
                return {
                    "id": row[0],
                    "program_uuid": row[1],
                    "target_id": row[2],
                    "scan_name": row[3],
                    "url": row[4],
                    "old_status_code": row[5],
                    "new_status_code": row[6],
                    "old_response_size": row[7],
                    "new_response_size": row[8],
                    "old_body_hash": row[9],
                    "new_body_hash": row[10],
                    "old_body_file_path": row[11],
                    "new_body_file_path": row[12],
                    "change_detected_at": row[13],
                    "need_review": row[14],
                    "last_check": row[15],
                }
            return None
        except Exception as e:
            logger.exception(f"Failed to get endpoint data for {url}: {str(e)}")
            raise

    def get_endpoint_data_by_id(self, id: str) -> Optional[Dict]:
        """Get current endpoint data from id"""
        try:
            result = self.db.execute_query(
                QueryManager.SELECT_ENDPOINT_DATA_BY_ID, (id,)
            )
            if result:
                row = result[0]
                return {
                    "id": row[0],
                    "program_uuid": row[1],
                    "target_id": row[2],
                    "scan_name": row[3],
                    "url": row[4],
                    "old_status_code": row[5],
                    "new_status_code": row[6],
                    "old_response_size": row[7],
                    "new_response_size": row[8],
                    "old_body_hash": row[9],
                    "new_body_hash": row[10],
                    "old_body_file_path": row[11],
                    "new_body_file_path": row[12],
                    "change_detected_at": row[13],
                    "need_review": row[14],
                    "last_check": row[15],
                }
            return None
        except Exception as e:
            logger.exception(f"Failed to get endpoint data for {id}: {str(e)}")
            raise

    def get_all_endpoints(self) -> List[Dict]:
        """Get all monitored endpoints"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ALL_ENDPOINTS)
            return [{"id": row[0], "url": row[1]} for row in result]
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

    def get_all_scannames(self) -> List[Dict]:
        """Get all scan names"""
        try:
            result = self.db.execute_query(QueryManager.SELECT_ALL_SCANNAMES, None)
            return result
        except Exception as e:
            logger.exception(f"Failed to get scan names: {str(e)}")
            raise

    def get_target_and_program_uuid(self, target_domain) -> List[Dict]:
        """Get target and program id for the endpoint"""
        try:
            result = self.db.execute_query(
                QueryManager.GET_TARGET_AND_program_uuid, (target_domain,)
            )
            if result != []:
                return result[0]
            else:
                return None
        except Exception as e:
            logger.exception(
                f"Failed to get target_id and program_uuid for endpoint: {str(e)}"
            )
            raise

    def get_need_review_endpoints(self) -> List[Dict]:
        """Get all endpoints that are left to review"""
        try:
            result = self.db.execute_query(
                QueryManager.GET_NEED_REVIEW_ENDPOINTS, (None,)
            )
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
            result = self.db.execute_query(
                QueryManager.GET_ENDPOINT_RESPONSE_BODY_FILEPATHS, (endpoint_id,)
            )
            if result != []:
                return result[0]
            else:
                return None
        except Exception as e:
            logger.exception(
                f"Failed to get response body endpoints that need review: {str(e)}"
            )
            raise

    def get_endpoints_data_by_status(self, status: str) -> List[Dict]:
        """Get data for all endpoints with provided status
        returns:-
        [('abcd1', 'abcd2', 'Test-Scan', 4, 'stopped', 'http://accounts.google.com/', 200, '108KB', '/file/path1', datetime.datetime(2025, 1, 16, 11, 58, 15, 166147)), ('abcd3', 'abcd4', 'Test-Scan', 4, 'active', 'http://studio.youtube.com/', 200, '10KB', '/file/path2', datetime.datetime(2025, 1, 16, 11, 58, 15, 208807))]
        """
        try:
            result = self.db.execute_query(
                QueryManager.GET_ENDPOINTS_DATA_BY_STATUS, (status,)
            )
            if result != []:
                return result
            else:
                return None
        except Exception as e:
            logger.exception(
                f"Failed to get endpoints data with Status [{status}]: {str(e)}"
            )
            raise

    def get_program_name(self, program_uuid) -> List[Dict]:
        """Get program name from program id
        Returns: [('Google',)]
        To get exact name use: result[0][0]
        """
        try:
            result = self.db.execute_query(
                QueryManager.GET_PROGRAM_NAME, (program_uuid,)
            )
            if result != []:
                return result
            else:
                return None
        except Exception as e:
            logger.exception(
                f"Failed to get program name for [{program_uuid}]: {str(e)}"
            )
            raise


    # --- Report ---
    def get_program_details(self, program_uuid=None, program_name=None) -> List[Dict]:
        """Returns program details from program_uuid or program_name"""
        try:
            if program_uuid is not None:
                results = self.db.execute_query(
                    QueryManager.GET_PROGRAM_DATA_BY_ID, (program_uuid,)
                )
                return results

            elif program_name is not None:
                results = self.db.execute_query(
                    QueryManager.GET_PROGRAM_DATA_BY_NAME, (program_name,)
                )
                return results
            else:
                return None
        except Exception as e:
            logger.exception(
                f"Failed to get program details [{str(program_name)}]: {str(e)}"
            )
            raise

    def check_program_exists(self, program_name) -> List[Dict]:
        """Check if program exists"""
        try:
            result = self.db.execute_query(
                QueryManager.CHECK_PROGRAM_EXISTS, (program_name,)
            )
            return result[0][0]
        except Exception as e:
            logger.exception(f"Failed to check if program exists: {str(e)}")
            raise

    def check_mobile_target_exists(self, target_package) -> List[Dict]:
        """Check if mobile target exists"""
        try:
            result = self.db.execute_query(
                QueryManager.CHECK_MOBILE_TARGET_EXISTS, (target_package,)
            )
            return result[0][0]
        except Exception as e:
            logger.exception(f"Failed to check if mobile target exists: {str(e)}")
            raise

    def check_web_target_exists(self, target_domain) -> List[Dict]:
        """Check if web target exists"""
        try:
            result = self.db.execute_query(
                QueryManager.CHECK_WEB_TARGET_EXISTS, (target_domain,)
            )
            return result[0][0]
        except Exception as e:
            logger.exception(f"Failed to check if web target exists: {str(e)}")
            raise

    def check_mobile_target_vuln_exists(
        self, vulnerability_reported, target_package
    ) -> List[Dict]:
        """Check if mobile target vulnerability already exists"""
        try:
            result = self.db.execute_query(
                QueryManager.CHECK_MOBILE_TARGET_VULN_EXISTS,
                (vulnerability_reported, target_package),
            )
            return result[0][0]
        except Exception as e:
            logger.exception(
                f"Failed to check if mobile target vulnerability already exists: {str(e)}"
            )
            raise

    def get_mobile_target_data(self, target_id=None, target_package=None) -> List[Dict]:
        """Returns mobile target data from target_package name or target_id"""
        try:
            if target_id is not None:
                result = self.db.execute_query(
                    QueryManager.GET_MOBILE_TARGET_BY_ID, (target_id,)
                )
                return result
            if target_package is not None:
                result = self.db.execute_query(
                    QueryManager.GET_MOBILE_TARGET_BY_NAME, (target_package,)
                )
                return result
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get mobile target data: {str(e)}")
            raise

    def get_all_web_targets(self) -> List[Dict]:
        """Returns all web targets present in DB"""
        try:
            result = self.db.execute_query(QueryManager.GET_ALL_WEB_TARGETS, None)
            return result
        except Exception as e:
            logger.exception(f"Failed to all web targets: {str(e)}")
            raise

    def get_program_name(self, program_uuid) -> List[Dict]:
        """Get program name from program id"""
        try:
            result = self.db.execute_query(
                QueryManager.GET_PROGRAM_NAME, (program_uuid,)
            )
            if result != []:
                return result
            else:
                return None
        except Exception as e:
            logger.exception(
                f"Failed to get program name for [{program_uuid}]: {str(e)}"
            )
            raise

    def get_program_uuid(self, program_name) -> List[Dict]:
        """
        Get program name from program id
        Returns program_uuid
        Example: 1fd2a300-8646-455a-9d0b-c090deae67d4
        """
        try:
            result = self.db.execute_query(
                QueryManager.GET_PROGRAM_UUID, (program_name,)
            )
            if result != []:
                return result[0][0]
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get program id for [{program_name}]: {str(e)}")
            raise

    def get_web_target_id(self, target_domain) -> List[Dict]:
        """Returns web target ID by searching from target domain
        Returns: id
        Example: 8bc2d48a-e09a-4800-ab80-580cc62063b2
        """
        try:
            result = self.db.execute_query(
                QueryManager.GET_WEB_TARGET_ID, (target_domain,)
            )
            return result[0][0]
        except Exception as e:
            logger.exception(f"Failed to web target id [{target_domain}]: {str(e)}")
            raise

    def get_web_targets_count(self) -> List[Dict]:
        """Get total web targets count
        Returns: count of web targets
        Example: 2450
        """
        try:
            result = self.db.execute_query(QueryManager.GET_WEB_TARGETS_COUNT, None)
            if result != []:
                return result[0][0]
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get web targets count: {str(e)}")
            raise

    def get_specifc_web_targets_count(self, program_uuid) -> List[Dict]:
        """Get total web targets count of specifc program
        Returns: count of web targets
        Example: 203
        """
        try:
            result = self.db.execute_query(
                QueryManager.GET_SPECIFIC_WEB_TARGETS_COUNT, (program_uuid,)
            )
            if result != []:
                return result[0][0]
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get web targets count: {str(e)}")
            raise

    def get_programs_count(self) -> List[Dict]:
        """Get total programs count
        Returns: count of programs
        Example: 10
        """
        try:
            result = self.db.execute_query(QueryManager.GET_PROGRAMS_COUNT, None)
            if result != []:
                return result[0][0]
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get programs count: {str(e)}")
            raise

    def get_endpoints_count(self) -> List[Dict]:
        """Get count of endpoints with active and stopped monitoring
        Returns: [(count of active, count of stopped)]
        Example: [(3, 5)]
        Means it has 3 active endpoints and 5 stopped.
        """
        try:
            result = self.db.execute_query(QueryManager.GET_ENDPOINTS_COUNT, None)
            if result != []:
                return result
            else:
                return None
        except Exception as e:
            logger.exception(f"Failed to get endpoints count: {str(e)}")
            raise
