import asyncio
from sqlalchemy import select
from app.usuario.model import Usuario
from app.db.base import SessionLocal
from app.core.security import hash_password

async def seed_initial_data():
    async with SessionLocal() as db:
        try:
            result = await db.execute(select(Usuario))
            usuario_existente = result.scalars().first()
            
            # Admin padrão
            if not usuario_existente:
                user = Usuario(
                    nome="admin",
                    login="admin",
                    senha_hash=hash_password("admin123"),
                    perfil="gestor",
                    ativo=True,
                )
                db.add(user)
                await db.commit()
                print("Admin criado: admin / admin123")
            else:
                print("O usuário admin já existe no banco.")

        except Exception as e:
            print("Houve um erro ao fazer a migração: ", e)
            await db.rollback()

if __name__ == "__main__":
    print("Iniciando o seed do banco de dados...")
    asyncio.run(seed_initial_data())
    print("Processo finalizado.")