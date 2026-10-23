# Pendências antes de publicar

Levantamento de 2026-10-06, atualizado em 2026-10-23.

Prioridades:
- 🔴 não publicar sem resolver;
- 🟡 resolver antes de entrarem usuários reais;
- 🔵 dívida conhecida, sem urgência.

## Situação

| ID | Item | Status |
|---|---|---|
| 🔴 B-1 | Seeders com senhas fracas e sem trava de produção | ⚠️ Parcial: seeders substituídos por `app.seed`, que tem trava e lê as senhas do ambiente. **Falta conferir** se `gestor`/`gestor123`, `farmaceut`/`farmaceut123` ou `atendente`/`atendente123` existem no banco de produção |
| 🔴 B-2 | Segredos expostos num transcript em 2026-08-23 | ✅ Credenciais do Supabase e `SECRET_KEY` trocadas |
| 🔴 B-3 | Sem TLS | 🔄 Caddy com HTTPS automático em [`DEPLOY.md`](DEPLOY.md). Validar no primeiro deploy |
| 🟡 F-1 | `console.log` com dados do usuário e permissões | ⏳ Pendente |
| 🟡 F-2 | Suíte de testes do frontend não compila | ⏳ Pendente |
| 🟡 B-4 | `/docs`, `/redoc` e `/openapi.json` públicos | ⏳ Pendente |
| 🟡 B-5 | CORS fixo em `localhost:4200` | ✅ Variável `CORS_ORIGINS` |
| 🟡 I-1 | Sem cabeçalhos de segurança | 🔄 Adicionados no Caddy (HSTS, `nosniff`, `X-Frame-Options`, `Referrer-Policy`). Validar no primeiro deploy |
| 🟡 B-6 | Duas engines SQLAlchemy | ⏳ Pendente |
| 🟡 I-2 | `node:20-alpine` no Dockerfile do frontend | ⏳ Pendente |
| 🔵 D-1 | `.browserslistrc` com navegadores sem suporte | ⏳ Pendente |
| 🔵 D-2 | `ng lint` documentado sem existir | ✅ Removido do README do frontend |
| 🔵 D-3 | Regra morta no `.gitignore` do backend | ⏳ Pendente |
| 🔵 D-4 | 2 avisos do `npm audit` | Sem ação possível: vêm de ferramentas de build e não têm correção. Ver [`frontend/README.md`](../frontend/README.md) |
| 🔵 D-5 | Karma em fim de vida | ⏳ Pendente (migrar para Vitest) |
| 🔵 D-6 | JWT em `localStorage` | Risco aceito (ver abaixo) |
| 🔵 D-7 | Bundle inicial de 1,08 MB, com budget afrouxado | ⏳ Pendente |

## Detalhes dos pendentes

**F-1: `console.log` em produção.** O build não os remove. `app.config.ts`,
`authGuard.ts` e `permissionGuard.ts` mostram no DevTools o usuário logado e o
mapa de permissões, e `auth.component.ts` mostra a resposta do login. Remova as
ocorrências fora dos specs, que podem ser listadas com:

```bash
grep -rn "console\.\(log\|debug\)" frontend/src --include=*.ts | grep -v spec
```

**F-2: testes do frontend.** O `app.component.spec.ts` ainda é o do starter do
Angular: espera `app.title` e um `<h1>Hello, bsfarma</h1>` que não existem mais.
Remova os dois testes obsoletos, mantenha o `should create the app` e então
inclua `npm test -- --watch=false --browsers=ChromeHeadless` no CI.

**B-4: documentação da API pública.** Decida se fica aberta, fechada em
produção (`docs_url=None if settings.is_production else "/docs"`, o mesmo para
`redoc_url` e `openapi_url`) ou protegida por login.

**B-6: duas engines.** `app/db/base.py` cria uma engine sem pool, e hoje só a
carga de demonstração a usa. A API usa a de `app/db/session.py`, com
`pool_size=10` e `max_overflow=20`. Deixe só a de `session.py` e faça o
`base.py` expor apenas a `Base`.

**I-2: imagem do Node.** O Node 20 saiu de suporte em abril de 2026, e o
desenvolvimento e o CI usam o 22. Troque para `node:22-alpine`.

**D-1: navegadores.** O `.browserslistrc` pede Chrome/Edge 90+, Firefox 90+ e
Safari 15+, mas o Angular 20 não gera código para eles. Alinhe a lista ao
suporte oficial para eliminar o aviso do build.

**D-3: `.gitignore` do backend.** A regra `app/db/migrations/versions/*.py`
aponta para um caminho inexistente. Se alguém mover as migrations para lá,
elas serão ignoradas em silêncio. Remova a regra.

**D-6: JWT em `localStorage`.** Qualquer script da página consegue lê-lo, então
um XSS vira roubo de sessão. A alternativa é um cookie `httpOnly`, que exige
mudar o login no backend e no frontend. É aceitável para o porte atual, desde
que o F-1 seja resolvido.

**D-7: tamanho do bundle.** O budget de erro foi afrouxado para 2 MB. O maior
peso é o `primeflex.css` (445 KB), carregado globalmente.
