"""
Testes unitários do UsuarioService.

PADRÃO DO PROJETO — testes unitários:
  - Testam o service isolado (sem banco real, sem HTTP).
  - Usam a fixture `session` com SQLite em memória.
  - Cada teste é independente — banco limpo a cada função.
  - Nomenclatura: test_<ação>_<cenário>_<resultado esperado>

Para criar testes de outro módulo, crie:
  tests/unit/test_<modulo>_service.py
e siga este mesmo padrão.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.usuario.model import PerfilUsuario
from app.usuario.schema import UsuarioCreate, UsuarioUpdate
from app.usuario.service import UsuarioService


# ── Criação de usuário ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_criar_usuario_dados_validos_retorna_usuario(session: AsyncSession):
    """Deve criar e retornar um usuário com os dados fornecidos."""
    service = UsuarioService(session)
    dados = UsuarioCreate(
        nome="Maria Silva",
        login="maria.silva",
        senha="senha-segura-123",
        perfil=PerfilUsuario.ATENDENTE,
    )

    usuario = await service.criar(dados)

    assert usuario.id is not None
    assert usuario.nome == "Maria Silva"
    assert usuario.login == "maria.silva"
    assert usuario.perfil == PerfilUsuario.ATENDENTE
    assert usuario.ativo is True
    # Senha nunca deve ser armazenada em texto plano.
    assert usuario.senha_hash != "senha-segura-123"


@pytest.mark.asyncio
async def test_criar_usuario_login_duplicado_levanta_409(session: AsyncSession):
    """Deve rejeitar criação com login já existente."""
    from fastapi import HTTPException

    service = UsuarioService(session)
    dados = UsuarioCreate(
        nome="Usuário Original",
        login="login.duplicado",
        senha="senha-segura-123",
        perfil=PerfilUsuario.ATENDENTE,
    )
    await service.criar(dados)

    with pytest.raises(HTTPException) as exc_info:
        await service.criar(dados)  # mesmo login

    assert exc_info.value.status_code == 409
    assert "login.duplicado" in exc_info.value.detail


# ── Autenticação ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_autenticar_credenciais_corretas_retorna_token(session: AsyncSession):
    """Credenciais válidas devem retornar um TokenResponse com access_token."""
    service = UsuarioService(session)
    await service.criar(UsuarioCreate(
        nome="Farmacêutico",
        login="farm.teste",
        senha="senha-segura-123",
        perfil=PerfilUsuario.FARMACEUTICO,
    ))

    token = await service.autenticar(login="farm.teste", senha="senha-segura-123")

    assert token.access_token is not None
    assert token.token_type == "bearer"


@pytest.mark.asyncio
async def test_autenticar_senha_errada_levanta_401(session: AsyncSession):
    """Senha incorreta deve retornar 401."""
    from fastapi import HTTPException

    service = UsuarioService(session)
    await service.criar(UsuarioCreate(
        nome="Usuário",
        login="usuario.401",
        senha="senha-correta",
        perfil=PerfilUsuario.ATENDENTE,
    ))

    with pytest.raises(HTTPException) as exc_info:
        await service.autenticar(login="usuario.401", senha="senha-errada")

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_autenticar_login_inexistente_levanta_401(session: AsyncSession):
    """Login que não existe deve retornar 401 (não revelar se login existe)."""
    from fastapi import HTTPException

    service = UsuarioService(session)

    with pytest.raises(HTTPException) as exc_info:
        await service.autenticar(login="nao.existe", senha="qualquer")

    assert exc_info.value.status_code == 401


# ── Atualização ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_atualizar_usuario_campos_parciais_nao_afeta_outros(session: AsyncSession):
    """PATCH com apenas 'nome' não deve alterar perfil nem ativo."""
    service = UsuarioService(session)
    usuario = await service.criar(UsuarioCreate(
        nome="Nome Antigo",
        login="patch.teste",
        senha="senha-segura-123",
        perfil=PerfilUsuario.ATENDENTE,
    ))

    atualizado = await service.atualizar(
        usuario.id,
        UsuarioUpdate(nome="Nome Novo"),
    )

    assert atualizado.nome == "Nome Novo"
    assert atualizado.perfil == PerfilUsuario.ATENDENTE  # não mudou
    assert atualizado.ativo is True                      # não mudou


@pytest.mark.asyncio
async def test_atualizar_usuario_inexistente_levanta_nao_encontrado(session: AsyncSession):
    """Atualizar ID que não existe deve levantar RecursoNaoEncontrado."""
    from app.core.exceptions import RecursoNaoEncontrado

    service = UsuarioService(session)

    with pytest.raises(RecursoNaoEncontrado):
        await service.atualizar("id-que-nao-existe", UsuarioUpdate(nome="X"))
