from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from app.dao.product_dao import IngredientDAO, AddonDAO, PresetDAO, PresetIngredientDAO
from app.schemas.product import (
    IngredientResponse,
    AddonResponse, 
    PresetResponse,
    PresetDetailResponse,
    PresetIngredientResponse
)
from app.utils.exceptions import NotFoundError


class ProductService:
    """Service for managing products (ingredients, addons, presets)"""
    
    def __init__(self):
        self.ingredient_dao = IngredientDAO()
        self.addon_dao = AddonDAO()
        self.preset_dao = PresetDAO()
        self.preset_ingredient_dao = PresetIngredientDAO()

    async def get_ingredients(
        self, 
        session: AsyncSession,
        available_only: bool = True
    ) -> List[IngredientResponse]:
        """Get all available ingredients"""
        ingredients = await self.ingredient_dao.get_all_available(
            session, available_only
        )
        
        return [
            IngredientResponse(
                id=ingredient.id,
                name=ingredient.name,
                emoji=ingredient.emoji,
                image=ingredient.image,
                min_qty_g=ingredient.min_qty_g,
                max_percent_limit=ingredient.max_percent_limit,
                calories_per_g=ingredient.calories_per_g,
                price_per_gram=ingredient.price_per_gram,
                created_at=ingredient.created_at
                # Note: updated_at field removed as it doesn't exist in the database schema
            )
            for ingredient in ingredients
        ]

    async def get_ingredient_by_id(
        self, 
        session: AsyncSession, 
        ingredient_id: UUID
    ) -> Optional[IngredientResponse]:
        """Get ingredient by ID"""
        ingredient = await self.ingredient_dao.get_by_id(session, ingredient_id)
        
        if not ingredient:
            return None
            
        return IngredientResponse(
            id=ingredient.id,
            name=ingredient.name,
            emoji=ingredient.emoji,
            image=ingredient.image,
            min_qty_g=ingredient.min_qty_g,
            max_percent_limit=ingredient.max_percent_limit,
            calories_per_g=ingredient.calories_per_g,
            price_per_gram=ingredient.price_per_gram,
            created_at=ingredient.created_at
            # Note: updated_at field removed as it doesn't exist in the database schema
        )

    async def get_addons(
        self, 
        session: AsyncSession,
        available_only: bool = True
    ) -> List[AddonResponse]:
        """Get addons with optional filtering"""
        addons = await self.addon_dao.get_available(session, available_only)
        
        return [
            AddonResponse(
                id=addon.id,
                name=addon.name,
                price=addon.price,
                calories=addon.calories,
                icon=addon.icon
                # Note: created_at and updated_at fields removed as they don't exist in the database schema
            )
            for addon in addons
        ]

    async def get_addon_by_id(
        self, 
        session: AsyncSession, 
        addon_id: UUID
    ) -> Optional[AddonResponse]:
        """Get addon by ID"""
        addon = await self.addon_dao.get_by_id(session, addon_id)
        
        if not addon:
            return None
            
        return AddonResponse(
            id=addon.id,
            name=addon.name,
            price=addon.price,
            calories=addon.calories,
            icon=addon.icon
            # Note: created_at and updated_at fields removed as they don't exist in the database schema
        )

    async def get_presets(
        self, 
        session: AsyncSession,
        category: Optional[str] = None
    ) -> List[PresetResponse]:
        """Get presets with optional category filtering"""
        presets = await self.preset_dao.get_by_category(session, category)
        
        return [
            PresetResponse(
                id=preset.id,
                name=preset.name,
                category=preset.category,
                price=preset.price,
                calories=preset.calories,
                description=preset.description,
                image=preset.image,
                created_at=preset.created_at
                # Note: updated_at field removed as it doesn't exist in the database schema
            )
            for preset in presets
        ]

    async def get_preset_details(
        self, 
        session: AsyncSession, 
        preset_id: UUID
    ) -> Optional[PresetDetailResponse]:
        """Get preset with ingredient details"""
        preset = await self.preset_dao.get_with_ingredients(session, preset_id)
        
        if not preset:
            return None

        # Get ingredients for this preset
        preset_ingredients = await self.preset_ingredient_dao.get_by_preset(session, preset_id)
        
        ingredients_list = []
        total_calories = 0
        total_price = Decimal('0.00')
        
        for pi in preset_ingredients:
            ingredient = pi.ingredient
            calories = int(ingredient.calories_per_g * pi.grams_used)
            price = ingredient.price_per_gram * pi.grams_used
            
            ingredients_list.append(
                PresetIngredientResponse(
                    ingredient_id=ingredient.id,
                    ingredient_name=ingredient.name,
                    ingredient_emoji=ingredient.emoji,
                    grams_used=pi.grams_used,
                    percent=pi.percent,  # Fixed: use 'percent' not 'percentage'
                    calories=calories,
                    price=price
                )
            )
            
            total_calories += calories
            total_price += price
        
        return PresetDetailResponse(
            id=preset.id,
            name=preset.name,
            category=preset.category,
            price=preset.price,
            calories=total_calories,
            description=preset.description,
            image=preset.image,
            ingredients=ingredients_list,
            created_at=preset.created_at
            # Note: updated_at field removed as it doesn't exist in the database schema
        )

    # Admin methods for ingredients
    async def list_ingredients_admin(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> dict:
        """List ingredients with pagination and filtering for admin"""
        # For now, use basic filtering - category can be ignored as ingredients don't have categories
        ingredients = await self.ingredient_dao.get_all_available(session, available_only=False)
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            ingredients = [i for i in ingredients if search_lower in i.name.lower()]
        
        # Apply pagination
        total = len(ingredients)
        ingredients = ingredients[skip:skip + limit]
        
        items = [
            IngredientResponse(
                id=ingredient.id,
                name=ingredient.name,
                emoji=ingredient.emoji,
                image=ingredient.image,
                min_qty_g=ingredient.min_qty_g,
                max_percent_limit=ingredient.max_percent_limit,
                calories_per_g=ingredient.calories_per_g,
                price_per_gram=ingredient.price_per_gram,
                created_at=ingredient.created_at
            )
            for ingredient in ingredients
        ]
        
        # Convert skip/limit to page/size format
        page = (skip // limit) + 1
        size = limit
        pages = (total + size - 1) // size  # Ceiling division
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }

    async def create_ingredient(
        self,
        session: AsyncSession,
        ingredient_data
    ) -> IngredientResponse:
        """Create a new ingredient"""
        # Convert Pydantic model to dict if needed
        if hasattr(ingredient_data, 'model_dump'):
            data = ingredient_data.model_dump()
        else:
            data = ingredient_data
            
        ingredient = await self.ingredient_dao.create(session, **data)
        
        return IngredientResponse(
            id=ingredient.id,
            name=ingredient.name,
            emoji=ingredient.emoji,
            image=ingredient.image,
            min_qty_g=ingredient.min_qty_g,
            max_percent_limit=ingredient.max_percent_limit,
            calories_per_g=ingredient.calories_per_g,
            price_per_gram=ingredient.price_per_gram,
            created_at=ingredient.created_at
        )

    async def update_ingredient(
        self,
        session: AsyncSession,
        ingredient_id: UUID,
        ingredient_data
    ) -> IngredientResponse:
        """Update an existing ingredient"""
        # Convert Pydantic model to dict if needed
        if hasattr(ingredient_data, 'model_dump'):
            data = ingredient_data.model_dump(exclude_unset=True)
        else:
            data = ingredient_data
            
        ingredient = await self.ingredient_dao.update(session, ingredient_id, **data)
        
        if not ingredient:
            raise NotFoundError(f"Ingredient {ingredient_id} not found")
        
        return IngredientResponse(
            id=ingredient.id,
            name=ingredient.name,
            emoji=ingredient.emoji,
            image=ingredient.image,
            min_qty_g=ingredient.min_qty_g,
            max_percent_limit=ingredient.max_percent_limit,
            calories_per_g=ingredient.calories_per_g,
            price_per_gram=ingredient.price_per_gram,
            created_at=ingredient.created_at
        )

    async def delete_ingredient(
        self,
        session: AsyncSession,
        ingredient_id: UUID
    ) -> bool:
        """Delete an ingredient"""
        return await self.ingredient_dao.delete(session, ingredient_id)

    # Admin methods for addons
    async def list_addons_admin(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None
    ) -> dict:
        """List addons with pagination and filtering for admin"""
        addons = await self.addon_dao.get_available(session, available_only=False)
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            addons = [a for a in addons if search_lower in a.name.lower()]
        
        # Apply pagination
        total = len(addons)
        addons = addons[skip:skip + limit]
        
        items = [
            AddonResponse(
                id=addon.id,
                name=addon.name,
                price=addon.price,
                calories=addon.calories,
                icon=addon.icon
            )
            for addon in addons
        ]
        
        # Convert skip/limit to page/size format
        page = (skip // limit) + 1
        size = limit
        pages = (total + size - 1) // size  # Ceiling division
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }

    async def create_addon(
        self,
        session: AsyncSession,
        addon_data
    ) -> AddonResponse:
        """Create a new addon"""
        # Convert Pydantic model to dict if needed
        if hasattr(addon_data, 'model_dump'):
            data = addon_data.model_dump()
        else:
            data = addon_data
            
        addon = await self.addon_dao.create(session, **data)
        
        return AddonResponse(
            id=addon.id,
            name=addon.name,
            price=addon.price,
            calories=addon.calories,
            icon=addon.icon
        )

    async def update_addon(
        self,
        session: AsyncSession,
        addon_id: UUID,
        addon_data
    ) -> AddonResponse:
        """Update an existing addon"""
        # Convert Pydantic model to dict if needed
        if hasattr(addon_data, 'model_dump'):
            data = addon_data.model_dump(exclude_unset=True)
        else:
            data = addon_data
            
        addon = await self.addon_dao.update(session, addon_id, **data)
        
        if not addon:
            raise NotFoundError(f"Addon {addon_id} not found")
        
        return AddonResponse(
            id=addon.id,
            name=addon.name,
            price=addon.price,
            calories=addon.calories,
            icon=addon.icon
        )

    async def delete_addon(
        self,
        session: AsyncSession,
        addon_id: UUID
    ) -> bool:
        """Delete an addon"""
        return await self.addon_dao.delete(session, addon_id)

    # Admin methods for presets
    async def list_presets_admin(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> dict:
        """List presets with pagination and filtering for admin"""
        presets = await self.preset_dao.get_by_category(session, category)
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            presets = [p for p in presets if search_lower in p.name.lower()]
        
        # Apply pagination
        total = len(presets)
        presets = presets[skip:skip + limit]
        
        items = [
            PresetResponse(
                id=preset.id,
                name=preset.name,
                category=preset.category,
                price=preset.price,
                calories=preset.calories,
                description=preset.description,
                image=preset.image,
                created_at=preset.created_at
            )
            for preset in presets
        ]
        
        # Convert skip/limit to page/size format
        page = (skip // limit) + 1
        size = limit
        pages = (total + size - 1) // size  # Ceiling division
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }

    async def create_preset(
        self,
        session: AsyncSession,
        preset_data
    ) -> PresetDetailResponse:
        """Create a new preset with ingredients"""
        # Convert Pydantic model to dict if needed
        if hasattr(preset_data, 'model_dump'):
            data = preset_data.model_dump()
        else:
            data = preset_data
        
        # Separate ingredients from preset data
        ingredients_data = data.pop('ingredients', [])
        
        # Create the preset first
        preset = await self.preset_dao.create(session, **data)
        
        # Create preset ingredients if provided
        ingredients_list = []
        if ingredients_data:
            for ingredient_data in ingredients_data:
                # Get the ingredient to calculate calories and price
                ingredient = await self.ingredient_dao.get_by_id(session, ingredient_data['ingredient_id'])
                if not ingredient:
                    continue
                
                # Calculate calories and price for this ingredient in the preset
                grams_used = ingredient_data['grams_used']
                percentage = ingredient_data.get('percent', 50)  # Default to 50% if not provided
                calories = int(ingredient.calories_per_g * grams_used)
                
                # Validate that percentage is within valid range
                if percentage <= 0 or percentage > 100:
                    percentage = 50  # Set to a safe default
                
                # Create preset ingredient record
                preset_ingredient_data = {
                    'preset_id': preset.id,
                    'ingredient_id': ingredient_data['ingredient_id'],
                    'grams_used': grams_used,
                    'percent': percentage,
                    'calories': calories
                }
                
                preset_ingredient = await self.preset_ingredient_dao.create(session, **preset_ingredient_data)
                
                # Add to response list
                price = ingredient.price_per_gram * grams_used
                ingredients_list.append(
                    PresetIngredientResponse(
                        ingredient_id=ingredient.id,
                        ingredient_name=ingredient.name,
                        ingredient_emoji=ingredient.emoji,
                        grams_used=grams_used,
                        percent=percentage,
                        calories=calories,
                        price=price
                    )
                )
        
        return PresetDetailResponse(
            id=preset.id,
            name=preset.name,
            category=preset.category,
            price=preset.price,
            calories=preset.calories,
            description=preset.description,
            image=preset.image,
            ingredients=ingredients_list,
            created_at=preset.created_at
        )

    async def update_preset(
        self,
        session: AsyncSession,
        preset_id: UUID,
        preset_data
    ) -> PresetDetailResponse:
        """Update an existing preset"""
        # Convert Pydantic model to dict if needed
        if hasattr(preset_data, 'model_dump'):
            data = preset_data.model_dump(exclude_unset=True)
        else:
            data = preset_data
            
        preset = await self.preset_dao.update(session, preset_id, **data)
        
        if not preset:
            raise NotFoundError(f"Preset {preset_id} not found")
        
        # Get the full preset details with ingredients after update
        return await self.get_preset_details(session, preset_id)

    async def delete_preset(
        self,
        session: AsyncSession,
        preset_id: UUID
    ) -> bool:
        """Delete a preset"""
        return await self.preset_dao.delete(session, preset_id)
