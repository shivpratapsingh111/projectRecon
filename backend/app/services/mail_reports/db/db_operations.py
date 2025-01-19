# db_operations.py

# ===[Imports]===
from typing import Dict, List
from psycopg2 import extensions

# ===[Local Imports]===
from app.services.mail_reports.db.db_queries import QueryManager
from app.services.mail_reports.db.db_manager import DatabaseManager
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='mail_reports', enable_debug = False)


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
            logger.info(f"New program created with id {result[0]}")
            return result[0]
        except Exception as e:
            logger.exception(f"Failed to insert program data {str(program_data['program_name'])}: {str(e)}")
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
            logger.info(f"New web-target created with id {result[0]}")
            return result[0]
        except Exception as e:
            logger.exception(f"Failed to insert web target data {str(web_target_data['target_domain'])} : {str(e)}")
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
            logger.info(f"New mobile-target created with id {result[0]}")
            
            return result[0]
        except Exception as e:
            logger.exception(f"Failed to insert mobile target data {str(mobile_target_data['target_package'])} : {str(e)}")
            raise


class EndpointUpdateOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

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
            logger.exception(f"Failed to update mobile target vulnerability {id}: {str(e)}")
            raise


class EndpointDeleteOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager


class EndpointQueryOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

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
            logger.exception(f"Failed to get program details [{str(program_name)}]: {str(e)}")
            raise

    def check_program_exists(self, program_name) -> List[Dict]:
        """Check if program exists"""
        try:
            result = self.db.execute_query(QueryManager.CHECK_PROGRAM_EXISTS, (program_name,))
            return result[0][0]
        except Exception as e:
            logger.exception(f"Failed to check if program exists: {str(e)}")
            raise
    def check_mobile_target_exists(self, target_package) -> List[Dict]:
        """Check if mobile target exists"""
        try:
            result = self.db.execute_query(QueryManager.CHECK_MOBILE_TARGET_EXISTS, (target_package,))
            return result[0][0]
        except Exception as e:
            logger.exception(f"Failed to check if mobile target exists: {str(e)}")
            raise
    def check_web_target_exists(self, target_domain) -> List[Dict]:
        """Check if web target exists"""
        try:
            result = self.db.execute_query(QueryManager.CHECK_WEB_TARGET_EXISTS, (target_domain,))
            return result[0][0]
        except Exception as e:
            logger.exception(f"Failed to check if web target exists: {str(e)}")
            raise
    def check_mobile_target_vuln_exists(self, vulnerability_reported, target_package) -> List[Dict]:
        """Check if mobile target vulnerability already exists"""
        try:
            result = self.db.execute_query(QueryManager.CHECK_MOBILE_TARGET_VULN_EXISTS, (vulnerability_reported, target_package))
            return result[0][0]
        except Exception as e:
            logger.exception(f"Failed to check if mobile target vulnerability already exists: {str(e)}")
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
            logger.exception(f"Failed to get mobile target data: {str(e)}")
            raise