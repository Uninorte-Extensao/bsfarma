from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.alertas.model import Alertas
from app.alertas.service import AlertaService
from app.core.security import hash_password
from app.dispensacao.model import Dispensacao
from app.lote.model import Lote
from app.medicamentos.model import Medicamento
from app.movimentacao.model import Movimentacao
from app.paciente.model import Paciente
from app.seed.simulacao import CargaDemo
from app.usuario.model import Usuario

ORDEM_INSERCAO = (Usuario, Medicamento, Paciente, Lote, Movimentacao, Dispensacao)
ORDEM_REMOCAO = (Alertas, Dispensacao, Movimentacao, Lote, Paciente, Medicamento, Usuario)
TAMANHO_BLOCO = 1000


async def banco_vazio(session: AsyncSession) -> bool:
    for modelo in (Usuario, Medicamento, Lote):
        total = await session.scalar(select(func.count()).select_from(modelo))
        if total:
            return False
    return True


async def limpar(session: AsyncSession) -> None:
    for modelo in ORDEM_REMOCAO:
        await session.execute(delete(modelo))


async def carregar(session: AsyncSession, carga: CargaDemo, senhas: dict[str, str]) -> dict:
    usuarios = [
        {**u, "senha_hash": hash_password(senhas[u["login"]])}
        for u in carga.usuarios
    ]
    linhas = {
        Usuario: usuarios,
        Medicamento: carga.medicamentos,
        Paciente: carga.pacientes,
        Lote: carga.lotes,
        Movimentacao: carga.movimentacoes,
        Dispensacao: carga.dispensacoes,
    }
    for modelo in ORDEM_INSERCAO:
        registros = linhas[modelo]
        for inicio in range(0, len(registros), TAMANHO_BLOCO):
            await session.execute(insert(modelo), registros[inicio:inicio + TAMANHO_BLOCO])
    await session.flush()
    return await AlertaService(session).verificar_todos()
