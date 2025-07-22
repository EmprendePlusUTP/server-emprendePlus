# utils/sanitization.py
import re
from fastapi import HTTPException

MALICIOUS_PATTERNS = [
    r"(?i)\b(SELECT|UPDATE|DELETE|INSERT|DROP|ALTER|UNION|--|;|OR\s+1=1|1=1|OR\s+'.*?'\s*=\s*'.*?')\b",
    r"(?i)<script.*?>.*?</script.*?>",
    r"(?i)<.*?on\w+=['\"].*?['\"].*?>",
]

def validate_safe_text(value: str, field_name: str) -> str:
    for pattern in MALICIOUS_PATTERNS:
        if re.search(pattern, value):
            raise HTTPException(
                status_code=400,
                detail=f"El campo '{field_name}' contiene contenido malicioso."
            )
    return value
