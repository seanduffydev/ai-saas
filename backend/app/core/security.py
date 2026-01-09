"""Authentication and authorization"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client

from app.core.database import get_supabase


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase)
):
    """
    Validate JWT token and return current user.
    
    Args:
        credentials: Bearer token from request header
        supabase: Supabase client instance
        
    Returns:
        User object from Supabase auth
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        user = supabase.auth.get_user(credentials.credentials)
        if not user or not user.user:
            raise HTTPException(
                status_code=401, 
                detail="Invalid authentication credentials"
            )
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Authentication failed: {str(e)}"
        )


def get_user_id_from_token(current_user) -> str:
    """
    Extract user ID from authenticated user object.
    
    Args:
        current_user: User object from get_current_user
        
    Returns:
        User ID string
    """
    return current_user.id
