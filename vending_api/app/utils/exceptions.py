from typing import Optional, Dict, Any


class VendingAPIException(Exception):
    """Base exception for Vending API"""
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(VendingAPIException):
    """Raised when input validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class NotFoundError(VendingAPIException):
    """Raised when a requested resource is not found"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "NOT_FOUND", details)


class ConflictError(VendingAPIException):
    """Raised when there's a conflict with current state"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFLICT", details)


class BusinessRuleError(VendingAPIException):
    """Raised when business rules are violated"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "BUSINESS_RULE_VIOLATION", details)


class InsufficientStockError(BusinessRuleError):
    """Raised when there's insufficient stock for an operation"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.error_code = "INSUFFICIENT_STOCK"


class MachineUnavailableError(BusinessRuleError):
    """Raised when machine is not available for operations"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)
        self.error_code = "MACHINE_UNAVAILABLE"


class OrderProcessingError(VendingAPIException):
    """Raised when order processing fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "ORDER_PROCESSING_ERROR", details)


class PaymentError(VendingAPIException):
    """Raised when payment processing fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "PAYMENT_ERROR", details)


class DatabaseError(VendingAPIException):
    """Raised when database operations fail"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", details)


class AuthenticationError(VendingAPIException):
    """Raised when authentication fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class AuthorizationError(VendingAPIException):
    """Raised when authorization fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ExternalServiceError(VendingAPIException):
    """Raised when external service calls fail"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)


class RateLimitError(VendingAPIException):
    """Raised when rate limits are exceeded"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)
