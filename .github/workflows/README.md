# Integração contínua (GitHub Actions)

Validação automática do backend e do frontend em todo Pull Request contra a
`main` e em todo push de branch. Baseado nos modelos `pr-checks.yml` e
`merge-main.yml` usados nos demais repositórios da Uninorte-Extensao, adaptados
para a stack real deste monorepo (FastAPI + Poetry e Angular + npm).

## Arquivos

| Arquivo | Gatilho | Papel |
|---|---|---|
| [`pr-checks.yml`](pr-checks.yml) | `pull_request` com destino `main` | Valida o PR, incluindo PRs vindos de fork |
| [`merge-main.yml`](merge-main.yml) | `push` em qualquer branch, `main` incluída | Pega erro cedo, antes de existir PR, e revalida a `main` depois do merge |
| [`ci.yml`](ci.yml) | `workflow_call` (não dispara sozinho) | Define os jobs. Os dois arquivos acima só o chamam |

Os jobs ficam num workflow reutilizável (`ci.yml`) para que PR e push rodem
exatamente os mesmos comandos. Com dois arquivos copiados, um seria atualizado e
o outro não, e os dois cenários passariam a validar coisas diferentes sem
ninguém perceber.

## Jobs

| Job | Comandos | Pega |
|---|---|---|
| **Backend - testes** | `poetry install --no-root`, depois `poetry run pytest -q` | Os 16 testes unitários e de integração (SQLite em memória) |
| **Backend - migrations** | `alembic upgrade head`, `alembic check`, `alembic downgrade base` e `alembic upgrade head` contra um Postgres 16 efêmero | Migration quebrada, model alterado sem migration correspondente, `downgrade` que não desfaz o que o `upgrade` fez |
| **Frontend - build** | `npm ci`, depois `npm run build` | Erro de tipo, erro de template, import quebrado e estouro de budget do bundle |

Os três jobs rodam em paralelo. Qualquer um vermelho reprova o run.

### Versões

| Runtime | CI | Por quê |
|---|---|---|
| Python | 3.12 | Mesma versão da imagem de produção (`backend/Dockerfile`). O `pyproject.toml` aceita `>=3.11,<3.13` |
| Poetry | 2.5.1 | Versão que gerou o `poetry.lock` atual |
| Node | 22 | LTS ativa e versão usada no desenvolvimento. O Angular 20 exige `^20.19 \|\| ^22.12 \|\| >=24` |

O `frontend/Dockerfile` ainda usa `node:20-alpine`. O Node 20 saiu de suporte em
abril de 2026, então vale alinhar a imagem para `node:22-alpine` numa tarefa à
parte.

## Variáveis de ambiente

O backend lê `DATABASE_URL` e `SECRET_KEY` **no momento do import**:
`app/core/config.py` instancia `Settings()` com os dois campos obrigatórios, e
`app/db/base.py` cria a engine no nível do módulo. Sem elas, o `pytest` falha
já na coleta.

Por isso o workflow declara **valores fictícios em texto**, não `secrets`:

```
DATABASE_URL=postgresql+asyncpg://ci:ci@localhost:5432/ci
SECRET_KEY=ci-dummy-secret
```

- **Não são credenciais reais.** No job de testes a URL nunca é usada para
  conectar, porque o `create_async_engine` é preguiçoso e os testes montam a
  própria engine SQLite no `conftest.py`. No job de migrations ela aponta para o
  Postgres descartável criado pelo próprio runner.
- **Precisa ser uma URL PostgreSQL.** `app/db/session.py` passa
  `pool_size`/`max_overflow`, que o SQLite rejeita.
- **Não pode depender de `secrets`.** PRs vindos de fork não têm acesso a
  secrets do repositório, por desenho do GitHub. Um CI que precisasse deles
  quebraria para todo contribuidor externo.

## O que fica de fora, e por quê

O critério de aceite "comandos batem com os scripts reais do projeto (sem falso
positivo)" impede chamar etapas que não existem ou que já nascem quebradas:

