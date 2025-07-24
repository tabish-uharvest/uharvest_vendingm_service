from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import uuid

from app.config.database import get_async_db
from app.services.product_service import ProductService
from app.schemas.product import (
    IngredientCreate,
    IngredientUpdate,
    IngredientResponse,
    AddonCreate,
    AddonUpdate,
    AddonResponse,
    PresetCreate,
    PresetUpdate,
    PresetResponse,
    PresetDetailResponse
)
from app.schemas.common import SuccessResponse, PaginatedResponse

router = APIRouter()
product_service = ProductService()


# Ingredients Management
@router.get("/ingredients", response_model=PaginatedResponse[IngredientResponse])
async def list_ingredients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_async_db)
):
    """List all ingredients with details"""
    try:
        result = await product_service.list_ingredients_admin(
            session=db,
            skip=skip,
            limit=limit,
            search=search,
            category=category
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingredients", response_model=IngredientResponse, status_code=201)
async def create_ingredient(
    ingredient_data: IngredientCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create new ingredient"""
    try:
        ingredient = await product_service.create_ingredient(
            session=db,
            ingredient_data=ingredient_data
        )
        await db.commit()  # Commit the transaction
        return ingredient
    except Exception as e:
        await db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
async def update_ingredient(
    ingredient_id: uuid.UUID,
    ingredient_data: IngredientUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update ingredient details"""
    try:
        ingredient = await product_service.update_ingredient(
            session=db,
            ingredient_id=ingredient_id,
            ingredient_data=ingredient_data
        )
        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        await db.commit()  # Commit the transaction
        return ingredient
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/ingredients/{ingredient_id}")
async def delete_ingredient(
    ingredient_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete ingredient"""
    try:
        success = await product_service.delete_ingredient(
            session=db,
            ingredient_id=ingredient_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        await db.commit()  # Commit the transaction
        return SuccessResponse(message="Ingredient deleted successfully")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Addons Management
@router.get("/addons", response_model=PaginatedResponse[AddonResponse])
async def list_addons(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name"),
    db: AsyncSession = Depends(get_async_db)
):
    """List all addons"""
    try:
        result = await product_service.list_addons_admin(
            session=db,
            skip=skip,
            limit=limit,
            search=search
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/addons", response_model=AddonResponse, status_code=201)
async def create_addon(
    addon_data: AddonCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create new addon"""
    try:
        addon = await product_service.create_addon(
            session=db,
            addon_data=addon_data
        )
        await db.commit()  # Commit the transaction
        return addon
    except Exception as e:
        await db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/addons/{addon_id}", response_model=AddonResponse)
async def update_addon(
    addon_id: uuid.UUID,
    addon_data: AddonUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update addon details"""
    try:
        addon = await product_service.update_addon(
            session=db,
            addon_id=addon_id,
            addon_data=addon_data
        )
        if not addon:
            raise HTTPException(status_code=404, detail="Addon not found")
        await db.commit()  # Commit the transaction
        return addon
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/addons/{addon_id}")
async def delete_addon(
    addon_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete addon"""
    try:
        success = await product_service.delete_addon(
            session=db,
            addon_id=addon_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Addon not found")
        await db.commit()  # Commit the transaction
        return SuccessResponse(message="Addon deleted successfully")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Presets Management
@router.get("/presets", response_model=PaginatedResponse[PresetResponse])
async def list_presets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_async_db)
):
    """List all presets with recipes"""
    try:
        result = await product_service.list_presets_admin(
            session=db,
            skip=skip,
            limit=limit,
            search=search,
            category=category
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presets", response_model=PresetDetailResponse, status_code=201)
async def create_preset(
    preset_data: PresetCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create new preset with ingredient recipe"""
    try:
        preset = await product_service.create_preset(
            session=db,
            preset_data=preset_data
        )
        await db.commit()  # Commit the transaction
        return preset
    except Exception as e:
        await db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/presets/{preset_id}", response_model=PresetDetailResponse)
async def update_preset(
    preset_id: uuid.UUID,
    preset_data: PresetUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update preset and recipe"""
    try:
        preset = await product_service.update_preset(
            session=db,
            preset_id=preset_id,
            preset_data=preset_data
        )
        if not preset:
            raise HTTPException(status_code=404, detail="Preset not found")
        await db.commit()  # Commit the transaction
        return preset
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/presets/{preset_id}")
async def delete_preset(
    preset_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete preset"""
    try:
        success = await product_service.delete_preset(
            session=db,
            preset_id=preset_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Preset not found")
        await db.commit()  # Commit the transaction
        return SuccessResponse(message="Preset deleted successfully")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
