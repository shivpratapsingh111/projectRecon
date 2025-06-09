# External Imports
import traceback
from typing import Literal
from fastapi import APIRouter, Query, status

# Local Imports
from app.config.db_config import db_config
from app.db.db_manager import DatabaseManager
from app.db.db_operations import DatabaseOperations
from app.logger.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG
from .data_model_summary import Generic__Response, DataCount__Response

# Initialization
logger = setup_logger(
    __name__, log_file_path="api_summary", enable_debug=LOG_LEVEL_DEBUG
)
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

router = APIRouter()

# Logic
@router.get(
        "/count",
        response_model = Generic__Response[DataCount__Response],
        summary =  "Fetch the count of data from database",
        )
async def api_get_count(data: Literal["subdomains", "programs", "endpoints"] = Query(..., description="Type of data to count: subdomains, programs, endpoints")):
    """
    Get the count of different entities based on the 'data' query parameter.
    Example: /count?data=subdomains
    """
    response = {
        "status": None,
        "message": "Successfully fetched data",
        "data": None,
    }
    try:
        db = db_ops.query_operations()

        if data == "subdomains":
            result = db.get_web_targets_count()
            response["status"] = True
            response["data"] = {"count": result}

        elif data == "programs":
            result = db.get_programs_count()
            response["status"] = True
            response["data"] = {"count": result}

        elif data == "endpoints":
            result = db.get_endpoints_count()
            response["status"] = True
            total = result[0][0] + result[0][1]
            response["data"] = {
                "count": total,
                "details": {"active": result[0][0], "stopped": result[0][1]}
            }
        else:
            return {
                    "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "status": False,
                    "message": f"Invalid data count requested, [{data}] data does not exsists in database ",
                }
    
        return Generic__Response[DataCount__Response](**response)
    
    except Exception as e:
        full_trace = traceback.format_exc()

        logger.exception(f"Error fetching count of {data} from database: {e}")
        return {
                "status": False,
                "message": f"Error fetching count of {data} from database",
                "debug": {"error": str(e), "traceback": full_trace},
            }