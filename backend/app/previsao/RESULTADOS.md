# Previsão de demanda e risco de vencimento

Carga de demonstração com data de referência 31/12/2026 e semente 20261023: 25 medicamentos, 174 pacientes, 2500 dispensações e 140 lotes em 365 dias.

Gerado por `python -m app.previsao`. O método está explicado em [`app/previsao/README.md`](README.md).

## 1. Classificação e comparação dos métodos

Série semanal de saídas de cada medicamento. As primeiras semanas treinam; as últimas 13 testam, sempre prevendo uma semana à frente só com o passado. Parâmetros fixos: α = 0,10, β (TSB) = 0,05.

Classes (Syntetos-Boylan): 13 intermitente, 12 suave.

Erro de cada método dividido pelo erro da média simples (MAE relativo). Abaixo de 1 é melhor que a média; o melhor de cada linha está em negrito.

| Medicamento | Classe | ADI | CV² | Média/sem. (teste) | Média | SES | Croston | SBA | TSB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Acetato De Medroxiprogesterona 150 MG | intermitente | 2,17 | 0,19 | 0,5 | 1,00 | 1,07 | 0,99 | **0,98** | 1,01 |
| Alendronato De Sódio 70 MG | intermitente | 1,39 | 0,18 | 5,8 | 1,00 | 0,99 | 0,98 | 1,00 | **0,97** |
| Atenolol 25 MG | intermitente | 3,00 | 0,10 | 18,5 | 1,00 | 1,00 | **0,99** | 1,00 | 1,00 |
| Budesonida 50 MCG | intermitente | 1,34 | 0,25 | 1,3 | **1,00** | 1,19 | 1,21 | 1,15 | 1,18 |
| Captopril 25 MG | intermitente | 1,44 | 0,31 | 62,3 | **1,00** | 1,05 | 1,06 | 1,04 | 1,06 |
| Carbidopa (Port. 344/98 Lista C 1);Levodopa 25 MG + 250 MG | intermitente | 2,60 | 0,29 | 48,5 | 1,00 | 1,01 | 1,00 | **0,99** | 1,02 |
| Dipropionato De Beclometasona 200 MCG | intermitente | 3,00 | 0,06 | 0,5 | 1,00 | 1,05 | 0,99 | **0,99** | 1,02 |
| Dipropionato De Beclometasona 50 MCG | intermitente | 1,77 | 0,25 | 1,2 | 1,00 | 1,01 | 0,99 | 1,00 | **0,98** |
| Insulina Humana 100 UI/ML (Humulin R) | intermitente | 1,44 | 0,19 | 1,1 | **1,00** | 1,03 | 1,03 | 1,01 | 1,04 |
| Levonorgestrel;Etinilestradiol 0,15 MG + 0,03 MG | intermitente | 1,62 | 0,39 | 2,3 | 1,00 | 1,04 | **1,00** | 1,00 | 1,01 |
| Maleato De Timolol 5 MG/ML | intermitente | 1,95 | 0,23 | 0,2 | 1,00 | **0,89** | 1,09 | 1,06 | 1,02 |
| Noretisterona 0,35 MG | intermitente | 1,56 | 0,37 | 1,4 | 1,00 | 1,06 | 1,03 | **0,99** | 0,99 |
| Sulfato De Salbutamol 100 MCG | intermitente | 1,62 | 0,38 | 0,8 | **1,00** | 1,12 | 1,06 | 1,02 | 1,05 |
| Besilato De Anlodipino 5 MG | suave | 1,03 | 0,24 | 126,9 | **1,00** | 1,03 | 1,03 | 1,08 | 1,04 |
| Cloridrato De Metformina 500 MG | suave | 1,30 | 0,26 | 136,2 | 1,00 | 1,07 | 1,04 | **1,00** | 1,09 |
| Cloridrato De Metformina 850 MG | suave | 1,00 | 0,07 | 570,0 | **1,00** | 1,03 | 1,03 | 1,02 | 1,03 |
| Dapagliflozina 10 MG | suave | 1,30 | 0,10 | 32,3 | 1,00 | 1,01 | 1,01 | **0,99** | 1,02 |
| Furosemida 40 MG | suave | 1,30 | 0,16 | 30,0 | 1,00 | 1,04 | 1,02 | **1,00** | 1,04 |
| Glibenclamida 5 MG | suave | 1,05 | 0,20 | 136,2 | **1,00** | 1,04 | 1,04 | 1,05 | 1,04 |
| Hidroclorotiazida 25 MG | suave | 1,11 | 0,42 | 73,8 | **1,00** | 1,02 | 1,05 | 1,04 | 1,03 |
| Insulina Humana 100 UI/ML (Humulin N) | suave | 1,11 | 0,30 | 2,3 | 1,00 | **0,93** | 0,99 | 0,95 | 0,97 |
| Losartana Potássica 50 MG | suave | 1,00 | 0,14 | 208,7 | 1,00 | **0,98** | 1,00 | 1,00 | 1,00 |
| Maleato De Enalapril 10 MG | suave | 1,30 | 0,22 | 147,7 | **1,00** | 1,06 | 1,03 | 1,02 | 1,04 |
| Sinvastatina 20 MG | suave | 1,11 | 0,26 | 71,5 | **1,00** | 1,05 | 1,03 | 1,04 | 1,04 |
| Sinvastatina 40 MG | suave | 1,03 | 0,30 | 73,8 | **1,00** | 1,05 | 1,05 | 1,05 | 1,05 |

