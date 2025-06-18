# External imports
from typing import Generic, Optional
from pydantic import BaseModel, Field
from typing import Optional, TypeVar, Dict, Any, List

# Internal imports
from app.interface.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Intialization
logger = setup_logger(
    __name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG
)
T = TypeVar(
    "T"
)  # This defines a type variable T — a placeholder for any Pydantic model (like User, Program, Product, etc.)


# Logic
class GetScanStatus__Response(BaseModel):
    scan_state: bool = Field(
        ...,
        example=True,
        description="Indicates if the endpoint monitoring scan is running (true) or stopped (false)",
    )


# ---


class ProgramEntry(BaseModel):
    id: Optional[str] = Field(
        default=None,
        example="d823n-m2439-k9042-js93nma-3nsi3",
        description="Id of the program",
    )
    program_name: Optional[str] = Field(
        default=None, example="Google", description="Name of the program"
    )
    program_url: Optional[str] = Field(
        default=None,
        example="https://google.com/bug-bounty",
        description="Url of program brief page",
    )
    acquisitions: Optional[List] = Field(
        default=None,
        example="['Wiz', 'Cameyo', 'Equalum']",
        description="Aquisitions of the program",
    )
    email: Optional[str] = Field(
        default=None, example="security@google.com", description="Email of the program"
    )
    report_form: Optional[str] = Field(
        default=None,
        example="https://form.google.com/report-bugs",
        description="Bug report form page of the program",
    )
    created_at: Optional[str] = Field(
        default=None,
        example="2025-05-28 23:42:56.214118",
        description="Date and time at which program was created Format: year-month-date hours-mintues-seconds.milliseconds",
    )


class GetExistingPrograms__Response(BaseModel):
    content: Optional[List[ProgramEntry]]


# ---


class GetExistingScanNames__Response(BaseModel):
    scan_names: Optional[List]


# ---


class EndpointChangeEntry(BaseModel):
    id: Optional[str] = Field(
        None,
        example="d823n-m2439-k9042-js93nma-3nsi3",
        description="Id of the endpoint",
    )
    program_uuid: Optional[str] = Field(
        None,
        example="l97rtg-563gf-h534ed-7jhh-2eedsf",
        description="Id of the program to which the endpoint belongs",
    )
    target_id: Optional[int] = Field(
        None,
        example="h54sd-m2439-s32ca-34rrfwe-ds23f",
        description="Id of the target to which the endpoint belongs",
    )
    scan_name: Optional[str] = Field(
        None,
        example="kt3fw-342fsdf-34gfsdf-345efsd-3ns34g34i3",
        description="Scan name to which the endpoint belongs",
    )
    url: Optional[str] = Field(
        None, example="https://google.com/file.txt", description="Endpoint url"
    )
    change_detected_at: Optional[str] = Field(
        None,
        example="2025-05-28 23:42:56.214118",
        description="Timestamp when a change was detected",
    )
    old_status_code: Optional[int] = Field(
        None, example="403", description="Old status code"
    )
    new_status_code: Optional[int] = Field(
        None, example="200", description="New status code"
    )
    old_response_size: Optional[int] = Field(
        None, example="5003", description="Old response size in KB"
    )
    new_response_size: Optional[int] = Field(
        None, example="9002", description="New response size in KB"
    )
    old_body_file_path: Optional[str] = Field(
        None,
        example="/home/user/xxx/xxx/xxx/responses/www.cloudflare.com_cdn-cgi_challenge-platform_scripts_jsd_main.js.bin_new",
        description="Old file path in which response body is saved",
    )
    new_body_file_path: Optional[str] = Field(
        None,
        example="/home/user/xxx/xxx/xxx/responses/www.cloudflare.com_cdn-cgi_challenge-platform_scripts_jsd_main.js.bin_new",
        description="New file path in which response body is saved",
    )


class GetReviewEndpointsData__Response(BaseModel):
    content: Optional[List[EndpointChangeEntry]]


# ---


class EndpointByStatusEntry(BaseModel):
    id: Optional[str] = Field(
        None,
        example="d823n-m2439-k9042-js93nma-3nsi3",
        description="Id of the endpoint",
    )
    program_uuid: Optional[str] = Field(
        None,
        example="l97rtg-563gf-h534ed-7jhh-2eedsf",
        description="Id of the program to which the endpoint belongs",
    )
    program_name: Optional[str] = Field(
        None, example="Google", description="Program name to which the endpoint belongs"
    )
    scan_name: Optional[str] = Field(
        None,
        example="kt3fw-342fsdf-34gfsdf-345efsd-3ns34g34i3",
        description="Scan name to which the endpoint belongs",
    )
    scan_interval: Optional[int] = Field(
        None, example="3600", description="Interval between scans in seconds"
    )
    status: Optional[str] = Field(
        None, example=True, description="Should it be scanned (true) or not (false)"
    )
    url: Optional[str] = Field(
        None, example="https://google.com/file.txt", description="Endpoint url"
    )
    new_status_code: Optional[int] = Field(
        None, example="200", description="New status code"
    )
    new_response_size: Optional[int] = Field(
        None, example="9002", description="New response size in KB"
    )
    new_body_file_path: Optional[str] = Field(
        None,
        example="/home/user/xxx/xxx/xxx/responses/www.cloudflare.com_cdn-cgi_challenge-platform_scripts_jsd_main.js.bin_new",
        description="New file path in which response body is saved",
    )
    last_check: Optional[str] = Field(
        None, example="2025-05-28 23:42:56.214118", description="Timestamp of last scan"
    )


class GetEndpointsByStatus__Response(BaseModel):
    content: Optional[List[EndpointByStatusEntry]]


# ---


class GetResponseBodyChanges__Response(BaseModel):
    old_response: Optional[str]
    new_response: Optional[str]


# ---


class Generic__Response(BaseModel, Generic[T]):
    status_code: Optional[int] = Field(default=None, example=200)
    status: bool = Field(
        ..., example=True, description="Indicates if the request was successfull"
    )
    message: str = Field(
        ...,
        example="Program inserted successfully",
        description="Brief message about the response",
    )
    data: Optional[T] = None
    debug: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional debug information, such as error details or internal context",
    )
