# BSFarma: API

API FastAPI do BSFarma. A visão geral, as variáveis de ambiente e as migrations
estão no [README da raiz](../README.md).

## Rodando sem Docker

Requisitos: Python 3.11 ou 3.12 e [Poetry](https://python-poetry.org/docs/#installation).

```bash
poetry install
```

```bash
cp .env.example .env
```

No `.env`, preencha `DATABASE_URL` e `SECRET_KEY`.

```bash
poetry run alembic upgrade head
```

```bash
poetry run uvicorn app.main:app --reload
```

A API sobe em http://localhost:8000, com a documentação em `/docs`.

Para subir só a API em Docker, use `docker compose up --build` neste
diretório. A stack completa está no README da raiz.

## Testes

```bash
poetry run pytest
```

```bash
poetry run pytest --cov=app --cov-report=term-missing
```

Os testes usam SQLite em memória. As fixtures compartilhadas ficam em
`tests/conftest.py`: sessão, cliente HTTP, usuários e tokens.

## Estrutura

```
app/
├── main.py          routers, middlewares e lifespan (scheduler de alertas)
├── core/            config, segurança (JWT, hash), dependências, exceções
├── db/              Base declarativa e sessão
├── seed/            carga de demonstração (python -m app.seed)
└── <modulo>/        um diretório por domínio
    ├── model.py       ORM
    ├── schema.py      DTOs Pydantic: Create, Update, Response
    ├── repository.py  queries, sem regra de negócio
    ├── service.py     regras de negócio, sem query direta
    └── router.py      HTTP, só delega ao service
alembic/             migrations
tests/               unit/ (services) e integration/ (rotas)
```

## Criando um módulo

O módulo `usuario/` é a referência.

1. Crie `app/<modulo>/` com `__init__.py` e os cinco arquivos acima. O model
   herda de `app.db.base.Base`, e o schema de resposta usa
   `ConfigDict(from_attributes=True)`.
2. Registre o router em `app/main.py` com `app.include_router(...)`.
3. Se o model for novo, importe-o em `app/db/models.py`, para o Alembic e os
   relacionamentos o enxergarem.
4. Gere e aplique a migration:

   ```bash
   poetry run alembic revision --autogenerate -m "add <modulo>"
   ```

   ```bash
   poetry run alembic upgrade head
   ```

5. Escreva os testes em `tests/unit/` e `tests/integration/`.

Para proteger rotas por perfil, use
`dependencies=[Depends(require_perfil("farmaceutico", "gestor"))]`.
