from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from urllib.parse import urlparse
import logging
import shutil
import json
import os

from app.config.db_config import db_config
from app.config.config import root_Data_Dir

from app.services.scans.db.db_manager import DatabaseManager
from app.services.scans.db.db_operations import DatabaseOperations
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)


db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)
    
async def get_existing_programnames():
    try:
        data = db_ops.query_operations().get_all_programnames()

        if data is not None:
            flattened = [item[0] for item in data]  # Flatten the list
            unique_items = sorted(set(flattened))   # Remove duplicates and sort
            return JSONResponse(content={"scan_name": unique_items}, status_code=200)
        else:
            return None
    
    except Exception as e:
        logger.exception("Error in getting program names")
        raise HTTPException(status_code=500, detail=f"Error in getting program names: {e}")
