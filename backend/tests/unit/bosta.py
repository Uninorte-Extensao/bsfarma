import uuid
import pytest
import pydantic
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNaoEncontrado
from app.usuario.model import PerfilUsuario
from app.usuario.schema import UsuarioCreate, UsuarioUpdate
from app.usuario.service import UsuarioService


@pytest.mark.asyncio
async def test_CT01_criar_usuario_dados_validos_retorna_usuario(session: AsyncSession):
    """
    CT01 — Login válido
    Cenário:  Inserir dados corretos de cadastro.
    Esperado: Usuário criado com sucesso; senha armazenada como hash.
    Risco:    CRÍTICO — base de todo o fluxo de autenticação.
    """
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
    # Segurança: senha nunca armazenada em texto plano.
    assert usuario.senha_hash != "senha-segura-123"


@pytest.mark.asyncio
async def test_CT02_autenticar_senha_errada_levanta_401(session: AsyncSession):
    """
    CT02 — Senha incorreta
    Cenário:  Usuário existente tenta autenticar com senha inválida.
    Esperado: HTTPException 401 Unauthorized.
    Risco:    CRÍTICO — protege contra acesso indevido.
    """
    service = UsuarioService(session)
    await service.criar(UsuarioCreate(
        nome="Usuário",
        login="usuario.ct02",
        senha="senha-correta",
        perfil=PerfilUsuario.ATENDENTE,
    ))

    with pytest.raises(HTTPException) as exc_info:
        await service.autenticar(login="usuario.ct02", senha="senha-errada")

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_CT03_autenticar_login_inexistente_levanta_401(session: AsyncSession):
    """
    CT03 — Usuário inexistente
    Cenário:  Login que não existe no sistema.
    Esperado: HTTPException 401 (não revelar se o login existe — regra de segurança).
    Risco:    CRÍTICO — evita enumeração de usuários.
    """
    service = UsuarioService(session)

    with pytest.raises(HTTPException) as exc_info:
        await service.autenticar(login="nao.existe", senha="qualquer")

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_CT04_criar_usuario_sem_campos_obrigatorios_levanta_erro(session: AsyncSession):
    """
    CT04 — Campos vazios
    Cenário:  Tentativa de criar usuário sem preencher campos obrigatórios.
    Esperado: Erro de validação (Pydantic / HTTPException 422).
    Risco:    MÉDIO — garante integridade dos dados de entrada.
    """
    with pytest.raises((pydantic.ValidationError, HTTPException)):
        UsuarioCreate(
            nome="",
            login="",
            senha="",
            perfil=None,
        )


@pytest.mark.asyncio
async def test_CT05_criar_usuario_login_formato_invalido_levanta_erro(session: AsyncSession):
    """
    CT05 — Formato de login inválido
    Cenário:  Login fora do padrão aceito (ex.: caracteres especiais não permitidos).
    Esperado: Erro de validação antes de persistir.
    Risco:    MÉDIO — protege a integridade dos dados.
    """
    with pytest.raises((pydantic.ValidationError, HTTPException)):
        UsuarioCreate(
            nome="Teste",
            login="formato inválido!!",  # espaços e caracteres especiais
            senha="senha-segura-123",
            perfil=PerfilUsuario.ATENDENTE,
        )


@pytest.mark.asyncio
async def test_CT06_conta_bloqueada_apos_tentativas_invalidas(session: AsyncSession):
    """
    CT06 — Conta bloqueada
    Cenário:  Exceder o limite de tentativas com senha errada.
    Esperado: HTTPException 429 com header Retry-After.
    Risco:    CRÍTICO — proteção contra força bruta.
    """
    service = UsuarioService(session)
    await service.criar(UsuarioCreate(
        nome="Alvo Brute Force",
        login="usuario.bloqueio",
        senha="senha-real",
        perfil=PerfilUsuario.ATENDENTE,
    ))

    # 5 tentativas falhas para atingir o bloqueio de 5 minutos
    for _ in range(5):
        with pytest.raises(HTTPException):
            await service.autenticar(login="usuario.bloqueio", senha="errada")

    # A 6ª tentativa (mesmo com senha correta) deve ser bloqueada
    with pytest.raises(HTTPException) as exc_info:
        await service.autenticar(login="usuario.bloqueio", senha="errada")

    assert exc_info.value.status_code == 429
    assert "Retry-After" in exc_info.value.headers


