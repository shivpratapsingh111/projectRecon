from fastapi import APIRouter
import subprocess, re

router = APIRouter()

@router.get("/tmux-sessions", tags=["tmux-sessions"])
async def func_get_tmux_sessions():
    """
    Endpoint to get currently running tmux sessions.
    """
    try:
        # Run 'tmux list-sessions' to fetch sessions
        result = subprocess.run(
            ['tmux', 'list-sessions'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            # Successfully retrieved tmux sessions
            sessions = result.stdout.strip().split('\n')
            # Extracting needed info from standard output
            output = await extract_key_and_datetime(sessions)
            return output
        else:
            # Error if no tmux sessions are found
            return {"error": result.stderr.strip()}
    except FileNotFoundError:
        # Handle the case where 'tmux' is not installed
        return {"error": "tmux is not installed or not found in the system path."}


# Filters standard tmux output, to get needed info
async def extract_key_and_datetime(data_list):
    
    """
    Before filtering:
        "aa: 1 windows (created Fri Dec 13 22:55:53 2024)",
        "bb: 1 windows (created Fri Dec 13 22:55:56 2024)",
        "cc: 1 windows (created Fri Dec 13 22:55:59 2024)",
        "dd: 1 windows (created Fri Dec 13 22:56:02 2024)"


    After filtering:
        "aa": "Fri Dec 13 22:55:53 2024",
        "bb": "Fri Dec 13 22:55:56 2024",
        "cc": "Fri Dec 13 22:55:59 2024",Filters
        "dd": "Fri Dec 13 22:56:02 2024"
    """

    result = {}
    for entry in data_list:
        # Use regex to extract key (before ":") and date-time part (after "created ")
        match = re.match(r"(\w+):.*created (.+\d{4})\)", entry)
        if match:
            key, datetime = match.groups()
            result[key] = datetime
    return result
