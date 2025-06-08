# External Imports
from fastapi import APIRouter, UploadFile, Form, status
from fastapi.responses import JSONResponse
from typing import Literal, Optional
import asyncio, traceback

# Local Imports
from app.logger.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG
from app.api.api_monitor_endpoints.endpoint_db_manager import (
    insert_new_endpoints,
    get_review_endpoints,
    get_response_body_changes,
    mark_review_endpoints,
    get_endpoints_by_state,
    update_endpoint_status,
    update_endpoint_scan_interval,
    get_existing_programs,
    get_existing_scans,
)
from app.api.api_monitor_endpoints.start_scan import (
    start_periodic_monitoring_scans,
    stop_periodic_monitoring_scans,
    get_scan_state,
)
from .data_model_monitor import (
    GetScanStatus__Response,
    GetExistingPrograms__Response,
    GetExistingScanNames__Response,
    GetReviewEndpointsData__Response,
    GetEndpointsByStatus__Response,
    GetResponseBodyChanges__Response,
    Generic__Response,
)

# Initialization
logger = setup_logger(
    __name__, log_file_path="api_monitor_endpoints", enable_debug=LOG_LEVEL_DEBUG
)
router = APIRouter()


# Handlers
@router.post(
    "/new",
    response_model=Generic__Response,
    summary="Insert a new endpoint to monitor",
)
async def api_insert_new_endpoints(
    endpoint: str = Form(..., example="https://api.example.com/v1/users"),
    scan_name: str = Form(..., example="Scan_1"),
    file: Optional[UploadFile] = Form(default=None),
    scan_options: Optional[str] = Form(default=None),
):
    try:
        result = await insert_new_endpoints(scan_name, endpoint, file, scan_options)

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


@router.get(
    "/get-scan-state",
    response_model=Generic__Response[GetScanStatus__Response],
    summary="Get endpoint monitor scan status",
)
async def api_get_scan_state():
    try:
        result = await get_scan_state()
        return Generic__Response[GetScanStatus__Response](**result)
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


@router.get(
    "/get-existing-programs",
    response_model=Generic__Response[GetExistingPrograms__Response],
    summary="Get existing programs from database",
)
async def api_get_existing_programs():
    try:
        result = await get_existing_programs()
        if result["status"]:
            return Generic__Response[GetExistingPrograms__Response](**result)
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


@router.get(
    "/get-existing-scans",
    response_model=Generic__Response[GetExistingScanNames__Response],
    summary="Get existing scan names from database",
)
async def api_get_existing_scans():
    try:
        result = await get_existing_scans()
        if result["status"]:
            return Generic__Response[GetExistingScanNames__Response](**result)
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
    "/start-scans",
    response_model=Generic__Response,
    summary="Start endpoint monitoring scan",
)
async def api_start_scan():
    try:
        asyncio.create_task(start_periodic_monitoring_scans())
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": True,
                "message": "Scan started successfully",
            },
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
    "/stop-scans",
    response_model=Generic__Response,
    summary="Stop endpoint monitoring scan",
)
async def api_start_scan():
    try:
        result = await stop_periodic_monitoring_scans()
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


@router.get(
    "/review-endpoints",
    response_model=Generic__Response[GetReviewEndpointsData__Response],
    summary="Get review endpoints data",
)
async def review_endpoints():
    try:
        result = get_review_endpoints()
        if result["status"]:
            return Generic__Response[GetReviewEndpointsData__Response](**result)
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


@router.get(
    "/get-endpoints/{state}",
    response_model=Generic__Response[GetEndpointsByStatus__Response],
    summary="Get review endpoints data",
)
async def get_endpoints(state: Literal["active", "stopped"]):
    try:
        result = get_endpoints_by_state(state)
        if result["status"]:
            return Generic__Response[GetEndpointsByStatus__Response](**result)
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
@router.get(
    "/review-endpoints/response-body-changes/{endpoint_id}",
    response_model=Generic__Response[GetResponseBodyChanges__Response],
    summary="Get old response and new response of the endpoint",
)
async def response_body_changes(endpoint_id):
    try:
        result = get_response_body_changes(endpoint_id)
        if result["status"]:
            return Generic__Response[GetResponseBodyChanges__Response](**result)
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

        result = mark_review_endpoints(endpoint_id)
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
    "/update-endpoint-interval/{endpoint_id}/{scan_interval}",
    response_model=Generic__Response,
    summary="Update endpoint scan interval",
)
async def update_endpoint_interval(endpoint_id, scan_interval: int):
    try:

        result = update_endpoint_scan_interval(endpoint_id, scan_interval)
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
    "/review-endpoints/update-status/{endpoint_id}/{status}",
    response_model=Generic__Response,
    summary="Update endpoint status to either 'active' or 'stopped'",
)
async def api_update_endpoint_status(endpoint_id, status: Literal["active", "stopped"]):
    try:

        result = update_endpoint_status(endpoint_id, status)
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
