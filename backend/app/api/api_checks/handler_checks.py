# External imports
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Literal
import traceback

# Internal imports
from app.interface.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG
from .data_model_checks import Generic__Response

# Initialization
logger = setup_logger(
    __name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG
)
router = APIRouter()


# Handlers
@router.get(
    "/pre-run",
    response_model=Generic__Response,
    summary="Get review endpoints data",
)
async def get_endpoints(state: Literal["active", "stopped"]):
    try:
        result = 2
        if result["status"]:
            return Generic__Response(**result)
        else:
            return JSONResponse(
                status_code=result.get(
                    "status_code",
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                ),
                content=result,
            )

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.error(f"Error at api handler level: {e} \n {full_trace}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": False,
                "message": "Error at api handler level",
                "debug": {"error": str(e), "traceback": full_trace},
            },
        )


# ---


@router.post(
    "/review-endpoints/update-status/{endpoint_id}",
    response_model=Generic__Response,
    summary="Mark endpoint as reviewd",
)
async def update_review_endpoint(endpoint_id):
    try:

        result = 1
        if result["status"]:
            return Generic__Response(**result)
        else:
            return JSONResponse(
                status_code=result.get(
                    "status_code",
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                ),
                content=result,
            )

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.error(f"Error at api handler level: {e} \n {full_trace}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": False,
                "message": "Error at api handler level",
                "debug": {"error": str(e), "traceback": full_trace},
            },
        )


# ---

