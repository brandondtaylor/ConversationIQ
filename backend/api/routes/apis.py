"""
API configuration management endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List

from src.api.config import APIConfigManager
from src.storage.schemas import APIConfig, APIConfigCreate

router = APIRouter()


@router.get("", response_model=List[APIConfig])
async def list_api_configs():
    """List all API configurations"""
    with APIConfigManager() as manager:
        return manager.list()


@router.post("", response_model=APIConfig, status_code=201)
async def create_api_config(config: APIConfigCreate):
    """Create a new API configuration"""
    with APIConfigManager() as manager:
        return manager.create(config)


@router.get("/{config_id}", response_model=APIConfig)
async def get_api_config(config_id: str):
    """Get API configuration by ID"""
    with APIConfigManager() as manager:
        config = manager.get(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="API configuration not found")
        return config


@router.put("/{config_id}", response_model=APIConfig)
async def update_api_config(config_id: str, **kwargs):
    """Update an API configuration"""
    with APIConfigManager() as manager:
        updated = manager.update(config_id, **kwargs)
        if not updated:
            raise HTTPException(status_code=404, detail="API configuration not found")
        return updated


@router.delete("/{config_id}", status_code=204)
async def delete_api_config(config_id: str):
    """Delete an API configuration"""
    with APIConfigManager() as manager:
        deleted = manager.delete(config_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="API configuration not found")


@router.post("/{config_id}/test")
async def test_api_config(config_id: str):
    """Test an API configuration connection"""
    with APIConfigManager() as manager:
        success, message = manager.test_config(config_id)
        return {"success": success, "message": message}
