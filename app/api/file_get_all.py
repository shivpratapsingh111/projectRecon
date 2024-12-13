from fastapi import APIRouter
from app.api.file_get_tmux_sessions import func_get_tmux_sessions
from app.api.file_get_system_res import func_get_system_res

router = APIRouter()

@router.get("/all", tags=["all"])
async def func_get_all():
    """
    Endpoint to fetch all updates.
    """

    var_tmux_sessions = await func_get_tmux_sessions()  # Get tmux sessions

    var_system_resources = await func_get_system_res()

    return {"Sessions": var_tmux_sessions, "System Resources": var_system_resources}