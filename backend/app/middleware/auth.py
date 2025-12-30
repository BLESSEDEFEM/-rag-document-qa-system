"""
Clerk JWT authentication middleware for FastAPI.
"""
import os
import logging
from typing import Optional
from fastapi import HTTPException, Header
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")


class ClerkAuth:
    """Clerk JWT authentication handler using secret key."""
    
    def __init__(self):
        if not CLERK_SECRET_KEY:
            logger.warning("CLERK_SECRET_KEY not found - auth disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Clerk auth initialized")
    
    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify Clerk session token using Clerk API.
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            User data dict or None if invalid
        """
        if not self.enabled:
            logger.warning("Auth disabled - no secret key")
            return {"sub": "anonymous", "email": "anonymous@example.com"}
        
        try:
            # Verify token with Clerk API
            response = requests.get(
                "https://api.clerk.com/v1/sessions/verify",
                headers={
                    "Authorization": f"Bearer {CLERK_SECRET_KEY}",
                    "Content-Type": "application/json",
                },
                params={"token": token},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Token verified for user: {data.get('user_id')}")
                return {
                    "sub": data.get("user_id"),
                    "email": data.get("user", {}).get("email_addresses", [{}])[0].get("email_address", "unknown")
                }
            else:
                logger.warning(f"Token verification failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None


# Global auth instance
clerk_auth = ClerkAuth()


def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Dependency to get current authenticated user.
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


def get_current_user_optional(authorization: str = Header(None)) -> dict:
    """
    Optional auth - returns anonymous user if no token.
    """
    if not authorization:
        return {"sub": "anonymous", "email": "anonymous@example.com"}
    
    if not authorization.startswith("Bearer "):
        return {"sub": "anonymous", "email": "anonymous@example.com"}
    
    token = authorization.replace("Bearer ", "")
    user = clerk_auth.verify_token(token)
    
    return user or {"sub": "anonymous", "email": "anonymous@example.com"}