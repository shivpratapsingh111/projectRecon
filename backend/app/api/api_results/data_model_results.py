# External imports
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, TypeVar, Generic
from enum import Enum

# Internal imports
from app.interface.logger_manager import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Intialization
logger = setup_logger(
    __name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG
)
T = TypeVar(
    "T"
)  # This defines a type variable T — a placeholder for any Pydantic model (like User, Program, Product, etc.)


# Logic
class FileType(str, Enum):
    urls = "urls"
    extensions = "extensions"
    live_extensions = "live_extensions"
    subdomains = "subdomains"
    live_subdomains = "live_subdomains"
    httpx_subdomains = "httpx_subdomains"
    nuclei = "nuclei"
    extracted_urls = "extracted_urls"
    extracted_paths = "extracted_paths"
    sensitive_data = "sensitive_data"
    sensitive_keywords = "sensitive_keywords"
    js_nuclei = "js_nuclei"


class StoredResults__Request(BaseModel):
    target_uuid: str = Field(
        ...,
        description="Unique ID for the scan target",
        example="0d7228af-154e-4423-84d6-4761efc6e59b",
    )
    file: FileType = Field(
        ...,
        description="Allowed file types to fetch results from",
        example="subdomains",
    )
    limit: Optional[int] = Field(
        20, gt=0, description="Max number of lines to return", example=20
    )
    offset: int = Field(
        0, ge=0, description="Line offset to start returning from", example=0
    )


# ---


class StoredResults__Response(BaseModel):
    domain: str = Field(..., example="bluevoyant.com")
    program: str = Field(..., example="bluevoyant")
    content: List[str] = Field(
        ...,
        example=[
            "brand.bluevoyant.com",
            "bv-gpt-35-turbo.bluevoyant.com",
            "bv-gpt-4.bluevoyant.com",
            "bvtoday.bluevoyant.com",
            "calendar.bluevoyant.com",
            "cdp.bluevoyant.com",
        ],
    )
    total_lines: int = Field(..., example=6)
    limit: int = Field(..., example=200)
    offset: int = Field(..., example=0)


# ---


class LogType__Response(str, Enum):
    stderr_log = "stderr_log"
    stdout_log = "stdout_log"


class GetLogFileContent__Response(BaseModel):
    content: str = Field(
        ...,
        description="Raw log file content with newline characters escaped",
        example="bluevoyant.com\n*.qa.bluevoyant.com\nqa.bluevoyant.com\n",
    )


# ---


class DownloadType(str, Enum):
    subdomains = "subdomains"
    live_subdomains = "live-subdomains"
    httpx_subdomains = "httpx-subdomains"
    urls = "urls"
    extensions = "extensions"
    live_extensions = "live-extensions"
    nuclei = "nuclei"
    js_nuclei = "js-nuclei"
    extracted_urls = "extracted-urls"
    extracted_paths = "extracted-paths"
    sensitive_data = "sensitive-data"
    sensitive_keywords = "sensitive-keywords"


# ---


class TargetDownload__Request(BaseModel):
    target_uuid: str = Field(
        ...,
        description="UUID of the scan target",
        example="123e4567-e89b-12d3-a456-426614174000",
    )
    download_type: DownloadType = Field(
        ..., description="Category of data to download", example=DownloadType.subdomains
    )


# ---


class DownloadProgramScanResults__Response(BaseModel):
    archive_path: str


# ---


class DownloadLogFile__Response(BaseModel):
    log_file_path: str


# ---


class Generic__Response(BaseModel, Generic[T]):
    status_code: Optional[int] = Field(default=None, example=200)
    status: bool = Field(
        ..., example=True, description="Indicates if the request was successfull"
    )
    message: str = Field(
        ...,
        example="Data successfully fetched",
        description="Brief message about the response",
    )
    data: Optional[T] = None
    debug: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional debug information, such as error details or internal context",
    )
