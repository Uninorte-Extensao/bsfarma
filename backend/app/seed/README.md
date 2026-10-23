# Carga de demonstração (`python -m app.seed`)

Popula um banco vazio com dados **fictícios e realistas** de uma UBS: um ano
inteiro de operação da farmácia, coerente de ponta a ponta. Serve para
apresentar o sistema, para desenvolvimento e como base para análises de
demanda (previsão de consumo e risco de vencimento).

```bash
docker compose exec api python -m app.seed
```

Fora do Docker, a partir de `backend/`:

```bash
poetry run python -m app.seed
```

## Opções

| Uso | Efeito |
|---|---|
| `python -m app.seed` | Popula o banco se ele estiver vazio. Se já houver usuários, medicamentos ou lotes, não altera nada e sai com código 0. |
| `python -m app.seed --recriar` | **Apaga todos os dados** de `alertas`, `dispensacao`, `movimentacao`, `lote`, `paciente`, `medicamento` e `usuario` e gera a carga de novo. Útil para atualizar as datas antes de uma apresentação. |
| `python -m app.seed --permitir-producao` | Necessário quando `ENVIRONMENT=production`. Sem a flag, o comando recusa e sai com código 2. Use **só** no banco de demonstração. |

Tudo roda numa única transação. Se algo falhar, nada é gravado, nem a limpeza
do `--recriar`.

## Variáveis de ambiente

| Variável | Uso |
|---|---|
| `SEED_SENHA_GESTOR`, `SEED_SENHA_FARMACEUTICO`, `SEED_SENHA_ATENDENTE` | Senhas dos três usuários. Se ficarem vazias, cada senha é gerada aleatoriamente e exibida **uma única vez** no fim da carga. |
| `ID_INTERNO_SALT` | Chave do código pseudonimizado do paciente (HMAC do CPF), a mesma que a API usa. Em produção é obrigatória. Fora de produção, sem ela, vale o salt de desenvolvimento. |

Nenhuma senha fica no código-fonte.

## Exemplo de saída

```
Carga de demonstração concluída.

  usuários .......... 3
  medicamentos ...... 25
  pacientes ......... 174
  lotes ............. 140
  movimentações ..... 2568
  dispensações ...... 2528
  alertas criados ... 14

Lotes vencendo em até 30 dias:
  BS246805     Captopril 25 MG                     vence 01/11/2026  saldo 208
  SF247392     Glibenclamida 5 MG                  vence 09/11/2026  saldo 370
  ...

Códigos de pacientes para testar uma dispensação:
  24ADD2697C32  Hipertensão arterial sistêmica (I10)
  ...
```

Os códigos impressos servem para registrar uma dispensação ao vivo durante a
apresentação. Eles dependem do `ID_INTERNO_SALT`, então mudam de um ambiente
para outro.

## O que é gerado

| Tabela | Quantidade | Como |
|---|---|---|
| `usuario` | 3 | `gestor` (GESTOR), `farmaceut` (FARMACEUTICO), `atendente` (ATENDENTE) |
| `medicamento` | 25 | Itens reais do elenco da Farmácia Popular, cobrindo 9 áreas: hipertensão, diabetes, dislipidemia, asma, rinite, anticoncepção, osteoporose, Parkinson e glaucoma |
| `paciente` | 174 | Distribuídos em 15 perfis clínicos com CID. O CPF é gerado com dígitos verificadores válidos e **não é gravado**: só o código pseudonimizado vai para o banco |
| `lote` | cerca de 140 | Inventário de implantação, reposições periódicas e lotes avulsos (ver cenários) |
| `movimentacao` | cerca de 2.600 | Saídas por dispensação, descartes por vencimento, avarias e ajustes de inventário |
| `dispensacao` | cerca de 2.500 | Uma por saída, ligada ao paciente, como faz `POST /dispensacoes` |
| `alertas` | cerca de 14 | Gerados no fim pelo próprio `AlertaService.verificar_todos()`, com as mesmas regras do sistema |

