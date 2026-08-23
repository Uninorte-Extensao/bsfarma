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