from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.db.db_operations import DatabaseOperations

from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='add', enable_debug = False)
from app.config.db_config import db_config

db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

async def add_program(program_data):
    try:
        db_ops.insert_operations().insert_program(program_data)
        logger.info("Program inserted successfully")
        return {"Program inserted successfully"}
    except Exception as e:
        logger.exception("Error in inserting program")
        return {"Error in inserting program"}
    
async def add_mobile_target(mobile_target_data):
    try:
        db_ops.insert_operations().insert_mobile_target(mobile_target_data)
        logger.info("Mobile target data inserted successfully")
        return {"Mobile target data inserted successfully"}
    except Exception as e:
        logger.exception("Error in inserting mobile target data")
        return {"Error in inserting mobile target data"}
    
async def add_web_target(web_target_data):
    try:
        db_ops.insert_operations().insert_web_target(web_target_data)
        logger.info("Web target data inserted successfully")
        return {"Web target data inserted successfully"}
    except Exception as e:
        logger.exception("Error in inserting web target data")
        return {"Error in inserting web target data"}