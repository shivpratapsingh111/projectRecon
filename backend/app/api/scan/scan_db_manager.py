# External Imports
from fastapi.responses import JSONResponse
from fastapi import HTTPException

# Internal Imports
from app.config.db_config import db_config
from app.services.scans.db.db_manager import DatabaseManager
from app.services.scans.db.db_operations import DatabaseOperations
from app.logger.logger import setup_logger

# Initialization
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

# Logic
async def get_existing_program_names():
    try:
        data = db_ops.query_operations().get_all_programnames()

        if data is not None:
            flattened = [item[0] for item in data]
            unique_items = sorted(set(flattened))
            return JSONResponse(content={"program_names": unique_items}, status_code=200)
        else:
            return None
    
    except Exception as e:
        logger.exception("Error in getting program names")
        raise HTTPException(status_code=500, detail=f"Error in getting program names: {e}")
