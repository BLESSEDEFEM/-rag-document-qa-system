"""
Clerk JWT authentication - PRODUCTION READY (Official Method)
Following Clerk's documented manual JWT verification approach.
"""
import os
import logging
from typing import Optional
from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import requests
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Clerk Configuration - USE ENVIRONMENT VARIABLES
CLERK_FRONTEND_API = os.getenv("CLERK_FRONTEND_API", "https://sunny-eel-93.clerk.accounts.dev")
CLERK_ISSUER = CLERK_FRONTEND_API
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", f"{CLERK_FRONTEND_API}/.well-known/jwks.json")

# Security
security = HTTPBearer()


@lru_cache(maxsize=1)
def get_jwks():
    """
    Fetch and cache Clerk's JWKS (public keys).
    Cached to avoid repeated network calls.
    """
    try:
        response = requests.get(CLERK_JWKS_URL, timeout=10)
        response.raise_for_status()
        jwks = response.json()
        logger.info(f"JWKS fetched successfully from {CLERK_JWKS_URL}")
        return jwks
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication service unavailable"
        )


def verify_clerk_token(token: str) -> Optional[dict]:
    """
    Verify Clerk JWT token using JWKS.
    
    Official Clerk verification method:
    - Validates signature using RS256
    - Validates issuer
    - Validates expiration
    - Returns user claims
    
    Args:
        token: JWT session token from Clerk
        
    Returns:
        User payload with claims (sub = user_id)
    """
    try:
        jwks = get_jwks()
        
        # Decode and verify JWT
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
            }
        )
        
        logger.info(f"Token verified for user: {payload.get('sub')}")
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Required authentication - throws 401 if invalid.
    
    Returns:
        User dict with Clerk claims (sub = user_id)
    """
    token = credentials.credentials
    user = verify_clerk_token(token)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token"
        )
    
    return user


def get_current_user_optional(
    authorization: str = Header(None)
) -> dict:
    """
    Optional authentication - returns anonymous if no token.
    
    Returns:
        User dict or anonymous user
    """
    if not authorization or not authorization.startswith("Bearer "):
        return {"sub": "anonymous", "email": "anonymous@example.com"}
    
    token = authorization.replace("Bearer ", "")
    user = verify_clerk_token(token)
    
    return user or {"sub": "anonymous", "email": "anonymous@example.com"}