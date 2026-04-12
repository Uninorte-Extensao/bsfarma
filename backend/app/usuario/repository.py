"""
Repositório de usuário — acesso ao banco de dados.

PADRÃO DO PROJETO — regras do repositório:
  - Só faz queries. Sem lógica de negócio.
  - Recebe AsyncSession via construtor (injetada pelo service).
  - Retorna modelos ORM ou None. Nunca levanta HTTPException.
  - Paginação: sempre com cursor ou limit/offset explícito.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.usuario.model import Usuario


class UsuarioRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, usuario_id: str) -> Usuario | None:
        """Busca um usuário pelo UUID. Retorna None se não existir."""
        result = await self.session.execute(
            select(Usuario).where(Usuario.id == usuario_id)
        )
        return result.scalar_one_or_none()

    async def get_by_login(self, login: str) -> Usuario | None:
        """Busca um usuário pelo login. Usado na autenticação."""
        result = await self.session.execute(
            select(Usuario).where(Usuario.login == login)
        )
        return result.scalar_one_or_none()

    async def list_all(self, apenas_ativos: bool = True) -> list[Usuario]:
        """
        Lista todos os usuários.

        Args:
            apenas_ativos: Se True (padrão), filtra apenas usuários ativos.
        """
        stmt = select(Usuario)
        if apenas_ativos:
            stmt = stmt.where(Usuario.ativo == True)  # noqa: E712
        stmt = stmt.order_by(Usuario.nome)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, usuario: Usuario) -> Usuario:
        """
        Persiste um novo usuário no banco.

        O objeto deve ser criado pelo service antes de chamar este método.
        """
        self.session.add(usuario)
        await self.session.flush()   # gera o ID sem commitar — o commit é do get_session
        await self.session.refresh(usuario)
        return usuario

    async def update(self, usuario: Usuario, dados: dict) -> Usuario:
        """
        Atualiza campos de um usuário existente.

        Args:
            usuario: Instância ORM já carregada.
            dados: Dicionário com apenas os campos a atualizar.
        """
        for campo, valor in dados.items():
            setattr(usuario, campo, valor)
        await self.session.flush()
        await self.session.refresh(usuario)
        return usuario
