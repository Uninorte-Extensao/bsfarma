# Publicação com HTTPS numa VM

Roteiro para publicar o BSFarma em qualquer VM Linux com Docker, usando domínio
próprio e certificado HTTPS automático.

```
internet ──▶ Caddy (:80/:443) ──▶ Nginx (Angular + /api) ──▶ API ──▶ Supabase
```

- [`docker-compose.https.yml`](docker-compose.https.yml) complementa o
  `docker-compose.prod.yml`, que não muda. Ele adiciona o Caddy e tira o Nginx
  da porta pública.
- O [`Caddyfile`](Caddyfile) emite e renova o certificado Let's Encrypt,
  redireciona HTTP para HTTPS e adiciona cabeçalhos de segurança: HSTS,
  `nosniff`, `X-Frame-Options` e `Referrer-Policy`.

## 1. Pré-requisitos

- **VM:** Ubuntu 22.04 ou 24.04, com IPv4 público, SSH e **2 GB de RAM ou
  mais**. Com menos, ative a swap do passo 3.
- **Firewall do provedor:** TCP 22, 80 e 443 liberados.
- **DNS:** um registro `A` do domínio (ou subdomínio) apontando para o IP da
  VM. **Não crie `AAAA`**, a menos que a VM sirva por IPv6; senão, a emissão do
  certificado falha. Para conferir, `getent hosts seu.dominio` deve mostrar o IP
  da VM.

## 2. Docker

```bash
curl -fsSL https://get.docker.com | sudo sh && sudo usermod -aG docker "$USER"
```

Saia e entre de novo no SSH. Depois confira a versão: o Compose precisa ser
**2.24.4 ou mais novo**, por causa do `!reset`.

```bash
docker compose version
```

## 3. Firewall e swap

```bash
sudo ufw allow OpenSSH && sudo ufw allow 80/tcp && sudo ufw allow 443 && sudo ufw --force enable
```

Swap, necessária com menos de 4 GB de RAM:

```bash
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile && echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 4. Código e configuração

```bash
git clone https://github.com/Uninorte-Extensao/bsfarma.git && cd bsfarma
```

Crie o `.env` da raiz. Ele existe **só no servidor**. O `COMPOSE_FILE` faz todo
`docker compose` deste diretório usar os dois arquivos juntos.

```bash
printf 'DOMINIO=seu.dominio\nCOMPOSE_FILE=docker-compose.prod.yml:deploy/docker-compose.https.yml\n' > .env
```

```bash
cp backend/.env.example backend/.env && chmod 600 backend/.env && nano backend/.env
```

| Variável | Valor em produção |
|---|---|
| `DATABASE_URL` | No Supabase, em *Connect*, copie a do **Session pooler** e troque `postgresql://` por `postgresql+asyncpg://`. A conexão direta só funciona por IPv6. Caracteres especiais na senha precisam ser codificados na URL |
| `SECRET_KEY`, `ID_INTERNO_SALT` | `openssl rand -hex 32`, uma para cada. O salt **não pode mudar** depois que houver pacientes cadastrados |
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS` | Vazio. Frontend e API ficam na mesma origem |
| `SEED_SENHA_*` | Senhas dos usuários da demonstração |

## 5. Build, banco e dados

```bash
docker compose build
```

Se o build do frontend for encerrado com `137`, faltou memória.

```bash
docker compose run --rm api alembic upgrade head
```

```bash
docker compose run --rm api alembic check
```

O esperado é `No new upgrade operations detected.`

```bash
docker compose run --rm api python -m app.seed --permitir-producao
```

A carga de demonstração não faz nada se o banco já tiver dados. Use
`--recriar` para gerar de novo com as datas de hoje.

## 6. Subir e verificar

```bash
docker compose up -d && docker compose logs -f caddy
```

Espere pela linha `certificate obtained successfully` e saia com `Ctrl+C`.
Depois, `docker compose ps` deve mostrar o `api` como `healthy`.

```bash
curl -sI http://seu.dominio | head -1
```

O esperado é `308 Permanent Redirect`.

```bash
curl -s https://seu.dominio/api/health
```

No navegador:
- [ ] cadeado sem aviso;
- [ ] login com os três perfis;
- [ ] F5 numa rota interna não dá 404;
- [ ] uma dispensação com um código de paciente impresso pela carga baixa o
  saldo do lote.

Depois, registre a URL no topo do `README.md`.

## Operação

| Tarefa | Comando |
|---|---|
| Atualizar | `git pull && docker compose up -d --build` |
| Aplicar migrations novas | `docker compose run --rm api alembic upgrade head` |
| Renovar os dados da demonstração | `docker compose run --rm api python -m app.seed --permitir-producao --recriar` |
| Ver logs | `docker compose logs -f api` (ou `web`, `caddy`) |

O Caddy renova o certificado sozinho. Não apague o volume `caddy_data` sem
necessidade: reemitir muitas vezes esbarra no limite do Let's Encrypt.

**Para encerrar:**
1. `docker compose down -v`;
2. destrua a VM no painel do provedor (só desligar continua cobrando);
3. remova o registro DNS.

Os dados ficam no Supabase.

## Problemas comuns

| Sintoma | Causa provável |
|---|---|
| Caddy com `challenge failed` ou `timeout` | DNS ainda não propagou, porta 80/443 fechada no provedor, ou `AAAA` errado |
| Caddy com `rateLimited` | Muitas falhas seguidas no Let's Encrypt. Corrija e espere 1 hora |
| Erro com `!reset` | Compose anterior à versão 2.24.4 |
| `DOMINIO` não definido | Comando rodado fora do diretório `bsfarma`, ou falta o `.env` da raiz |
| `api` reiniciando | `docker compose logs api`. Em geral: falta `+asyncpg` na URL, conexão direta em vez do pooler (`Network is unreachable`), ou senha sem codificar |
| `ID_INTERNO_SALT não configurado` | Variável vazia com `ENVIRONMENT=production` |
