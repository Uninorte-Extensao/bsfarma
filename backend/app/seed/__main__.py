import argparse
import asyncio
import os
import secrets
import sys

import app.db.models  # noqa: F401
from app.core.config import settings
from app.core.fuso import hoje_ubs
from app.db.base import SessionLocal
from app.paciente.service import gerar_codigo
from app.seed.carga import banco_vazio, carregar, limpar
from app.seed.catalogo import USUARIOS
from app.seed.simulacao import CargaDemo, gerar_carga


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m app.seed",
        description="Popula o banco com a carga de demonstração do BSFarma.",
    )
    parser.add_argument(
        "--recriar",
        action="store_true",
        help="apaga TODOS os dados das tabelas do sistema antes de popular",
    )
    parser.add_argument(
        "--permitir-producao",
        action="store_true",
        help="autoriza rodar com ENVIRONMENT=production (use só no banco de demonstração)",
    )
    return parser.parse_args(argv)


def _senhas() -> tuple[dict[str, str], list[str]]:
    senhas, geradas = {}, []
    for u in USUARIOS:
        valor = os.environ.get(u.variavel_senha, "").strip()
        if not valor:
            valor = secrets.token_urlsafe(9)
            geradas.append(u.login)
        senhas[u.login] = valor
    return senhas, geradas


def _relatorio(carga: CargaDemo, alertas: dict, senhas: dict[str, str], geradas: list[str]) -> None:
    print("\nCarga de demonstração concluída.\n")
    print(f"  usuários .......... {len(carga.usuarios)}")
    print(f"  medicamentos ...... {len(carga.medicamentos)}")
    print(f"  pacientes ......... {len(carga.pacientes)}")
    print(f"  lotes ............. {len(carga.lotes)}")
    print(f"  movimentações ..... {len(carga.movimentacoes)}")
    print(f"  dispensações ...... {len(carga.dispensacoes)}")
    print(f"  alertas criados ... {alertas['alertas_criados']}")

    nomes = {m["id"]: f"{m['nome_generico']} {m['concentracao']}" for m in carga.medicamentos}
    proximos = sorted(
        (l for l in carga.lotes if l["quantidade_atual"] > 0 and 0 <= (l["validade"] - carga.hoje).days <= 30),
        key=lambda l: l["validade"],
    )
    if proximos:
        print("\nLotes vencendo em até 30 dias:")
        for l in proximos:
            print(f"  {l['numero_lote']:<12} {nomes[l['medicamento_id']][:45]:<45} "
                  f"vence {l['validade']:%d/%m/%Y}  saldo {l['quantidade_atual']}")

    print("\nCódigos de pacientes para testar uma dispensação:")
    for codigo, condicao in carga.pacientes_exemplo[:5]:
        print(f"  {codigo}  {condicao}")

    print("\nAcesso:")
    for u in USUARIOS:
        if u.login in geradas:
            print(f"  {u.login:<10} senha gerada: {senhas[u.login]}")
        else:
            print(f"  {u.login:<10} senha definida em {u.variavel_senha}")
    if geradas:
        print("\n  As senhas geradas não ficam salvas em lugar nenhum. Anote-as agora.")


async def _executar(args: argparse.Namespace) -> int:
    hoje = hoje_ubs()
    async with SessionLocal() as session:
        if not await banco_vazio(session):
            if not args.recriar:
                print("O banco já tem dados. Nada foi alterado.")
                print("Para apagar tudo e gerar a carga de novo, use --recriar.")
                return 0
            print("Apagando os dados existentes...")
            await limpar(session)

        senhas, geradas = _senhas()
        carga = gerar_carga(hoje, gerar_codigo)
        try:
            alertas = await carregar(session, carga, senhas)
            await session.commit()
        except Exception:
            await session.rollback()
            raise

    _relatorio(carga, alertas, senhas, geradas)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _argumentos(argv)
    if settings.is_production and not args.permitir_producao:
        print("ENVIRONMENT=production: a carga de demonstração não roda em produção.", file=sys.stderr)
        print("Se este for o banco de demonstração, repita com --permitir-producao.", file=sys.stderr)
        return 2
    return asyncio.run(_executar(args))


if __name__ == "__main__":
    sys.exit(main())
