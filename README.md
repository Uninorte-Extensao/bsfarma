# BSFarma

Sistema de controle de estoque farmacêutico da **UBS Saúde Sempre**.

Projeto de extensão — Uninorte.

---

## Sobre este repositório

Este é o repositório **único e oficial** do BSFarma. Ele reúne o backend e o
frontend, que antes viviam em dois repositórios separados:

| Origem | Conteúdo | Situação |
|---|---|---|
| `julysantos/bsfarma` | API FastAPI | Legado — arquivado, sem novas atualizações |
| `AlessaSousa/bsfarma` | SPA Angular | Legado — arquivado, sem novas atualizações |

O histórico completo dos dois repositórios foi preservado e reescrito para os
diretórios `backend/` e `frontend/`, de modo que `git log` e `git blame`
continuam funcionando normalmente em todo o código.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Angular 20 + PrimeNG 20 + Chart.js |
| Backend | FastAPI + Uvicorn |
| Banco de dados | PostgreSQL (Supabase em produção) |
| ORM / Migrations | SQLAlchemy 2.0 (async) + Alembic |
| Autenticação | JWT (python-jose + passlib/bcrypt) |
| Servidor de produção | Nginx (arquivos estáticos + proxy reverso) |
| Testes | pytest + pytest-asyncio + httpx |

---

## Estrutura

```
.
├── backend/                  ← API FastAPI  (README próprio em backend/README.md)
│   ├── app/                  ← código da aplicação, um diretório por domínio
│   ├── alembic/              ← migrations
│   ├── tests/                ← testes unitários e de integração
│   ├── Dockerfile
│   └── docker-compose.yml    ← sobe só a API, para quem mexe apenas no backend
├── frontend/                 ← SPA Angular (README próprio em frontend/README.md)
│   ├── src/
│   ├── public/
│   ├── Dockerfile            ← multi-stage: deps → dev → build → production
│   └── nginx.conf            ← configuração do Nginx de produção
├── docker-compose.yml        ← stack completa em DESENVOLVIMENTO
└── docker-compose.prod.yml   ← stack completa em PRODUÇÃO
```

---

## Rodando em desenvolvimento

### Opção A — Docker (recomendado)

Sobe frontend, API e PostgreSQL de uma vez, com hot-reload nos dois lados.

**Pré-requisitos:** Docker Desktop (ou Docker Engine + Compose v2).

```bash
cp backend/.env.example backend/.env
```

Preencha o `backend/.env` — no mínimo a `SECRET_KEY`. O `DATABASE_URL` é
sobrescrito pelo compose para apontar ao PostgreSQL do próprio ambiente, então
em desenvolvimento você não precisa de credenciais do Supabase.

```bash
docker compose up --build
```

| Serviço | Endereço |
|---|---|
| Frontend | http://localhost:4200 |
| API | http://localhost:8000 |
| Documentação da API | http://localhost:8000/docs |
| PostgreSQL | `localhost:5432` (usuário/senha `postgres`) |

Aplique as migrations na primeira subida:

```bash
docker compose exec api alembic upgrade head
```

Para derrubar tudo, incluindo o volume do banco:

```bash
docker compose down -v
```

### Opção B — sem Docker

Rode cada parte na sua própria máquina. Os passos detalhados estão nos READMEs
de cada diretório:

- **Backend:** [`backend/README.md`](backend/README.md) — Python 3.11 + Poetry
- **Frontend:** [`frontend/README.md`](frontend/README.md) — Node 20+ e Angular CLI

Em resumo:

```bash
# terminal 1 — API em http://localhost:8000
cd backend
cp .env.example .env
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

```bash
# terminal 2 — frontend em http://localhost:4200
cd frontend
npm install
npm start
```

---

## Rodando em produção

```bash
cp backend/.env.example backend/.env    # preencha DATABASE_URL (Supabase) e SECRET_KEY
docker compose -f docker-compose.prod.yml up --build -d
```

A aplicação fica disponível em **http://localhost** (porta 80).

Como funciona:

```
navegador ──▶ Nginx (:80) ──┬──▶ /          arquivos estáticos do Angular
                            └──▶ /api/...   proxy para a API (api:8000)
                                                    │
                                                    └──▶ PostgreSQL (Supabase)
