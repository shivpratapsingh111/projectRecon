from app.api.results.get_results import get_results
from app.api.results.get_complete_results import get_complete_results
from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter
import asyncio
import json

from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='results', enable_debug = True)

router = APIRouter()

@router.get("")
async def results():
    return {"message": "Yeah! Running"}

@router.websocket("/subdomains/{domain_id}")
async def get_running_results_subdomains(domain_id, websocket: WebSocket):
    try:
        await websocket.accept()  # Accept the WebSocket connection
        while True:
            result = await get_results(domain_id, 'subdomains')  # Get your data
            # Convert result to JSON string before sending
            await websocket.send_text(json.dumps(result))  # Send the result over the WebSocket
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.warning("Client disconnected")
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()


@router.websocket("/urls/{domain_id}")
async def api_get_running_results_urls(domain_id, websocket: WebSocket):
    try:
        await websocket.accept()  # Accept the WebSocket connection
        while True:
            result = await get_results(domain_id, 'urls')  # Get your data
            # Convert result to JSON string before sending
            await websocket.send_text(json.dumps(result))  # Send the result over the WebSocket
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.warning("Client disconnected")
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()

@router.get("/completed/urls/{domain_id}")
async def api_get_complete_results_urls(domain_id):
    try:
        result = get_complete_results(domain_id, 'urls')
        return result  
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

@router.get("/completed/subdomains/{domain_id}")
async def api_get_complete_results_subdomains(domain_id):
    try:
        result = get_complete_results(domain_id, 'subdomains')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/completed/nuclei/{domain_id}")
async def api_get_complete_results_subdomains(domain_id):
    try:
        result = get_complete_results(domain_id, 'nuclei')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
