import hmac
import hashlib
import os
import asyncio
from sqlalchemy import select
# IMPORTAÇÃO VITAL: carrega todos os models antes de qualquer uso do ORM.
# Sem isso, relationship() com strings (ex.: back_populates="Dispensacao")
# falha com "expression 'X' failed to locate a name" quando este seeder
# roda sozinho (python -m app.<modulo>.seeder), porque nem todo model do
# projeto chega a ser importado — só os que este arquivo referencia direto.
import app.db.models
from app.paciente.model import Paciente
from app.db.base import SessionLocal

PACIENTES = [
        # ── Hipertensão arterial sistêmica ───────────────────────────────────
        {"cpf": "111.222.333-41", "condicao_clinica": "Hipertensão arterial sistêmica (I10)"},
        {"cpf": "222.333.444-52", "condicao_clinica": "Hipertensão arterial sistêmica (I10)"},
        {"cpf": "333.444.555-63", "condicao_clinica": "Hipertensão arterial sistêmica (I10)"},
        {"cpf": "444.555.666-74", "condicao_clinica": "Hipertensão arterial sistêmica (I10)"},
        {"cpf": "555.666.777-85", "condicao_clinica": "Hipertensão arterial sistêmica (I10)"},
        {"cpf": "666.777.888-96", "condicao_clinica": "Hipertensão arterial sistêmica (I10)"},
        {"cpf": "777.888.999-07", "condicao_clinica": "Hipertensão arterial sistêmica (I10)"},

        # ── Diabetes mellitus tipo 2 ─────────────────────────────────────────
        {"cpf": "888.999.000-18", "condicao_clinica": "Diabetes mellitus tipo 2 (E11)"},
        {"cpf": "999.000.111-29", "condicao_clinica": "Diabetes mellitus tipo 2 (E11)"},
        {"cpf": "100.200.300-41", "condicao_clinica": "Diabetes mellitus tipo 2 (E11)"},
        {"cpf": "200.300.400-52", "condicao_clinica": "Diabetes mellitus tipo 2 (E11)"},
        {"cpf": "300.400.500-63", "condicao_clinica": "Diabetes mellitus tipo 2 (E11)"},

        # ── Diabetes mellitus tipo 1 (insulinodependente) ────────────────────
        {"cpf": "400.500.600-74", "condicao_clinica": "Diabetes mellitus tipo 1 (E10)"},
        {"cpf": "500.600.700-85", "condicao_clinica": "Diabetes mellitus tipo 1 (E10)"},

        # ── Dislipidemia ─────────────────────────────────────────────────────
        {"cpf": "600.700.800-96", "condicao_clinica": "Dislipidemia mista (E78.2)"},
        {"cpf": "700.800.900-07", "condicao_clinica": "Hipercolesterolemia pura (E78.0)"},
        {"cpf": "800.900.100-18", "condicao_clinica": "Dislipidemia mista (E78.2)"},

        # ── Asma ─────────────────────────────────────────────────────────────
        {"cpf": "900.100.200-29", "condicao_clinica": "Asma moderada persistente (J45.1)"},
        {"cpf": "110.220.330-41", "condicao_clinica": "Asma leve persistente (J45.0)"},
        {"cpf": "220.330.440-52", "condicao_clinica": "Asma grave persistente (J45.8)"},

        # ── Rinite alérgica ──────────────────────────────────────────────────
        {"cpf": "330.440.550-63", "condicao_clinica": "Rinite alérgica (J30.1)"},
        {"cpf": "440.550.660-74", "condicao_clinica": "Rinite alérgica perene (J30.3)"},

        # ── Comorbidades associadas (HAS + DM) ───────────────────────────────
        {"cpf": "550.660.770-85", "condicao_clinica": "Hipertensão arterial sistêmica (I10) + Diabetes mellitus tipo 2 (E11)"},
        {"cpf": "660.770.880-96", "condicao_clinica": "Hipertensão arterial sistêmica (I10) + Diabetes mellitus tipo 2 (E11)"},
        {"cpf": "770.880.990-07", "condicao_clinica": "Hipertensão arterial sistêmica (I10) + Diabetes mellitus tipo 2 (E11)"},

        # ── HAS + Dislipidemia ───────────────────────────────────────────────
        {"cpf": "880.990.100-18", "condicao_clinica": "Hipertensão arterial sistêmica (I10) + Hipercolesterolemia (E78.0)"},
        {"cpf": "990.100.200-29", "condicao_clinica": "Hipertensão arterial sistêmica (I10) + Dislipidemia mista (E78.2)"},

        # ── DM + Doença cardiovascular (Dapagliflozina) ──────────────────────
        {"cpf": "121.232.343-41", "condicao_clinica": "Diabetes mellitus tipo 2 (E11) + Doença cardiovascular aterosclerótica (I25)"},
        {"cpf": "232.343.454-52", "condicao_clinica": "Diabetes mellitus tipo 2 (E11) + Insuficiência cardíaca (I50)"},

        # ── Osteoporose ──────────────────────────────────────────────────────
        {"cpf": "343.454.565-63", "condicao_clinica": "Osteoporose pós-menopáusica (M81.0)"},
        {"cpf": "454.565.676-74", "condicao_clinica": "Osteoporose senil (M81.1)"},

        # ── Glaucoma ─────────────────────────────────────────────────────────
        {"cpf": "565.676.787-85", "condicao_clinica": "Glaucoma primário de ângulo aberto (H40.1)"},
        {"cpf": "676.787.898-96", "condicao_clinica": "Glaucoma primário de ângulo aberto (H40.1)"},

        # ── Doença de Parkinson ───────────────────────────────────────────────
        {"cpf": "787.898.909-07", "condicao_clinica": "Doença de Parkinson (G20)"},
        {"cpf": "898.909.010-18", "condicao_clinica": "Doença de Parkinson (G20)"},

        # ── Planejamento familiar / Anticoncepção ────────────────────────────
        {"cpf": "909.010.121-29", "condicao_clinica": "Planejamento familiar — anticoncepção hormonal (Z30.0)"},
        {"cpf": "010.121.232-41", "condicao_clinica": "Planejamento familiar — anticoncepção hormonal (Z30.0)"},
        {"cpf": "121.232.343-52", "condicao_clinica": "Planejamento familiar — anticoncepção hormonal injetável (Z30.0)"},
    ]


