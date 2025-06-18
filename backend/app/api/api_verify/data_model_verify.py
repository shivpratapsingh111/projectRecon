# External imports
from typing import Generic, Optional
from pydantic import BaseModel, Field
from typing import Optional, TypeVar, Dict, Any, List, Union, Literal

# Internal imports
from app.interface.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Intialization
logger = setup_logger(__name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG)
T = TypeVar(
    "T"
)  # This defines a type variable T — a placeholder for any Pydantic model (like User, Program, Product, etc.)


# Logic
class OSInfo(BaseModel):
    distro: str = Field(
        ...,
        example="fedora",
        description="The specific Linux distribution (e.g. 'ubuntu', 'fedora').",
    )
    family: str = Field(
        ...,
        example="fedora",
        description="The OS family (e.g. 'debian', 'rhel', etc.).",
    )


class UpdatesInfo(BaseModel):
    repo: Optional[List[Literal["projectrecon", "pentest-dashboard"]]] = Field(
        None,
        example=["projectrecon"],
        description="List of repository names with available updates. Available: 'projectrecon', 'pentest-dashboard'.",
    )


class EnvironmentReport__Response(BaseModel):
    os: OSInfo = Field(..., description="Information about the operating system.")
    missing_system_packages: Optional[List[str]] = Field(
        None, example=["curl", "git"], description="System packages that are missing on the host machine."
    )
    unset_env_vars: Optional[List[str]] = Field(
        None,
        example=["GITHUB_TOKEN", "GITLAB_TOKEN"],
        description="Environment variables required but not currently set.",
    )
    python_environment: bool = Field(
        ...,
        example=True,
        description="Whether the required Python virtual environment exists.",
    )
    updates: Union[UpdatesInfo, bool] = Field(
        ...,
        description="Update information, or `False` if updates are disabled or unavailable.",
    )
    missing_tools: Optional[List[str]] = Field(
        None,
        example=["subfinder", "amass", "nuclei"],
        description="CLI tools that were expected but not found in the system.",
    )
    postgresql: Union[List[str], bool] = Field(
        ...,
        example=["cannot connect to postgres as user", "something went wrong"],
        description="`True` if PostgreSQL is functional; otherwise, a list of error messages.",
    )


# ---


class Generic__Response(BaseModel, Generic[T]):
    status_code: Optional[int] = Field(default=None, example=200)
    status: bool = Field(
        ..., example=True, description="Indicates if the request was successfull"
    )
    message: str = Field(
        ...,
        example="Report fetched",
        description="Brief message about the response",
    )
    data: Optional[T] = None
    debug: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional debug information, such as error details or internal context",
    )
