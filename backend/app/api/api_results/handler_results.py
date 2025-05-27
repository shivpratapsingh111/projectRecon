# External Imports
import asyncio, json
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Query,
    Path as FPath,
    status,
)
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import traceback

# Local Imports
from app.api.api_results.read_results import websocket_read_results
from app.api.api_results.read_results import http_read_results
from app.api.api_results.read_results import get_log_file_content
from app.api.api_results.get_download_ready import get_download
from app.api.api_results.get_download_ready import get_program_scan_results
from app.logger.logger import setup_logger
from .data_model_results import (
    Generic__Response,
    StoredResults__Request,
    StoredResults__Response,
    GetLogFileContent__Response,
    LogType__Response,
    DownloadType,
    TargetDownload__Request,
    DownloadProgramScanResults__Response,
    DownloadLogFile__Response,
)
from app.config.config import LOG_LEVEL_DEBUG

# Initialization
logger = setup_logger(
    __name__, log_file_path="api_results", enable_debug=LOG_LEVEL_DEBUG
)
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
            result = await websocket_read_results(target_uuid, "subdomains")

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
            result = await websocket_read_results(target_uuid, "urls")

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
    response_model=Generic__Response[StoredResults__Response],
    summary="Fetch stored scan results",
    description="Retrieve a paginated portion of stored scan results for a given UUID and file.",
)
async def api_stored_results(
    target_uuid: str,
    file: str = Query(
        ...,
        description="The name of the file to fetch results from",
        example="subdomains.txt",
    ),
    limit: Optional[int] = Query(
        20, gt=0, description="Max number of lines to return", example=20
    ),
    offset: int = Query(
        0, ge=0, description="Line offset to start returning from", example=0
    ),
):
    """
    Get stored scan results for a specific target UUID and file.

    - **target_uuid**: Unique ID for the scan target.
    - **file**: Name of the file containing the results.
    - **limit**: Maximum number of result lines to return (default 20).
    - **offset**: Start line offset in the results (default 0).
    """
    try:
        try:
            request_data = StoredResults__Request(
                target_uuid=target_uuid, file=file, limit=limit, offset=offset
            )
        except Exception as e:
            full_trace = traceback.format_exc()
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "status": False,
                    "message": "Error in validating request data",
                    "debug": {"error": str(e), "traceback": full_trace},
                },
            )
        result = await http_read_results(
            request_data.target_uuid,
            request_data.file,
            request_data.limit,
            request_data.offset,
        )
        if result["status"]:
            return Generic__Response[StoredResults__Response](**result)
        else:
            return JSONResponse(
                status_code=result.get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
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
    "/get-log",
    response_model=Generic__Response[GetLogFileContent__Response],
    summary="Fetch raw process log",
    description=(
        "Retrieve the full contents of a process's log file. "
        "The response is a JSON object containing the raw log lines, "
        "with newlines escaped (`\\n`) and double quotes escaped."
    ),
    response_description="A JSON object with a single `content` field holding the escaped log text",
)
async def api_get_log_file_content(
    pid: int = Query(
        ..., description="The process ID whose log you want to retrieve", example=8190
    ),
    log_type: LogType__Response = Query(
        ...,
        description="Type of log to fetch (`stderr_log` or `stdout_log`)",
        example=LogType__Response.stdout_log,
    ),
):
    """
    - **pid**: Integer process ID.
    - **log_type**: Either `stderr_log` or `stdout_log`.
    """

    try:
        result = await get_log_file_content(pid, log_type.value)
        logger.debug(f"Type of result: {type(result)}, Value: {result}")

        if result["status"]:
            return Generic__Response[GetLogFileContent__Response](**result)
        else:
            return JSONResponse(
                status_code=result.get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
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
    "/download/{program_name}",
    summary="Download full program scan as ZIP",
    description=(
        "Returns a `.zip` archive containing all stored scan results for the given program name. "
        "Delivered as a downloadable attachment."
    ),
    response_description="ZIP file download",
    response_model=Generic__Response[DownloadProgramScanResults__Response],
)
async def download_program_scan(
    program_name: str = FPath(
        ...,
        description="Name of the program whose scan yyou wish to download",
        example="google-scan",
    )
):
    """
    - **program_name**: the name of the program whose scan you wish to download.
    """

    try:
        result = await get_program_scan_results(program_name)
        if result["status"]:
            return Generic__Response[DownloadProgramScanResults__Response](**result)
        else:
            return JSONResponse(
                status_code=result.get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
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
    "/download/{target_uuid}/{download_type}",
    summary="Download specific scan data as TXT",
    description=(
        "Returns a `.txt` file (as raw bytes) of one category of scan results "
        "(e.g. `subdomains`, `urls`, etc.) for a given target UUID, "
        "with newline characters escaped (`\\n`). Delivered as an attachment."
    ),
    response_description="Plain-text file download",
    response_model=Generic__Response[DownloadLogFile__Response],
)
async def download_target_data(
    target_uuid: str = FPath(
        ...,
        description="UUID of the scan target",
        example="123e4567-e89b-12d3-a456-426614174000",
    ),
    download_type: DownloadType = FPath(
        ...,
        description="Type of data slice to download",
        example=DownloadType.subdomains,
    ),
):
    """
    - **target_uuid**: UUID of the target whose data to download.
    - **download_type**: one of the allowed categories (see `DownloadType` enum).
    """
    try:
        # Validate & group
        req = TargetDownload__Request(target_uuid=target_uuid, download_type=download_type)

        result = await get_download(req.target_uuid, req.download_type.value)
        if result["status"]:
            return Generic__Response[DownloadLogFile__Response](**result)
        else:
            return JSONResponse(
                status_code=result.get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
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