def gerar_codigo(cpf: str, salt: str) -> str:
    """
    Gera o código pseudonimizado a partir do CPF e do salt institucional.

    Args:
        cpf:  CPF do paciente (com ou sem pontuação — normalizado internamente).
        salt: Chave secreta da UBS (ID_INTERNO_SALT).

    Returns:
        String de 12 caracteres hexadecimais maiúsculos.
        Exemplo: "A3F9D2C18B4E"
    """
    cpf_limpo = ''.join(c for c in cpf if c.isdigit())
    mac = hmac.new(
        salt.encode("utf-8"),
        cpf_limpo.encode("utf-8"),
        hashlib.sha256,
    )
    return mac.hexdigest()[:12].upper()

async def seed_initial_data():
    async with SessionLocal() as db:
        try:
            salt = os.environ.get("ID_INTERNO_SALT", "")

            if not salt:
                # Em desenvolvimento sem o salt configurado, usa um salt padrão
                # com aviso explícito — nunca use em produção.
                salt = "salt-de-desenvolvimento-nao-usar-em-producao"
                print("    [AVISO] ID_INTERNO_SALT não configurado.")
                print("            Usando salt padrão de desenvolvimento.")
                print("            Configure a variável de ambiente antes do deploy.\n")

            criados   = 0
            ignorados = 0

            for dados in PACIENTES:
                codigo = gerar_codigo(dados["cpf"], salt)

                existe = (await db.execute(
                    select(Paciente).where(Paciente.codigo == codigo)
                )).scalar_one_or_none()

                if existe:
                    ignorados += 1
                    continue

                db.add(Paciente(
                    codigo           = codigo,
                    condicao_clinica = dados["condicao_clinica"],
                    ativo            = True,
                ))
                criados += 1
                print(f"    [+] {codigo}  {dados['condicao_clinica'][:55]}")

            await db.flush()
            print(f"\n    Pacientes criados: {criados} | Ignorados (já existiam): {ignorados}")
            if criados > 0:
                print("    Códigos gerados com HMAC-SHA256. CPFs não armazenados.")
            await db.commit()
        except Exception as e:
            print("Houve um erro ao fazer a migração: ", e)
            await db.rollback()

if __name__ == "__main__":
    print("Iniciando o seed do banco de dados...")
    asyncio.run(seed_initial_data())
    print("Processo finalizado.")