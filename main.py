from fastapi import FastAPI
from app.api import file_get_all
# from app.api import file_get_tmux_sessions


# Initialize FastAPI app
app = FastAPI(title="Recon Framework")

app.include_router(file_get_all.router, prefix="/api", tags=["all"])
# app.include_router(file_get_tmux_sessions.router, prefix="/api", tags=["sessions"])

@app.get("/", tags=["root"])
async def root():
    """Root endpoint to check service status."""

    return {"message": "Yeah! Running"}


