"""
Clerk JWT authentication middleware for FastAPI.
"""
import os
import logging
import base64
from typing import Optional
from fastapi import HTTPException, Header
import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY", "")


def get_clerk_frontend_api_url(publishable_key: str) -> Optional[str]:
    """
    Extract the Frontend API URL from Clerk publishable key.
    
    Clerk publishable keys are base64 encoded and contain the frontend API URL.
    Format: pk_test_<base64_encoded_frontend_api>$ or pk_live_<base64_encoded_frontend_api>$
    """
    try:
        # Remove pk_test_ or pk_live_ prefix
        if publishable_key.startswith("pk_test_"):
            encoded_part = publishable_key[8:]  # Remove "pk_test_"
        elif publishable_key.startswith("pk_live_"):
            encoded_part = publishable_key[8:]  # Remove "pk_live_"
        else:
            logger.error(f"Invalid publishable key format")
            return None
        
        # Remove trailing $ if present
        if encoded_part.endswith("$"):
            encoded_part = encoded_part[:-1]
        
        # Add padding if needed for base64 decoding
        padding = 4 - len(encoded_part) % 4
        if padding != 4:
            encoded_part += "=" * padding
        
        # Decode base64 to get the frontend API URL
        decoded = base64.b64decode(encoded_part).decode('utf-8')
        
        # The decoded value is the frontend API hostname (e.g., "ideal-bonefish-44.clerk.accounts.dev")
        frontend_api_url = f"https://{decoded}"
        
        logger.info(f"Extracted Clerk Frontend API URL: {frontend_api_url}")
        return frontend_api_url
        
    except Exception as e:
        logger.error(f"Failed to extract Frontend API URL from publishable key: {e}")
        return None


class ClerkAuth:
    """Clerk JWT authentication handler."""
    
    def __init__(self):
        if not CLERK_SECRET_KEY or not CLERK_PUBLISHABLE_KEY:
            logger.warning("Clerk keys not found - auth disabled")
            self.enabled = False
            self.jwks_client = None
            return
        
        self.enabled = True
        
        # Extract Frontend API URL from publishable key
        frontend_api_url = get_clerk_frontend_api_url(CLERK_PUBLISHABLE_KEY)
        
        if not frontend_api_url:
            logger.error("Could not extract Frontend API URL - auth disabled")
            self.enabled = False
            self.jwks_client = None
            return
        
        # Use the Frontend API JWKS endpoint (this is PUBLIC and doesn't require auth)
        jwks_url = f"{frontend_api_url}/.well-known/jwks.json"
        
        try:
            self.jwks_client = PyJWKClient(jwks_url)
            logger.info(f"Clerk auth initialized with JWKS: {jwks_url}")
        except Exception as e:
            logger.error(f"Failed to initialize JWKS client: {e}")
            self.enabled = False
            self.jwks_client = None
    
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