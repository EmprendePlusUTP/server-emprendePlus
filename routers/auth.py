# auth.py
import json
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from jose import jwt

# Configuración de Auth0 (pon esto en variables de entorno en un proyecto real)
import os
from dotenv import load_dotenv

from db.models import User

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("API_AUDIENCE")
ALGORITHMS = ["RS256"]

# Esquema de seguridad
token_auth_scheme = HTTPBearer()

# Caché para la clave pública de Auth0 para no pedirla en cada request
jwks_cache = {}

def get_token_auth_header(auth: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    """
    Función de dependencia para validar y decodificar el token JWT.
    """
    token = auth.credentials
    
    # Obtener la clave pública de Auth0 (JWKS)
    global jwks_cache
    if not jwks_cache:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks_cache = requests.get(jwks_url).json()

    # Extraer la cabecera del token para encontrar la clave correcta
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
        )

    rsa_key = {}
    for key in jwks_cache["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            break
    
    if not rsa_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key",
        )

    # Validar el token
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid claims, please check audience and issuer")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to parse authentication token.")
    
def get_current_user(payload: dict = Depends(get_token_auth_header)) -> User:
    user_id = payload.get("sub")
    user_email = payload.get("https://emprendeplus.com/email")
    user_name = payload.get("https://emprendeplus.com/name")

    if not user_id or not user_email:
        raise HTTPException(status_code=401, detail="Faltan datos en el token")

    return {
        "id": user_id,
        "email": user_email,
        "name": user_name,
    }