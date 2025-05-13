# External Imports
from fastapi import APIRouter
from fastapi import UploadFile, Form
from typing import Union
import asyncio

# Internal Imports
from app.logger.logger import setup_logger
from app.config.config  import *
from app.api.monitor_endpoints.endpoint_db_manager import (
	add_new_endpoints,
    get_review_endpoints,
    get_response_body_changes,
    mark_review_endpoints,
    get_endpoints_by_status,
    update_endpoint_status,
    update_endpoint_scan_interval,
    get_existing_programs,
    get_existing_scans
)
from app.api.monitor_endpoints.start_scan import (
    start_periodic_monitoring_scans,
    stop_periodic_monitoring_scans,
    get_scan_state
)

# Initialization
logger = setup_logger(__name__, log_file_path='monitor_endpoints', enable_debug = False)
router = APIRouter()

# Handlers
@router.post("/new")
async def api_add_new_endpoints(
    endpoint: Union[str, None] = Form(None), 
    scan_name: Union[str, None] = Form(None),
    file: Union[UploadFile, None] = None,
    scan_options: Union[str, None] = Form(None),
):
    return await add_new_endpoints(scan_name, endpoint, file, scan_options)

@router.get("/get-scan-state")
async def api_get_scan_state():
    return await get_scan_state()

@router.get("/get-existing-programs")
async def api_get_existing_programs():
    return await get_existing_programs()

@router.get("/get-existing-scans")
async def api_get_existing_scans():
    return await get_existing_scans()

@router.post("/start-scans")
async def api_start_scan():
    asyncio.create_task(start_periodic_monitoring_scans())
    return {"message": "Scan Started"}

@router.post("/stop-scans")
async def api_start_scan():
    return await stop_periodic_monitoring_scans()

@router.get("/review-endpoints")
async def review_endpoints():
    return get_review_endpoints()

@router.get("/get-endpoints/{status}")
async def get_endpoints(status: str):
    return get_endpoints_by_status(status)

@router.get("/review-endpoints/response-body-changes/{endpoint_id}")
async def response_body_changes(endpoint_id):
    return get_response_body_changes(endpoint_id)

@router.post("/review-endpoints/update-status/{endpoint_id}")
async def update_review_endpoint(endpoint_id):
    return mark_review_endpoints(endpoint_id)

@router.post("/update-endpoint-interval/{endpoint_id}/{scan_interval}")
async def update_endpoint_interval(endpoint_id, scan_interval):
    return update_endpoint_scan_interval(endpoint_id, scan_interval)

@router.post("/review-endpoints/update-status/{endpoint_id}/{status}")
async def api_update_endpoint_status(endpoint_id, status):
    return update_endpoint_status(endpoint_id, status)
