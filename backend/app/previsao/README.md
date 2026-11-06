# Previsão de demanda e risco de vencimento

Demonstração da feature de IA do BSFarma. A partir do histórico de saídas,
prevê a demanda de cada medicamento e estima, lote a lote, quanto vai vencer
na prateleira antes de ser dispensado.

```bash
python -m app.previsao --hoje 2026-10-30 --saida app/previsao/RESULTADOS.md
```

| Opção | Efeito |
|---|---|
| `--hoje` | Data de referência da carga simulada. Padrão: hoje em Manaus |
| `--saida` | Grava o relatório em Markdown. Sem ela, imprime na tela |

Não usa o banco: gera a [carga de demonstração](../seed/README.md) em memória,
com a mesma semente, e analisa. Com a mesma data, o resultado é sempre o mesmo.
O relatório de referência está em [`RESULTADOS.md`](RESULTADOS.md).

## Por que Croston

A farmácia de uma UBS tem muitos itens de **demanda intermitente**: semanas sem
nenhuma saída, intercaladas com saídas de tamanho variável. Médias móveis e
suavização exponencial (SES) tratam os zeros como queda de demanda e oscilam.

O método de Croston (1972) separa a série em duas e atualiza as duas **só
quando há demanda**:

- **z**, o tamanho típico de uma saída;
- **p**, o intervalo típico entre saídas, em semanas.

A previsão por semana é `z / p`. Variantes implementadas em
[`metodos.py`](metodos.py):

| Método | Ideia |
|---|---|
| Média | Média de todo o histórico. É a referência |
| SES | Suavização exponencial simples, α = 0,1 |
| Croston | `z / p`, com z e p suavizados por α = 0,1 |
| SBA | Croston × (1 − α/2). Corrige o viés para cima do Croston (Syntetos e Boylan, 2005) |
| TSB | Troca o intervalo por uma probabilidade de demanda, atualizada **toda** semana com β = 0,05. Detecta quando um item para de sair (Teunter, Syntetos e Babai, 2011) |

## Classificação da demanda

[`classificacao.py`](classificacao.py) usa a classificação de Syntetos e
Boylan, com duas medidas:

- **ADI**: intervalo médio entre semanas com demanda;
- **CV²**: variabilidade do tamanho das saídas.

| | CV² < 0,49 | CV² ≥ 0,49 |
|---|---|---|
| **ADI < 1,32** | suave | errática |
| **ADI ≥ 1,32** | intermitente | irregular |

## Risco de vencimento

[`risco.py`](risco.py) faz uma simulação de Monte Carlo para cada medicamento:

1. Parte dos lotes com saldo no dia da análise.
2. Sorteia 10.000 futuros de demanda semanal. A chance de haver saída numa
   semana vem do SBA, e o tamanho é sorteado entre as saídas reais das últimas
   26 semanas.
3. Consome os lotes em **FEFO**, primeiro o que vence antes. Um lote vencido não
   é mais usado.
4. O que sobra em cada lote na data de validade é a perda.

O resultado por lote é a perda esperada, o percentil 90 e a probabilidade de
perder alguma unidade. Para comparar, a **projeção linear** faz a mesma conta
com um consumo fixo, igual à previsão média.

## Como os resultados são validados

**Previsão.** As últimas 13 semanas ficam de fora do treino. Em cada uma, cada
método prevê a semana seguinte usando só o passado. O erro (MAE) é dividido pelo
erro da média simples: abaixo de 1, o método ganhou da média.

**Risco.** O modelo volta no tempo de 14 em 14 dias, entre 308 e 28 dias antes
da data de referência. Em cada ponto, vê apenas os saldos e as saídas
conhecidos até ali e prevê a perda dos lotes que vencem nos 84 dias seguintes.
Depois, compara com o que foi de fato descartado por vencimento (`PERDA` com
justificativa "Descarte por vencimento").

**Demanda censurada.** A carga registra também a demanda que ficou sem
atender por falta de estoque (`CargaDemo.demanda`). Isso permite comparar a
previsão treinada no que o sistema vê com a treinada na demanda real.

## O que os resultados mostram

Números de [`RESULTADOS.md`](RESULTADOS.md), com data de referência 30/10/2026.