| Etapa | Situação | Para incluir |
|---|---|---|
| Lint do backend | Não há linter configurado (sem `ruff`/`flake8` no `pyproject.toml`) | Adicionar o linter, definir regras e corrigir o código existente. Depois, um passo `poetry run ruff check .` |
| Lint do frontend | Não há script `lint` no `package.json` nem ESLint instalado | `ng add @angular-eslint/schematics`, corrigir os avisos e depois incluir `npm run lint` |
| Testes do frontend | A suíte não compila: `app.component.spec.ts` ainda é o spec do starter do Angular (espera `app.title`). Ver F-2 em [`deploy/PRE-PUBLICACAO.md`](../../deploy/PRE-PUBLICACAO.md) | Corrigir os specs e incluir `npm test -- --watch=false --browsers=ChromeHeadless` no job do frontend |

Cada linha é um acréscimo de um passo no [`ci.yml`](ci.yml), sem mudar a
estrutura.

## Execuções duplicadas

Um push numa branch do próprio repositório que já tem PR aberto dispara os dois
workflows. Cada um reporta seu próprio check, então isso é esperado. Dentro de
cada workflow, `concurrency` cancela o run anterior da mesma ref quando chega um
push novo. Na `main` o cancelamento fica desligado, para que todo merge tenha
seu run completo.

No fluxo fork + PR isso quase não acontece. O push vai para o fork e o PR roda
no repositório principal.

## Fluxo fork + PR: o que cada pessoa precisa saber

- **Push em branch do fork:** o `merge-main.yml` roda **no fork**, nas Actions
  de quem fez o push. O GitHub desliga workflows em forks por padrão. Cada
  contribuidor precisa abrir a aba **Actions** do próprio fork uma vez e clicar
  em *"I understand my workflows, go ahead and enable them"*.
- **PR para a `main`:** o `pr-checks.yml` roda no repositório principal. Na
  primeira contribuição de alguém de fora da organização, o GitHub pode exigir
  que um mantenedor aprove a execução (botão *Approve and run* no PR). Isso
  depende de **Settings → Actions → General → Fork pull request workflows**.

## Onde a falha aparece

O próprio GitHub mostra o resultado, sem configuração extra:

- **No PR:** seção de checks no fim da conversa, com um item por job (por
  exemplo `PR Checks / Validação / Backend - testes`). Um job vermelho mostra
  "Some checks were not successful".
- **No commit:** ícone ✓ ou ✗ ao lado do hash, no histórico e na lista de
  branches.
- **Na aba Actions:** log completo de cada passo.

### Recomendado: tornar os checks obrigatórios

Para que um PR vermelho **não possa** ser mergeado, alguém com permissão de
administrador configura em **Settings → Branches → Branch protection rules**
(ou **Rulesets**) para a `main`:

1. Ativar *Require status checks to pass before merging*.
2. Adicionar os três checks: `Validação / Backend - testes`,
   `Validação / Backend - migrations` e `Validação / Frontend - build`.
   Eles só aparecem na busca depois de o workflow ter rodado pelo menos uma vez.

Sem esse passo, a falha fica visível, mas o botão de merge continua habilitado.

## Rodando localmente o mesmo que o CI

```bash
cd backend
DATABASE_URL="postgresql+asyncpg://ci:ci@localhost:5432/ci" SECRET_KEY=ci-dummy-secret poetry run pytest -q
```

```bash
cd frontend
npm ci
npm run build
```

As migrations precisam de um Postgres vazio. Com Docker:

```bash
docker run --rm -d --name pg-ci -e POSTGRES_USER=ci -e POSTGRES_PASSWORD=ci -e POSTGRES_DB=ci -p 5433:5432 postgres:16
```

```bash
cd backend
export DATABASE_URL="postgresql+asyncpg://ci:ci@localhost:5433/ci" SECRET_KEY=ci-dummy-secret
poetry run alembic upgrade head && poetry run alembic check && poetry run alembic downgrade base && poetry run alembic upgrade head
```

```bash
docker stop pg-ci
```

Use sempre um banco descartável. Nunca rode o `downgrade base` com o
`DATABASE_URL` do `.env`, porque ele apaga todas as tabelas.
