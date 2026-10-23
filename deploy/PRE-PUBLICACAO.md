# Pré-publicação — viabilidade do CI/CD e pendências do projeto

> **Levantamento de 2026-10-06.** Todos os pontos abaixo foram verificados
> executando os comandos reais do projeto, não por leitura de código apenas. O
> [Anexo](#anexo--como-reproduzir-o-levantamento) traz os comandos para
> reproduzir cada afirmação.

---

## Parte 1 — Viabilidade do CI/CD

### Veredito

**A issue é resolvível e os quatro critérios de aceite são atingíveis**, com uma
ressalva honesta: a issue pede "lint, build, testes", e **não existe linter em
nenhum dos dois lados do projeto**. O CI vai cobrir *build + testes*.

Isso não é um desvio do critério — é o que o critério pede. "Comandos batem com
os scripts reais do projeto (sem falso positivo)" significa exatamente que o
workflow não pode chamar um `npm run lint` que não existe, porque isso falharia
por ausência de script, não por problema de código. Adicionar linter é tarefa
própria, com decisão de regras e um esforço de correção inicial que não cabe
dentro desta issue.

### Mapeamento com os critérios de aceite

| Critério | Como será atendido | Ressalva |
|---|---|---|
| Workflow roda em PR contra `main` | `on.pull_request.branches: [main]` | — |
| Workflow roda em push de branch | `on.push` sem filtro de branch | Push + PR na mesma branch disparam 2 runs; mitigado com `concurrency` + `cancel-in-progress` |
| Falha visível no PR/commit | Nativo do GitHub (checks no commit e na aba do PR) | — |
| Comandos batem com os scripts reais | `pytest`, `npm ci`, `npm run build`, `alembic upgrade head` — todos validados | **Lint fora** (não existe); **teste do frontend fora** (suíte quebrada, ver [F-2](#f-2--suíte-de-testes-do-frontend-não-compila)) |

### Cobertura resultante

| Escopo | Coberto | Não coberto |
|---|---|---|
| Backend | 16 testes (`pytest`) + migrations (`alembic upgrade head` + `alembic check`) | lint |
| Frontend | build de produção (`npm run build`, que inclui type-check de todos os componentes) | testes unitários, lint |

O build do Angular não é um check fraco: ele compila templates e faz type-check
do projeto inteiro. Um erro de tipo ou de template reprova o PR. O que falta é
cobertura de *comportamento*.

### Restrições técnicas que o workflow precisa respeitar

Estas foram descobertas empiricamente e são as causas clássicas de "passa local,
vermelho no CI":

**1. O backend exige variáveis de ambiente para *importar*, não só para rodar.**

[`app/core/config.py`](../backend/app/core/config.py) instancia `settings = Settings()`
no nível do módulo, com `database_url` e `secret_key` **obrigatórios** (sem
default). E [`app/db/base.py`](../backend/app/db/base.py) chama
`create_async_engine(os.getenv("DATABASE_URL"))` também no import. Sem essas
variáveis, o `pytest` falha **na coleta**:

```
sqlalchemy.exc.ArgumentError: Expected string or URL object, got None
```

Em CI não existe `.env` (está gitignorado, corretamente), então o workflow tem
que injetá-las.

**2. O `DATABASE_URL` dummy precisa ser PostgreSQL, não SQLite.**

[`app/db/session.py`](../backend/app/db/session.py) cria a engine com
`pool_size=10, max_overflow=20`, que o `StaticPool` do SQLite rejeita:

```
TypeError: Invalid argument(s) 'pool_size','max_overflow' sent to create_engine()
```

O valor validado para o CI é `postgresql+asyncpg://ci:ci@localhost:5432/ci`. O
`create_async_engine` é *lazy* — nunca abre conexão no import — então a URL não
precisa apontar para um banco real nos jobs de teste.

**3. PRs de fork não têm acesso a `secrets`.**

O fluxo da issue é fork + PR. Em PRs vindos de fork, o GitHub **não expõe
secrets** ao workflow, por design. Qualquer CI que dependa de credencial real
quebra para contribuidor externo. Como os 16 testes usam SQLite em memória
(`conftest.py` monta a própria engine) e as variáveis acima são só para satisfazer
o import, o CI deve usar **valores dummy declarados em texto no workflow** — não
secrets. Isso é desenho correto, não atalho.

**4. O Alembic usa engine assíncrona.**

[`alembic/env.py`](../backend/alembic/env.py) usa `async_engine_from_config` +
`asyncio.run(run_async_migrations())`, e sobrescreve a URL do `.ini` com
`os.getenv("DATABASE_URL")`. Então o job de migrations precisa de um
`DATABASE_URL` com driver `+asyncpg` apontando para o Postgres efêmero do runner.

As 2 migrations existentes **estão versionadas** no git (`alembic/versions/`), o
que torna o job viável. A regra `app/db/migrations/versions/*.py` no
`backend/.gitignore` aponta para um caminho que não existe e é inofensiva, mas
confunde — ver [D-3](#d-3--regra-morta-no-gitignore-do-backend).

**5. Versões de runtime.**

| Runtime | Exigido | Usado localmente | Observação |
|---|---|---|---|
| Node | `^20.19.0 \|\| ^22.12.0 \|\| >=24.0.0` | 22.19.0 | CI deve usar **22** para espelhar o dev |
| Python | `>=3.11,<3.13` (pyproject) | 3.11.9 | CI deve usar **3.11** |

### Decisões de desenho do workflow

**Um único `ci.yml`, sem filtro de `paths`.** O padrão de filtrar por diretório
num monorepo tem uma armadilha conhecida: se os checks forem marcados como
obrigatórios no branch protection, um PR que toca só o frontend nunca reporta o
check do backend, e o PR fica travado em *waiting* para sempre. Contornar isso
exige um job agregador (`ci-ok`) ou `dorny/paths-filter` — complexidade que não
se paga neste porte, onde o backend roda em ~7s e o frontend em ~12s. **Fica
anotado como otimização para quando o tempo de CI incomodar.**

**`concurrency` com `cancel-in-progress`.** Push em branch e abertura de PR na
mesma branch geram dois runs. Em vez de desabilitar um dos gatilhos (o que
violaria um dos critérios de aceite), cancelamos runs superados da mesma ref.

**Jobs separados para testes e migrations.** O job de migrations precisa de um
`services: postgres:16`; os testes não precisam de banco nenhum. Separar dá
sinal claro no PR (`backend-tests` vs `migrations`) e mantém os testes rápidos.

---

## Parte 2 — Pendências antes de publicar

Classificação:

- 🔴 **Bloqueador** — não publicar sem resolver
- 🟡 **Importante** — resolver antes de usuário real entrar
- 🔵 **Desejável** — dívida conhecida, sem urgência

---

### 🔴 Bloqueadores

#### B-1 — Seeders criam credenciais fracas e não têm guarda de ambiente

[`app/usuario/seeder.py`](../backend/app/usuario/seeder.py) cadastra:

| login | senha | perfil |
|---|---|---|
| `gestor` | `gestor123` | **GESTOR** (acesso total) |
| `farmaceut` | `farmaceut123` | FARMACEUTICO |
| `atendente` | `atendente123` | ATENDENTE |

Os seeders rodam manualmente (`python -m app.usuario.seeder`, documentado no
README da raiz) e conectam **no que o `DATABASE_URL` aponta**, sem verificar o
ambiente. Com o `.env` de produção carregado, um seeder executado por engano
injeta um usuário de acesso total com senha adivinhável num sistema de saúde.

**Ação:** adicionar guarda no início de cada seeder, abortando se
`ENVIRONMENT == "production"`. O projeto já tem `settings.is_production` em
[`app/core/config.py`](../backend/app/core/config.py) para isso. Idealmente,
também tirar as senhas do código e lê-las de variável de ambiente.

- [ ] Guarda de ambiente nos 6 seeders
- [ ] Confirmar que nenhum desses logins existe no banco de produção
- [ ] Senhas dos seeders fora do código-fonte

#### B-2 — Rotacionar os segredos antes de publicar

O `backend/.env` com a `SECRET_KEY` e a connection string do Supabase foi lido
durante uma sessão de assistente em 2026-08-23, ficando registrado no transcript
dessa sessão. Qualquer segredo que apareça em log, transcript ou histórico de
terminal deve ser tratado como comprometido, independentemente de quem teve
acesso.

**Ação:**

- [ ] Trocar a senha do banco no painel do Supabase e atualizar o `DATABASE_URL`
- [ ] Gerar nova `SECRET_KEY` (`python -c "import secrets; print(secrets.token_hex(32))"`) — invalida tokens emitidos, usuários refazem login
- [ ] Confirmar que o `.env` de produção nunca é commitado (hoje está corretamente no `.gitignore`)

#### B-3 — Sem TLS: tráfego de dados de paciente em texto claro

[`nginx.conf`](../frontend/nginx.conf) só escuta na porta 80, sem TLS, e o
[`docker-compose.prod.yml`](../docker-compose.prod.yml) publica `80:80`. Hoje
trafegam em claro: credenciais no login, o JWT em todas as requisições e dados
de paciente.

**Ação:** terminar TLS antes de expor. Dois caminhos, dependendo da hospedagem:

- Se for atrás de um load balancer / Cloudflare / plataforma que termina TLS
  (Railway, Render, Fly), **não há o que fazer no nginx** — só confirmar que o
  TLS está ativo na borda e que o HTTP redireciona para HTTPS.
- Se o nginx for a borda, adicionar `listen 443 ssl`, certificado (Let's Encrypt
  via certbot) e redirecionamento de 80 → 443.

- [ ] Definir onde o TLS termina
- [ ] Validar que não existe caminho HTTP sem redirecionamento

---

### 🟡 Importantes

#### F-1 — 18 `console.log` em código de produção, alguns com dados do usuário

O build de produção **não remove** `console.log`. Estão logando no console do
navegador, em produção:

```
app.config.ts:51        console.log('[INIT] user carregado:', auth.user());
app.config.ts:52        console.log('[INIT] perfil:', auth.user()?.perfil);
core/authGuard.ts:33    console.log('[HOME GUARD] rodando, perfil:', ...);
core/permissionGuard.ts:18  console.log('[PERMISSION GUARD] rota:', ..., '| tem permissão:', ...);
modules/auth/auth/auth.component.ts:38  console.log(res)
```

O objeto do usuário e o mapa de permissões vão para o console. `auth.component.ts:38`
loga a resposta do login. Além do vazamento, entrega a estrutura de autorização
para quem abrir o DevTools.

- [ ] Remover os `console.log` de depuração (18 ocorrências em `frontend/src`, fora de specs)
- [ ] Considerar um wrapper de log que silencia fora de desenvolvimento

#### F-2 — Suíte de testes do frontend não compila

```
X [ERROR] TS2339: Property 'title' does not exist on type 'AppComponent'.
    src/app/app.component.spec.ts:20
```

`app.component.spec.ts` é o spec original do starter do Angular (commit inicial
`7a3e399`), nunca atualizado depois que o componente foi customizado: espera
`app.title` (o componente tem `isAuthRoute`) e um `<h1>Hello, bsfarma</h1>` que
não existe mais no template. **A suíte está quebrada desde o início do projeto** —
não há rede de segurança nenhuma no frontend.

Enquanto não for corrigido, o CI não pode incluir o job de teste do frontend sem
nascer vermelho.

- [ ] Remover os 2 testes obsoletos, mantendo o `should create the app` (~8 linhas)
- [ ] Incluir o job de teste do frontend no CI depois disso

#### B-4 — `/docs`, `/redoc` e `/openapi.json` públicos

[`app/main.py`](../backend/app/main.py) instancia `FastAPI(...)` sem
`docs_url=None`, então a documentação interativa fica acessível a qualquer um que
alcance a API. Para um sistema interno de UBS, isso entrega o mapa completo de
endpoints, schemas e regras de validação.

Não é necessariamente errado — depende de a API ser ou não alcançável publicamente.
Mas precisa ser **decisão consciente**, não default.

- [ ] Decidir: manter aberto, fechar em produção (`docs_url=None if settings.is_production else "/docs"`), ou proteger com autenticação

#### B-5 — CORS hardcoded para `localhost:4200`

```python
allow_origins=["http://localhost:4200"],
```

Atrás do proxy do nginx isso funciona, porque o navegador vê front e API na mesma
origem (`/api/` é proxyado) e CORS nem entra em jogo. **Mas quebra silenciosamente**
se algum dia o frontend for servido de um domínio diferente da API — e a origem de
desenvolvimento ficar liberada em produção não é desejável.

- [ ] Tornar `allow_origins` configurável por variável de ambiente

#### I-1 — Sem cabeçalhos de segurança no nginx

A configuração atual só define `Cache-Control`. Faltam os cabeçalhos básicos:
`X-Content-Type-Options`, `X-Frame-Options` (ou `frame-ancestors` via CSP),
`Referrer-Policy` e, quando houver HTTPS, `Strict-Transport-Security`.

- [ ] Adicionar cabeçalhos de segurança ao `nginx.conf`

#### B-6 — Duas engines SQLAlchemy concorrentes

Existem duas engines distintas para o mesmo banco:

| Arquivo | Configuração |
|---|---|
| [`app/db/base.py`](../backend/app/db/base.py):25 | `create_async_engine(DATABASE_URL)` — sem pool configurado |
| [`app/db/session.py`](../backend/app/db/session.py):10 | `create_async_engine(..., pool_size=10, max_overflow=20)` |

Duas engines significam dois pools de conexão para o mesmo Postgres. Com o
Supabase (que tem limite de conexões), isso dobra o consumo sem necessidade, e a
engine de `base.py` fica sem o controle de pool que a outra tem. Foi o que
derrubou o teste de `DATABASE_URL` com SQLite.

- [ ] Consolidar numa única engine (provavelmente manter a de `session.py` e fazer `base.py` só expor a `Base`)

#### I-2 — Tag flutuante do Node no Dockerfile

[`frontend/Dockerfile`](../frontend/Dockerfile):7 usa `FROM node:20-alpine`, mas o
Angular 20 exige `^20.19.0 || ^22.12.0 || >=24.0.0`. A tag `node:20-alpine` hoje
resolve para um 20.19+, então funciona — mas é uma tag móvel sendo validada contra
um piso de versão. Além disso, o desenvolvimento usa Node 22.19, então a imagem
testa um runtime diferente do usado no dia a dia.

- [ ] Alinhar para `node:22-alpine` (ou fixar a minor explicitamente)

---

### 🔵 Desejáveis

#### D-1 — `.browserslistrc` declara browsers que o Angular 20 não suporta

```
chrome >= 90
firefox >= 90
safari >= 15
edge >= 90
```

O build avisa que Chrome 90–106, Firefox 90–103, Safari 15–15.6 e Edge 90–106
estão fora do suporte da versão. Sem efeito prático além do aviso, mas a
intenção de suportar browsers antigos **não se concretiza** — o Angular não gera
código para eles. Existe um commit `d0500b8 fix: config browsers unsopported`
que não resolveu.

#### D-2 — `ng lint` documentado sem existir

O README do frontend lista `ng lint` em "Scripts úteis", mas não há script `lint`
nem ESLint no projeto.

#### D-3 — Regra morta no `.gitignore` do backend

`app/db/migrations/versions/*.py` aponta para um diretório que não existe (as
migrations vivem em `alembic/versions/`, conforme `script_location` do
`alembic.ini`). Inofensivo hoje, mas se alguém mover as migrations para o caminho
mencionado, elas serão silenciosamente ignoradas pelo git — o que quebraria o
deploy e o CI.

#### D-4 — 8 vulnerabilidades npm remanescentes, sem ação útil

Após a atualização de 2026-10-06, restam 8 ocorrências (2 avisos distintos:
`braces` e `@modelcontextprotocol/sdk`), **todas dev-only** e nenhuma no bundle
que vai para produção. O único "fix" que o npm oferece é downgrade, que piora a
situação. Resolvem-se quando o Karma e o Angular CLI atualizarem suas transitivas.
Detalhes em [`frontend/README.md`](../frontend/README.md#dependências-e-vulnerabilidades).

#### D-5 — Karma em EOL

Fonte dos avisos de depreciação do `npm install` (`inflight`, `glob@7`,
`rimraf@3`) e de toda a cadeia `socket.io`. O Angular 20+ suporta Vitest.

#### D-6 — Token JWT em `localStorage`

`localStorage.getItem('tokenBsFarma')`. Token em `localStorage` é legível por
qualquer JavaScript da página, então um XSS vira roubo de sessão. A alternativa
(cookie `httpOnly` + `SameSite`) exige mudança no backend e no fluxo de login.
Para o porte do projeto é uma escolha defensável, mas vale registrar como risco
aceito conscientemente — ainda mais combinado com [F-1](#f-1--18-consolelog-em-código-de-produção-alguns-com-dados-do-usuário).

#### D-7 — Bundle inicial de 1.08 MB

O budget de erro foi afrouxado para 2 MB em `angular.json` para o build passar.
O maior contribuinte é o `primeflex.css` (445 KB) carregado globalmente. O gzip
do nginx reduz bastante o que trafega, e as rotas já são lazy-loaded, então o
impacto real é moderado — mas o budget deixou de ser um guarda-corpo útil.

---

## Resumo executivo

**Para o CI/CD:** viável agora. Nenhuma das pendências acima impede construir o
workflow — elas apenas definem seu escopo inicial (build + testes do backend +
migrations, sem lint e sem teste de frontend) e as variáveis dummy que ele precisa
injetar.

**Para publicar:** há **3 bloqueadores** (seeders com credencial fraca sem guarda,
segredos a rotacionar, ausência de TLS) que são rápidos de resolver mas não devem
ser ignorados, considerando que o sistema manipula dados de paciente. Os itens
🟡 valem resolver antes de usuário real entrar; os 🔵 podem ser planejados.

---

## Anexo — como reproduzir o levantamento

```bash
# Backend: testes passam sem banco externo
cd backend && poetry run pytest -q

# Backend: confirma que o import exige env vars (deve FALHAR)
cd "$(mktemp -d)" && PYTHONPATH=/caminho/para/backend python -c "import app.main"

# Backend: confirma que funciona só com env vars dummy (deve PASSAR)
cd "$(mktemp -d)" && DATABASE_URL="postgresql+asyncpg://ci:ci@localhost:5432/ci" \
  SECRET_KEY=dummy PYTHONPATH=/caminho/para/backend python -c "import app.main"

# Backend: suíte completa com as variáveis do CI
cd backend && DATABASE_URL="postgresql+asyncpg://ci:ci@localhost:5432/ci" \
  SECRET_KEY=dummy poetry run pytest -q

# Frontend: build passa
cd frontend && npm run build

# Frontend: suíte de testes NÃO compila
cd frontend && npm test -- --watch=false --browsers=ChromeHeadless

# Frontend: confirma ausência de linter
node -e "console.log(Object.keys(require('./frontend/package.json').scripts))"

# Frontend: console.log em código de produção
grep -rn "console\.\(log\|debug\)" frontend/src --include=*.ts | grep -v spec

# Versões exigidas
node -e "console.log(require('@angular/core/package.json').engines)"  # dentro de frontend/
grep 'python = ' backend/pyproject.toml

# Vulnerabilidades por origem (dev vs produção)
cd frontend && npm audit --json
```
