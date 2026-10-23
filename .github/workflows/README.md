# Integração contínua

| Arquivo | Quando roda |
|---|---|
| [`pr-checks.yml`](pr-checks.yml) | Em todo pull request contra a `main`, inclusive de fork |
| [`merge-main.yml`](merge-main.yml) | Em todo push, em qualquer branch, inclusive na `main` após o merge |
| [`ci.yml`](ci.yml) | Define os jobs; os dois arquivos acima só o chamam |

Os dois gatilhos rodam os mesmos jobs, em paralelo:

| Job | O que roda |
|---|---|
| Backend - testes | `poetry run pytest` (Python 3.12) |
| Backend - migrations | `alembic upgrade head`, `check`, `downgrade base` e `upgrade head` num Postgres 16 temporário |
| Frontend - build | `npm ci` e `npm run build` (Node 22), que faz a checagem de tipos e de templates |

**Fora do CI, por enquanto:**
- **Lint:** não há linter configurado em nenhum dos lados.
- **Testes do frontend:** a suíte não compila (F-2 em
  [`PRE-PUBLICACAO.md`](../../deploy/PRE-PUBLICACAO.md)).

Cada um vira um passo a mais no `ci.yml` quando existir.

## Variáveis de ambiente

O backend exige `DATABASE_URL` e `SECRET_KEY` já ao importar o código. O
workflow usa **valores fictícios em texto**, não `secrets`, porque PRs de fork
não têm acesso a secrets. Nos testes, a URL nunca é usada, porque eles montam
um SQLite próprio. Nas migrations, ela aponta para o Postgres do runner.

## Para quem contribui por fork

- **Push no fork:** o workflow roda nas Actions do próprio fork, que vêm
  desligadas. Ative uma vez em **Actions → I understand my workflows**.
- **Primeiro PR de alguém de fora da organização:** pode exigir que um
  mantenedor clique em **Approve and run**.

## Resultado e checks obrigatórios

O resultado aparece nos checks do PR, ao lado de cada commit e na aba Actions.
Para **bloquear o merge** quando algo falhar, um administrador precisa ir em
**Settings → Branches → Branch protection rules** da `main`, ativar *Require
status checks to pass* e escolher os três checks:
- `Validação / Backend - testes`;
- `Validação / Backend - migrations`;
- `Validação / Frontend - build`.

## Reproduzir localmente

```bash
cd backend && DATABASE_URL="postgresql+asyncpg://ci:ci@localhost:5432/ci" SECRET_KEY=ci poetry run pytest -q
```

```bash
cd frontend && npm ci && npm run build
```

Para testar as migrations, use sempre um Postgres descartável. O
`downgrade base` apaga todas as tabelas.
