from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from uuid import UUID
import logging
from fastapi import Depends

from app.dao.machine_dao import MachineDAO
from app.models.machine import VendingMachine
from app.schemas.machine import MachineCreate
from app.config.machine_config import machine_settings
from app.utils.exceptions import NotFoundError, ConflictError
from app.config.database import get_async_db

logger = logging.getLogger(__name__)


class MachineRegistrationService:
    """Service for machine registration and discovery"""
    
    def __init__(self):
        self.machine_dao = MachineDAO()
    
    async def get_current_machine_id(self, session: AsyncSession) -> Optional[UUID]:
        """
        Get the current machine ID based on configuration:
        1. From environment variable (single machine mode)
        2. Auto-discovery based on network/hardware
        3. Return None for multi-machine mode
        """
        if not machine_settings.multi_machine_mode:
            # Single machine mode - get from environment
            machine_id = machine_settings.get_machine_id()
            if machine_id:
                # Verify machine exists in database
                machine = await self.machine_dao.get_by_id(session, machine_id)
                if machine:
                    return machine_id
                else:
                    logger.warning(f"Machine ID {machine_id} not found in database")
                    
                    # Auto-register if enabled
                    if machine_settings.auto_register_machine:
                        return await self.auto_register_machine(session, machine_id)
            
            # Try auto-discovery
            if machine_settings.auto_register_machine:
                return await self.discover_and_register_machine(session)
        
        # Multi-machine mode or no configuration
        return None
    
    async def auto_register_machine(
        self, 
        session: AsyncSession, 
        machine_id: Optional[UUID] = None
    ) -> UUID:
        """Auto-register this machine in the database"""
        try:
            machine_data = MachineCreate(
                location=machine_settings.machine_location or "Auto-registered Machine",
                status="active",
                cups_qty=100,  # Default values
                bowls_qty=50
            )
            
            if machine_id:
                # Use specific machine ID if provided
                machine = await self.machine_dao.create(
                    session, 
                    id=machine_id,
                    **machine_data.dict()
                )
            else:
                # Let database generate UUID
                machine = await self.machine_dao.create(session, **machine_data.dict())
            
            logger.info(f"Auto-registered machine: {machine.id} at {machine.location}")
            return machine.id
            
        except Exception as e:
            logger.error(f"Failed to auto-register machine: {e}")
            raise ConflictError("Failed to register machine")
    
    async def discover_and_register_machine(self, session: AsyncSession) -> Optional[UUID]:
        """
        Discover machine identity and register if needed
        This could use hardware ID, MAC address, etc.
        """
        try:
            # Get hardware/network identifier
            hardware_id = self._get_hardware_identifier()
            
            # Check if machine already exists with this identifier
            # (You'd need to add a hardware_id field to the machines table)
            
            # For now, just auto-register with location detection
            location = self._detect_location()
            
            machine_data = MachineCreate(
                location=location,
                status="active",
                cups_qty=100,
                bowls_qty=50
            )
            
            machine = await self.machine_dao.create(session, **machine_data.dict())
            logger.info(f"Auto-discovered and registered machine: {machine.id}")
            return machine.id
            
        except Exception as e:
            logger.error(f"Failed to discover and register machine: {e}")
            return None
    
    async def validate_or_register_machine(
        self, 
        session: AsyncSession, 
        machine_id: UUID,
        location_hint: Optional[str] = None
    ) -> bool:
        """
        Validate machine ID exists in database, or auto-register if enabled
        This is the main method for UI-provided machine IDs
        """
        try:
            # First, check if machine already exists
            machine = await self.machine_dao.get_by_id(session, machine_id)
            if machine:
                logger.debug(f"Machine {machine_id} found in database")
                return True
            
            # Machine doesn't exist - auto-register if enabled
            if machine_settings.auto_register_machine:
                logger.info(f"Auto-registering new machine: {machine_id}")
                
                machine_data = MachineCreate(
                    location=location_hint or f"Auto-registered ({machine_id})",
                    status="active",
                    cups_qty=machine_settings.default_cups_qty,
                    bowls_qty=machine_settings.default_bowls_qty
                )
                
                # Create machine with the provided UUID
                await self.machine_dao.create(
                    session, 
                    id=machine_id,
                    **machine_data.dict()
                )
                
                logger.info(f"Successfully auto-registered machine: {machine_id}")
                return True
            else:
                logger.warning(f"Machine {machine_id} not found and auto-registration disabled")
                return False
                
        except Exception as e:
            logger.error(f"Error validating/registering machine {machine_id}: {e}")
            return False

    def _get_hardware_identifier(self) -> str:
        """Get unique hardware identifier for this machine"""
        import platform
        import socket
        
        # Combine multiple identifiers for uniqueness
        hostname = socket.gethostname()
        platform_info = platform.machine()
        
        # You could also use MAC address, CPU serial, etc.
        return f"{hostname}-{platform_info}"
    
    def _detect_location(self) -> str:
        """Detect machine location (IP-based, GPS, manual config, etc.)"""
        import socket
        
        hostname = socket.gethostname()
        
        # Map hostnames to locations (customize for your setup)
        location_map = {
            "vending-machine-01": "Main Campus - Building A",
            "vending-machine-02": "Student Center",
            "vending-machine-03": "Library - Ground Floor",
        }
        
        return location_map.get(hostname, f"Unknown Location ({hostname})")


# Dependency for getting current machine ID in endpoints
async def get_current_machine_id(session: AsyncSession = Depends(get_async_db)) -> Optional[UUID]:
    """Dependency to get current machine ID for single-machine deployments"""
    service = MachineRegistrationService()
    return await service.get_current_machine_id(session)
