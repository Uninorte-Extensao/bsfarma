"""
Testes de integração dos endpoints de usuário.

PADRÃO DO PROJETO — testes de integração:
  - Testam as rotas HTTP de ponta a ponta (request → response).
  - Usam a fixture `client` (AsyncClient com banco SQLite de teste).
  - Verificam status code, corpo da resposta e efeitos colaterais.
  - Testam cenários de autorização (quem pode chamar o quê).

Para criar testes de outro módulo, crie:
  tests/integration/test_<modulo>_router.py
e siga este mesmo padrão.
"""

import pytest
from httpx import AsyncClient

from app.usuario.model import Usuario


# ── POST /auth/login ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_credenciais_validas_retorna_200_e_token(
    client: AsyncClient,
    usuario_gestor: Usuario,
):
    response = await client.post("/auth/login", data={
        "username": "gestor.teste",
        "password": "senha-segura-123",
    })

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_senha_errada_retorna_401(
    client: AsyncClient,
    usuario_gestor: Usuario,
):
    response = await client.post("/auth/login", data={
        "username": "gestor.teste",
        "password": "senha-errada",
    })

    assert response.status_code == 401


# ── POST /usuarios ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_criar_usuario_como_gestor_retorna_201(
    client: AsyncClient,
    token_gestor: str,
):
    response = await client.post(
        "/usuarios",
        json={
            "nome": "Novo Atendente",
            "login": "novo.atendente",
            "senha": "senha-segura-123",
            "perfil": "atendente",
        },
        headers={"Authorization": f"Bearer {token_gestor}"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["login"] == "novo.atendente"
    assert "senha" not in body        # senha nunca exposta
    assert "senha_hash" not in body   # hash nunca exposto


@pytest.mark.asyncio
async def test_criar_usuario_como_atendente_retorna_403(
    client: AsyncClient,
    token_atendente: str,
):
    """Atendente não tem permissão para criar usuários."""
    response = await client.post(
        "/usuarios",
        json={
            "nome": "Tentativa",
            "login": "tentativa",
            "senha": "senha-segura-123",
            "perfil": "atendente",
        },
        headers={"Authorization": f"Bearer {token_atendente}"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_criar_usuario_sem_token_retorna_401(client: AsyncClient):
    """Rota protegida sem token deve retornar 401."""
    response = await client.post(
        "/usuarios",
        json={
            "nome": "Sem Token",
            "login": "sem.token",
            "senha": "senha-segura-123",
            "perfil": "atendente",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_criar_usuario_login_duplicado_retorna_409(
    client: AsyncClient,
    token_gestor: str,
    usuario_gestor: Usuario,
):
    """Tentar criar usuário com login já existente deve retornar 409."""
    response = await client.post(
        "/usuarios",
        json={
            "nome": "Duplicado",
            "login": "gestor.teste",  # login do usuario_gestor já criado
            "senha": "senha-segura-123",
            "perfil": "atendente",
        },
        headers={"Authorization": f"Bearer {token_gestor}"},
    )

    assert response.status_code == 409


# ── GET /usuarios ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_listar_usuarios_como_gestor_retorna_200(
    client: AsyncClient,
    token_gestor: str,
    usuario_gestor: Usuario,
):
    response = await client.get(
        "/usuarios",
        headers={"Authorization": f"Bearer {token_gestor}"},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


# ── PATCH /usuarios/{id} ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_atualizar_usuario_como_gestor_retorna_200(
    client: AsyncClient,
    token_gestor: str,
    usuario_gestor: Usuario,
):
    response = await client.patch(
        f"/usuarios/{usuario_gestor.id}",
        json={"nome": "Gestor Atualizado"},
        headers={"Authorization": f"Bearer {token_gestor}"},
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Gestor Atualizado"


@pytest.mark.asyncio
async def test_atualizar_usuario_inexistente_retorna_404(
    client: AsyncClient,
    token_gestor: str,
):
    response = await client.patch(
        "/usuarios/id-que-nao-existe",
        json={"nome": "Nome Qualquer"},
        headers={"Authorization": f"Bearer {token_gestor}"},
    )

    assert response.status_code == 404
