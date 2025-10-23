# handlers/__init__.py
from .start_handler import router as start_router
from .photo_handler import router as photo_router
from .payment_handler import router as payment_router
from .admin_handler import router as admin_router

__all__ = ["start_router", "photo_router", "payment_router", "admin_router"]