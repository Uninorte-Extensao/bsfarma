import asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import Asyncdb

from app.db.base import SessionLocal
from app.medicamentos.model import Medicamento

MEDICAMENTOS = [
        # ── ASMA ────────────────────────────────────────────────────────────
        {
            "nome_generico": "Brometo De Ipratrópio", "nome_comercial": "Atrovent",
            "concentracao": "0,25 MG/ML", "forma_farmaceutica": "Solução para inalação",
            "via_administracao": "Inalatória", "fabricante": "Boehringer Ingelheim Do Brasil",
            "classe_terapeutica": "R3A - Anticolinérgicos", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Asma", "estoque_minimo": 20,
        },
        {
            "nome_generico": "Dipropionato De Beclometasona", "nome_comercial": "Clenil",
            "concentracao": "50 MCG", "forma_farmaceutica": "Aerossol para inalação",
            "via_administracao": "Inalatória", "fabricante": "Chiesi Farmaceutici",
            "classe_terapeutica": "R3B - Glicocorticóides Inalatórios", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Asma", "estoque_minimo": 20,
        },
        {
            "nome_generico": "Dipropionato De Beclometasona", "nome_comercial": "Clenil",
            "concentracao": "200 MCG", "forma_farmaceutica": "Aerossol para inalação",
            "via_administracao": "Inalatória", "fabricante": "Chiesi Farmaceutici",
            "classe_terapeutica": "R3B - Glicocorticóides Inalatórios", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Asma", "estoque_minimo": 20,
        },
        {
            "nome_generico": "Sulfato De Salbutamol", "nome_comercial": "Aerolin",
            "concentracao": "100 MCG", "forma_farmaceutica": "Aerossol para inalação",
            "via_administracao": "Inalatória", "fabricante": "Glaxosmithkline Brasil Ltda",
            "classe_terapeutica": "R3A - Broncodilatadores Beta-2", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Asma", "estoque_minimo": 30,
        },
        {
            "nome_generico": "Sulfato De Salbutamol", "nome_comercial": "Aerolin",
            "concentracao": "5 MG/ML", "forma_farmaceutica": "Solução para inalação",
            "via_administracao": "Inalatória", "fabricante": "Glaxosmithkline Brasil Ltda",
            "classe_terapeutica": "R3A - Broncodilatadores Beta-2", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Asma", "estoque_minimo": 20,
        },

        # ── DIABETES ─────────────────────────────────────────────────────────
        {
            "nome_generico": "Cloridrato De Metformina", "nome_comercial": "Glifage",
            "concentracao": "500 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Merck S.A.",
            "classe_terapeutica": "A10K - Biguanidas", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Diabetes", "estoque_minimo": 200,
        },
        {
            "nome_generico": "Cloridrato De Metformina", "nome_comercial": "Glifage XR",
            "concentracao": "500 MG", "forma_farmaceutica": "Comprimido de liberação prolongada",
            "via_administracao": "Oral", "fabricante": "Merck S.A.",
            "classe_terapeutica": "A10K - Biguanidas", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Diabetes", "estoque_minimo": 150,
        },
        {
            "nome_generico": "Cloridrato De Metformina", "nome_comercial": "Glifage",
            "concentracao": "850 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Merck S.A.",
            "classe_terapeutica": "A10K - Biguanidas", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Diabetes", "estoque_minimo": 200,
        },
        {
            "nome_generico": "Glibenclamida", "nome_comercial": "Daonil",
            "concentracao": "5 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Sanofi-Aventis Farmacêutica Ltda",
            "classe_terapeutica": "A10J - Sulfonilureias", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Diabetes", "estoque_minimo": 150,
        },
        {
            "nome_generico": "Insulina Humana", "nome_comercial": "Humulin R",
            "concentracao": "100 UI/ML", "forma_farmaceutica": "Solução injetável",
            "via_administracao": "Parenteral", "fabricante": "Eli Lilly Do Brasil Ltda",
            "classe_terapeutica": "A10A - Insulinas", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Diabetes", "estoque_minimo": 30,
        },
        {
            "nome_generico": "Insulina Humana", "nome_comercial": "Humulin N",
            "concentracao": "100 UI/ML", "forma_farmaceutica": "Suspensão injetável",
            "via_administracao": "Parenteral", "fabricante": "Eli Lilly Do Brasil Ltda",
            "classe_terapeutica": "A10A - Insulinas", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Diabetes", "estoque_minimo": 30,
        },

        # ── HIPERTENSÃO ──────────────────────────────────────────────────────
        {
            "nome_generico": "Atenolol", "nome_comercial": "Atenolol",
            "concentracao": "25 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Eurofarma Laboratorios S.A.",
            "classe_terapeutica": "C1D - Betabloqueadores", "tipo_produto": "Genérico",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Hipertensão", "estoque_minimo": 200,
        },
        {
            "nome_generico": "Besilato De Anlodipino", "nome_comercial": "Norvasc",
            "concentracao": "5 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Pfizer Brasil Ltda",
            "classe_terapeutica": "C1B - Antagonistas Do Cálcio", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Hipertensão", "estoque_minimo": 200,
        },
        {
            "nome_generico": "Captopril", "nome_comercial": "Capoten",
            "concentracao": "25 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Bristol-Myers Squibb",
            "classe_terapeutica": "C1E - Inibidores Da Eca", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Hipertensão", "estoque_minimo": 200,
        },
        {
            "nome_generico": "Cloridrato De Propranolol", "nome_comercial": "Propranolol",
            "concentracao": "40 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Eurofarma Laboratorios S.A.",
            "classe_terapeutica": "C1D - Betabloqueadores", "tipo_produto": "Genérico",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Hipertensão", "estoque_minimo": 150,
        },
        {
            "nome_generico": "Hidroclorotiazida", "nome_comercial": "Hidroclorotiazida",
            "concentracao": "25 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Medquímica Indústria Farmacêutica",
            "classe_terapeutica": "C3A - Diuréticos Tiazídicos", "tipo_produto": "Genérico",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Hipertensão", "estoque_minimo": 200,
        },
        {
            "nome_generico": "Losartana Potássica", "nome_comercial": "Cozaar",
            "concentracao": "50 MG", "forma_farmaceutica": "Comprimido revestido",
            "via_administracao": "Oral", "fabricante": "Merck Sharp & Dohme",
            "classe_terapeutica": "C1F - Antagonistas Da Angiotensina Ii", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Hipertensão", "estoque_minimo": 200,
        },
        {
            "nome_generico": "Maleato De Enalapril", "nome_comercial": "Renitec",
            "concentracao": "10 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Merck Sharp & Dohme",
            "classe_terapeutica": "C1E - Inibidores Da Eca", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Hipertensão", "estoque_minimo": 150,
        },
        {
            "nome_generico": "Espironolactona", "nome_comercial": "Aldactone",
            "concentracao": "25 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Pfizer Brasil Ltda",
            "classe_terapeutica": "C3C - Diuréticos Poupadores De Potássio", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Hipertensão", "estoque_minimo": 100,
        },
        {
            "nome_generico": "Furosemida", "nome_comercial": "Lasix",
            "concentracao": "40 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Sanofi-Aventis Farmacêutica Ltda",
            "classe_terapeutica": "C3B - Diuréticos De Alça", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Hipertensão", "estoque_minimo": 150,
        },
        {
            "nome_generico": "Succinato De Metoprolol", "nome_comercial": "Seloken ZOK",
            "concentracao": "25 MG", "forma_farmaceutica": "Comprimido de liberação prolongada",
            "via_administracao": "Oral", "fabricante": "Astrazeneca Do Brasil Ltda",
            "classe_terapeutica": "C1D - Betabloqueadores", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Hipertensão", "estoque_minimo": 100,
        },

        # ── ANTICONCEPÇÃO ────────────────────────────────────────────────────
        {
            "nome_generico": "Acetato De Medroxiprogesterona", "nome_comercial": "Depo-Provera",
            "concentracao": "150 MG", "forma_farmaceutica": "Suspensão injetável",
            "via_administracao": "Parenteral", "fabricante": "Pfizer Brasil Ltda",
            "classe_terapeutica": "G3A - Progestágenos", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Anticoncepção", "estoque_minimo": 30,
        },
        {
            "nome_generico": "Levonorgestrel;Etinilestradiol", "nome_comercial": "Microvlar",
            "concentracao": "0,15 MG + 0,03 MG", "forma_farmaceutica": "Comprimido revestido",
            "via_administracao": "Oral", "fabricante": "Bayer S.A.",
            "classe_terapeutica": "G3B - Anticoncepcionais Orais Combinados", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Anticoncepção", "estoque_minimo": 50,
        },
        {
            "nome_generico": "Noretisterona", "nome_comercial": "Norestin",
            "concentracao": "0,35 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Libbs Farmacêutica Ltda",
            "classe_terapeutica": "G3A - Progestágenos", "tipo_produto": "Similar",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Anticoncepção", "estoque_minimo": 30,
        },
        {
            "nome_generico": "Enantato De Noretisterona;Valerato De Estradiol", "nome_comercial": "Mesigyna",
            "concentracao": "50 MG + 5 MG", "forma_farmaceutica": "Suspensão injetável",
            "via_administracao": "Parenteral", "fabricante": "Bayer S.A.",
            "classe_terapeutica": "G3B - Anticoncepcionais Injetáveis Combinados", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Anticoncepção", "estoque_minimo": 20,
        },

        # ── OSTEOPOROSE ──────────────────────────────────────────────────────
        {
            "nome_generico": "Alendronato De Sódio", "nome_comercial": "Fosamax",
            "concentracao": "70 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Merck Sharp & Dohme",
            "classe_terapeutica": "M5B - Bisfosfonatos", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Osteoporose", "estoque_minimo": 30,
        },

        # ── DISLIPIDEMIA ─────────────────────────────────────────────────────
        {
            "nome_generico": "Sinvastatina", "nome_comercial": "Zocor",
            "concentracao": "10 MG", "forma_farmaceutica": "Comprimido revestido",
            "via_administracao": "Oral", "fabricante": "Merck Sharp & Dohme",
            "classe_terapeutica": "C4A - Inibidores Da Hmg-Coa Redutase", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Dislipidemia", "estoque_minimo": 150,
        },
        {
            "nome_generico": "Sinvastatina", "nome_comercial": "Zocor",
            "concentracao": "20 MG", "forma_farmaceutica": "Comprimido revestido",
            "via_administracao": "Oral", "fabricante": "Merck Sharp & Dohme",
            "classe_terapeutica": "C4A - Inibidores Da Hmg-Coa Redutase", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Dislipidemia", "estoque_minimo": 150,
        },
        {
            "nome_generico": "Sinvastatina", "nome_comercial": "Zocor",
            "concentracao": "40 MG", "forma_farmaceutica": "Comprimido revestido",
            "via_administracao": "Oral", "fabricante": "Merck Sharp & Dohme",
            "classe_terapeutica": "C4A - Inibidores Da Hmg-Coa Redutase", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Dislipidemia", "estoque_minimo": 100,
        },

        # ── DOENÇA DE PARKINSON ──────────────────────────────────────────────
        {
            "nome_generico": "Carbidopa (Port. 344/98 Lista C 1);Levodopa", "nome_comercial": "Sinemet",
            "concentracao": "25 MG + 250 MG", "forma_farmaceutica": "Comprimido",
            "via_administracao": "Oral", "fabricante": "Merck Sharp & Dohme",
            "classe_terapeutica": "N4A - Dopaminérgicos", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Doença de Parkinson", "estoque_minimo": 15,
        },
        {
            "nome_generico": "Cloridrato De Benserazida;Levodopa", "nome_comercial": "Prolopa",
            "concentracao": "25 MG + 100 MG", "forma_farmaceutica": "Cápsula dura",
            "via_administracao": "Oral", "fabricante": "Roche",
            "classe_terapeutica": "N4A - Dopaminérgicos", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Doença de Parkinson", "estoque_minimo": 15,
        },

        # ── GLAUCOMA ─────────────────────────────────────────────────────────
        {
            "nome_generico": "Maleato De Timolol", "nome_comercial": "Timoptol",
            "concentracao": "2,5 MG/ML", "forma_farmaceutica": "Solução oftálmica",
            "via_administracao": "Oftálmica", "fabricante": "Merck Sharp & Dohme",
            "classe_terapeutica": "S1E - Betabloqueadores Oftálmicos", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Glaucoma", "estoque_minimo": 10,
        },
        {
            "nome_generico": "Maleato De Timolol", "nome_comercial": "Timoptol",
            "concentracao": "5 MG/ML", "forma_farmaceutica": "Solução oftálmica",
            "via_administracao": "Oftálmica", "fabricante": "Merck Sharp & Dohme",
            "classe_terapeutica": "S1E - Betabloqueadores Oftálmicos", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Glaucoma", "estoque_minimo": 10,
        },

        # ── RINITE ───────────────────────────────────────────────────────────
        {
            "nome_generico": "Budesonida", "nome_comercial": "Rhinocort",
            "concentracao": "32 MCG", "forma_farmaceutica": "Suspensão para inalação nasal",
            "via_administracao": "Inalatória", "fabricante": "Astrazeneca Do Brasil Ltda",
            "classe_terapeutica": "R1A - Corticosteróides Nasais", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Rinite", "estoque_minimo": 20,
        },
        {
            "nome_generico": "Budesonida", "nome_comercial": "Rhinocort",
            "concentracao": "50 MCG", "forma_farmaceutica": "Suspensão para inalação nasal",
            "via_administracao": "Inalatória", "fabricante": "Astrazeneca Do Brasil Ltda",
            "classe_terapeutica": "R1A - Corticosteróides Nasais", "tipo_produto": "Referência",
            "tarja": "- (*)", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Rinite", "estoque_minimo": 20,
        },

        # ── DIABETES + DOENÇA CARDIOVASCULAR ────────────────────────────────
        {
            "nome_generico": "Dapagliflozina", "nome_comercial": "Forxiga",
            "concentracao": "10 MG", "forma_farmaceutica": "Comprimido revestido",
            "via_administracao": "Oral", "fabricante": "Astrazeneca Do Brasil Ltda",
            "classe_terapeutica": "A10N - Inibidores De Sglt-2", "tipo_produto": "Referência",
            "tarja": "Tarja Vermelha", "restricao_hospitalar": False,
            "indicacao_farmacia_popular": "Diabetes + Doença Cardiovascular", "estoque_minimo": 50,
        },
    ]

async def seed_initial_data():
    async with SessionLocal() as db:
        try:
            for d in MEDICAMENTOS:
                existe = (await db.execute(
                    select(Medicamento).where(
                        Medicamento.nome_generico == d["nome_generico"],
                        Medicamento.concentracao  == d["concentracao"],
                    )
                )).scalar_one_or_none()

                if existe:
                    print(f"    [skip] {d['nome_generico']} {d['concentracao']}")
                    continue

                db.add(Medicamento(**d, ativo=True))
                await db.commit()
                print(f"    [+] {d['nome_generico']} {d['concentracao']}")
        except Exception as e:
            print("Houve um erro ao fazer a migração: ", e)
            await db.rollback()

if __name__ == "__main__":
    print("Iniciando o seed do banco de dados...")
    asyncio.run(seed_initial_data())
    print("Processo finalizado.")