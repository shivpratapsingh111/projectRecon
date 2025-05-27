from app.config.config  import *
from fastapi import APIRouter, Query

from app.config.db_config import db_config
from app.db.db_manager import DatabaseManager
from app.db.db_operations import DatabaseOperations

from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='summary', enable_debug = True)


db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

router = APIRouter()

@router.get("", tags=["start-operation-web"])
async def root():
    return {"Yeah Running!"}
        
@router.get("/count")
async def api_get_count(data: str = Query(..., description="Type of data to count: subdomains, programs, endpoints")):
    """
    Get the count of different entities based on the 'data' query parameter.
    Example: /count?data=subdomains
    """
    try:
        db = db_ops.query_operations()

        if data == "subdomains":
            result = db.get_web_targets_count()
            return {"count": result}
        elif data == "programs":
            result = db.get_programs_count()
            return {"count": result}
        elif data == "endpoints":
            result = db.get_endpoints_count()
            result = {"active": result[0][0], "stopped": result[0][1]}
            return {"count": result}
        else:
            return {"error": "Invalid data type"}, 400

    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        return {"error": "Internal server error"}, 500
    
@router.get("/program")
async def api_get_count(id: str = Query(..., description="Type of data to count: subdomains, programs, endpoints"), data: str = Query(..., description="Type of data to count: subdomains, programs, endpoints")):
    """
    Get the count of different entities based on the 'data' query parameter.
    Example: /count?data=subdomains
    """
    try:
        db = db_ops.query_operations()

        if data == "subdomains":
            result = db.get_web_targets_count()
            return {"count": result}
        elif data == "programs":
            result = db.get_programs_count()
            return {"count": result}
        elif data == "endpoints":
            result = db.get_endpoints_count()
            result = {"active": result[0][0], "stopped": result[0][1]}
            return {"count": result}
        else:
            return {"error": "Invalid data type"}, 400

    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        return {"error": "Internal server error"}, 500