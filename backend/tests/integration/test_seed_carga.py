
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.alertas.model import Alertas
from app.core.fuso import hoje_ubs
from app.dispensacao.model import Dispensacao
from app.lote.model import Lote
from app.paciente.service import gerar_codigo
from app.seed.carga import banco_vazio, carregar, limpar
from app.seed.simulacao import gerar_carga
from app.usuario.model import Usuario

SENHAS = {"gestor": "s1", "farmaceut": "s2", "atendente": "s3"}


async def _contar(session: AsyncSession, modelo) -> int:
    return await session.scalar(select(func.count()).select_from(modelo))


async def test_carregar_banco_vazio_persiste_carga_e_gera_alertas(session: AsyncSession):
    carga = gerar_carga(hoje_ubs(), gerar_codigo)
    assert await banco_vazio(session)

    resultado = await carregar(session, carga, SENHAS)

    assert not await banco_vazio(session)
    assert await _contar(session, Usuario) == len(carga.usuarios)
    assert await _contar(session, Lote) == len(carga.lotes)
    assert await _contar(session, Dispensacao) == len(carga.dispensacoes)
    assert resultado["alertas_criados"] > 0
    assert await _contar(session, Alertas) == resultado["alertas_criados"]


async def test_limpar_apos_carga_deixa_banco_vazio(session: AsyncSession):
    await carregar(session, gerar_carga(hoje_ubs(), gerar_codigo), SENHAS)

    await limpar(session)

    assert await banco_vazio(session)
    assert await _contar(session, Dispensacao) == 0
