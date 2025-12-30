"""
Clerk JWT authentication middleware for FastAPI.
"""
import os
import logging
import requests
from typing import Optional
from fastapi import HTTPException, Header
import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_JWKS_URL = "https://api.clerk.com/v1/jwks"


class ClerkAuth:
    """Clerk JWT authentication handler."""
    
    def __init__(self):
        self.jwks_client = PyJWKClient(CLERK_JWKS_URL)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify Clerk JWT token and return user data.
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            User data dict or None if invalid
        """
        try:
            # Get signing key from Clerk JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and verify token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_exp": True}
            )
            
            logger.info(f"Token verified for user: {payload.get('sub')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None


# Global auth instance
clerk_auth = ClerkAuth()


def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Dependency to get current authenticated user.
    
    Usage:
        @router.get("/protected")
        def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["sub"]}
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    user = clerk_auth.verify_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user