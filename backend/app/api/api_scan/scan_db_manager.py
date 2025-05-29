# External Imports
import traceback

# Local Imports
from app.config.db_config import db_config
from app.services.scans.db.db_manager import DatabaseManager
from app.services.scans.db.db_operations import DatabaseOperations
from app.logger.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Initialization
logger = setup_logger(__name__, log_file_path="api_scan", enable_debug=LOG_LEVEL_DEBUG)
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)


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
