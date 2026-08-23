# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Estágio "deps" — instala as dependências uma única vez e é reaproveitado
# pelos estágios de dev e de build de produção.
# ---------------------------------------------------------------------------
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# ---------------------------------------------------------------------------
# Estágio "dev" — usado pelo docker-compose de desenvolvimento.
# Roda `ng serve` com hot-reload; o código-fonte é montado como volume.
# ---------------------------------------------------------------------------
FROM deps AS dev

WORKDIR /app
COPY . .

EXPOSE 4200

CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--poll", "2000"]

# ---------------------------------------------------------------------------
# Estágio "build" — gera o bundle estático de produção.
# ---------------------------------------------------------------------------
FROM deps AS build

WORKDIR /app
COPY . .
RUN npx ng build --configuration production

# ---------------------------------------------------------------------------
# Estágio "production" — serve o bundle estático via Nginx.
# ---------------------------------------------------------------------------
FROM nginx:1.27-alpine AS production

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/bsfarma/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
