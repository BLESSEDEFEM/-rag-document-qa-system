"""
Clerk JWT authentication middleware for FastAPI.
"""
import os
import logging
import base64
import re
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
    
    Clerk publishable keys encode the frontend API URL in base64.
    Format: pk_test_<base64>$ or pk_live_<base64>$
    
    The base64 decodes to something like: ideal-bonefish-44.clerk.accounts.dev
    """
    try:
        if not publishable_key:
            return None
            
        # Remove pk_test_ or pk_live_ prefix
        if publishable_key.startswith("pk_test_"):
            encoded_part = publishable_key[8:]
        elif publishable_key.startswith("pk_live_"):
            encoded_part = publishable_key[8:]
        else:
            logger.error("Invalid publishable key format - must start with pk_test_ or pk_live_")
            return None
        
        # Remove trailing $ if present
        encoded_part = encoded_part.rstrip('$')
        
        # Base64 URL-safe decoding with padding fix
        # Add padding characters if needed
        padding_needed = 4 - (len(encoded_part) % 4)
        if padding_needed != 4:
            encoded_part += "=" * padding_needed
        
        # Try standard base64 first, then URL-safe base64
        decoded = None
        for decode_func in [base64.b64decode, base64.urlsafe_b64decode]:
            try:
                decoded = decode_func(encoded_part).decode('utf-8')
                break
            except Exception:
                continue
        
        if not decoded:
            logger.error("Failed to decode publishable key")
            return None
        
        # Clean up the decoded string - remove any trailing null chars or whitespace
        decoded = decoded.strip().rstrip('\x00')
        
        # Validate it looks like a clerk domain
        if 'clerk' not in decoded.lower():
            logger.error(f"Decoded value doesn't look like a Clerk domain: {decoded}")
            return None
        
        frontend_api_url = f"https://{decoded}"
        logger.info(f"Extracted Clerk Frontend API URL: {frontend_api_url}")
        return frontend_api_url
        
    except Exception as e:
        logger.error(f"Failed to extract Frontend API URL from publishable key: {e}")
        return None


class CustomPyJWKClient(PyJWKClient):
    """Custom PyJWKClient with better caching and timeout handling"""
    def __init__(self, uri, **kwargs):
        super().__init__(uri, lifespan=3600, max_cached_keys=16)  # Cache for 1 hour


class ClerkAuth:
    """Clerk JWT authentication handler."""
    
    def __init__(self):
        logger.info(f"Initializing ClerkAuth...")
        logger.info(f"CLERK_SECRET_KEY present: {bool(CLERK_SECRET_KEY)}")
        logger.info(f"CLERK_PUBLISHABLE_KEY present: {bool(CLERK_PUBLISHABLE_KEY)}")
        
        if not CLERK_SECRET_KEY or not CLERK_PUBLISHABLE_KEY:
            logger.warning("Clerk keys not found - auth disabled")
            self.enabled = False
            self.jwks_client = None
            return
        
        # Extract Frontend API URL from publishable key
        frontend_api_url = get_clerk_frontend_api_url(CLERK_PUBLISHABLE_KEY)
        
        if not frontend_api_url:
            # Fallback: Try to construct from environment or use known pattern
            logger.warning("Could not extract Frontend API URL from publishable key, trying fallback...")
            
            # Check if there's a CLERK_FRONTEND_API env var
            clerk_frontend_api = os.getenv("CLERK_FRONTEND_API")
            if clerk_frontend_api:
                frontend_api_url = f"https://{clerk_frontend_api}"
                logger.info(f"Using CLERK_FRONTEND_API env var: {frontend_api_url}")
            else:
                logger.error("No CLERK_FRONTEND_API fallback available - auth disabled")
                self.enabled = False
                self.jwks_client = None
                return
        
        # Use the Frontend API JWKS endpoint (this is PUBLIC and doesn't require auth)
        jwks_url = f"{frontend_api_url}/.well-known/jwks.json"
        
        try:
            # Create a custom PyJWKClient with longer timeout and better caching
            self.jwks_client = CustomPyJWKClient(jwks_url)
            self.enabled = True
            logger.info(f"Clerk auth initialized successfully with JWKS: {jwks_url}")
        except Exception as e:
            logger.error(f"Failed to initialize JWKS client with URL {jwks_url}: {e}")
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