Resumo por grupo (média geométrica do MAE relativo):

| Grupo | Séries | Média | SES | Croston | SBA | TSB |
|---|---:|---:|---:|---:|---:|---:|
| intermitente/irregular | 13 | 1,000 | 1,038 | 1,031 | 1,017 | 1,027 |
| suave/errática | 12 | 1,000 | 1,025 | 1,027 | 1,019 | 1,032 |
| todos | 25 | 1,000 | 1,032 | 1,029 | 1,018 | 1,029 |

Vitórias por método: Média 11, SES 3, Croston 2, SBA 7, TSB 2.

## 2. Demanda censurada: o que o sistema não vê

Quando falta estoque, o paciente volta para casa sem o medicamento e nada é registrado. A simulação conhece a demanda real; o sistema só vê as saídas. Médias das últimas 13 semanas e previsão SBA para a próxima semana, treinada em cada fonte.

| Medicamento | Demanda real/sem. | Saídas/sem. | Não atendida | Previsão com saídas | Previsão com demanda real | Subestimação |
|---|---:|---:|---:|---:|---:|---:|
| Insulina Humana 100 UI/ML (Humulin N) | 3,4 | 2,3 | 32% | 2,7 | 3,5 | 22% |
| Losartana Potássica 50 MG | 336,9 | 208,7 | 38% | 235,3 | 310,7 | 24% |
| Maleato De Timolol 5 MG/ML | 0,9 | 0,2 | 75% | 0,7 | 0,8 | 14% |

## 3. Validação do risco de vencimento

O modelo volta no tempo: a cada 14 dias do histórico, olha só o que se sabia naquele dia (saldos e saídas), simula 10.000 futuros de demanda com consumo FEFO e prevê quanto de cada lote vai vencer. Depois compara com o que realmente foi descartado por vencimento.

50 previsões sobre 10 lotes que venceram no histórico.

| Critério | Monte Carlo | Projeção linear | Sem modelo (perde tudo) |
|---|---:|---:|---:|
| Erro médio por previsão (unidades) | 10,0 | 9,7 | 44,4 |
| Perda total prevista × real | 1.933 × 1.500 | 1.922 × 1.500 | 3.721 × 1.500 |
| Brier: acerto de "vai perder algo?" (0 = perfeito) | 0,062 | 0,060 | – |
| Perda real ≤ p90 (ideal: perto de 90%) | 100% | – | – |

Previsão de cada lote feita cerca de 56 dias antes do vencimento:

| Medicamento | Lote | Dias até vencer | Saldo | P(perda) | Perda esperada | Perda p90 | Perda real |
|---|---:|---:|---:|---:|---:|---:|---:|
| Budesonida 50 MCG | AD243670 | 50 | 12 | 100% | 7 | 9 | 0 |
| Captopril 25 MG | BS245166 | 84 | 220 | 0% | 0 | 0 | 0 |
| Acetato De Medroxiprogesterona 150 MG | PB245520 | 57 | 7 | 96% | 4 | 6 | 4 |
| Dipropionato De Beclometasona 200 MCG | CF249688 | 59 | 15 | 100% | 13 | 14 | 11 |
| Alendronato De Sódio 70 MG | MS241073 | 62 | 24 | 0% | 0 | 0 | 0 |
| Alendronato De Sódio 70 MG | MS241338 | 63 | 97 | 100% | 59 | 69 | 66 |
| Acetato De Medroxiprogesterona 150 MG | PB246674 | 61 | 13 | 100% | 9 | 11 | 7 |
| Dipropionato De Beclometasona 200 MCG | CF248263 | 51 | 10 | 100% | 8 | 9 | 3 |
| Furosemida 40 MG | SF249828 | 60 | 519 | 100% | 261 | 369 | 159 |
| Atenolol 25 MG | EL244946 | 54 | 18 | 3% | 1 | 0 | 0 |

## 4. Risco de vencimento hoje

Lotes com pelo menos 5% de chance de vencer com saldo. Perda esperada somada: 480 unidades.

| Medicamento | Lote | Validade | Saldo | P(perda) | Perda esperada | Perda p90 |
|---|---:|---:|---:|---:|---:|---:|
| Atenolol 25 MG | EL250072 | 24/02/2027 | 308 | 100% | 194 | 248 |
| Captopril 25 MG | BS250779 | 09/01/2027 | 208 | 86% | 141 | 208 |
| Levonorgestrel;Etinilestradiol 0,15 MG + 0,03 MG | BS253340 | 11/03/2027 | 79 | 100% | 58 | 68 |
| Glibenclamida 5 MG | SF252311 | 17/01/2027 | 370 | 56% | 48 | 160 |
| Sulfato De Salbutamol 100 MCG | GB252899 | 05/04/2027 | 52 | 100% | 37 | 44 |
| Dipropionato De Beclometasona 50 MCG | CF257504 | 24/01/2027 | 7 | 74% | 2 | 5 |
| Sulfato De Salbutamol 100 MCG | GB254400 | 26/07/2027 | 11 | 12% | 0 | 1 |
