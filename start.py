#!/usr/bin/env python3
# External imports
import webbrowser, time, os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio, subprocess, signal, sys, uvicorn
from uvicorn import Config, Server

# Internal imports
from app.config.config import BACKEND_DIR, FRONTEND_DIR

# Initalization
app = FastAPI()
BACKEND_SESSION = "back"
FRONTEND_SESSION = "front"
server: Server = None  # global


# Logix
def cleanup():
    """Kill tmux sessions before exiting."""
    subprocess.run(
        ["tmux", "kill-session", "-t", BACKEND_SESSION],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        ["tmux", "kill-session", "-t", FRONTEND_SESSION],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )


# ---


# Register the cleanup function for program exit and signal handling
def handle_exit(*args):
    cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# ---


async def read_tmux_output(websocket: WebSocket):
    last_output = ""
    try:
        while True:
            result = subprocess.run(
                ["tmux", "capture-pane", "-p", "-t", BACKEND_SESSION, "-S-"],
                capture_output=True,
                text=True,
            )
            output = result.stdout
            if output != last_output:
                last_output = output
                await websocket.send_text(output)
            await asyncio.sleep(0.2)
    except Exception as e:
        print(f"Error in read_tmux_output: {e}")


# ---


@app.websocket("/terminal/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint to send/receive shell data."""
    await websocket.accept()
    task = asyncio.create_task(read_tmux_output(websocket))

    try:
        while True:
            data = await websocket.receive_text()
            subprocess.run(["tmux", "send-keys", "-t", BACKEND_SESSION, data])
    except WebSocketDisconnect:
        task.cancel()


# ---


@app.get("/stop")
async def stop_whole_framework():
    """Gracefully stop the FastAPI framework and cleanup."""
    global server
    cleanup()
    if server:
        server.should_exit = True
        return {"message": "Shutdown signal sent."}
    else:
        return {"error": "Server not running via Server() API."}


# ---

def open_browser_later():
    time.sleep(2)  # wait until server likely starts
    webbrowser.open("http://localhost:5173")

# ---

if __name__ == "__main__":

    # Kill existing tmux session if it exists, then create a new one
    cleanup()
    subprocess.run(["tmux", "new-session", "-d", "-s", BACKEND_SESSION])
    subprocess.run(["tmux", "new-session", "-d", "-s", FRONTEND_SESSION])
    subprocess.run(
        [
            "tmux",
            "send-keys",
            "-t",
            BACKEND_SESSION,
            f"cd {BACKEND_DIR}/backend/ && uvicorn main:app --host 0.0.0.0 --port 8000",
            "C-m",
        ]
    )
    subprocess.run(
        [
            "tmux",
            "send-keys",
            "-t",
            FRONTEND_SESSION,
            f"cd {FRONTEND_DIR} && npm run dev",
            "C-m",
        ]
    )


    # threading.Thread(target=open_browser_later, daemon=True).start()
    
    config = Config(app=app, host="0.0.0.0", port=8002, log_level="info")
    server = Server(config)

    try:
        server.run()
    finally:
        cleanup()
