# External Imports
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any, TypeVar, Generic

# Local Imports
from app.logger.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Intialization
logger = setup_logger(__name__, log_file_path="api_scan", enable_debug=LOG_LEVEL_DEBUG)
T = TypeVar(
    "T"
)  # This defines a type variable T — a placeholder for any Pydantic model (like User, Program, Product, etc.)


# Logic
class Command(BaseModel):
    command_name: Optional[str] = Field(
        default=None,
        example="subfinder",
        description="Name of the command/tool being run",
    )
    pid: Optional[int] = Field(
        default=None, example=1111, description="Process ID of the running command"
    )
    command: Optional[str] = Field(
        default=None,
        example="cat subdomains.txt | subfinder",
        description="The actual command that was executed",
    )
    status: Optional[Literal["pending", "running", "completed", "error", "killed"]] = (
        Field(
            default=None,
            example="completed",
            description="Execution status of the command. Allowed values: 'pending', 'running', 'completed', 'error', 'killed'",
        )
    )
    start_time: Optional[str] = Field(
        default=None,
        example="02:04:54, Thursday, 24-04-2025",
        description="When the command started executing",
    )
    stdout_log: Optional[str] = Field(
        default=None,
        example="/var/log/stdout_log.txt",
        description="Path or content of the standard output log",
    )
    stderr_log: Optional[str] = Field(
        default=None,
        example="/var/log/stderr_log.txt",
        description="Path or content of the standard error log",
    )
    return_code: Optional[int] = Field(
        default=None,
        example=0,
        description="Exit code of the command. Typically 0 = success",
    )
    completion_time: Optional[str] = Field(
        default=None,
        example="02:10:54, Thursday, 24-04-2025",
        description="When the command completed or was terminated",
    )


class Domain(BaseModel):
    domain_name: Optional[str] = Field(
        default=None,
        example="google.com",
        description="Domain or subdomain being scanned",
    )
    status: Optional[Literal["pending", "running", "completed", "error", "killed"]] = (
        Field(
            default=None,
            example="completed",
            description="Overall scan status for the domain. Allowed values: 'pending', 'running', 'completed', 'error', 'killed'",
        )
    )
    commands: Optional[Dict[str, Command]] = Field(
        default=None,
        description="Dictionary mapping command names (e.g. 'bbot', 'nuclei') to their execution details",
    )


class Program(BaseModel):
    program_name: Optional[str] = Field(
        default=None, example="Google", description="Name of the program or asset group"
    )
    status: Optional[Literal["pending", "running", "completed", "error", "killed"]] = (
        Field(
            default=None,
            example="completed",
            description="Overall status of the program. Allowed values: 'pending', 'running', 'completed', 'error', 'killed'",
        )
    )
    domains: Optional[Dict[str, Domain]] = Field(
        default=None,
        description="Dictionary mapping domain IDs to their associated domain scan data",
    )


class ProgramsData(BaseModel):
    programs: Optional[Dict[str, Program]] = Field(
        default=None,
        description="Mapping of unique program IDs to their corresponding program data, including domains and command execution info",
    )


# ---


class ExistingProgramNamesResponse(BaseModel):
    scan_name: Optional[List[str]] = Field(
        default=None,
        example=[
            "CUCHD",
            "CULKO",
            "Cyberboy-Scan",
            "cuchd",
            "cyberboy",
            "newcyberboy",
            "thecyberboy",
        ],
    )


# ---


class SubdomainEnumOptions(BaseModel):
    run: bool
    includeApi: bool
    toolSelection: bool
    selectedTools: List[str]
    isPassive: bool
    dnsBruteforce: bool
    httpx: bool
    screenshot: bool


class UrlEnumOptions(BaseModel):
    run: bool
    includeApi: bool
    toolSelection: bool
    selectedTools: List[str]
    isPassive: bool
    dnsBruteforce: bool


class NucleiOptions(BaseModel):
    run: bool
    allTemplates: bool
    specificTemplates: bool
    templateInput: str
    customTemplates: bool
    specificCommand: bool
    commandInput: str


class NmapOptions(BaseModel):
    run: bool
    allPorts: bool
    topPorts: bool
    webPorts: bool
    specificPorts: bool
    portInput: str
    specificCommand: bool
    commandInput: str


class JSOptions(BaseModel):
    run: bool
    doEverything: bool
    specificRegex: bool
    regexInput: str
    regexOnly: bool


class ScanOptionsRequest(BaseModel):
    subdomainEnum: Optional[SubdomainEnumOptions]
    urlEnum: Optional[UrlEnumOptions]
    nuclei: Optional[NucleiOptions]
    nmap: Optional[NmapOptions]
    js: Optional[JSOptions]


# ---


class ProcessScanResponse(BaseModel):
    message: str = Field(..., example="Scan started successfully")


# ---


class VerifyScanSetupResponse(BaseModel):
    message: str = Field(..., example="Environment setup verified.")


# ---


class StopCommandProcessResponse(BaseModel):
    status: Literal["killed", "not found"] = Field(..., example="killed")


# ---


class StopDomainProcessResponse(BaseModel):
    status: List = Field(..., example=[3344, 12312, 3213])


# ---


class StopProgramProcessResponse(BaseModel):
    status: List = Field(..., example=[3344, 12312, 3213])


# ---


class Generic__Response(BaseModel, Generic[T]):
    status: bool = Field(
        ..., example=True, description="Indicates if the request was successfull"
    )
    message: str = Field(
        ...,
        example="Scan started successfully",
        description="Brief message about the response",
    )
    data: Optional[T] = None
    debug: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional debug information, such as error details or internal context",
    )
