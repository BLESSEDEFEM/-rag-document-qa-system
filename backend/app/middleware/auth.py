"""
Clerk JWT authentication middleware for FastAPI.
"""
import os
import logging
from typing import Optional
from fastapi import HTTPException, Header
import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY", "")


class ClerkAuth:
    """Clerk JWT authentication handler."""
    
    def __init__(self):
        if not CLERK_SECRET_KEY or not CLERK_PUBLISHABLE_KEY:
            logger.warning("Clerk keys not found - auth disabled")
            self.enabled = False
            self.jwks_client = None
            return
        
        self.enabled = True
        
        # Extract the instance identifier from publishable key
        # pk_test_xxx or pk_live_xxx format
        key_parts = CLERK_PUBLISHABLE_KEY.split("_")
        
        # For development keys, use the standard Clerk frontend API
        if "test" in CLERK_PUBLISHABLE_KEY:
            # Development JWKS endpoint - works for all test instances
            jwks_url = "https://api.clerk.com/v1/jwks"
        else:
            # Production - extract domain from key
            jwks_url = "https://api.clerk.com/v1/jwks"
        
        self.jwks_client = PyJWKClient(jwks_url)
        logger.info(f"Clerk auth initialized with JWKS: {jwks_url}")
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify Clerk JWT token locally using JWKS."""
        if not self.enabled:
            logger.debug("Auth disabled - returning anonymous user")
            return {"sub": "anonymous", "email": "anonymous@example.com"}
        
        try:
            # Get signing key from JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and verify JWT
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


# Global instance
clerk_auth = ClerkAuth()


def get_current_user_optional(authorization: str = Header(None)) -> dict:
    """Optional auth - returns anonymous user if no token."""
    if not authorization or not authorization.startswith("Bearer "):
        return {"sub": "anonymous", "email": "anonymous@example.com"}
    
    token = authorization.replace("Bearer ", "")
    user = clerk_auth.verify_token(token)
    
    return user or {"sub": "anonymous", "email": "anonymous@example.com"}


def get_current_user(authorization: str = Header(None)) -> dict:
    """Required auth - throws 401 if invalid."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    user = clerk_auth.verify_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user