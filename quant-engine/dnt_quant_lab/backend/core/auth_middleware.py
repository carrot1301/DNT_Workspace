from fastapi import HTTPException, Header, status
from core.supabase_client import get_supabase

async def get_current_user(authorization: str = Header(None)):
    """
    Dependency to get the current authenticated user from the Authorization header.
    Returns None if not authenticated.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split("Bearer ")[1]
    supabase = get_supabase()
    try:
        # Use Supabase client to verify the token via API
        response = supabase.auth.get_user(token)
        if response and response.user:
            return response.user
        return None
    except Exception as e:
        print(f"Auth verification error: {e}")
        return None

async def require_auth(authorization: str = Header(None)):
    """
    Dependency that enforces authentication.
    Raises 401 if the user is not authenticated.
    """
    user = await get_current_user(authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng đăng nhập để sử dụng tính năng này",
        )
    return user
