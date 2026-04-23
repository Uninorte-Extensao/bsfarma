"""
Dependências reutilizáveis do FastAPI.

Injete com Depends() nas rotas. Exemplo:
    @router.get("/rota")
    async def rota(
        session: AsyncSession = Depends(get_session),
        usuario: UsuarioModel = Depends(get_current_user),
    ):
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_session() -> AsyncSession:
    """
    Fornece uma sessão de banco de dados por requisição.

    A sessão é aberta no início e fechada (com rollback em caso de erro)
    ao final de cada requisição, garantindo isolamento de transação.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Valida o JWT e retorna o usuário autenticado.

    Injete esta dependência em rotas protegidas.
    Para verificar o perfil, use get_current_gestor ou get_current_farmaceutico.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Import aqui para evitar dependência circular entre core e usuario.
    from app.usuario.repository import UsuarioRepository

    repo = UsuarioRepository(session)
    usuario = await repo.get_by_id(user_id)
    if usuario is None or not usuario.ativo:
        raise credentials_exception
    return usuario


def require_perfil(*perfis: str):
    """
    Fábrica de dependências para controle de acesso por perfil.

    Uso:
        @router.delete("/item/{id}")
        async def deletar(usuario = Depends(require_perfil("gestor", "farmaceutico"))):
    """
    async def verificar(usuario=Depends(get_current_user)):
        if usuario.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Usuários do perfil de acesso '{usuario.perfil}' não tem acesso a este recurso.",
            )
        return usuario

    return verificar
