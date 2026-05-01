"""
Service de usuário — regras de negócio.

PADRÃO DO PROJETO — regras do service:
  - Orquestra repositórios. Nunca acessa self.session.execute() diretamente.
  - Contém TODA a lógica de negócio (validações, decisões, cálculos).
  - Levanta exceções de domínio (app.core.exceptions), não HTTPException.
  - É a camada testada nos testes unitários (sem banco real).
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNaoEncontrado
from app.core.security import create_access_token, hash_password, verify_password
from app.usuario.model import Usuario
from app.usuario.repository import UsuarioRepository
from app.usuario.schema import TokenResponse, UsuarioCreate, UsuarioUpdate


class UsuarioService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UsuarioRepository(session)

    async def criar(self, dados: UsuarioCreate) -> Usuario:
        """
        Cria um novo usuário após validar unicidade do login.

        Raises:
            HTTPException 409: Se o login já estiver em uso.
        """
        existente = await self.repo.get_by_login(dados.login)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Login '{dados.login}' já está em uso.",
            )

        usuario = Usuario(
            nome=dados.nome,
            login=dados.login,
            senha_hash=hash_password(dados.senha),
            perfil=dados.perfil,
        )
        return await self.repo.create(usuario)

    async def autenticar(self, login: str, senha: str):
        """
        Valida credenciais e retorna um JWT.

        Raises:
            HTTPException 401: Se as credenciais forem inválidas.
        """
        usuario = await self.repo.get_by_login(login)

        # Verificação unificada: não revelar se o login existe ou não.
        if not usuario or not verify_password(senha, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login ou senha incorretos.",
            )
        if not usuario.ativo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo. Contate o gestor.",
            )

        token = create_access_token(subject=usuario.id, perfil=usuario.perfil)
        return TokenResponse(access_token=token, token_type="bearer", id_user=usuario.id)

    async def buscar_por_id(self, usuario_id: str) -> Usuario:
        """
        Retorna um usuário pelo ID.

        Raises:
            RecursoNaoEncontrado: Se o ID não existir.
        """
        usuario = await self.repo.get_by_id(usuario_id)
        if not usuario:
            raise RecursoNaoEncontrado("Usuário", usuario_id)
        return usuario

    async def listar(self, apenas_ativos: bool = True) -> list[Usuario]:
        return await self.repo.list_all(apenas_ativos=apenas_ativos)

    async def atualizar(self, usuario_id: str, dados: UsuarioUpdate) -> Usuario:
        """
        Atualiza parcialmente um usuário.

        Raises:
            RecursoNaoEncontrado: Se o ID não existir.
        """
        usuario = await self.buscar_por_id(usuario_id)
        # exclude_unset=True garante que só campos enviados sejam atualizados.
        campos = dados.model_dump(exclude_unset=True)
        return await self.repo.update(usuario, campos)
