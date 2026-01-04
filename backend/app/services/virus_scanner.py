"""
Virus scanning service using VirusTotal API.
"""
import os
import hashlib
import vt
from typing import Dict
import logging

logger = logging.getLogger(__name__)

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

async def scan_file(file_path: str) -> Dict[str, any]:
    """
    Scan a file for viruses using VirusTotal.
    
    Args:
        file_path: Path to the file to scan
        
    Returns:
        Dict with keys: is_safe (bool), scan_result (str), details (dict)
    """
    if not VIRUSTOTAL_API_KEY:
        logger.warning("VirusTotal API key not configured - skipping virus scan")
        return {
            "is_safe": True,
            "scan_result": "skipped",
            "details": {"reason": "No API key configured"}
        }
    
    try:
        # Calculate file hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
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
                # File not in VirusTotal database - upload for scanning
                with open(file_path, 'rb') as f:
                    analysis = await client.scan_file_async(f)
                
                # Note: Full analysis takes time, so we allow upload
                # and mark for later verification
                logger.info(f"File uploaded to VirusTotal for analysis: {file_hash}")
                return {
                    "is_safe": True,  # Assume safe for new files
                    "scan_result": "pending",
                    "details": {"analysis_id": analysis.id}
                }
            else:
                raise
        
        finally:
            await client.close_async()
            
    except Exception as e:
        logger.error(f"Virus scan error: {e}")
        # Fail-safe: allow upload but log error
        return {
            "is_safe": True,
            "scan_result": "error",
            "details": {"error": str(e)}
        }