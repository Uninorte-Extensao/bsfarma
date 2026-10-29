import asyncio
from sqlalchemy import select
# IMPORTAÇÃO VITAL: carrega todos os models antes de qualquer uso do ORM.
# Sem isso, relationship() com strings (ex.: back_populates="Dispensacao")
# falha com "expression 'X' failed to locate a name" quando este seeder
# roda sozinho (python -m app.<modulo>.seeder), porque nem todo model do
# projeto chega a ser importado — só os que este arquivo referencia direto.
import app.db.models
from app.db.base import SessionLocal
from app.dispensacao.model import Dispensacao
from app.lote.model import Lote
from app.medicamentos.model import Medicamento
from app.movimentacao.model import Movimentacao, TipoMovimentacao
from app.paciente.model import Paciente

# Vincula as saídas criadas pelo MovimentacaoSeeder a pacientes cuja condição
# clínica justifica o medicamento. Rode depois dos seeders de movimentação e paciente.
# (nome_generico do medicamento, trechos aceitos em paciente.condicao_clinica)
CONDICOES_POR_MEDICAMENTO = [
    ("Cloridrato De Metformina",       ["Diabetes mellitus tipo 2"]),
    ("Glibenclamida",                  ["Diabetes mellitus tipo 2"]),
    ("Insulina Humana",                ["Diabetes mellitus tipo 1"]),
    ("Dapagliflozina",                 ["Doença cardiovascular", "Insuficiência cardíaca"]),
    ("Atenolol",                       ["Hipertensão"]),
    ("Losartana Potássica",            ["Hipertensão"]),
    ("Captopril",                      ["Hipertensão"]),
    ("Sinvastatina",                   ["Dislipidemia", "Hipercolesterolemia"]),
    ("Sulfato De Salbutamol",          ["Asma"]),
    ("Levonorgestrel;Etinilestradiol", ["anticoncepção hormonal (Z30.0)"]),
]

async def seed_initial_data():
    async with SessionLocal() as db:
        try:
            pacientes = (await db.execute(
                select(Paciente).where(Paciente.ativo.is_(True)).order_by(Paciente.codigo)
            )).scalars().all()

            total = 0
            for (nome_gen, trechos) in CONDICOES_POR_MEDICAMENTO:
                candidatos = [p for p in pacientes if any(t in p.condicao_clinica for t in trechos)]
                if not candidatos:
                    print(f"    [skip] Nenhum paciente compatível com {nome_gen}")
                    continue

                # Saídas deste medicamento que ainda não têm dispensação vinculada
                saidas = (await db.execute(
                    select(Movimentacao)
                    .join(Lote, Lote.id == Movimentacao.lote_id)
                    .join(Medicamento, Medicamento.id == Lote.medicamento_id)
                    .outerjoin(Dispensacao, Dispensacao.movimentacao_id == Movimentacao.id)
                    .where(
                        Medicamento.nome_generico == nome_gen,
                        Movimentacao.tipo == TipoMovimentacao.SAIDA,
                        Dispensacao.id.is_(None),
                    )
                    .order_by(Movimentacao.ocorrido_em)
                )).scalars().all()

                # Distribui as saídas entre os pacientes compatíveis (round-robin)
                for i, mov in enumerate(saidas):
                    db.add(Dispensacao(
                        paciente_id=candidatos[i % len(candidatos)].id,
                        movimentacao_id=mov.id,
                        dispensado_em=mov.ocorrido_em,
                    ))
                total += len(saidas)
                print(f"    [+] {nome_gen[:30]:<30} {len(saidas)} dispensações -> {len(candidatos)} paciente(s)")

            await db.commit()
            print(f"\n    Total de dispensações criadas: {total}")
        except Exception as e:
            print("Houve um erro ao fazer a migração: ", e)
            await db.rollback()

if __name__ == "__main__":
    print("Iniciando o seed de dispensações...")
    asyncio.run(seed_initial_data())
    print("Processo finalizado.")
