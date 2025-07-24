from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID

from .base_dao import BaseDAO
from app.models.product import Ingredient, Addon, Preset, PresetIngredient


class IngredientDAO(BaseDAO[Ingredient]):
    def __init__(self):
        super().__init__(Ingredient)

    async def get_all_available(
        self, 
        session: AsyncSession, 
        available_only: bool = True
    ) -> List[Ingredient]:
        """Get all ingredients with optional availability filtering"""
        query = select(self.model)
        
        # Note: available_only would need machine-specific inventory check
        # For now, return all ingredients
        
        result = await session.execute(query)
        return result.scalars().all()


class AddonDAO(BaseDAO[Addon]):
    def __init__(self):
        super().__init__(Addon)

    async def get_available(
        self, 
        session: AsyncSession,
        available_only: bool = True
    ) -> List[Addon]:
        """Get available addons"""
        query = select(self.model)
        
        # Note: available_only would need machine-specific inventory check
        # For now, return all addons
        
        result = await session.execute(query)
        return result.scalars().all()


class PresetDAO(BaseDAO[Preset]):
    def __init__(self):
        super().__init__(Preset)

    async def get_by_category(
        self, 
        session: AsyncSession, 
        category: Optional[str] = None
    ) -> List[Preset]:
        """Get presets filtered by category"""
        query = select(self.model)
        
        if category:
            query = query.where(self.model.category == category)
            
        result = await session.execute(query)
        return result.scalars().all()

    async def get_with_ingredients(
        self, 
        session: AsyncSession, 
        preset_id: UUID
    ) -> Optional[Preset]:
        """Get preset with its ingredient details"""
        query = select(self.model).options(
            selectinload(self.model.preset_ingredients)
            .selectinload(PresetIngredient.ingredient)
        ).where(self.model.id == preset_id)
        
        result = await session.execute(query)
        return result.scalar_one_or_none()


class PresetIngredientDAO(BaseDAO[PresetIngredient]):
    def __init__(self):
        super().__init__(PresetIngredient)

    async def get_by_preset(
        self, 
        session: AsyncSession, 
        preset_id: UUID
    ) -> List[PresetIngredient]:
        """Get all ingredients for a preset"""
        query = select(self.model).options(
            selectinload(self.model.ingredient)
        ).where(self.model.preset_id == preset_id)
        
        result = await session.execute(query)
        return result.scalars().all()
