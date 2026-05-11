from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import blocklist, timeout
from app.core.exceptions import RecursoNaoEncontrado
from app.core.security import create_access_token, hash_password, verify_password, decode_access_token
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
        bloqueado, segundos = timeout.verificar_bloqueio(login)
        if bloqueado:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Muitas tentativas. Tente novamente em {segundos}s.",
                headers={"Retry-After": str(segundos)},
            )

        usuario = await self.repo.get_by_login(login)
        if not usuario or not verify_password(senha, usuario.senha_hash):
            timeout.registrar_falha(login)          # incrementa contador
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login ou senha incorretos.",
            )
        
        if not usuario.ativo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo. Contate o gestor.",
            )

        # limpar histórico de falhas
        timeout.resetar(login)

        token = create_access_token(subject=usuario.id, perfil=usuario.perfil)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            id_user=usuario.id,
        )
    
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
    
    async def logout(self, token: str) -> None:
        """
        Invalida um JWT adicionando-o à blocklist até sua expiração.
        Raises:
            HTTPException 401: Se o token já for inválido.
        """
        payload = decode_access_token(token)  # já levanta 401 se inválido

        exp = payload.get("exp")
        expira_em = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc) if exp else datetime.now(tz=timezone.utc)

        blocklist.adicionar(token, expira_em)

    async def verificar_token(self, token: str) -> dict:
        """
        Verifica se um token é válido e não está na blocklist.
        Raises:
            HTTPException 401: Se inválido, expirado ou invalidado por logout.
        """
        if blocklist.esta_bloqueado(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalidado. Faça login novamente.",
            )
        return decode_access_token(token)
    