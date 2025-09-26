"""
API Dependencies Package
"""

from .auth import verify_admin_access, require_admin_permissions

__all__ = ["verify_admin_access", "require_admin_permissions"]