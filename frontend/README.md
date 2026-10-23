# BsFarma - Frontend

> ⚠️ **Repositório legado.** Este repositório não recebe mais atualizações.
> O desenvolvimento ativo do backend e do frontend foi unificado em:
> **https://github.com/Uninorte-Extensao/bsfarma**

Sistema de controle de estoque farmacêutico da UBS Saúde Sempre.

---

## Stack

- Angular `v20.3.18`
- TypeScript `v5.9.3`
- PrimeNG `v20.4.0`
- PrimeFlex `v4.0.0`
- Chart.js `v0.3.24`

---

# Pré-requisitos

Antes de executar o projeto, instale:

## 1. Instalar Node.js

Baixe e instale a versão LTS:

https://nodejs.org

Verifique a instalação:

```bash
node -v
npm -v
```

---

## 2. Instalar Angular CLI

Instale globalmente:

```bash
npm install -g @angular/cli
```

Verifique:

```bash
ng version
```

---

## 3. Clonar o projeto

```bash
git clone https://github.com/AlessaSousa/bsfarma.git
cd bsfarma
```

---

## 4. Instalar dependências do projeto

```bash
npm install
```

ou

```bash
npm i
```

Isso instalará todas as dependências do projeto, incluindo:

- Angular
- PrimeNG
- PrimeFlex
- Chart.js
- Demais bibliotecas do package.json

---

## 5. Executar aplicação

Suba o ambiente local:

```bash
ng serve
```

ou

```bash
ng s
```

Aplicação disponível em:

```bash
http://localhost:4200
```

---

# Build de produção

```bash
ng build
```

---

# Scripts úteis

```bash
ng serve         # iniciar projeto
ng build         # gerar build
ng test          # testes
ng lint          # lint
```

---

# Docker

