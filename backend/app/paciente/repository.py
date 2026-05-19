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
    
    async def get_by_codigo(self, codigo: str) -> Paciente | None:
        """
        Busca um paciente pelo ID interno do sistema. 
        
        Usado para dispensação de medicamentos.
        """
        result = await self.session.execute(
            select(Paciente).where(Paciente.codigo == codigo)
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
    
    async def list_all(self, codigo: str | None = None) -> list[Paciente]:
        stmt = select(Paciente).order_by(Paciente.criado_em.desc())
        
        if codigo:
            stmt = stmt.where(Paciente.codigo == codigo)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def atualizar(self,  paciente: Paciente, dados: dict) -> Paciente:
        for campo, valor in dados.items():
            setattr(paciente, campo, valor)
        await self.session.flush()
        await self.session.refresh(paciente)
        return paciente
    
    async def inativar_paciente(self, codigo: str) -> Paciente | None:
        paciente = await self.get_by_codigo(codigo)
        paciente.ativo = False
        await self.session.flush()
        return paciente

    

    