# from fastapi import APIRouter
# import psutil, os

# router = APIRouter()

# # Route to return the system stats in HTML
# @router.get("/system-resources", tags=["system-resources"])
# async def func_get_system_res():

#     """
#     Endpoint to get current system resource status.
#     """

#     # CPU Usage
#     cpu_usage = psutil.cpu_percent(interval=1)
    
#     # Memory Usage
#     memory = psutil.virtual_memory()
#     memory_usage = memory.percent
    
#     # Storage Usage
#     disk = psutil.disk_usage('/')
#     storage_usage = disk.percent
    
#     # Network Usage (bytes sent and received)
#     network = psutil.net_io_counters()
#     network_sent = network.bytes_sent
#     network_received = network.bytes_recv
    
#     return {
#         "cpu_usage": cpu_usage,
#         "memory_usage": memory_usage,
#         "storage_usage": storage_usage,
#         "network_sent": network_sent, #bytes
#         "network_received": network_received #bytes
#     }

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import psutil
import asyncio

router = APIRouter()

# Function to gather system resources (without WebSocket-specific code)
async def func_get_system_res():

    """
    Endpoint to get current system resource status.
    """

    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    network = psutil.net_io_counters()

    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory.percent,
        "storage_usage": disk.percent,
        "network_sent": network.bytes_sent,  # bytes
        "network_received": network.bytes_recv,  # bytes
    }

# WebSocket endpoint to stream system resource status in real-time
@router.websocket("/ws/system-resources")
async def func_ws_get_system_res(websocket: WebSocket):

    """
    Endpoint to get current system resource status using websockets.
    """

    await websocket.accept()
    try:
        while True:
            data = func_get_system_res()  # Use the new function
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
