from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

class MachineSettings(BaseSettings):
    """Machine-specific configuration"""
    
    # Backend deployment mode
    multi_machine_mode: bool = os.getenv("MULTI_MACHINE_MODE", "true").lower() == "true"
    
    # Auto-registration settings
    auto_register_machine: bool = os.getenv("AUTO_REGISTER_MACHINE", "true").lower() == "true"
    
    # Default settings for auto-registered machines
    default_cups_qty: int = int(os.getenv("DEFAULT_CUPS_QTY", "100"))
    default_bowls_qty: int = int(os.getenv("DEFAULT_BOWLS_QTY", "50"))
    
    # Legacy single-machine mode support (for backwards compatibility)
    machine_id: Optional[str] = os.getenv("VENDING_MACHINE_ID")
    machine_location: Optional[str] = os.getenv("VENDING_MACHINE_LOCATION")
    
    def get_machine_id(self) -> Optional[uuid.UUID]:
        """Get machine ID with validation (legacy single-machine mode)"""
        if self.machine_id:
            try:
                return uuid.UUID(self.machine_id)
            except ValueError:
                raise ValueError(f"Invalid machine ID format: {self.machine_id}")
        return None

machine_settings = MachineSettings()
