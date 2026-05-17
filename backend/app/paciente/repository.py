from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.paciente.model import Paciente

class PacienteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, paciente_id: str) -> Paciente | None:
        """Busca um paciente pelo UUID. Retorna None se não existir."""
        result = await self.session.execute(
            select(Paciente).where(Paciente.id == paciente_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_interno(self, paciente: str) -> Paciente | None:
        """
        Busca um paciente pelo ID interno do sistema. 
        
        Usado para dispensação de medicamentos.
        """
        result = await self.session.execute(
            select(Paciente).where(Paciente.id_interno == paciente)
        )
        return result.scalar_one_or_none()
    
    async def create(self, paciente: Paciente) -> Paciente:
        """
        Cadastra um novo paciente. O objeto deve ser criado pelo service 
        (paciente/service.py) antes de chamar esse método.
        """

        self.session.add(paciente)
        await self.session.flush()
        await self.session.refresh(paciente)
        return paciente

    