
from fastapi import FastAPI, WebSocket
from fastapi import APIRouter
import os
import pty
import subprocess
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio

router = APIRouter()

SESSION_NAME = "sess"

# Ensure tmux session exists
# subprocess.run(["tmux", "new-session", "-d", "-s", SESSION_NAME])

async def read_tmux_output(websocket: WebSocket):
    """ Continuously read tmux output and send to the WebSocket client. """
    last_output = ""
    while True:
        result = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", SESSION_NAME],
            capture_output=True, text=True
        )
        output = result.stdout
        if output != last_output:
            last_output = output
            await websocket.send_text(output)
        await asyncio.sleep(0.2)

@router.websocket("/terminal/ws")
async def websocket_endpoint(websocket: WebSocket):
    """ WebSocket endpoint to send/receive shell data. """
    await websocket.accept()
    try:
        task = asyncio.create_task(read_tmux_output(websocket))
        while True:
            data = await websocket.receive_text()
            subprocess.run(["tmux", "send-keys", "-t", SESSION_NAME, data])
    except WebSocketDisconnect:
        task.cancel()