## Como os dados são simulados

A carga não sorteia números soltos. Ela simula a operação da farmácia dia a dia,
nos 365 dias anteriores à data em que o comando roda.

### Demanda: vem dos pacientes

Cada paciente recebe um **esquema terapêutico** sorteado dentro do seu perfil
clínico. Um hipertenso pode usar só losartana, losartana com
hidroclorotiazida, anlodipino etc. A dose também é sorteada (30 ou 60
comprimidos, 1 a 3 frascos de insulina) e fica fixa para aquele paciente.

| Comportamento | Regra |
|---|---|
| Uso contínuo | Retirada a cada ~30 dias (28 para anticoncepcional oral e alendronato, 90 para injetável trimestral), com atraso aleatório de alguns dias |
| Esquecimento | 7% de chance, a cada retirada, de pular um mês |
| Retirada dobrada | 5% de chance de levar dois meses de uma vez (viagem, receita bimestral) |
| Uso eventual | Salbutamol (resgate da asma) e budesonida nasal são retirados de forma irregular, sem calendário |
| Sazonalidade | O uso eventual respiratório fica 2,2× mais frequente de julho a outubro, época de queimadas e fumaça no Acre |
| Pacientes novos | 12% começam o tratamento no meio do ano |
| Abandono | 8% param de retirar em algum momento |
| Expediente | Dispensações de segunda a sexta, das 7h30 às 16h30, no horário do Acre (UTC−5). No banco, gravadas em UTC |

Isso produz o que se vê numa UBS real: demanda **intermitente**, com
quantidades variadas por retirada. São as séries em que métodos como
Croston/SBA fazem diferença, ao contrário de séries com quantidade sempre igual.

### Estoque: reposição e FEFO

- **Implantação:** no primeiro dia da janela, cada medicamento recebe 1 ou 2
  lotes com cerca de 65 dias de consumo.
- **Reposição:** a cada ~60 dias a farmácia faz um pedido. A quantidade completa
  o estoque até cobrir o ciclo, o prazo de entrega e 25 dias de segurança,
  arredondada para a embalagem de compra. O lote chega de 5 a 12 dias depois,
  com validade de 24 ou 36 meses menos o tempo que já passou na distribuidora.
- **Consumo:** cada dispensação sai do lote que vence primeiro (FEFO). Se o lote
  não basta, o restante sai do próximo, e cada parte vira uma dispensação, como
  aconteceria no balcão. Sem estoque, a demanda fica **não atendida** e não é
  registrada.
- **Vencimento:** um lote vencido com saldo é descartado de 1 a 6 dias úteis
  depois, como `PERDA` "Descarte por vencimento".
- **Avarias:** perdas eventuais de 1 a 3 unidades (blister danificado, frasco
  quebrado, quebra da cadeia de frio da insulina).
- **Inventário trimestral:** em 3 datas do ano, alguns lotes recebem `AJUSTE`
  de 1 a 6 unidades, porque a contagem física deu abaixo do sistema.
- **Estoque mínimo** de cada medicamento: 20 dias do consumo médio simulado.

### Cenários garantidos

Para que a demonstração sempre mostre algo para cada funcionalidade, alguns
medicamentos têm situações forçadas. Elas estão definidas em
[`catalogo.py`](catalogo.py), em `LOTES_AVULSOS` e `DESABASTECIMENTOS`.

| Medicamento | Cenário | O que aparece no sistema |
|---|---|---|
| Captopril, Glibenclamida, Beclometasona 50, Sinvastatina 40 | Lote remanejado com validade curta, recebido há 2 a 3 meses | Lotes **vencendo em 9 a 28 dias** com saldo. Geram alertas de 15 e 30 dias |
| Furosemida, Medroxiprogesterona | Lote com validade curta que venceu há 1 a 2 meses | **Descarte por vencimento** no histórico (perda) |
| Salbutamol, Levonorgestrel | Compra centralizada muito acima do consumo | **Excesso de estoque** que vai vencer sem uso. É o caso de uso da previsão de demanda e do risco de vencimento |
| Losartana, Insulina NPH, Timolol | Fornecedor entregando 0% a 30% do pedido nos últimos meses | **Estoque crítico** ou zerado, e demanda não atendida |

