# BSFarma: Frontend

SPA Angular do BSFarma. A visão geral e a stack completa estão no
[README da raiz](../README.md).

**Stack:** Angular 20, TypeScript 5.9, PrimeNG 20, PrimeFlex 4 e Chart.js 4.

## Rodando sem Docker

Requisito: Node 20.19+ ou 22.12+, a versão exigida pelo Angular 20.

```bash
npm install
```

```bash
npm start
```

A aplicação sobe em http://localhost:4200 e espera a API em
http://localhost:8000.

| Script | O que faz |
|---|---|
| `npm start` | Servidor de desenvolvimento (`ng serve`) |
| `npm run build` | Build de produção em `dist/` |
| `npm test` | Testes com Karma. A suíte não compila hoje (F-2 em [`PRE-PUBLICACAO.md`](../deploy/PRE-PUBLICACAO.md)) |

Não há linter configurado.

O [`Dockerfile`](Dockerfile) tem dois alvos:
- `dev`: `ng serve` com hot-reload;
- `production`: build servido pelo Nginx, configurado em [`nginx.conf`](nginx.conf),
  com proxy de `/api` para a API.

Os dois são usados pelos compose da raiz.

## Estrutura

```
src/app/
├── core/       guards, interceptors (token, loading) e mapa de permissões por perfil
├── modules/    alerts, auth, batch (lotes), catalog (medicamentos), dispersation
│               (dispensação), home, management (usuários), movement, patient, report
└── shared/     componentes, layout (header, menu, breadcrumb), models, services, utils
```

## Dependências e vulnerabilidades

- **Nunca rode `npm audit fix --force`.** Aqui ele sugere *downgrades* que
  pioram a situação. Em 2026, um desses rebaixou o `karma` para 4.0.0 e subiu
  as vulnerabilidades críticas de 3 para 8.
- **Pacotes do Angular:** atualize sempre com `npx ng update @angular/core@20 @angular/cli@20`.
  Eles andam juntos, em versões exatas.
- **Demais pacotes:** use `npm audit fix`, sem `--force`, e depois `npm run build` para conferir.
- **O que importa no `npm audit` é a origem.** Avisos em `karma`, `vite`,
  `esbuild`, `@angular/cli` e `@angular/build` são de ferramentas de build e
  não chegam ao navegador. Os que contam são os de `dependencies`.

**Situação (8 de novembro de 2026):** o `npm audit` conta 42 avisos, que são
17 problemas distintos repetidos por caminho de dependência. **Um** chega ao
navegador e precisa de ação:

| Pacote | Aviso | Correção |
|---|---|---|
| `@angular/common` | vazamento do token XSRF pelo HTTP Client, por divergência na análise da URL (correção incompleta da CVE-2025-66035) | `20.3.34`, uma versão de patch à frente |

Suba o conjunto junto, com `npx ng update @angular/core@20 @angular/cli@20`, e
confira com `npm run build`. Os outros 16 são de ferramentas de build e de
lint — `vite`, `undici`, `zod`, `@modelcontextprotocol/sdk`, utilitários do
próprio npm — e não vão para o bundle.

**Dívida conhecida:**
- o Karma está em fim de vida, e migrar para Vitest elimina a maior parte dos avisos;
- o `@primeng/themes` foi substituído por `@primeuix/themes`, o que afeta o
  `src/app/primeng.theme.ts`.
