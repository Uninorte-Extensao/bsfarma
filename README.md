# BSFarma

Sistema de controle de estoque farmacêutico da **UBS Saúde Sempre**. Projeto
de extensão da Uninorte.

Este repositório reúne o backend (`julysantos/bsfarma`) e o frontend
(`AlessaSousa/bsfarma`), cujos repositórios originais estão arquivados. O
histórico dos dois foi preservado. O [`.mailmap`](.mailmap) unifica as
identidades de autoria no `git log` e no `git blame`. O site do GitHub ignora
esse arquivo.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Angular 20, PrimeNG 20, Chart.js |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Alembic, JWT |
| Banco | PostgreSQL (Supabase em produção) |
| Produção | Nginx (estáticos + proxy da API), Caddy (HTTPS) |
| Testes e CI | pytest, GitHub Actions |

## Estrutura

```
.
├── backend/                 API FastAPI          → backend/README.md
├── frontend/                SPA Angular          → frontend/README.md
├── deploy/                  publicação com HTTPS → deploy/DEPLOY.md
├── .github/workflows/       CI                   → .github/workflows/README.md
├── docker-compose.yml       stack de desenvolvimento
└── docker-compose.prod.yml  stack de produção
```

## Desenvolvimento

Com Docker, o compose sobe frontend, API e PostgreSQL com hot-reload:

```bash
cp backend/.env.example backend/.env
```

```bash
docker compose up --build
```

```bash
docker compose exec api alembic upgrade head
```

```bash
docker compose exec api python -m app.seed
```

| Serviço | Endereço |
|---|---|
| Frontend | http://localhost:4200 |
| API e documentação | http://localhost:8000/docs |
| PostgreSQL | `localhost:5432` (usuário e senha `postgres`) |

No `backend/.env`, só a `SECRET_KEY` é necessária, porque o compose aponta o
`DATABASE_URL` para o PostgreSQL local. Para derrubar tudo, incluindo o banco,
use `docker compose down -v`.

Sem Docker, siga o [`backend/README.md`](backend/README.md) e o
[`frontend/README.md`](frontend/README.md).

## Produção

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

```
navegador ──▶ Nginx (:80) ──┬──▶ /        Angular compilado
                            └──▶ /api/    API (rede interna) ──▶ Supabase
```

Frontend e API ficam na mesma origem, então não há CORS. A API não publica
porta no host. Para publicar na internet com domínio e HTTPS, siga o
[`deploy/DEPLOY.md`](deploy/DEPLOY.md). O que falta antes de receber usuários
reais está em [`deploy/PRE-PUBLICACAO.md`](deploy/PRE-PUBLICACAO.md).

## Variáveis de ambiente

As variáveis ficam em `backend/.env`; o modelo é o
[`backend/.env.example`](backend/.env.example). O `.env` nunca é versionado.

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...`. No Supabase, use o **Session pooler** (porta 5432); o modo Transaction não funciona com asyncpg |
| `SECRET_KEY` | Assinatura dos JWT. Use uma diferente por ambiente (`openssl rand -hex 32`) |
| `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT: o padrão é `HS256` e 60 minutos |
| `ENVIRONMENT` | `development` ou `production` |
| `CORS_ORIGINS` | Origens liberadas, separadas por vírgula. O padrão `http://localhost:4200` atende o `ng serve`. Em produção com o Nginx, deixe vazio. Nunca use `*`, porque a API aceita credenciais |
| `ID_INTERNO_SALT` | Chave do código pseudonimizado do paciente. Obrigatória em produção, e **não pode mudar** depois que houver pacientes cadastrados |
| `SEED_SENHA_GESTOR`, `SEED_SENHA_FARMACEUTICO`, `SEED_SENHA_ATENDENTE` | Senhas dos usuários da carga de demonstração. Se ficarem vazias, são geradas |

## Migrations

```bash
alembic upgrade head
```

Em banco novo, esse comando cria todo o schema: o baseline `c2cf2197c6b3` e,
em seguida, `a575246ce0ba`, que é o head. Para criar uma migration:

```bash
alembic revision --autogenerate -m "descrição"
```

Revise o arquivo gerado antes de aplicar. O autogenerate trata renomeações como
drop + create e não remove os tipos ENUM no downgrade.

Quando o banco já tem as tabelas mas não tem `alembic_version`, porque foram
criadas fora do Alembic, o `upgrade` falha com `DuplicateTableError`. Nesse
caso, registre o estado atual sem executar DDL e depois confira:

```bash
alembic stamp a575246ce0ba
```

Use essa revisão se a tabela `dispensacao` existir. Se não existir, use
`alembic stamp c2cf2197c6b3` e depois `alembic upgrade head`.

```bash
alembic check
```

O `alembic check` é obrigatório depois do `stamp`, porque o `stamp` não compara
colunas. Se ele acusar diferença, gere uma migration ou, em desenvolvimento,
recrie o banco. O Supabase de produção foi conferido em 2026-10-23 e está em
dia.

## Testes

```bash
cd backend && poetry run pytest
```

Os testes usam SQLite em memória e não precisam do Supabase. O CI roda os
testes, as migrations e o build do frontend em todo PR contra a `main` e em
todo push de branch. Veja o [`.github/workflows/README.md`](.github/workflows/README.md).

## Carga de demonstração

`python -m app.seed` popula um banco vazio com dados fictícios e realistas:

- 3 usuários, um por perfil;
- 25 medicamentos e 174 pacientes;
- cerca de 140 lotes, alguns vencendo em até 30 dias;
- 12 meses de dispensações, perdas e ajustes.

As datas são relativas ao dia da execução.

- **Banco com dados:** o comando não faz nada.
- **`--recriar`:** apaga tudo e gera de novo.
- **`--permitir-producao`:** necessário com `ENVIRONMENT=production`.

Detalhes em [`backend/app/seed/README.md`](backend/app/seed/README.md).

## Alertas automáticos

Todo dia às 00:30 (America/Manaus), a própria API roda a verificação de
alertas: vencimento em 30, 15 e 7 dias, estoque crítico e expiração de alertas
de lotes vencidos. Ela é iniciada pelo `lifespan` em
[`main.py`](backend/app/main.py), com o job em
[`scheduler.py`](backend/app/alertas/scheduler.py).

Farmacêutico e gestor podem disparar a mesma verificação na hora, por
`POST /alertas/verificar`. Se a API estiver fora do ar às 00:30 e voltar em até
1 hora, o job ainda roda.

O fuso da UBS (`America/Manaus`) fica em
[`app/core/fuso.py`](backend/app/core/fuso.py). Ele vale para o job e para todo
"hoje" da API: validade na dispensação, alertas, períodos padrão e limites de
dia dos relatórios. Assim, às 21h de Manaus o sistema ainda está no mesmo dia,
mesmo com o servidor em UTC. Com vários processos da API, cada um roda o seu
scheduler. A verificação não duplica alertas.

## Perfis de acesso

| Perfil | Permissões |
|---|---|
| `atendente` | Registrar dispensações e consultar estoque |
| `farmaceutico` | O mesmo do atendente, mais gerenciar lotes e alertas |
| `gestor` | Acesso total, incluindo usuários e relatórios |

## Contribuindo

Para criar um módulo novo no backend, siga o padrão model → schema → repository
→ service → router, descrito no [`backend/README.md`](backend/README.md).
