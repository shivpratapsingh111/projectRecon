from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class StoredResultsResponse(BaseModel):
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
            "cdp.bluevoyant.com"
        ]
    )
    total_lines: int = Field(..., example=6)
    limit: int = Field(..., example=200)
    offset: int = Field(..., example=0)

# ---

class LogTypeResponse(str, Enum):
    stderr_log = "stderr_log"
    stdout_log = "stdout_log"
class GetLogFileContentResponse(BaseModel):
    content: str = Field(
        ...,
        description="Raw log file content with newline characters escaped",
        example="bluevoyant.com\n*.qa.bluevoyant.com\nqa.bluevoyant.com\n"
    )

# ---

class DownloadType(str, Enum):
    subdomains         = "subdomains"
    live_subdomains    = "live-subdomains"
    httpx_subdomains   = "httpx-subdomains"
    urls               = "urls"
    extensions         = "extensions"
    live_extensions    = "live-extensions"
    nuclei             = "nuclei"
    js_nuclei          = "js-nuclei"
    extracted_urls     = "extracted-urls"
    extracted_paths    = "extracted-paths"
    sensitive_data     = "sensitive-data"
    sensitive_keywords = "sensitive-keywords"

class ProgramDownloadRequest(BaseModel):
    program_name: str = Field(
        ..., description="Name of the program scan to download",
        example="bluevoyant"
    )

class TargetDownloadRequest(BaseModel):
    target_uuid: str = Field(
        ..., description="UUID of the scan target",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    download_type: DownloadType = Field(
        ..., description="Category of data to download",
        example=DownloadType.subdomains
    )
