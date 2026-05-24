"""
Service de dispensacao — regras de negócio.

PADRÃO DO PROJETO — regras do service:
  - Orquestra múltiplos repositórios em uma única transação atômica.
  - Contém a regra de negócio mais crítica: a baixa do estoque.
  - Levanta exceções de domínio ou HTTPException.
"""

from sqlalchemy import select

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNaoEncontrado, RegraDeNegocioViolada
from app.dispensacao.model import Dispensacao
from app.dispensacao.repository import DispensacaoRepository
from app.dispensacao.schema import DispensacaoCreate
from app.lote.repository import LoteRepository
from app.movimentacao.model import Movimentacao, TipoMovimentacao
from app.movimentacao.repository import MovimentacaoRepository
from app.paciente.model import Paciente


class DispensacaoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        # Orquestração: o Service acessa os 3 repositórios para compor a transação
        self.repo = DispensacaoRepository(session)
        self.lote_repo = LoteRepository(session)
        self.mov_repo = MovimentacaoRepository(session)

    async def criar(self, dados: DispensacaoCreate, usuario_id: str) -> Dispensacao:
        """
        Executa o fluxo completo de dispensação:
        1. Valida se o lote existe.
        2. Verifica se há saldo suficiente.
        3. Deduz a quantidade do lote.
        4. Registra a saída na Movimentação.
        5. Registra o evento de Dispensação no paciente.
        """
        # 1. Buscar o Lote
        lote = await self.lote_repo.get_by_id(dados.lote_id)
        if not lote:
            raise RecursoNaoEncontrado("Lote", dados.lote_id)

        # 2. Validar o estoque físico real
        if lote.quantidade_atual < dados.quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Saldo insuficiente no lote '{lote.numero_lote}'. Disponível: {lote.quantidade_atual}, Solicitado: {dados.quantidade}."
            )

        # 3. Deduzir o saldo do lote
        # Como os repositórios usam .flush(), essa alteração fica pendente na transação
        await self.lote_repo.update(lote, {"quantidade_atual": lote.quantidade_atual - dados.quantidade})

        # 4. Registrar a Movimentação (a trilha de auditoria)
        nova_movimentacao = Movimentacao(
            lote_id=lote.id,
            usuario_id=usuario_id,  
            tipo=TipoMovimentacao.SAIDA,
            quantidade=dados.quantidade,
            justificativa="Dispensação direta ao paciente"
        )
        movimentacao = await self.mov_repo.create(nova_movimentacao)
        paciente = await self.retornar_id_paciente_pelo_codigo(dados.codigo)
        # 5. Registrar a Dispensação (o evento clínico)
        nova_dispensacao = Dispensacao(
            paciente_id=paciente.id,
            movimentacao_id=movimentacao.id,
        )
        dispensacao = await self.repo.create(nova_dispensacao)

        # ATENÇÃO: Confirme que sua injeção de dependência em app.core.dependencies
        # realiza o `await session.commit()` ao final da requisição sem erros.
        # Caso contrário, insira `await self.session.commit()` aqui.
        
        return dispensacao

    async def buscar_por_id(self, dispensacao_id: str) -> Dispensacao:
        """Busca o detalhe de uma dispensação específica."""
        dispensacao = await self.repo.get_by_id(dispensacao_id)
        if not dispensacao:
            raise RecursoNaoEncontrado("Dispensacao", dispensacao_id)
        return dispensacao

    async def listar(self, paciente_id: str | None = None) -> list[Dispensacao]:
        """Lista histórico de dispensações, podendo filtrar por paciente."""
        return await self.repo.list_all(paciente_id=paciente_id)
    
    async def retornar_id_paciente_pelo_codigo(self, codigo: str) -> Paciente:
        resultado = await self.session.execute(
            select(Paciente).where(Paciente.codigo == codigo.upper())
        )
        paciente = resultado.scalar_one_or_none()
        if not paciente:
            raise RecursoNaoEncontrado(
                "Paciente",
                f"código '{codigo}' — verifique o cartão ou cadastre o paciente",
            )
        if not paciente.ativo:
            raise RegraDeNegocioViolada(
                f"Paciente com código '{codigo}' está inativo no sistema."
            )
        return paciente