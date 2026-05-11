"""
Seeder de movimentações.

Simula 6 meses de histórico de uma UBS com ~800 pacientes cadastrados,
exercitando todos os tipos de movimentação:

  ENTRADA     — recebimento do almoxarifado central (toda segunda-feira)
  DISPENSACAO — dispensação diária no balcão (volume proporcional à prevalência)
  AJUSTE      — correção de inventário mensal (diferença de contagem)
  PERDA       — descarte de lotes vencidos ou danificados

Distribuição baseada em dados epidemiológicos do SUS:
  - Hipertensão:  ~35% dos atendimentos
  - Diabetes:     ~20%
  - Dislipidemia: ~15%
  - Demais:       ~30%

As movimentações de ENTRADA correspondem aos lotes do LoteSeeder —
a quantidade_inicial de cada lote é a soma das entradas daquele lote.
"""

from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import SessionLocal
from app.lote.model import Lote
from app.medicamentos.model import Medicamento
from app.movimentacao.model import Movimentacao, TipoMovimentacao
from app.usuario.model import Usuario


def dt(ano, mes, dia, hora=9, minuto=0):
    """Cria datetime com timezone UTC."""
    return datetime(ano, mes, dia, hora, minuto, tzinfo=timezone.utc)

async def seed_initial_data():
    async with SessionLocal() as db:
        try:
            # Carrega usuários
            gestor     = (await db.execute(select(Usuario).where(Usuario.login == "gestor"))).scalar_one_or_none()
            farmaceut  = (await db.execute(select(Usuario).where(Usuario.login == "farmaceut"))).scalar_one_or_none()
            atendente  = (await db.execute(select(Usuario).where(Usuario.login == "atendente"))).scalar_one_or_none()

            gid = gestor.id    if gestor    else None
            fid = farmaceut.id if farmaceut else None
            aid = atendente.id if atendente else None

            # Helper para buscar lote pelo número
            async def lote(numero: str) -> Lote | None:
                return (await db.execute(
                    select(Lote).where(Lote.numero_lote == numero)
                )).scalar_one_or_none()

            movs = []

            # ── ENTRADAS DE ESTOQUE (registradas pelo farmacêutico) ───────────────
            # Refletem o recebimento dos lotes cadastrados no LoteSeeder.
            entradas = [
                # (numero_lote, quantidade, data)
                # Salbutamol
                ("GK240089", 200, dt(2024,  1, 8,  8, 30)),
                ("GK240312", 300, dt(2024,  7, 1,  8, 30)),
                ("GK241105", 300, dt(2025,  1, 6,  8, 30)),
                # Beclometasona 200mcg
                ("CH231044", 150, dt(2023, 11, 6,  8, 0)),
                ("CH240876", 200, dt(2024,  8, 5,  8, 0)),
                # Ipratrópio
                ("BI240233", 120, dt(2024,  5, 6,  8, 0)),
                # Metformina 500mg
                ("EU230741", 500, dt(2023,  4, 3,  8, 0)),
                ("EU240388", 600, dt(2024,  4, 1,  8, 0)),
                ("EU241200", 600, dt(2025,  1, 6,  8, 0)),
                # Metformina 850mg
                ("MK240512", 400, dt(2024,  6, 3,  8, 0)),
                ("MK241088", 400, dt(2025,  1, 6,  8, 0)),
                # Glibenclamida
                ("SA240199", 300, dt(2024,  3, 4,  8, 0)),
                # Insulina R
                ("EL240067",  80, dt(2024,  1, 8,  8, 0)),
                ("EL240412", 100, dt(2024,  8, 5,  8, 0)),
                # Atenolol
                ("EF231155", 800, dt(2023,  6, 5,  8, 0)),
                ("EF240733",1000, dt(2024,  6, 3,  8, 0)),
                ("EF241300",1000, dt(2025,  1, 6,  8, 0)),
                # Anlodipino
                ("PF240088", 800, dt(2024,  2, 5,  8, 0)),
                ("PF241044", 800, dt(2025,  1, 6,  8, 0)),
                # Captopril
                ("BM240311", 700, dt(2024,  4, 1,  8, 0)),
                ("BM241099", 700, dt(2025,  1, 6,  8, 0)),
                # Hidroclorotiazida
                ("MQ230988", 500, dt(2023,  7, 3,  8, 0)),
                ("MQ240621", 800, dt(2024,  7, 1,  8, 0)),
                # Losartana
                ("MK240188", 800, dt(2024,  3, 4,  8, 0)),
                ("MK241022", 800, dt(2025,  1, 6,  8, 0)),
                # Enalapril
                ("MK240244", 500, dt(2024,  4, 1,  8, 0)),
                # Espironolactona
                ("PF240399", 300, dt(2024,  5, 6,  8, 0)),
                # Furosemida
                ("SA240567", 400, dt(2024,  7, 1,  8, 0)),
                # Metoprolol
                ("AZ240712", 300, dt(2024,  8, 5,  8, 0)),
                # Sinvastatinas
                ("MK240155", 500, dt(2024,  2, 5,  8, 0)),
                ("MK240277", 500, dt(2024,  4, 1,  8, 0)),
                ("MK241088", 500, dt(2025,  1, 6,  8, 0)),
                ("MK240388", 200, dt(2024,  2, 5,  8, 0)),
                ("MK241144", 300, dt(2025,  1, 6,  8, 0)),
                # Anticoncepcionais
                ("BY240433", 200, dt(2024,  5, 6,  8, 0)),
                ("PF240511",  80, dt(2024,  6, 3,  8, 0)),
                # Alendronato
                ("MK240622", 100, dt(2024,  8, 5,  8, 0)),
                # Parkinson
                ("MK240109",  60, dt(2024,  2, 5,  8, 0)),
                ("RC240088",  60, dt(2024,  2, 5,  8, 0)),
                # Glaucoma
                ("MK240744",  30, dt(2024,  9, 2,  8, 0)),
                ("MK240788",  30, dt(2024,  9, 2,  8, 0)),
                # Rinite
                ("AZ240655",  60, dt(2024,  8, 5,  8, 0)),
                ("AZ240699",  60, dt(2024,  8, 5,  8, 0)),
                # Dapagliflozina
                ("AZ240901", 150, dt(2024, 10, 7,  8, 0)),
            ]

            for (numero, qtd, ocorrido_em) in entradas:
                lt = await lote(numero)
                if not lt:
                    continue
                if await _mov_existe(db, lt.id, TipoMovimentacao.ENTRADA):
                    print(f"    [skip] ENTRADA lote {numero}")
                    continue
                movs.append(Movimentacao(
                    lote_id=lt.id, usuario_id=fid,
                    tipo=TipoMovimentacao.ENTRADA,
                    quantidade=qtd, ocorrido_em=ocorrido_em,
                ))
                print(f"    [+] ENTRADA  {numero:<12} +{qtd}")

            # ── DISPENSAÇÕES (registradas pelo atendente) ──────────────────────────
            # Cada tupla: (numero_lote, qtd_por_dispensacao, [(data, hora), ...])
            dispensacoes = [
                # Metformina 500mg — alta rotatividade
                ("EU240388", 30, [
                    dt(2024,4,3,9,15), dt(2024,4,10,10,0), dt(2024,4,17,9,30),
                    dt(2024,5,2,9,0),  dt(2024,5,9,10,30), dt(2024,5,16,9,0),
                    dt(2024,6,3,9,15), dt(2024,6,10,11,0), dt(2024,6,20,9,30),
                    dt(2024,7,1,9,0),  dt(2024,7,8,10,0),
                ]),
                # Atenolol — alta rotatividade
                ("EF240733", 30, [
                    dt(2024,6,5,9,0),  dt(2024,6,12,10,0), dt(2024,6,19,9,30),
                    dt(2024,7,2,9,0),  dt(2024,7,10,10,30),dt(2024,7,17,9,0),
                    dt(2024,8,1,9,15), dt(2024,8,8,10,0),  dt(2024,8,15,9,30),
                    dt(2024,9,2,9,0),  dt(2024,9,10,10,0), dt(2024,9,20,9,0),
                    dt(2024,10,3,9,15),dt(2024,10,14,10,0),
                ]),
                # Losartana
                ("MK240188", 30, [
                    dt(2024,3,5,9,0),  dt(2024,3,12,10,0), dt(2024,4,2,9,0),
                    dt(2024,4,9,10,30),dt(2024,5,6,9,0),   dt(2024,5,14,10,0),
                    dt(2024,6,3,9,30), dt(2024,7,1,9,0),
                ]),
                # Captopril
                ("BM240311", 30, [
                    dt(2024,4,4,9,0),  dt(2024,4,18,10,0), dt(2024,5,7,9,30),
                    dt(2024,5,21,10,0),dt(2024,6,5,9,0),   dt(2024,7,3,9,0),
                    dt(2024,8,7,9,30),
                ]),
                # Sinvastatina 20mg
                ("MK240277", 30, [
                    dt(2024,4,2,9,0),  dt(2024,4,16,10,0), dt(2024,5,7,9,0),
                    dt(2024,6,4,9,30), dt(2024,7,2,9,0),   dt(2024,8,6,9,0),
                ]),
                # Insulina — dispensação menor quantidade, maior frequência
                ("EL240067", 5, [
                    dt(2024,1,10,9,0), dt(2024,1,17,9,0),  dt(2024,1,24,9,0),
                    dt(2024,2,7,9,0),  dt(2024,2,14,9,0),  dt(2024,2,21,9,0),
                    dt(2024,3,6,9,0),  dt(2024,3,13,9,0),  dt(2024,3,20,9,0),
                    dt(2024,4,3,9,0),  dt(2024,4,10,9,0),  dt(2024,4,17,9,0),
                    dt(2024,5,1,9,0),  dt(2024,5,8,9,0),   dt(2024,5,15,9,0),
                ]),
                # Salbutamol inalador
                ("GK240089", 1, [
                    dt(2024,1,9,9,0),  dt(2024,1,16,9,0),  dt(2024,2,6,9,0),
                    dt(2024,2,20,9,0), dt(2024,3,5,9,0),   dt(2024,3,19,9,0),
                    dt(2024,4,2,9,0),  dt(2024,4,16,9,0),  dt(2024,5,7,9,0),
                    dt(2024,5,21,9,0), dt(2024,6,4,9,0),   dt(2024,6,18,9,0),
                    dt(2024,7,2,9,0),  dt(2024,7,16,9,0),
                ]),
                # Levonorgestrel+Etinilestradiol
                ("BY240433", 1, [
                    dt(2024,5,8,9,0),  dt(2024,5,22,9,0),  dt(2024,6,5,9,0),
                    dt(2024,6,19,9,0), dt(2024,7,3,9,0),   dt(2024,7,17,9,0),
                    dt(2024,8,7,9,0),  dt(2024,8,21,9,0),  dt(2024,9,4,9,0),
                    dt(2024,9,18,9,0), dt(2024,10,2,9,0),  dt(2024,10,16,9,0),
                ]),
                # Dapagliflozina
                ("AZ240901", 1, [
                    dt(2024,10,9,9,0), dt(2024,10,16,9,0), dt(2024,10,23,9,0),
                    dt(2024,11,6,9,0), dt(2024,11,13,9,0), dt(2024,11,20,9,0),
                    dt(2024,12,4,9,0), dt(2024,12,11,9,0), dt(2024,12,18,9,0),
                    dt(2025,1,8,9,0),  dt(2025,1,15,9,0),  dt(2025,1,22,9,0),
                    dt(2025,2,5,9,0),  dt(2025,2,12,9,0),  dt(2025,2,19,9,0),
                    dt(2025,3,5,9,0),  dt(2025,3,12,9,0),  dt(2025,3,19,9,0),
                    dt(2025,4,2,9,0),
                ]),
                # Glibenclamida
                ("SA240199", 30, [
                    dt(2024,3,6,9,0),  dt(2024,4,3,9,0),   dt(2024,5,8,9,0),
                ]),
            ]

            for (numero, qtd_por_disp, datas) in dispensacoes:
                lt = await lote(numero)
                if not lt:
                    continue
                for data_ocorrido in datas:
                    movs.append(Movimentacao(
                        lote_id=lt.id, usuario_id=aid,
                        tipo=TipoMovimentacao.DISPENSACAO,
                        quantidade=qtd_por_disp, ocorrido_em=data_ocorrido,
                    ))
                print(f"    [+] DISPENSACAO {numero:<12} {len(datas)} dispensações x{qtd_por_disp}")

            # ── AJUSTES DE INVENTÁRIO ────────────────────────────────────────────
            # Realizados mensalmente pelo farmacêutico após contagem física.
            ajustes = [
                ("EU240388", -8,  dt(2024,7,31,17,0),  "Divergência na contagem de inventário de julho/2024. Diferença de 8 unidades a menor."),
                ("MK240188", -4,  dt(2024,6,28,17,0),  "Inventário junho/2024: 4 comprimidos danificados por umidade — descartados e registrados como ajuste."),
                ("EF240733", +12, dt(2024,9,30,17,0),  "Inventário setembro/2024: 12 unidades encontradas em outro armário, sem registro de entrada anterior."),
                ("GK240312",  -3, dt(2024,10,31,17,0), "Inventário outubro/2024: 3 inaladores com embalagem danificada, impróprios para dispensação."),
            ]

            for (numero, qtd, ocorrido_em, justificativa) in ajustes:
                lt = await lote(numero)
                if not lt:
                    continue
                movs.append(Movimentacao(
                    lote_id=lt.id, usuario_id=fid,
                    tipo=TipoMovimentacao.AJUSTE,
                    quantidade=abs(qtd), ocorrido_em=ocorrido_em,
                    justificativa=justificativa,
                ))
                print(f"    [+] AJUSTE   {numero:<12} {qtd:+d}  {justificativa[:50]}...")

            # ── PERDAS ────────────────────────────────────────────────────────────
            # Descarte de lotes vencidos ou danificados, autorizado pelo gestor.
            perdas = [
                ("EU230741", 500, dt(2025,2,3,10,0),
                "Descarte do lote EU230741 (Metformina 500mg) vencido em 31/01/2025. Inutilização conforme RDC 306/2004. Laudo assinado pelo farmacêutico responsável."),
                ("EF231155", 800, dt(2025,1,6,10,0),
                "Descarte do lote EF231155 (Atenolol 25mg) vencido em 31/12/2024. Inutilização conforme protocolo da VISA municipal. Auto de inutilização nº 2025/001."),
                ("MQ230988", 500, dt(2025,5,5,10,0),
                "Descarte do lote MQ230988 (Hidroclorotiazida 25mg) vencido em 30/04/2025. Inutilização conforme RDC 306/2004."),
                ("GK240089",  14, dt(2024,10,1,10,0),
                "Descarte de 14 unidades do lote GK240089 por violação da embalagem identificada no inventário. Registro fotográfico arquivado."),
            ]

            for (numero, qtd, ocorrido_em, justificativa) in perdas:
                lt = await lote(numero)
                if not lt:
                    continue
                movs.append(Movimentacao(
                    lote_id=lt.id, usuario_id=gid,
                    tipo=TipoMovimentacao.PERDA,
                    quantidade=qtd, ocorrido_em=ocorrido_em,
                    justificativa=justificativa,
                ))
                print(f"    [+] PERDA    {numero:<12} -{qtd}  {justificativa[:50]}...")

            # Persiste tudo em batch
            db.add_all(movs)
            await db.commit()
            print(f"\n    Total de movimentações criadas: {len(movs)}")
        except Exception as e:
            print("Houve um erro ao fazer a migração: ", e)
            await db.rollback()

    async def _mov_existe(db, lote_id: int, tipo: TipoMovimentacao) -> bool:
        r = await db.execute(
            select(Movimentacao).where(
                Movimentacao.lote_id == lote_id,
                Movimentacao.tipo    == tipo,
            ).limit(1)
        )
        return r.scalar_one_or_none() is not None
