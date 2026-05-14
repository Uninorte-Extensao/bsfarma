import asyncio
from sqlalchemy import select
from app.usuario.model import Paciente, PerfilPaciente
from app.movimentacao.model import Movimentacao, TipoMovimentacao
from app.lote.model import Lote
from app.medicamentos.model import Medicamento
from app.db.base import SessionLocal
from app.core.security import hash_password

PACIENTES = [
    {"nome": "Gestor Teste",        "login": "gestor",     "senha": "gestor123",     "perfil": PerfilPaciente.GESTOR},
    {"nome": "Farmacêutico Teste",  "login": "farmaceut",  "senha": "farmaceut123",  "perfil": PerfilPaciente.FARMACEUTICO},
    {"nome": "Atendente Teste",  "login": "atendente",  "senha": "atendente123",  "perfil": PerfilPaciente.ATENDENTE},
]

async def seed_initial_data():
    async with SessionLocal() as db:
        try:
            for d in PACIENTES:
                existe = (await db.execute(select(Paciente).where(Paciente.login == d["login"]))).scalar_one_or_none()
                if existe:
                    print(f"    [skip] {d['login']}")
                    continue
                db.add(Paciente(nome=d["nome"], login=d["login"], senha_hash=hash_password(d["senha"]), perfil=d["perfil"], ativo=True))
                print(f"    [+] {d['login']} ({d['perfil'].value})")
                await db.commit()
        except Exception as e:
            print("Houve um erro ao fazer a migração: ", e)
            await db.rollback()

if __name__ == "__main__":
    print("Iniciando o seed do banco de dados...")
    asyncio.run(seed_initial_data())
    print("Processo finalizado.")