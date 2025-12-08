import sys
import logging
import requests
from typing import List, Dict, Any

from fastapi import APIRouter, Request, HTTPException

from core.config import APIs, ADBLOCK_GROUP_ID, NON_ADBLOCK_GROUP_ID
from core.pihole_auth import pihole_auth
from core.schemas import ClientSchema, GroupSchema, EditClientRequest

logger = logging.getLogger("app")
router = APIRouter()

def get_endpoint_from_request(request: Request) -> str:
    """Determines which Pi-hole endpoint to use based on query parameters or default."""
    if not pihole_auth.endpoints:
        raise HTTPException(status_code=500, detail="No Pi-hole endpoints configured")
    
    ep = request.query_params.get("ep")
    if ep and ep in pihole_auth.endpoints:
        return ep
    
    return pihole_auth.endpoints[0]

@router.get("/clients", response_model=List[ClientSchema])
async def get_clients(request: Request):
    """Fetches the list of clients from a Pi-hole API instance."""
    try:
        endpoint = get_endpoint_from_request(request)
        session = pihole_auth.sessions.get(endpoint)

        if not session:
            raise HTTPException(status_code=500, detail="Pi-hole session not active.")

        url = f"{endpoint}{APIs.CLIENTS.value}"
        headers = {
            "X-FTL-SID": session.sid,
            "X-FTL-CSRF": session.csrf
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("clients", [])
        else:
            logger.error(f"GetClients API error from {endpoint}: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching clients from Pi-hole.")
            
    except Exception as e:
        logger.error(f"GetClients exception: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching clients.")

@router.get("/groups", response_model=List[GroupSchema])
async def get_groups(request: Request):
    """Fetches the list of groups from a Pi-hole API instance."""
    try:
        endpoint = get_endpoint_from_request(request)
        session = pihole_auth.sessions.get(endpoint)
        
        if not session:
            raise HTTPException(status_code=500, detail="Pi-hole session not active.")

        url = f"{endpoint}{APIs.GROUPS.value}"
        headers = {
            "X-FTL-SID": session.sid,
            "X-FTL-CSRF": session.csrf
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("groups", [])
        else:
            logger.error(f"GetGroups API error from {endpoint}: {response.status_code}")
            raise HTTPException(status_code=response.status_code, detail="Error fetching groups from Pi-hole.")

    except Exception as e:
        logger.error(f"GetGroups exception: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching groups.")

@router.get("/group-ids")
async def get_group_ids():
    return {
        "adblock_group_id": ADBLOCK_GROUP_ID,
        "non_adblock_group_id": NON_ADBLOCK_GROUP_ID,
    }

@router.post("/editclient", response_model=Dict[str, Any])
async def edit_client(client_data: EditClientRequest):
    """Edits a client's comment and group assignments across all Pi-hole instances."""
    
    json_data = {
        "comment": client_data.comment,
        "groups": [client_data.group] if client_data.group is not None else []
    }

    results = {}

    for ep in pihole_auth.endpoints:
        session = pihole_auth.sessions.get(ep)
        
        if not session:
            results[ep] = "Session not available"
            continue

        url = f"{ep}{APIs.CLIENTS.value}{client_data.client}"

        headers = {
            "X-FTL-SID": session.sid,
            "X-FTL-CSRF": session.csrf
        }

        try:
            r = requests.put(url, headers=headers, json=json_data) 
            results[ep] = r.status_code

        except Exception as e:
            results[ep] = str(e)

    return results
