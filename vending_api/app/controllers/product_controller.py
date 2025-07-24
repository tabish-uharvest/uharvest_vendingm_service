from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid

from app.config.database import get_async_db
from app.services.product_service import ProductService
from app.schemas.product import (
    IngredientResponse,
    AddonResponse,
    PresetResponse,
    PresetDetailResponse
)
from app.schemas.common import SuccessResponse

router = APIRouter()
product_service = ProductService()


@router.get("/ingredients", response_model=List[IngredientResponse])
async def get_ingredients(
    available_only: bool = Query(True, description="Show only available ingredients"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get list of all ingredients"""
    try:
        ingredients = await product_service.get_ingredients(
            session=db,
            available_only=available_only
        )
        return ingredients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingredients/{ingredient_id}", response_model=IngredientResponse)
async def get_ingredient(
    ingredient_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get ingredient details"""
    try:
        ingredient = await product_service.get_ingredient_by_id(db, ingredient_id)
        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        return ingredient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/addons", response_model=List[AddonResponse])
async def get_addons(
    available_only: bool = Query(True, description="Show only available addons"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get list of all addons"""
    try:
        addons = await product_service.get_addons(
            session=db,
            available_only=available_only
        )
        return addons
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/addons/{addon_id}", response_model=AddonResponse)
async def get_addon(
    addon_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get addon details"""
    try:
        addon = await product_service.get_addon_by_id(db, addon_id)
        if not addon:
            raise HTTPException(status_code=404, detail="Addon not found")
        return addon
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets", response_model=List[PresetResponse])
async def get_presets(
    category: Optional[str] = Query(None, description="Filter by category (smoothie/salad)"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get list of all preset recipes"""
    try:
        presets = await product_service.get_presets(
            session=db,
            category=category
        )
        return presets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/{preset_id}", response_model=PresetDetailResponse)
async def get_preset(
    preset_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get preset details with ingredient recipe"""
    try:
        preset = await product_service.get_preset_details(db, preset_id)
        if not preset:
            raise HTTPException(status_code=404, detail="Preset not found")
        return preset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
