import asyncio

from datetime import date
from sqlalchemy import select
from app.db.base import SessionLocal
from app.lote.model import Lote
from app.movimentacao.model import Movimentacao
from app.medicamentos.model import Medicamento
from app.usuario.model import Usuario


LOTES = [
# ── ASMA ────────────────────────────────────────────────────────────
("Sulfato De Salbutamol", "100 MCG", [
    ("GK240089", "Glaxosmithkline Brasil Ltda", date(2025, 3, 31),  200, 0),    # vencido/esgotado
    ("GK240312", "Glaxosmithkline Brasil Ltda", date(2026, 8, 31),  300, 187),  # vigente
    ("GK241105", "Glaxosmithkline Brasil Ltda", date(2027, 2, 28),  300, 300),  # vigente novo
]),
("Dipropionato De Beclometasona", "200 MCG", [
    ("CH231044", "Chiesi Farmaceutici",         date(2025, 6, 30),  150, 12),   # crítico (< 30 dias)
    ("CH240876", "Chiesi Farmaceutici",         date(2026, 11, 30), 200, 198),  # vigente
]),
("Brometo De Ipratrópio", "0,25 MG/ML", [
    ("BI240233", "Boehringer Ingelheim Do Brasil", date(2026, 9, 30), 120, 84),
]),

# ── DIABETES ─────────────────────────────────────────────────────────
("Cloridrato De Metformina", "500 MG", [
    ("EU230741", "Eurofarma Laboratorios S.A.", date(2025, 1, 31),  500, 0),    # vencido/esgotado
    ("EU240388", "Eurofarma Laboratorios S.A.", date(2026, 7, 31),  600, 412),  # vigente principal
    ("EU241200", "Eurofarma Laboratorios S.A.", date(2027, 1, 31),  600, 600),  # vigente reserva
]),
("Cloridrato De Metformina", "850 MG", [
    ("MK240512", "Merck S.A.",                  date(2026, 10, 31), 400, 287),
    ("MK241089", "Merck S.A.",                  date(2027, 4, 30),  400, 400),
]),
("Glibenclamida", "5 MG", [
    ("SA240199", "Sanofi-Aventis Farmacêutica Ltda", date(2026, 5, 31),  300, 241),
]),
("Insulina Humana", "100 UI/ML", [
    ("EL240067", "Eli Lilly Do Brasil Ltda",    date(2025, 5, 31),  80,  4),    # crítico
    ("EL240412", "Eli Lilly Do Brasil Ltda",    date(2026, 3, 31),  100, 98),   # vigente
]),

# ── HIPERTENSÃO ──────────────────────────────────────────────────────
("Atenolol", "25 MG", [
    ("EF231155", "Eurofarma Laboratorios S.A.", date(2024, 12, 31), 800, 0),    # vencido
    ("EF240733", "Eurofarma Laboratorios S.A.", date(2026, 12, 31), 1000, 634),
    ("EF241300", "Eurofarma Laboratorios S.A.", date(2027, 6, 30),  1000, 1000),
]),
("Besilato De Anlodipino", "5 MG", [
    ("PF240088", "Pfizer Brasil Ltda",          date(2026, 8, 31),  800, 521),
    ("PF241044", "Pfizer Brasil Ltda",          date(2027, 2, 28),  800, 800),
]),
("Captopril", "25 MG", [
    ("BM240311", "Bristol-Myers Squibb",        date(2026, 6, 30),  700, 488),
    ("BM241099", "Bristol-Myers Squibb",        date(2027, 1, 31),  700, 700),
]),
("Hidroclorotiazida", "25 MG", [
    ("MQ230988", "Medquímica Indústria Farmacêutica", date(2025, 4, 30), 500, 0),    # vencido
    ("MQ240621", "Medquímica Indústria Farmacêutica", date(2026, 9, 30), 800, 577),
]),
("Losartana Potássica", "50 MG", [
    ("MK240188", "Merck Sharp & Dohme",         date(2026, 11, 30), 800, 634),
    ("MK241022", "Merck Sharp & Dohme",         date(2027, 5, 31),  800, 800),
]),
("Maleato De Enalapril", "10 MG", [
    ("MK240244", "Merck Sharp & Dohme",         date(2026, 7, 31),  500, 311),
]),
("Espironolactona", "25 MG", [
    ("PF240399", "Pfizer Brasil Ltda",          date(2026, 10, 31), 300, 188),
]),
("Furosemida", "40 MG", [
    ("SA240567", "Sanofi-Aventis Farmacêutica Ltda", date(2026, 8, 31),  400, 256),
]),
("Succinato De Metoprolol", "25 MG", [
    ("AZ240712", "Astrazeneca Do Brasil Ltda",  date(2026, 9, 30),  300, 201),
]),

# ── DISLIPIDEMIA ─────────────────────────────────────────────────────
("Sinvastatina", "10 MG", [
    ("MK240155", "Merck Sharp & Dohme",         date(2026, 6, 30),  500, 388),
]),
("Sinvastatina", "20 MG", [
    ("MK240277", "Merck Sharp & Dohme",         date(2026, 6, 30),  500, 321),
    ("MK241088", "Merck Sharp & Dohme",         date(2027, 1, 31),  500, 500),
]),
("Sinvastatina", "40 MG", [
    ("MK240388", "Merck Sharp & Dohme",         date(2025, 6, 30),  200, 8),    # crítico
    ("MK241144", "Merck Sharp & Dohme",         date(2027, 2, 28),  300, 300),
]),

# ── ANTICONCEPÇÃO ────────────────────────────────────────────────────
("Levonorgestrel;Etinilestradiol", "0,15 MG + 0,03 MG", [
    ("BY240433", "Bayer S.A.",                  date(2026, 7, 31),  200, 144),
]),
("Acetato De Medroxiprogesterona", "150 MG", [
    ("PF240511", "Pfizer Brasil Ltda",          date(2026, 8, 31),  80,  61),
]),

# ── OSTEOPOROSE ──────────────────────────────────────────────────────
("Alendronato De Sódio", "70 MG", [
    ("MK240622", "Merck Sharp & Dohme",         date(2026, 10, 31), 100, 72),
]),

# ── DOENÇA DE PARKINSON ──────────────────────────────────────────────
("Carbidopa (Port. 344/98 Lista C 1);Levodopa", "25 MG + 250 MG", [
    ("MK240109", "Merck Sharp & Dohme",         date(2026, 5, 31),  60,  38),
]),
("Cloridrato De Benserazida;Levodopa", "25 MG + 100 MG", [
    ("RC240088", "Roche",                       date(2026, 6, 30),  60,  41),
]),

# ── GLAUCOMA ─────────────────────────────────────────────────────────
("Maleato De Timolol", "2,5 MG/ML", [
    ("MK240744", "Merck Sharp & Dohme",         date(2026, 9, 30),  30,  22),
]),
("Maleato De Timolol", "5 MG/ML", [
    ("MK240788", "Merck Sharp & Dohme",         date(2026, 9, 30),  30,  19),
]),

# ── RINITE ───────────────────────────────────────────────────────────
("Budesonida", "32 MCG", [
    ("AZ240655", "Astrazeneca Do Brasil Ltda",  date(2026, 8, 31),  60,  43),
]),
("Budesonida", "50 MCG", [
    ("AZ240699", "Astrazeneca Do Brasil Ltda",  date(2026, 8, 31),  60,  37),
]),

# ── DIABETES + DCV ───────────────────────────────────────────────────
("Dapagliflozina", "10 MG", [
    ("AZ240901", "Astrazeneca Do Brasil Ltda",  date(2026, 11, 30), 150, 112),
]),
]
async def seed_initial_data():
    async with SessionLocal() as db:
        try:
            farmaceut = (await db.execute(
                select(Usuario).where(Usuario.login == "farmaceut")
            )).scalar_one_or_none()

            registrado_por = farmaceut.id if farmaceut else None

            for (nome_gen, concentracao, lotes) in LOTES:
                med = (await db.execute(
                    select(Medicamento).where(
                        Medicamento.nome_generico == nome_gen,
                        Medicamento.concentracao  == concentracao,
                    )
                )).scalar_one_or_none()

                if not med:
                    print(f"    [skip] Medicamento não encontrado: {nome_gen} {concentracao}")
                    continue

                for (numero, fabricante, validade, qtd_inicial, qtd_atual) in lotes:
                    existe = (await db.execute(
                        select(Lote).where(
                            Lote.medicamento_id == med.id,
                            Lote.numero_lote    == numero,
                        )
                    )).scalar_one_or_none()

                    if existe:
                        print(f"    [skip] Lote {numero}")
                        continue
                    lote = Lote(
                        medicamento_id    = med.id,
                        registrado_por = registrado_por,
                        numero_lote       = numero,
                        fabricante        = fabricante,
                        validade          = validade,
                        quantidade_inicial = qtd_inicial,
                        quantidade_atual  = qtd_atual,
                    )
                    db.add(lote)
                    status = "Crítico" if qtd_atual <= med.estoque_minimo else "Normal"
                    venc   = "Vencido" if validade < date.today() else str(validade)
                    print(f"    [+] {numero} | {nome_gen[:30]:<30} {concentracao:<18} val={venc} saldo={qtd_atual} {status}")

                await db.commit()

        except Exception as e:
            print("Houve um erro ao fazer a migração: ", e)
            await db.rollback()

if __name__ == "__main__":
    print("Iniciando o seed do banco de dados...")
    asyncio.run(seed_initial_data())
    print("Processo finalizado.")