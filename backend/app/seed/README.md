# Carga de demonstração

Popula um banco vazio com um ano de operação fictícia, mas realista, da
farmácia de uma UBS, coerente de ponta a ponta. Serve para apresentações,
desenvolvimento e análises de demanda.

```bash
python -m app.seed
```

| Opção | Efeito |
|---|---|
| sem opção | Popula o banco se ele estiver vazio. Se já houver dados, não faz nada |
| `--recriar` | **Apaga** alertas, dispensações, movimentações, lotes, pacientes, medicamentos e usuários, e gera tudo de novo |
| `--permitir-producao` | Obrigatória com `ENVIRONMENT=production`. Sem ela, o comando sai com código 2 |

Tudo roda numa transação: se algo falhar, nada é gravado.

As senhas dos usuários vêm de `SEED_SENHA_GESTOR`, `SEED_SENHA_FARMACEUTICO` e
`SEED_SENHA_ATENDENTE`. Se estiverem vazias, são geradas e exibidas uma única
vez no fim. O resumo final também lista os lotes que vencem em até 30 dias e
alguns códigos de paciente para testar uma dispensação ao vivo.

## O que é gerado

| Tabela | Volume | Origem |
|---|---|---|
| `usuario` | 3 | `gestor`, `farmaceut` e `atendente` |
| `medicamento` | 25 | Elenco da Farmácia Popular, em 9 áreas terapêuticas |
| `paciente` | 174 | 15 perfis clínicos com CID. O CPF é gerado válido, mas só o código pseudonimizado é gravado |
| `lote` | ~140 | Inventário inicial, reposições e lotes avulsos |
| `movimentacao` / `dispensacao` | ~2.500 | Uma dispensação ligada a paciente para cada saída, mais descartes, avarias e ajustes |
| `alertas` | ~14 | Gerados no fim pelo próprio `AlertaService` |

## Como a simulação funciona

A carga simula os 365 dias anteriores à execução, dia a dia.

**A demanda vem dos pacientes.** Cada paciente recebe um esquema terapêutico e
uma dose, e retira a cada ~30 dias, com variações:
- atraso aleatório na retirada;
- 7% de chance de pular um mês;
- 5% de chance de retirar dois meses de uma vez;
- 12% começam o tratamento no meio do ano;
- 8% abandonam.

Salbutamol e budesonida nasal têm uso eventual, 2,2× mais frequente de julho a
outubro, a época de queimadas e fumaça no Amazonas. As dispensações acontecem
em dias úteis, das 7h30 às 16h30 no horário de Manaus (UTC−4).

O resultado é uma demanda intermitente, com quantidades variadas: o tipo de
série para o qual servem métodos de previsão como Croston/SBA.

**O estoque segue regras de farmácia:**
- **Pedidos:** a cada ~60 dias, completando ciclo, prazo de entrega e 25 dias
  de segurança, arredondados para a embalagem.
- **Consumo:** FEFO, saindo primeiro do lote que vence antes.
- **Sem estoque:** a demanda fica sem atender e não é registrada.
- **Lote vencido:** descartado como `PERDA` alguns dias depois.
- **Inventário trimestral:** gera `AJUSTE`.
- **Estoque mínimo:** 20 dias de consumo médio.

## Cenários garantidos

Definidos em `LOTES_AVULSOS` e `DESABASTECIMENTOS`, no
[`catalogo.py`](catalogo.py). Valem para qualquer data de execução, e há testes
cobrindo os 7 dias da semana.

| Medicamentos | Cenário |
|---|---|
| Captopril, Glibenclamida, Beclometasona 50, Sinvastatina 40 | Lote com saldo **vencendo em 9 a 28 dias**, que gera alertas |
| Furosemida, Medroxiprogesterona | Lote vencido e **descartado** no histórico |
| Salbutamol, Levonorgestrel | **Excesso de estoque** que vai vencer sem uso |
| Losartana, Insulina NPH, Timolol | Entrega reduzida: **estoque crítico** ou zerado |

## Coerência com o sistema

- Para todo lote, `quantidade_atual` = `quantidade_inicial` − saídas − perdas − ajustes.
- Não há `ENTRADA` na criação do lote, igual à API. Uma entrada nesse momento
  contaria o estoque em dobro.
- Só há `AJUSTE` para baixo, porque o sistema hoje sempre subtrai ajustes.
- As dispensações têm o mesmo formato das criadas por `POST /dispensacoes`.
- Com a semente fixa (`SEMENTE_PADRAO`), a mesma data gera exatamente a mesma
  carga.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| [`catalogo.py`](catalogo.py) | Medicamentos, doses (`Uso`), perfis clínicos e cenários. É aqui que se ajusta a carga |
| [`simulacao.py`](simulacao.py) | Gera a carga em memória, sem acessar o banco. Os parâmetros ficam no topo |
| [`carga.py`](carga.py) | Gravação no banco, limpeza e verificação de alertas |
| [`__main__.py`](__main__.py) | Linha de comando, trava de produção e resumo final |

Os testes estão em `tests/unit/test_seed_simulacao.py` e em
`tests/integration/test_seed_carga.py`.
