# External imports
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Literal
import traceback

# Internal imports
from app.interface.logger_manager import setup_logger
from app.config.config import LOG_LEVEL_DEBUG
from .data_model_verify import Generic__Response, EnvironmentReport__Response
from .verify_setup import verify_setup

# Initialization
logger = setup_logger(
    __name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG
)
router = APIRouter()


# Handlers
@router.get(
    "/setup",
    response_model=Generic__Response[EnvironmentReport__Response],
    summary="Verify framework setup",
)
async def api_verify_setup():
    try:

        result = verify_setup()
        if result["status"]:
            return Generic__Response[EnvironmentReport__Response](**result)
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