Este diretório tem um `Dockerfile` multi-estágio: alvo `dev` (roda `ng serve` com hot-reload) e alvo `production` (build estático servido via Nginx, com proxy para a API em `/api`, configurado em `nginx.conf`). Para subir o projeto fullstack (API + frontend) junto, veja o [README na raiz do projeto](../README.md#rodando-em-desenvolvimento).

```bash
# build da imagem de dev
docker build --target dev -t bsfarma-frontend:dev .
docker run -p 4200:4200 -v $(pwd):/app -v /app/node_modules bsfarma-frontend:dev

# build da imagem de produção
docker build --target production -t bsfarma-frontend:prod .
docker run -p 80:80 bsfarma-frontend:prod
```

# Dependências e vulnerabilidades

## ⚠ Nunca rode `npm audit fix --force` neste projeto

O `--force` tem permissão para sair do range declarado como vulnerável, e na
prática isso costuma significar **rebaixar** o pacote para uma versão muito mais
antiga — que tem problemas próprios, só não indexados naquele aviso.

Isso já aconteceu aqui: um `audit fix --force` rebaixou `karma` de `6.4.x` para
`4.0.0` (de 2019), o `@angular/cli` de `20.3.22` para `20.0.6`, e arrastou
`karma-jasmine` e `karma-jasmine-html-reporter` junto. O resultado foi **pior**
que o ponto de partida: 46 → 51 vulnerabilidades, e os críticos subiram de 3
para 8, porque o Karma antigo trouxe uma cadeia inteira de pacotes vulneráveis
(`minimist`, `braces`, `micromatch`, `log4js`, `tmp`, `useragent`, `socket.io`...).

O `npm audit` continua sugerindo esses downgrades como "correção". Ignore:

```
fix=@angular/build@19.1.9  [MAJOR]   ← downgrade, não aplique
fix=@angular/cli@20.0.6    [MAJOR]   ← downgrade, não aplique
fix=karma@4.0.0            [MAJOR]   ← downgrade, não aplique
```

## Como atualizar de forma correta

**1. Pacotes do Angular — sempre via `ng update`.** Os pacotes do framework se
atualizam em *lockstep*: o `@angular/common`, por exemplo, declara peer
dependency do `@angular/core` numa **versão exata**, não num range. Para corrigir
um, o npm precisa mover os sete de uma vez — e o resolvedor do `npm audit fix`
desiste dessa cadeia e não faz nada, mesmo continuando a anunciar
"fix available". O `ng update` entende esse acoplamento:

```bash
npx ng update @angular/core@20 @angular/cli@20
```

**2. Demais pacotes — `npm audit fix` sem `--force`.** Por definição ele só
aplica correções semver-compatíveis, então não rebaixa nada:

```bash
npm audit fix
```

**3. Confira que nada regrediu** antes de commitar:

```bash
npm ls @angular/core @angular/build @angular/cli karma --depth=0
npm run build        # o build precisa continuar passando
```

## Como ler o número do `npm audit`

O total é uma métrica ruim: o npm conta **cada pacote da cadeia** separadamente
(um aviso no `tar` aparece várias vezes) e não distingue o que chega no navegador
do que só roda na sua máquina durante o build.

O que importa é a origem. Vulnerabilidade em `vite`, `esbuild`, `karma`,
`@angular/cli` ou `@angular/build` é **dev-only**: não entra no bundle que o
Nginx serve em produção. Várias delas, inclusive, são DoS/ReDoS que exigem que
o atacante já controle a entrada do seu build.

As que realmente importam são as dos pacotes de runtime (`@angular/core`,
`@angular/common`, `@angular/compiler`, `@angular/router`, `primeng`...), porque
essas sim vão para o navegador.

Para separar um grupo do outro:

```bash
npm audit --json
```

e olhe o campo `effects` de cada entrada até chegar num pacote de
`dependencies` (produção) ou de `devDependencies` (dev-only).

## Situação atual (outubro de 2026)

Depois de reverter o downgrade e atualizar corretamente: **8 ocorrências, que
são só 2 avisos distintos**, ambos dev-only e sem correção aplicável (o único
caminho que o npm oferece é downgrade):

| aviso | origem | natureza |
|---|---|---|
| `braces` — DoS por exaustão de pilha | `karma`, `@angular/build` | dev-only |
| `@modelcontextprotocol/sdk` — vazamento de credencial OAuth | `@angular/cli` | dev-only |

**Nenhuma vulnerabilidade atinge o código que vai para produção.** Essas duas se
resolvem quando o Karma e o Angular CLI atualizarem suas próprias dependências
transitivas — não há ação útil do nosso lado.

## Dívida conhecida

- **O Karma está em EOL.** É de onde vêm os avisos de depreciação do `npm install`
  (`inflight`, `glob@7`, `rimraf@3`) e a cadeia `socket.io`. O Angular 20+ já
  suporta Vitest como runner; migrar eliminaria esse grupo inteiro.
- **`@primeng/themes` foi descontinuado** em favor de
  [`@primeuix/themes`](https://www.npmjs.com/package/@primeuix/themes). A troca
  afeta o tema customizado em `src/app/primeng.theme.ts`.
- **Angular 20.x está dois majors atrás** (o atual é o 22.x). A 20.x ainda recebe
  patches de segurança, mas a distância tende a crescer.

---

# Estrutura do Projeto

```bash
src/
└── app/
    ├── modules/
    │   ├── alerts/
    │   ├── batch/
    │   ├── catalog/
    │   ├── dispersation/
    │   └── management/
    ├── core/
    └── shared/
        ├── components/
        │   └── card-view/
        ├── layout/
        │   ├── breadcrumb/
        │   ├── header/
        │   └── menu/
        ├── mocks/
        ├── models/
        └── services/
└──  environments/

```

---

# Módulos

## Catálogo
Gestão de medicamentos.

## Lote / Estoque
Controle de lotes, validade e estoque.

## Dispensação
Registro e acompanhamento de dispensações.

## Alertas
Alertas operacionais e preventivos.

## Gestão de Usuários
Perfis, permissões e controle de acesso.

---

## Arquitetura da Solução

A solução BsFarma é composta por dois repositórios:

- **Frontend (este repositório)**  
Aplicação web desenvolvida em Angular.

- **Backend**  
API responsável por autenticação, regras de negócio e persistência de dados.

Repositório unificado (backend + frontend): [bsfarma](https://github.com/Uninorte-Extensao/bsfarma)