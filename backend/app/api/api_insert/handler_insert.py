# External Imports
import traceback
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

# Local Imports
from app.logger.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG
from .insert_manager import insert_program
from .insert_manager import insert_mobile_target
from .insert_manager import insert_web_target
from .data_model_insert import (
    InsertProgram__Request,
    InsertMobileTarget__Request,
    InsertWebTarget__Request,
    Generic__Response,
)

# Initialization
logger = setup_logger(
    __name__, log_file_path="api_insert", enable_debug=LOG_LEVEL_DEBUG
)
router = APIRouter()


# Handlers
@router.post(
    "/program",
    response_model=Generic__Response,
    summary="Insert a new program in database",
)
async def api_insert_program(program_data: InsertProgram__Request):

    try:
        program_dict = program_data.dict()
        program_dict["program_url"] = str(program_dict["program_url"])
        result = await insert_program(program_dict)

        if result["status"]:
            return Generic__Response(**result)
        else:
            return JSONResponse(
                status_code=result.get(
                    "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
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
    "/target/mobile",
    response_model=Generic__Response,
    summary="Add a new mobile target in database",
)
async def api_insert_mobile_target(data: InsertMobileTarget__Request):

    try:
        if not data.target_package or not data.program_uuid:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=Generic__Response(
                    status=False,
                    message="Both program_uuid and target_package must be provided",
                ),
            )
        mobile_target_data = {
            "program_uuid": str(data.program_uuid),
            "target_package": data.target_package,
            "target_apk": data.target_apk if data.target_apk else None,
            "technology": data.technology or [""],
            "download_url": str(data.download_url) if data.download_url else None,
            "vulnerability_reported": [],
        }
        result = await insert_mobile_target(mobile_target_data)

        if result["status"]:
            return Generic__Response(**result)
        else:
            return JSONResponse(
                status_code=result.get(
                    "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
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
    "/target/web",
    response_model=Generic__Response,
    summary="Add a new web target in database",
)
async def api_insert_web_target(data: InsertWebTarget__Request):

    try:
        if not data.target_domain or not data.program_uuid:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=Generic__Response(
                    status=False,
                    message="Both target domain and program_uuid is required",
                ),
            )
        web_target_data = {
            "program_uuid": str(data.program_uuid),
            "target_domain": data.target_domain,
            "technology": data.technology or [""],
            "status_code": None,
            "port": None,
            "host": None,
            "ipv4": [""],
            "ipv6": [""],
            "response_time": None,
            "webserver": None,
            "vulnerability_reported": [""],
        }
        result = await insert_web_target(web_target_data)

        if result["status"]:
            return Generic__Response(**result)
        else:
            return JSONResponse(
                status_code=result.get(
                    "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
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
