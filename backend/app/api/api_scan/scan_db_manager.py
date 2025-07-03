# External imports
import traceback

# Internal imports
from app.interface.logger_manager import setup_logger
from app.config.config import LOG_LEVEL_DEBUG
from app.interface.database_manager import db_ops

# Initialization
logger = setup_logger(__name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG)

# Logic
async def get_existing_program_names():
    try:
        data = db_ops.query_operations().get_all_programnames()

        if data is not None:
            flattened = [item[0] for item in data]
            unique_items = sorted(set(flattened))
            return {
                "status": True,
                "message": "Fetched program names",
                "data": {"program_names": unique_items},
            }
        else:
            return {
                "status": True,
                "message": "No programs found",
                "data": {"program_names": None},
            }
    except Exception as e:
        logger.exception("Error in getting program names")
        full_trace = traceback.format_exc()
        return {
            "status": False,
            "message": "Error in getting program names",
            "debug": {"error": str(e), "traceback": full_trace},
        }