```

Pontos importantes desse desenho:

- O frontend é compilado com `--configuration production`, o que troca
  `environment.ts` por `environment.prod.ts` e faz a `apiUrl` virar `/api`.
- Como o Nginx serve o frontend e faz proxy da API na **mesma origem**, o
  navegador nunca dispara requisições cross-origin — não há CORS em produção.
- A API **não** expõe porta para o host: apenas o Nginx a alcança, pela rede
  interna do Compose.
- Não existe container de banco em produção. O PostgreSQL é o Supabase, apontado
  pelo `DATABASE_URL`.

Comandos úteis:

```bash
docker compose -f docker-compose.prod.yml logs -f       # acompanhar logs
docker compose -f docker-compose.prod.yml ps            # status e healthcheck
docker compose -f docker-compose.prod.yml down          # derrubar
```

---

## Variáveis de ambiente

Todas ficam em `backend/.env` (modelo em `backend/.env.example`):

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | Connection string do PostgreSQL. Use o modo **Session** do Supabase (porta 5432) — o asyncpg não é compatível com o modo Transaction. |
| `SECRET_KEY` | Chave de assinatura dos tokens JWT. Gere uma aleatória e **nunca** reaproveite a de desenvolvimento em produção. |
| `ALGORITHM` | Algoritmo do JWT (padrão `HS256`). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token de acesso, em minutos. |
| `ENVIRONMENT` | `development` ou `production`. |

O `.env` está no `.gitignore` e não deve ser versionado em hipótese alguma.

---

## Migrations

O schema é gerenciado pelo Alembic e a cadeia atual tem duas revisões:

```
<base> -> c2cf2197c6b3  (baseline: schema inicial completo)
       -> a575246ce0ba  (incluindo dispensacoes)  [head]
```

Provisionar um banco novo é só rodar:

```bash
alembic upgrade head            # ou: docker compose exec api alembic upgrade head
```

**Por que existe uma migration de baseline.** As seis primeiras tabelas do
sistema foram criadas manualmente no Supabase, sem passar pelo Alembic. Por
causa disso a migration `a575246ce0ba` pressupunha essas tabelas já existentes e
falhava em qualquer banco vazio, o que impedia provisionar um ambiente novo a
partir do repositório. O baseline `c2cf2197c6b3` reconstrói o schema como ele
era antes dela e fecha essa lacuna.

Bancos que já existiam continuam gravados em `a575246ce0ba`, que segue sendo o
head — para eles `alembic upgrade head` é um no-op e nada precisa ser feito.

### Banco que já tem as tabelas mas não tem `alembic_version`

É o caso de qualquer banco cujas tabelas foram criadas fora do Alembic. Rodar
`alembic upgrade head` direto nele falha com
`DuplicateTableError: relation "medicamento" already exists`, porque o Alembic o
considera vazio e tenta aplicar o baseline.

A saída é registrar a revisão correspondente ao estado atual, sem executar DDL:

```bash
# o banco NÃO tem a tabela dispensacao -> está no estado do baseline
alembic stamp c2cf2197c6b3
alembic upgrade head              # aplica a a575246ce0ba a partir daí

# o banco JÁ tem a tabela dispensacao -> já está no head
alembic stamp a575246ce0ba
```

Confira com `alembic check` depois: ele acusa qualquer divergência que sobrar.

### Criando uma migration nova

```bash
alembic revision --autogenerate -m "descrição curta"
alembic upgrade head
alembic check                   # confirma que banco e models estão em sincronia
```

Revise sempre o arquivo gerado antes de aplicar: o autogenerate não detecta
tudo (renomeações, por exemplo, viram drop + create) e não remove os tipos ENUM
no downgrade.

---

## Testes

```bash
cd backend
poetry run pytest                                  # todos
poetry run pytest --cov=app --cov-report=term-missing
```

Ou dentro do container de desenvolvimento:

```bash
docker compose exec api pytest
```

Os testes usam **SQLite em memória** — não precisam de conexão com o Supabase.

---

## Perfis de acesso

| Perfil | Permissões |
|---|---|
| `atendente` | Registrar dispensações, consultar estoque |
| `farmaceutico` | Tudo do atendente + gerenciar lotes e alertas |
| `gestor` | Acesso total, incluindo usuários e relatórios |

---

## Contribuindo

O padrão de arquitetura do backend (model → schema → repository → service →
router) está documentado em [`backend/README.md`](backend/README.md#padrão-de-desenvolvimento--como-criar-um-novo-módulo).
Siga-o ao criar novos módulos.
