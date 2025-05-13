# External Imports
import asyncio, json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query, Path as FPath, Response
from fastapi.responses import FileResponse
from typing import Optional

# Internal Imports
from app.api.results.read_results import websocket_read_results
from app.api.results.read_results import http_read_results
from app.api.results.read_results import get_log_file_content
from app.api.results.get_download_ready import get_download
from app.api.results.get_download_ready import get_program_scan
from app.logger.logger import setup_logger
from .data_model_results import (
    StoredResultsResponse,
    GetLogFileContentResponse,
    LogTypeResponse,
    DownloadType,
    ProgramDownloadRequest,
    TargetDownloadRequest
    )

# Initialization
logger = setup_logger(__name__, log_file_path='results', enable_debug = True)
router = APIRouter()

# Handlers
@router.websocket("/subdomains/{target_uuid}")
async def api_running_results_subdomains(target_uuid, websocket: WebSocket):
    """
    - Get real-time stream of currenlty found subdomains, that refreshes every 10 seconds
    - Returns a list of strings
    - Ex: "[\"abc1.google.com\", \"abc2.google.com\", \"abc3.google.com\", \"abc4.google.com\"]"
    """
    try:
        await websocket.accept()
        while True:
            result = await websocket_read_results(target_uuid, 'subdomains') 
            
            await websocket.send_text(json.dumps(result))
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        logger.warning("Client disconnected")
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()

# ---

@router.websocket("/urls/{target_uuid}")
async def api_running_results_urls(target_uuid, websocket: WebSocket):
    """
    - Get real-time stream of currenlty found urls, that refreshes every 10 seconds
    - Returns a list of strings
    - Ex: "[\"https://abc.com/path\", \"https://abc.com/path/ac\", \"https://abc.com/path/12\", \"https://abc.com/path/231\"]"
    """

    try:
        await websocket.accept() 
        while True:
            result = await websocket_read_results(target_uuid, 'urls')
            
            await websocket.send_text(json.dumps(result))
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        logger.warning("Client disconnected")
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()

# ---

@router.get(
    "/get/{target_uuid}",
    response_model=StoredResultsResponse,
    summary="Fetch stored scan results",
    description="Retrieve a paginated portion of stored scan results for a given UUID and file."
)
async def api_stored_results(
    target_uuid: str,
    file: str = Query(..., description="The name of the file to fetch results from", example="subdomains.txt"),
    limit: Optional[int] = Query(20, gt=0, description="Max number of lines to return", example=20),
    offset: int = Query(0, ge=0, description="Line offset to start returning from", example=0)
):
    """
    Get stored scan results for a specific target UUID and file.

    - **target_uuid**: Unique ID for the scan target.
    - **file**: Name of the file containing the results.
    - **limit**: Maximum number of result lines to return (default 20).
    - **offset**: Start line offset in the results (default 0).
    """
    try:
        result = await http_read_results(target_uuid, file, limit, offset)
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ---

@router.get(
    "/get-log",
    response_model=GetLogFileContentResponse,
    summary="Fetch raw process log",
    description=(
        "Retrieve the full contents of a process's log file. "
        "The response is a JSON object containing the raw log lines, "
        "with newlines escaped (`\\n`) and double quotes escaped."
    ),
    response_description="A JSON object with a single `content` field holding the escaped log text"
)
async def api_get_log_file_content(
    pid: int = Query(
        ...,
        description="The process ID whose log you want to retrieve",
        example=8190
    ),
    log_type: LogTypeResponse = Query(
        ...,
        description="Type of log to fetch (`stderr_log` or `stdout_log`)",
        example=LogTypeResponse.stdout_log
    )
):
    """
    - **pid**: Integer process ID.
    - **log_type**: Either `stderr_log` or `stdout_log`.
    """
    try:
        raw = await get_log_file_content(pid, log_type.value)
        return GetLogFileContentResponse(content=raw)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error fetching log for pid={pid}, type={log_type}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

#---

@router.get(
    "/download/{program_name}",
    summary="Download full program scan as ZIP",
    description=(
        "Returns a `.zip` archive containing all stored scan results for the given program name. "
        "Delivered as a downloadable attachment."
    ),
    response_description="ZIP file download",
response_class=FileResponse)
async def download_program_scan(
    program_name: str = FPath(
        ...,
        description="Program identifier to fetch scan results for",
        example="google"
    )
):
    """
    - **program_name**: the name of the program whose scan you wish to download.
    """
    req = ProgramDownloadRequest(program_name=program_name)

    try:
        file_response = await get_program_scan(req.program_name)
        return file_response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to download program scan for {req.program_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ---

@router.get(
    "/download/{target_uuid}/{download_type}",
    summary="Download specific scan data as TXT",
    description=(
        "Returns a `.txt` file (as raw bytes) of one category of scan results "
        "(e.g. `subdomains`, `urls`, etc.) for a given target UUID, "
        "with newline characters escaped (`\\n`). Delivered as an attachment."
    ),
    response_description="Plain-text file download",
response_class=FileResponse)
async def download_target_data(
    target_uuid: str = FPath(
        ...,
        description="UUID of the scan target",
        example="123e4567-e89b-12d3-a456-426614174000"
    ),
    download_type: DownloadType = FPath(
        ...,
        description="Type of data slice to download",
        example=DownloadType.subdomains
    )
):
    """
    - **target_uuid**: UUID of the target whose data to download.
    - **download_type**: one of the allowed categories (see `DownloadType` enum).
    """
    # Validate & group
    req = TargetDownloadRequest(target_uuid=target_uuid, download_type=download_type)

    try:
        file_response = await get_download(req.target_uuid, req.download_type.value)
        return file_response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to download {download_type} for {target_uuid}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")