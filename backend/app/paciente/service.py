import os
import re
import hmac
import hashlib
from select import select

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNaoEncontrado, RegraDeNegocioViolada, ErroDeFormulario
from app.paciente.model import Paciente
from app.paciente.repository import PacienteRepository
from app.paciente.schema import PacienteCreate, PacienteUpdate

def normalizar_cpf(cpf: str) -> str:
    """Remove pontuação e espaços do CPF. Ex: '123.456.789-09' → '12345678909'"""
    return re.sub(r'\D', '', cpf)


def validar_cpf(cpf: str) -> bool:
    """
    Valida o CPF pelo algoritmo dos dígitos verificadores da Receita Federal.

    Rejeita sequências trivialmente inválidas (ex: '00000000000', '11111111111').
    Retorna True para CPF válido, False caso contrário.
    """
    cpf = normalizar_cpf(cpf)

    if len(cpf) != 11:
        return False

    # Rejeita sequências repetidas (000...0, 111...1, etc.)
    if len(set(cpf)) == 1:
        return False

    # Primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    d1 = (soma * 10 % 11) % 10
    if d1 != int(cpf[9]):
        return False

    # Segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    d2 = (soma * 10 % 11) % 10
    if d2 != int(cpf[10]):
        return False

    return True


def gerar_codigo(cpf: str) -> str:
    """
    Deriva o código pseudonimizado do paciente a partir do CPF.

    Usa HMAC-SHA256 com o salt institucional (ID_INTERNO_SALT).
    O mesmo CPF sempre gera o mesmo código — isso permite recuperação.

    O salt é lido da variável de ambiente a cada chamada para que
    rotações de chave (key rotation) sejam possíveis no futuro.

    Raises:
        RuntimeError: Se ID_INTERNO_SALT não estiver configurado em produção.
    """
    salt = os.environ.get("ID_INTERNO_SALT", "")

    if not salt:
        if os.environ.get("ENVIRONMENT", "development") == "production":
            raise RuntimeError(
                "ID_INTERNO_SALT não configurado. "
                "Configure a variável de ambiente antes de usar em produção."
            )
        # Desenvolvimento: usa salt padrão com aviso no log
        salt = "salt-de-desenvolvimento-nao-usar-em-producao"

    cpf_limpo = normalizar_cpf(cpf)
    mac = hmac.new(
        salt.encode("utf-8"),
        cpf_limpo.encode("utf-8"),
        hashlib.sha256,
    )
    return mac.hexdigest()[:12].upper()



class PacienteService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = PacienteRepository(session)

    async def criar(self, dados: PacienteCreate) -> Paciente:
        """
        Cadastra um código de paciente para dispensação de medicamentos.
        
        É preenchido automaticamente pelo sistema. Retorna o paciente criado ou já existente para o mesmo CPF.

        Raises:
            RegraDeNegocioViolada: Se o CPF for inválido.
        """

        if not validar_cpf(dados.cpf):
            raise RegraDeNegocioViolada("CPF inválido. Verifique os dígitos e tente novamente.")

        codigo = gerar_codigo(dados.cpf)

        paciente_ja_cadastrado = await self.paciente_ja_existe(codigo)
        if paciente_ja_cadastrado:
            raise ErroDeFormulario("Paciente já cadastrado no sistema!")
        paciente = Paciente(
            codigo           = codigo,
            condicao_clinica = dados.condicao_clinica,
            ativo            = True,
        )

        return await self.repo.create(paciente)


    async def paciente_ja_existe(self, codigo: str) -> Paciente:
        paciente = await self.repo.get_by_codigo(codigo)
        if paciente:
            raise ErroDeFormulario("Paciente já cadastrado no sistema!")
        return paciente

    async def buscar_por_codigo(self, codigo: str) -> Paciente:
        """
        Busca um paciente pelo código do cartão.

        Raises:
            RecursoNaoEncontrado: Se nenhum paciente for encontrado para o código.
        """
        paciente = await self.repo.get_by_codigo(codigo)
        if not paciente:
            raise RecursoNaoEncontrado("Paciente", codigo)
        return paciente
        
    
    async def recuperar_por_cpf(self, cpf: str) -> Paciente:
        """
        Recupera um paciente pelo CPF na ocasião de perda do cartão.

        O CPF é verificado presencialmente pelo atendente e usado para recomputar o código.
        Retorna o paciente correspondente ou levanta erro se não encontrado.

        Raises:
            RecursoNaoEncontrado: Se nenhum paciente for encontrado para o CPF.
        """
        if not validar_cpf(cpf):
            raise RegraDeNegocioViolada("CPF inválido. Verifique os dígitos e tente novamente.")

        codigo = gerar_codigo(cpf)
        paciente = await self.buscar_por_codigo(codigo)

        if not paciente:
            raise RecursoNaoEncontrado(
                "Paciente",
                "CPF informado",
            )
        return paciente

    async def listar(self, codigo: str | None = None, apenas_ativos: bool = True) -> list[Paciente]:
        """
        Lista pacientes, opcionalmente filtrando por um paciente específico.
        """
        return await self.repo.list_all(codigo=codigo, apenas_ativos=apenas_ativos)

    async def atualizar(self, codigo: str, dados: PacienteUpdate) -> Paciente:
        """Atualiza a condição clínica de um paciente existente."""
        paciente = await self.buscar_por_codigo(codigo)
        campos = dados.model_dump(exclude_unset=True)

        return await self.repo.atualizar(paciente, campos)

    async def inativar(self, codigo: str) -> Paciente:
        """Inativa um paciente (soft delete — não apaga o registro)."""
        return await self.repo.inativar_paciente(codigo=codigo)