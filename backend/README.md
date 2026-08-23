# BSFarma  — API

> ⚠️ **Repositório legado.** Este repositório não recebe mais atualizações.
> O desenvolvimento ativo do backend e do frontend foi unificado em:
> **https://github.com/Uninorte-Extensao/bsfarma**

Sistema de controle de estoque farmacêutico da UBS Saúde Sempre.

---

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | FastAPI + Uvicorn |
| Banco de dados | PostgreSQL via Supabase |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Autenticação | JWT (python-jose + passlib/bcrypt) |
| Testes | pytest + pytest-asyncio + httpx |

---

## Primeiros passos

### 1. Pré-requisitos

- Python 3.11
- [Poetry](https://python-poetry.org/docs/#installation)

### 2. Configurar ambiente virtual e instalar dependências

```bash
python -m venv .venv
```
```bash
.venv/Scripts/Activate.ps1 # no PowershelL
.venv/Scripts/activate.bat # no cmd
```

```bash
poetry install
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com sua connection string do Supabase e uma SECRET_KEY segura.
# A connection string está em: Supabase > Project Settings > Database > Connection string
# Selecione o modo "Session" (porta 5432) — necessário para asyncpg.
```

### 4. Rodar as migrations

```bash
poetry run alembic upgrade head
```

### 5. Iniciar o servidor

```bash
poetry run uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.  
Documentação interativa: `http://localhost:8000/docs`

---

## Rodar os testes

```bash
# Todos os testes
poetry run pytest

# Com cobertura
poetry run pytest --cov=app --cov-report=term-missing

# Apenas unitários
poetry run pytest tests/unit/

# Apenas integração
poetry run pytest tests/integration/
```

Os testes usam **SQLite em memória** — não precisam de conexão com o Supabase.

---

## Estrutura do projeto

```
app/
├── main.py               ← entrypoint: registra routers e middlewares
├── core/
│   ├── config.py         ← variáveis de ambiente (Settings)
│   ├── security.py       ← JWT e hash de senha
│   ├── dependencies.py   ← get_session, get_current_user, require_perfil
│   └── exceptions.py     ← exceções de domínio e handlers globais
├── db/
│   ├── base.py           ← DeclarativeBase (herde aqui nos models)
│   ├── session.py        ← AsyncEngine e AsyncSessionLocal
│   └── migrations/       ← gerenciado pelo Alembic
└── <modulo>/             ← um diretório por domínio
    ├── model.py          ← ORM SQLAlchemy
    ├── schema.py         ← Pydantic DTOs (Create, Update, Response)
    ← repository.py      ← queries async (sem regras de negócio)
    ├── service.py        ← regras de negócio (sem queries diretas)
    └── router.py         ← rotas HTTP (sem lógica, só delega ao service)

tests/
├── conftest.py           ← fixtures compartilhadas (session, client, usuários, tokens)
├── unit/                 ← testam o service isolado
└── integration/          ← testam as rotas HTTP de ponta a ponta
```

---

## Padrão de desenvolvimento — como criar um novo módulo

O módulo `usuario/` é o **módulo de referência**. Siga exatamente a mesma
estrutura ao criar `medicamento/`, `lote/`, `movimentacao/`, etc.

### Passo a passo

**1. Crie o diretório do módulo:**
```bash
mkdir app/<modulo>
touch app/<modulo>/__init__.py
```

**2. `model.py`** — defina a tabela herdando de `Base`:
```python
from app.db.base import Base

class MeuModelo(Base):
    __tablename__ = "meu_modulo"
    # campos...
```

**3. `schema.py`** — três schemas por entidade:
- `<Entidade>Create` — payload de entrada para criação
- `<Entidade>Update` — payload de entrada para atualização (todos opcionais)
- `<Entidade>Response` — dados de saída (com `model_config = ConfigDict(from_attributes=True)`)

**4. `repository.py`** — apenas queries, sem regras:
```python
class MeuRepository:
    def __init__(self, session: AsyncSession): ...
    async def get_by_id(self, id: str): ...
    async def create(self, obj): ...
```

**5. `service.py`** — toda a lógica de negócio:
```python
class MeuService:
    def __init__(self, session: AsyncSession):
        self.repo = MeuRepository(session)
    async def criar(self, dados: MeuCreate): ...
```

**6. `router.py`** — só HTTP, delega ao service:
```python
router = APIRouter(tags=["Meu Módulo"])

@router.post("/meu-modulo", response_model=MeuResponse, status_code=201)
async def criar(dados: MeuCreate, session: AsyncSession = Depends(get_session)):
    return await MeuService(session).criar(dados)
```

**7. Registre o router em `main.py`:**
```python
from app.meu_modulo.router import router as meu_router
app.include_router(meu_router)
```

**8. Crie a migration:**
```bash
poetry run alembic revision --autogenerate -m "add meu_modulo"
poetry run alembic upgrade head
```

**9. Crie os testes** seguindo os arquivos em `tests/unit/` e `tests/integration/`.

---

## Perfis de acesso

| Perfil | Permissões |
|---|---|
| `atendente` | Registrar dispensações, consultar estoque |
| `farmaceutico` | Tudo do atendente + gerenciar lotes, alertas |
| `gestor` | Acesso total, incluindo usuários e relatórios |

Use `Depends(require_perfil("gestor"))` nas rotas para protegê-las.

---

## Docker

Este diretório tem seu próprio `Dockerfile` e um `docker-compose.yml` para rodar a API isoladamente (útil se você só mexe no backend). Para subir o projeto fullstack (API + frontend) junto, veja o [README na raiz do projeto](../README.md#rodando-em-desenvolvimento).

```bash
cp .env.example .env   # preencha DATABASE_URL e SECRET_KEY
docker compose up --build
```

---

## Conexão com o Supabase

O Supabase expõe um PostgreSQL padrão. A única configuração necessária é a
`DATABASE_URL` no `.env`. Use **sempre** a connection string no modo **Session**
(porta 5432), não a modo Transaction (porta 6543) — o asyncpg não é compatível
com o modo Transaction do pgBouncer do Supabase.

```
postgresql+asyncpg://postgres:<senha>@db.<ref>.supabase.co:5432/postgres
```
