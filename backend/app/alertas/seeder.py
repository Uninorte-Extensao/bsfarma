import asyncio
from datetime import date, timedelta
from sqlalchemy import select

# IMPORTAÇÃO VITAL: Carrega todos os modelos na memória
import app.db.models 

from app.db.base import SessionLocal
from app.medicamentos.model import Medicamento
from app.lote.model import Lote
from app.alertas.service import AlertaService

async def seed_e_testar_alertas():
    async with SessionLocal() as db:
        try:
            hoje = date.today()
            
            # --- 1. CRIAR MEDICAMENTO BASE ---
            # Buscando agora pelo nome_generico em vez de 'nome'
            med = (await db.execute(
                select(Medicamento).where(Medicamento.nome_generico == "Ibuprofeno")
            )).scalar_one_or_none()
            
            if not med:
                # Criando o medicamento com todos os campos obrigatórios do novo Model
                med = Medicamento(
                    nome_generico="Ibuprofeno",
                    nome_comercial="Alivium Teste",  # Opcional, mas útil para testes
                    forma_farmaceutica="Comprimido", # Obrigatório
                    concentracao="400mg",            # Obrigatório
                    via_administracao="Oral",        # Obrigatório
                    classe_terapeutica="Anti-inflamatório",
                    tarja="Amarela",
                    estoque_minimo=10,               # Importante para a regra do Alerta Crítico
                    ativo=True
                )
                db.add(med)
                await db.flush() # Sincroniza para gerar o ID do medicamento

            # --- 2. CRIAR LOTES PARA CADA CENÁRIO ---
            cenarios = [
                {"num": "LOTE-30D", "val": hoje + timedelta(days=29), "atual": 50, "ini": 100},
                {"num": "LOTE-15D", "val": hoje + timedelta(days=14), "atual": 50, "ini": 100},
                {"num": "LOTE-07D", "val": hoje + timedelta(days=6),  "atual": 50, "ini": 100},
                {"num": "LOTE-CRIT-ABS", "val": hoje + timedelta(days=300), "atual": 8, "ini": 100}, # Menor que estoque_minimo (10)
                {"num": "LOTE-CRIT-REL", "val": hoje + timedelta(days=300), "atual": 9, "ini": 100}, # Menor que 10% do inicial
                {"num": "LOTE-VENCIDO", "val": hoje - timedelta(days=2), "atual": 50, "ini": 100},
            ]

            for c in cenarios:
                lote_existe = (await db.execute(
                    select(Lote).where(Lote.numero_lote == c["num"])
                )).scalar_one_or_none()
                
                if not lote_existe:
                    db.add(Lote(
                        numero_lote=c["num"], 
                        medicamento_id=med.id,
                        validade=c["val"], 
                        quantidade_atual=c["atual"], 
                        quantidade_inicial=c["ini"]
                    ))
            
            await db.commit()
            print("[+] Medicamento e Lotes de teste inseridos com sucesso.")

            # --- 3. EXECUTAR O SERVIÇO DE ALERTAS ---
            print("\nRodando a verificação de alertas...")
            service = AlertaService(db)
            resultado = await service.verificar_todos()
            await db.commit() # Efetiva os alertas gerados no banco!
            
            print(f"Resultado da Verificação: {resultado}")

        except Exception as e:
            print("Erro ao popular alertas:", e)
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_e_testar_alertas())