1. **Na previsão semanal, nenhum método ganha da média de forma relevante.** Em
   média, todos ficam até 3% acima dela, e a média vence em 12 dos 24
   medicamentos. É o esperado com a demanda simulada, que é estável: pacientes
   crônicos retiram todo mês, sem tendência. Croston, SBA e TSB ganham quando a
   demanda muda de patamar ou some. O teste
   `test_tsb_tende_a_zero_quando_a_demanda_para_e_croston_nao` mostra esse caso.
   Para o produto, a conclusão é que a escolha do método pesa pouco: o valor
   está no que se faz com a previsão.

2. **A falta de estoque esconde a demanda.** Na Losartana, 34% da procura das
   últimas 13 semanas não foi atendida, e a previsão treinada nas saídas fica
   28% abaixo da real. Na Insulina NPH, 22%. Um sistema que só olha as saídas
   compra pouco e perpetua a falta. Registrar a demanda não atendida é uma
   melhoria de produto com efeito direto na previsão.

3. **O risco de vencimento acerta a ordem de grandeza.** Foram 48 previsões
   sobre 11 lotes que venceram no histórico:
   - **Erro médio:** 11,7 unidades por previsão. Sem modelo, assumindo que tudo
     vence, o erro é 58,5.
   - **Perda real ≤ p90:** em 85% das previsões, perto dos 90% esperados.
   - **Perda total:** prevista em 2.417 unidades, contra 2.026 reais. A maior
     diferença é a Furosemida, cuja demanda subiu de 30 para 41 por semana
     durante a vida do lote. Um modelo que só olha o passado não antecipa isso.

4. **Monte Carlo × projeção linear.** Nos lotes da validação, a perda esperada
   das duas é praticamente igual. A diferença está nos lotes duvidosos. Hoje, o
   lote de Glibenclamida tem 56% de chance de perda, e o de Atenolol 57%. A
   projeção linear só responde sim ou não; o Monte Carlo informa a chance e o
   pior caso plausível (p90). Isso ajuda a priorizar remanejamentos.

5. **Hoje**, 9 lotes têm pelo menos 5% de chance de perda, com 352 unidades em
   risco. O maior caso é o Captopril: 208 unidades vencem em 9 dias, com perda
   esperada de 140.

## Limitações

- **Dados simulados.** Os cenários de vencimento e de excesso foram plantados
  pelo [`catalogo.py`](../seed/catalogo.py). O modelo os encontra, mas não foi
  testado com dados reais de uma UBS.
- **Avarias e ajustes de inventário não são simulados no futuro.** Em lotes
  pequenos, como o Salbutamol GB247130, isso faz a perda prevista passar da real.
- **Reposições futuras são ignoradas.** Lotes que ainda vão chegar só
  competiriam pelo consumo se vencessem antes dos atuais, o que é raro.
- **Parâmetros fixos**, α = 0,1 e β = 0,05, sem otimização por medicamento.
- **Sem preço.** A perda está em unidades. Com o preço unitário, por exemplo do
  Banco de Preços em Saúde, vira valor em reais.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| [`metodos.py`](metodos.py) | Média, SES, Croston, SBA e TSB. Cada um devolve a previsão um passo à frente para todos os períodos |
| [`classificacao.py`](classificacao.py) | ADI, CV² e classe |
| [`risco.py`](risco.py) | Monte Carlo e projeção linear com consumo FEFO |
| [`avaliacao.py`](avaliacao.py) | Séries semanais a partir da carga, validação da previsão e do risco |
| [`__main__.py`](__main__.py) | Linha de comando e relatório |

Os testes estão em `tests/unit/test_previsao_metodos.py` e
`tests/unit/test_previsao_risco.py`.

## Referências

- Croston, J. D. (1972). Forecasting and stock control for intermittent demands. *Operational Research Quarterly*, 23(3), 289–303.
- Syntetos, A. A.; Boylan, J. E. (2005). The accuracy of intermittent demand estimates. *International Journal of Forecasting*, 21(2), 303–314.
- Syntetos, A. A.; Boylan, J. E.; Croston, J. D. (2005). On the categorization of demand patterns. *Journal of the Operational Research Society*, 56(5), 495–503.
- Teunter, R. H.; Syntetos, A. A.; Babai, M. Z. (2011). Intermittent demand: linking forecasting to inventory obsolescence. *European Journal of Operational Research*, 214(3), 606–615.
