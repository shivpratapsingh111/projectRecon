# External Imports
from fastapi import HTTPException

# Local Imports
from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.db.db_operations import DatabaseOperations
from app.logger.logger import setup_logger
from app.config.db_config import db_config

# Intialization
logger = setup_logger(__name__, log_file_path='add', enable_debug = False)
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)


async def add_program(program_data):
    try:
        program_id = db_ops.insert_operations().insert_program(program_data)
        logger.info("Program inserted successfully")
    
        return {
            "message": "Program inserted successfully",
            "program_id": program_id
        }
    
    except Exception as e:
        logger.exception("Error in inserting program")
        raise HTTPException(status_code=500, detail="Error inserting program")
    
async def add_mobile_target(mobile_target_data):
    try:
        mobile_target_id = db_ops.insert_operations().insert_mobile_target(mobile_target_data)
        logger.info("Mobile target inserted successfully")
    
        return {
            "message": "Mobile target inserted successfully",
            "id": mobile_target_id
        }
    
    except Exception as e:
        logger.exception("Error in inserting mobile target")
        raise HTTPException(status_code=500, detail="Error in inserting mobile target")
        
async def add_web_target(web_target_data):
    try:
        web_target_id = db_ops.insert_operations().insert_web_target(web_target_data)
        logger.info("Web target inserted successfully")

        return {
            "message": "Web target inserted successfully",
            "id": web_target_id
        }
    
    except Exception as e:
        logger.exception("Error in inserting web target")
        raise HTTPException(status_code=500, detail="Error in inserting web target")