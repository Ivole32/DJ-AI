"""
Class readiness check utilities.
"""

from fastapi import HTTPException, status
from typing import Any

def ensure_ready(obj: Any, *, check: str = "is_ready", name: str | None = None) -> bool:
    """
    Ensure that an object is ready.

    Args:
        obj: Object to check
        check: Name of readiness method (default: is_ready)
        name: Name for error message

    Raises:
        HTTPException(500) if check method not found
        HTTPException(503) if not ready
    """
    checker = getattr(obj, check, None)

    if not callable(checker):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{name or obj.__class__.__name__} has no '{check}()' method",
        )

    if not checker():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{name or obj.__class__.__name__} not ready",
        )

    return True