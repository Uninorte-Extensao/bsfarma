from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNaoEncontrado
from app.core.security import create_access_token, hash_password, verify_password
from app.paciente.model import Paciente
from app.paciente.repository import PacienteRepository
from app.paciente.schema import PacienteCreate

class PacienteService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = PacienteRepository(session)

    async def criar(self, dados: PacienteCreate) -> Paciente:
        """
        Cadastra um código de paciente para dispensação de medicamentos.
        
        É preenchido automaticamente pelo sistema.
        """
        paciente = Paciente(
            codigo=dados.codigo,
            condicao_clinica=dados.condicao_clinica
        )
        return await self.repo.create(paciente)