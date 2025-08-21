"""
Data Access Objects for database views.
These DAOs provide read-only access to PostgreSQL views for reporting and analytics.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from app.dao.base_dao import BaseDAO
from app.models.views import (
    VMachineIngredientInventory,
    VMachineAddonInventory, 
    VCompleteOrderDetails,
    VMachineDashboard,
    VLowStockAlerts,
    VPresetAvailabilityPerMachine,
    VAvailableItemsPerMachine,
    VOrderSummary,
    VPresetDetails
)
from app.utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class MachineInventoryViewDAO:
    """DAO for machine inventory views"""
    
    async def get_machine_ingredient_inventory(
        self, 
        session: AsyncSession, 
        machine_id: Optional[UUID] = None,
        stock_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get machine ingredient inventory from view"""
        try:
            query = select(VMachineIngredientInventory)
            
            if machine_id:
                query = query.where(VMachineIngredientInventory.machine_id == machine_id)
            
            if stock_status:
                query = query.where(VMachineIngredientInventory.stock_status == stock_status)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            # Convert SQLAlchemy objects to dictionaries
            inventory_list = []
            for row in rows:
                obj = row[0]  # Get the VMachineIngredientInventory object
                inventory_list.append({
                    'machine_id': obj.machine_id,
                    'machine_location': obj.machine_location,
                    'machine_status': obj.machine_status,
                    'ingredient_id': obj.ingredient_id,
                    'ingredient_name': obj.ingredient_name,
                    'ingredient_emoji': obj.ingredient_emoji,
                    'price_per_gram': obj.price_per_gram,
                    'calories_per_g': obj.calories_per_g,
                    'max_percent_limit': obj.max_percent_limit,
                    'qty_available_g': obj.qty_available_g,
                    'low_stock_threshold_g': obj.low_stock_threshold_g,
                    'stock_status': obj.stock_status,
                    'stock_percentage': obj.stock_percentage,
                    'inventory_updated_at': obj.inventory_updated_at,
                    'min_qty_g': obj.min_qty_g
                })
            
            return inventory_list
        except Exception as e:
            logger.error(f"Error getting machine ingredient inventory: {e}")
            raise DatabaseError("Failed to get machine ingredient inventory")
    
    async def get_machine_addon_inventory(
        self, 
        session: AsyncSession, 
        machine_id: Optional[UUID] = None,
        stock_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get machine addon inventory from view"""
        try:
            query = select(VMachineAddonInventory)
            
            if machine_id:
                query = query.where(VMachineAddonInventory.machine_id == machine_id)
            
            if stock_status:
                query = query.where(VMachineAddonInventory.stock_status == stock_status)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            # Convert SQLAlchemy objects to dictionaries
            inventory_list = []
            for row in rows:
                obj = row[0]  # Get the VMachineAddonInventory object
                inventory_list.append({
                    'machine_id': obj.machine_id,
                    'machine_location': obj.machine_location,
                    'machine_status': obj.machine_status,
                    'addon_id': obj.addon_id,
                    'addon_name': obj.addon_name,
                    'addon_icon': obj.addon_icon,
                    'addon_price': obj.addon_price,
                    'addon_calories': obj.addon_calories,
                    'qty_available': obj.qty_available,
                    'low_stock_threshold': obj.low_stock_threshold,
                    'stock_status': obj.stock_status,
                    'stock_percentage': obj.stock_percentage,
                    'inventory_updated_at': obj.inventory_updated_at
                })
            
            return inventory_list
        except Exception as e:
            logger.error(f"Error getting machine addon inventory: {e}")
            raise DatabaseError("Failed to get machine addon inventory")
    
    async def get_available_items_for_machine(
        self, 
        session: AsyncSession, 
        machine_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all available items for a specific machine"""
        try:
            query = select(VAvailableItemsPerMachine).where(
                VAvailableItemsPerMachine.machine_id == machine_id
            )
            
            result = await session.execute(query)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(f"Error getting available items for machine {machine_id}: {e}")
            raise DatabaseError("Failed to get available items")


class DashboardViewDAO:
    """DAO for dashboard and reporting views"""
    
    async def get_machine_dashboard_data(
        self, 
        session: AsyncSession, 
        machine_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get machine dashboard metrics"""
        try:
            query = select(VMachineDashboard)
            
            if machine_id:
                query = query.where(VMachineDashboard.machine_id == machine_id)
            
            result = await session.execute(query)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(f"Error getting machine dashboard data: {e}")
            raise DatabaseError("Failed to get machine dashboard data")
    
    async def get_low_stock_alerts(
        self, 
        session: AsyncSession, 
        machine_location: Optional[str] = None,
        alert_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get low stock alerts"""
        try:
            query = select(VLowStockAlerts)
            
            if machine_location:
                query = query.where(VLowStockAlerts.machine_location == machine_location)
            
            if alert_level:
                query = query.where(VLowStockAlerts.alert_level.ilike(f'%{alert_level}%'))
            
            query = query.order_by(VLowStockAlerts.priority_order, VLowStockAlerts.machine_location)
            
            result = await session.execute(query)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(f"Error getting low stock alerts: {e}")
            raise DatabaseError("Failed to get low stock alerts")


class OrderViewDAO:
    """DAO for order-related views"""
    
    async def get_order_summary(
        self, 
        session: AsyncSession, 
        machine_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get order summary from view"""
        try:
            query = select(VOrderSummary)
            
            if machine_id:
                query = query.where(VOrderSummary.machine_id == machine_id)
            
            query = query.order_by(VOrderSummary.order_date.desc()).offset(offset).limit(limit)
            
            result = await session.execute(query)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(f"Error getting order summary: {e}")
            raise DatabaseError("Failed to get order summary")
    
    async def get_complete_order_details(
        self, 
        session: AsyncSession, 
        order_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get complete order details from view"""
        try:
            query = select(VCompleteOrderDetails).where(
                VCompleteOrderDetails.order_id == order_id
            )
            
            result = await session.execute(query)
            row = result.first()
            return dict(row._mapping) if row else None
        except Exception as e:
            logger.error(f"Error getting complete order details for {order_id}: {e}")
            raise DatabaseError("Failed to get complete order details")


class PresetViewDAO:
    """DAO for preset-related views"""
    
    async def get_preset_details(
        self, 
        session: AsyncSession, 
        preset_id: Optional[UUID] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get preset details with ingredients"""
        try:
            query = select(VPresetDetails)
            
            if preset_id:
                query = query.where(VPresetDetails.preset_id == preset_id)
            
            if category:
                query = query.where(VPresetDetails.preset_category == category)
            
            query = query.order_by(VPresetDetails.preset_name, VPresetDetails.ingredient_percent.desc())
            
            result = await session.execute(query)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.error(f"Error getting preset details: {e}")
            raise DatabaseError("Failed to get preset details")
    
    async def get_preset_availability_for_machine(
        self, 
        session: AsyncSession, 
        machine_id: UUID,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get preset availability for a specific machine"""
        try:
            query = select(VPresetAvailabilityPerMachine).where(
                VPresetAvailabilityPerMachine.machine_id == machine_id
            )
            
            if category:
                query = query.where(VPresetAvailabilityPerMachine.preset_category == category)
            
            query = query.order_by(
                VPresetAvailabilityPerMachine.preset_category,
                VPresetAvailabilityPerMachine.preset_name
            )
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            # Convert SQLAlchemy objects to dictionaries
            preset_list = []
            for row in rows:
                obj = row[0]  # Get the VPresetAvailabilityPerMachine object
                preset_list.append({
                    'machine_id': obj.machine_id,
                    'machine_location': obj.machine_location,
                    'preset_id': obj.preset_id,
                    'preset_name': obj.preset_name,
                    'preset_category': obj.preset_category,
                    'preset_price': obj.preset_price,
                    'preset_calories': obj.preset_calories,
                    'preset_description': obj.preset_description,
                    'preset_image': obj.preset_image,
                    'availability_status': obj.availability_status,
                    'missing_ingredients': obj.missing_ingredients
                })
            
            return preset_list
        except Exception as e:
            logger.error(f"Error getting preset availability for machine {machine_id}: {e}")
            raise DatabaseError("Failed to get preset availability")


class AnalyticsViewDAO:
    """DAO for analytics and reporting queries using views"""
    
    async def get_sales_analytics(
        self, 
        session: AsyncSession, 
        machine_id: Optional[UUID] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get sales analytics using order views"""
        try:
            # Use raw SQL to leverage the views for complex analytics
            sql = text("""
                SELECT 
                    COUNT(*) as total_orders,
                    COALESCE(SUM(total_price), 0) as total_revenue,
                    COALESCE(AVG(total_price), 0) as avg_order_value,
                    COUNT(*) FILTER (WHERE order_status = 'completed') as completed_orders,
                    COUNT(*) FILTER (WHERE order_status = 'cancelled') as cancelled_orders,
                    ROUND(
                        (COUNT(*) FILTER (WHERE order_status = 'completed')::DECIMAL / 
                         NULLIF(COUNT(*), 0)) * 100, 2
                    ) as completion_rate
                FROM v_order_summary
                WHERE order_date >= CURRENT_DATE - INTERVAL ':days days'
                  AND (:machine_id IS NULL OR machine_id = :machine_id)
            """)
            
            result = await session.execute(sql, {"days": days, "machine_id": machine_id})
            row = result.first()
            return dict(row._mapping) if row else {}
        except Exception as e:
            logger.error(f"Error getting sales analytics: {e}")
            raise DatabaseError("Failed to get sales analytics")
    
    async def get_inventory_analytics(
        self, 
        session: AsyncSession, 
        machine_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get inventory analytics using inventory views"""
        try:
            sql = text("""
                SELECT 
                    COUNT(*) as total_items,
                    COUNT(*) FILTER (WHERE stock_status = 'AVAILABLE') as available_items,
                    COUNT(*) FILTER (WHERE stock_status = 'LOW_STOCK') as low_stock_items,
                    COUNT(*) FILTER (WHERE stock_status = 'OUT_OF_STOCK') as out_of_stock_items,
                    ROUND(AVG(stock_percentage), 2) as avg_stock_percentage
                FROM (
                    SELECT stock_status, stock_percentage 
                    FROM v_machine_ingredient_inventory
                    WHERE (:machine_id IS NULL OR machine_id = :machine_id)
                    UNION ALL
                    SELECT stock_status, stock_percentage 
                    FROM v_machine_addon_inventory
                    WHERE (:machine_id IS NULL OR machine_id = :machine_id)
                ) combined_inventory
            """)
            
            result = await session.execute(sql, {"machine_id": machine_id})
            row = result.first()
            return dict(row._mapping) if row else {}
        except Exception as e:
            logger.error(f"Error getting inventory analytics: {e}")
            raise DatabaseError("Failed to get inventory analytics")