As quantidades desses lotes são calculadas a partir da demanda simulada. Por
isso o resultado vale para **qualquer data** em que o comando rodar, e há
teste cobrindo os 7 dias da semana.

## Coerência com as regras do sistema

- **Saldo consistente.** Para todo lote, `quantidade_atual` =
  `quantidade_inicial` − (saídas + perdas + ajustes). A carga gera os
  saldos rodando a simulação, não escrevendo um número qualquer.
- **Sem movimentação de `ENTRADA` na criação do lote.** A API cria o lote com
  `quantidade_atual = quantidade_inicial` e não registra entrada. Uma
  `ENTRADA` com a quantidade inicial contaria o estoque em dobro.
- **`AJUSTE` só para baixo.** Hoje o sistema sempre subtrai ajustes
  (`movimentacao/service.py`, `_novo_saldo`) e exige quantidade positiva,
  então um ajuste para cima não é representável. A carga só usa ajustes de
  falta.
- **Dispensações iguais às da API:** justificativa "Dispensação direta ao
  paciente", uma `movimentacao` `SAIDA` mais uma `dispensacao` ligada ao
  paciente. A maioria é feita pelo atendente e o restante pelo farmacêutico.

## Reprodutibilidade

O gerador usa uma semente fixa (`SEMENTE_PADRAO` em
[`simulacao.py`](simulacao.py)): na mesma data, o resultado é idêntico,
inclusive os UUIDs. Em datas diferentes, os números mudam um pouco, porque
fins de semana deslocam as dispensações. Os cenários garantidos se mantêm.

## Como ajustar

Tudo que define a carga está em [`catalogo.py`](catalogo.py):

| Para | Altere |
|---|---|
| Incluir ou remover medicamentos | `MEDICAMENTOS`, com a embalagem de compra e a validade em meses |
| Mudar doses ou frequência | As constantes `Uso` (por exemplo `LOSARTANA`) |
| Mudar quantos pacientes há em cada condição, ou os esquemas | `PERFIS_CLINICOS` |
| Criar ou mudar cenários | `LOTES_AVULSOS` (chegada e validade em dias relativos a hoje, sobra em dias de consumo) e `DESABASTECIMENTOS` |

Os parâmetros da simulação (janela, ciclo de pedido, probabilidades) ficam
no topo de [`simulacao.py`](simulacao.py).

## Estrutura

| Arquivo | Papel |
|---|---|
| [`catalogo.py`](catalogo.py) | Dados de entrada: usuários, medicamentos, esquemas, perfis clínicos e cenários |
| [`simulacao.py`](simulacao.py) | Gera a carga completa em memória. É puro: não acessa banco e é testável isoladamente |
| [`carga.py`](carga.py) | Verifica se o banco está vazio, limpa (`--recriar`), insere em lotes de 1.000 linhas e roda a verificação de alertas |
| [`__main__.py`](__main__.py) | Linha de comando: opções, trava de produção, senhas e resumo final |

Testes: `tests/unit/test_seed_simulacao.py` (propriedades da carga gerada) e
`tests/integration/test_seed_carga.py` (gravação no banco de teste).

## Histórico

Este comando substituiu os 6 seeders por módulo (`python -m app.<modulo>.seeder`),
removidos em 2026-10-23. Eles tinham senhas fixas no código, não tinham trava
de produção (B-1 em [`deploy/PRE-PUBLICACAO.md`](../../../deploy/PRE-PUBLICACAO.md)),
usavam datas fixas de 2024 e 2025 e geravam saldos que não batiam com o
histórico de movimentações.
