from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import subprocess

app = FastAPI()
SESSION_NAME = "sess"

# Kill existing tmux session if it exists, then create a new one
subprocess.run(["tmux", "kill-session", "-t", SESSION_NAME], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
subprocess.run(["tmux", "new-session", "-d", "-s", SESSION_NAME])
subprocess.run(["tmux", "send-keys", "-t", SESSION_NAME, "cd backend/ && uvicorn main:app --host 0.0.0.0 --port 8000", "C-m"])

async def read_tmux_output(websocket: WebSocket):
    """ Continuously read tmux output and send to the WebSocket client. """
    last_output = ""
    while True:
        result = subprocess.run(["tmux", "capture-pane", "-p", "-t", SESSION_NAME, "-S-"], capture_output=True, text=True)
        output = result.stdout
        if output != last_output:
            last_output = output
            await websocket.send_text(output)
        await asyncio.sleep(0.2)

@app.websocket("/terminal/ws")
async def websocket_endpoint(websocket: WebSocket):
    """ WebSocket endpoint to send/receive shell data. """
    await websocket.accept()
    task = asyncio.create_task(read_tmux_output(websocket))

    try:
        while True:
            data = await websocket.receive_text()
            subprocess.run(["tmux", "send-keys", "-t", SESSION_NAME, data])
    except WebSocketDisconnect:
        task.cancel()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
