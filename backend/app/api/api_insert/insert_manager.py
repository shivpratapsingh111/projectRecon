# External imports
import traceback

# Internal imports
from app.interface.database_manager import db_ops
from app.interface.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Intialization
logger = setup_logger(
    __name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG
)

# Logic
async def insert_program(program_data):
    try:
        program_id = db_ops.insert_operations().insert_program(program_data)
        logger.info("Program inserted successfully")
        return {
            "status": True,
            "message": "Program inserted successfully",
            "data": {"id": program_id},
        }
    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception("Error in inserting program")
        return {
            "status": False,
            "message": "Error in inserting program",
            "debug": {"error": str(e), "traceback": full_trace},
            "data": {"id": None},
        }


# ---


async def insert_mobile_target(mobile_target_data):
    try:
        mobile_target_id = db_ops.insert_operations().insert_mobile_target(
            mobile_target_data
        )
        logger.info("Mobile target inserted successfully")
        return {
            "status": True,
            "message": "Mobile target inserted successfully",
            "data": {"id": mobile_target_id},
        }

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception("Error in inserting mobile target")
        return {
            "status": False,
            "message": "Error in inserting mobile target",
            "debug": {"error": str(e), "traceback": full_trace},
            "data": {"id": None},
        }


# ---


async def insert_web_target(web_target_data):
    try:
        web_target_id = db_ops.insert_operations().insert_web_target(web_target_data)
        logger.info("Web target inserted successfully")
        return {
            "status": True,
            "message": "Web target inserted successfully",
            "data": {"id": web_target_id},
        }

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception("Error in inserting web target")
        return {
            "status": False,
            "message": "Error in inserting web target",
            "debug": {"error": str(e), "traceback": full_trace},
            "data": {"id": None},
        }
