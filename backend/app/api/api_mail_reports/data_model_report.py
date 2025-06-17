# External imports
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, TypeVar, Generic

# Internal imports
from app.interface.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Intialization
logger = setup_logger(__name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG)
T = TypeVar(
    "T"
)  # This defines a type variable T — a placeholder for any Pydantic model (like User, Program, Product, etc.)


# Logic
class Report__Request(BaseModel):
    program_name: Optional[str] = Field(
        default=None, example="Example", description="Name of the program"
    )
    program_url: Optional[str] = Field(
        default=None,
        example="https://example.com/bugbounty",
        description="URL of the program",
    )
    target_package: Optional[str] = Field(
        default=None,
        example="com.example.com",
        description="package name of the target apk",
    )
    target_apk: Optional[str] = Field(
        default=None,
        example="example android app",
        description="Name of the target apk",
    )
    technology: Optional[List[str]] = Field(
        default=None,
        example=["AWS", "Cloudflare"],
        description="Technology getting used in the application (web/android)",
    )
    download_url: Optional[str] = Field(
        default=None,
        example="https://apkmirror.com/exmaple.apk",
        description="Download url of the target apk",
    )
    email: Optional[str] = Field(
        default=None, example="security@example.com", description="Email of the program"
    )
    attachment_url: Optional[str] = Field(
        default=None,
        example="https://drive.google.com/example_poc.mp4",
        description="Attachment url of the poc",
    )
    report_form: Optional[str] = Field(
        default=None,
        example="https://example.com/bugbounty/report",
        description="Report form url of the program",
    )
    poc_path: Optional[str] = Field(
        default=None,
        example="~/pocs/example_xss_poc.mp4",
        description="Path of poc stored on local pc",
    )
    acquisitions: Optional[List[str]] = Field(
        default=None,
        example=["Sub brand 1", "sub brand 2"],
        description="Companies acquired by the target program",
    )
    strandhog: Optional[bool] = Field(
        default=None,
        example="True",
        description="True if reporting this vulnerability, otherwise False",
    )
    oauth: Optional[bool] = Field(
        default=None,
        example="True",
        description="True if reporting this vulnerability, otherwise False",
    )


# ---


class ReportList__Request(BaseModel):
    formData: Optional[List[Report__Request]]


# ---


class Report__Response(BaseModel):
    message: Optional[List[str]]


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
