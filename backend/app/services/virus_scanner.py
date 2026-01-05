"""
Virus scanning service using VirusTotal API.
"""
import os
import hashlib
import vt
from typing import Dict, Any
import logging
import aiofiles

logger = logging.getLogger(__name__)

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
VIRUS_SCAN_REQUIRED = os.getenv("VIRUS_SCAN_REQUIRED", "false").lower() == "true"

async def scan_file(file_path: str) -> Dict[str, Any]:
    """
    Scan a file for viruses using VirusTotal.
    
    Args:
        file_path: Path to the file to scan
        
    Returns:
        Dict with keys: is_safe (bool), scan_result (str), details (dict)
    """
    if not VIRUSTOTAL_API_KEY:
        if VIRUS_SCAN_REQUIRED:
            logger.error("VirusTotal API key not configured - blocking upload")
            return {
                "is_safe": False,
                "scan_result": "error",
                "details": {"reason": "Virus scanning required but unavailable"}
            }
        else:
            logger.warning("VirusTotal API key not configured - allowing upload (scan not required)")
            return {
                "is_safe": True,
                "scan_result": "skipped",
                "details": {"reason": "No API key configured, scanning not required"}
            }
    
    try:
        # Calculate file hash asynchronously with incremental reading
        sha256_hash = hashlib.sha256()
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(65536):  # 64KB chunks
                sha256_hash.update(chunk)
        file_hash = sha256_hash.hexdigest()
        
        # Check with VirusTotal
        client = vt.Client(VIRUSTOTAL_API_KEY)
        
        try:
            # Look up file by hash
            file_obj = await client.get_object_async(f"/files/{file_hash}")
            
            # Check scan results
            stats = file_obj.last_analysis_stats
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            
            is_safe = (malicious == 0 and suspicious == 0)
            
            return {
                "is_safe": is_safe,
                "scan_result": "clean" if is_safe else "threat_detected",
                "details": {
                    "malicious": malicious,
                    "suspicious": suspicious,
                    "harmless": stats.get('harmless', 0),
                    "undetected": stats.get('undetected', 0)
                }
            }
            
        except vt.error.APIError as e:
            if e.code == "NotFoundError":
                # File not in database - fail closed for security
                logger.warning(f"File not in VirusTotal database: {file_hash} - rejecting for safety")
                return {
                    "is_safe": False,
                    "scan_result": "unknown",
                    "details": {"reason": "File not in VirusTotal database - rejected for security"}
                }
            else:
                raise
        
        finally:
            await client.close_async()
            
    except Exception as e:
        logger.exception(f"Virus scan error: {e}")
        # Fail-closed: reject on error
        return {
            "is_safe": False,
            "scan_result": "error",
            "details": {"error": str(e)}
        }