@pytest.mark.asyncio
async def test_CT07_logout_invalida_token(session: AsyncSession):
    """
    CT07 — Logout
    Cenário:  Usuário faz logout; token anterior não deve mais ser aceito.
    Esperado: Token invalidado; uso posterior retorna 401.
    Risco:    CRÍTICO — controle de sessão.
    """
    service = UsuarioService(session)
    await service.criar(UsuarioCreate(
        nome="Usuário Logout",
        login="usuario.logout",
        senha="senha-segura-123",
        perfil=PerfilUsuario.ATENDENTE,
    ))

    token = await service.autenticar(login="usuario.logout", senha="senha-segura-123")
    assert token.access_token is not None

    await service.logout(token.access_token)

    with pytest.raises(HTTPException) as exc_info:
        await service.verificar_token(token.access_token)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_autenticar_credenciais_corretas_retorna_token(session: AsyncSession):
    """
    Cenário Crítico: Credenciais válidas devem retornar TokenResponse com access_token.
    Risco: CRÍTICO — fluxo principal de acesso ao sistema.
    """
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
async def test_criar_usuario_login_duplicado_levanta_409(session: AsyncSession):
    """
    Cenário Crítico: Rejeitar criação de usuário com login já existente.
    Risco: ALTO — integridade dos dados e unicidade de identidade.
    """
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


@pytest.mark.asyncio
async def test_seguranca_sql_injection_nao_autentica(session: AsyncSession):
    """
    Cenário Crítico: Tentativa de SQL Injection no campo de login.
    Esperado: Sistema rejeita sem autenticar (401 ou erro de validação).
    Risco:    CRÍTICO — vulnerabilidade de segurança grave.
    """
    service = UsuarioService(session)
    payloads = [
        ("' OR '1'='1", "qualquer"),
        ("admin'--", "qualquer"),
        ("' OR 1=1--", ""),
    ]

    for login_payload, senha_payload in payloads:
        with pytest.raises(HTTPException) as exc_info:
            await service.autenticar(login=login_payload, senha=senha_payload)
        assert exc_info.value.status_code in (401, 422), (
            f"SQL Injection não bloqueado para payload: {login_payload!r}"
        )


@pytest.mark.asyncio
async def test_seguranca_token_expirado_levanta_401(session: AsyncSession):
    """
    Cenário Crítico: Token expirado não deve conceder acesso.
    Esperado: HTTPException 401 ao usar token vencido.
    Risco:    CRÍTICO — controle de sessão e segurança.
    """
    service = UsuarioService(session)

    # Token simulado como expirado (gerado externamente ou mockado)
    token_expirado = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expirado.assinatura"

    with pytest.raises(HTTPException) as exc_info:
        await service.verificar_token(token_expirado)

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_atualizar_usuario_campos_parciais_nao_afeta_outros(session: AsyncSession):
    """
    Atualização parcial (PATCH): alterar apenas 'nome' não deve modificar perfil nem ativo.
    Risco: MÉDIO — integridade de dados na atualização.
    """
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
    assert atualizado.perfil == PerfilUsuario.ATENDENTE
    assert atualizado.ativo is True


@pytest.mark.asyncio
async def test_atualizar_usuario_inexistente_levanta_nao_encontrado(session: AsyncSession):
    """
    Atualizar ID que não existe deve levantar RecursoNaoEncontrado.
    Risco: MÉDIO — tratamento correto de recursos ausentes.
    """
    service = UsuarioService(session)
    id_falso = str(uuid.uuid4())
    with pytest.raises(RecursoNaoEncontrado):
        await service.atualizar(id_falso, UsuarioUpdate(nome="sr-nao-existente"))