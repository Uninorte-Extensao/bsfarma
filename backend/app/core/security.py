"""
Segurança: hashing de senha e geração/validação de tokens JWT.

Não contém lógica de negócio — apenas mecanismos de autenticação.
"""
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Contexto de hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Gera o hash bcrypt de uma senha em texto plano."""
    
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha em texto plano corresponde ao hash armazenado."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, perfil: str) -> str:
    """
    Gera um JWT com o ID do usuário e seu perfil.

    Args:
        subject: ID do usuário (UUID como string).
        perfil: Perfil do usuário (atendente | farmaceutico | gestor).

    Returns:
        Token JWT assinado como string.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": subject,
        "perfil": perfil,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    """
    Decodifica e valida um JWT.

    Raises:
        JWTError (se o token for inválido ou expirado) / Erro 401 Unauthorized
    """
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
        )