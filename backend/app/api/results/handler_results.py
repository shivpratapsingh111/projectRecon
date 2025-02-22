from backend.app.api.results.read_results import websocket_read_results
from backend.app.api.results.read_results import http_read_results
from backend.app.api.results.read_results import get_log_file_content
from app.api.results.get_download_ready import get_download
from app.api.results.get_download_ready import get_group_scan

from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter
import asyncio
import json
from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from pathlib import Path

from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='results', enable_debug = True)

router = APIRouter()

@router.get("")
async def results():
    return {"message": "Yeah! Running"}

@router.websocket("/subdomains/{domain_id}")
async def api_running_results_subdomains(domain_id, websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            result = await websocket_read_results(domain_id, 'subdomains') 
            
            await websocket.send_text(json.dumps(result)) 
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        logger.warning("Client disconnected")
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()


@router.websocket("/urls/{domain_id}")
async def api_running_results_urls(domain_id, websocket: WebSocket):
    try:
        await websocket.accept() 
        while True:
            result = await websocket_read_results(domain_id, 'urls')
            
            await websocket.send_text(json.dumps(result))
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        logger.warning("Client disconnected")
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()



@router.get("/get/{domain_id}")
async def api_stored_results(domain_id: str, file: str = Query(..., description="The file name"), limit: Optional[int] = Query(20, gt=0), offset: int = Query(0, ge=0)):
    try:
        result = await http_read_results(domain_id, file, limit, offset)
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/get-log")
async def api_get_log_file_content(pid: int = Query(..., description="Process ID"), log_type: str = Query(..., description="Log type")):
    try:
        result = await get_log_file_content(pid, log_type)
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



# ============================[Download Routes]

@router.get("/download/{group_name}")
async def download_group_scan(group_name):
    try:
        result = await get_group_scan(group_name)
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/download/{domain_id}/subdomains")
async def download(domain_id):
    try:
        result = await get_download(domain_id, 'subdomains')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/download/{domain_id}/live-subdomains")
async def download(domain_id):
    try:
        result = await get_download(domain_id, 'live_subdomains')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

        
@router.get("/download/{domain_id}/httpx-subdomains")
async def download(domain_id):
    try:
        result = await get_download(domain_id, 'httpx_subdomains')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

        
@router.get("/download/{domain_id}/urls")
async def download(domain_id):
    try:
        result = await get_download(domain_id, 'urls')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/download/{domain_id}/extensions")
async def download(domain_id):
    try:
        result = await get_download(domain_id, 'extensions')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/download/{domain_id}/live-extensions")
async def download(domain_id):
    try:
        result = await get_download(domain_id, 'live_extensions')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/download/{domain_id}/nuclei")
async def download(domain_id):
    try:
        result = await get_download(domain_id, 'nuclei')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
