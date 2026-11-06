import argparse
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from app.core.fuso import hoje_ubs
from app.paciente.service import gerar_codigo
from app.previsao.avaliacao import (
    SEMANAS_TESTE,
    PrevisaoRisco,
    avaliar_previsao,
    avaliar_risco,
    historico,
    previsao_proxima_semana,
    resumo_por_classe,
    validar_risco,
)
from app.previsao.metodos import ALFA_PADRAO, BETA_PADRAO, METODOS
from app.seed.simulacao import SEMENTE_PADRAO, gerar_carga

ANTECEDENCIA_TABELA = 56
PROB_MINIMA_RISCO = 0.05


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m app.previsao",
        description="Demonstração de previsão de demanda (Croston/SBA/TSB) e risco de vencimento.",
    )
    parser.add_argument("--hoje", type=date.fromisoformat, default=None,
                        help="data de referência da carga (AAAA-MM-DD). Padrão: hoje em Manaus")
    parser.add_argument("--saida", type=Path, default=None,
                        help="arquivo .md para o relatório. Padrão: imprime na tela")
    return parser.parse_args(argv)


def _n(valor: float, casas: int = 1) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(valor: float) -> str:
    return f"{valor * 100:.0f}%"


def _tabela(cabecalho: list[str], linhas: list[list[str]]) -> list[str]:
    alinhamento = ["---"] + ["---:"] * (len(cabecalho) - 1)
    return [
        "| " + " | ".join(cabecalho) + " |",
        "|" + "|".join(alinhamento) + "|",
        *("| " + " | ".join(l) + " |" for l in linhas),
        "",
    ]


def _secao_previsao(meds) -> list[str]:
    resultados = [r for m in meds if (r := avaliar_previsao(m))]
    classes = Counter(r.classificacao.classe for r in resultados)
    linhas = []
    for r in sorted(resultados, key=lambda r: (r.classificacao.adi < 1.32, r.medicamento)):
        c = r.classificacao
        melhor = min(r.mae, key=r.mae.get)
        relativos = [
            (f"**{_n(r.mae[k] / r.mae['Média'], 2)}**" if k == melhor else _n(r.mae[k] / r.mae["Média"], 2))
            if r.mae["Média"] > 0 else "–"
            for k in METODOS
        ]
        linhas.append([r.medicamento, c.classe, _n(c.adi, 2), _n(c.cv2, 2), _n(r.media_teste), *relativos])

    resumo = resumo_por_classe(resultados)
    linhas_resumo = [
        [grupo, str(int(v["_n"])), *(_n(v[k], 3) for k in METODOS)]
        for grupo, v in sorted(resumo.items(), key=lambda kv: kv[0] == "todos")
    ]
    vitorias = Counter(min(r.mae, key=r.mae.get) for r in resultados)

    return [
        "## 1. Classificação e comparação dos métodos",
        "",
        f"Série semanal de saídas de cada medicamento. As primeiras semanas treinam; as últimas "
        f"{SEMANAS_TESTE} testam, sempre prevendo uma semana à frente só com o passado. "
        f"Parâmetros fixos: α = {_n(ALFA_PADRAO, 2)}, β (TSB) = {_n(BETA_PADRAO, 2)}.",
        "",
        "Classes (Syntetos-Boylan): " + ", ".join(f"{n} {c}" for c, n in classes.most_common()) + ".",
        "",
        "Erro de cada método dividido pelo erro da média simples (MAE relativo). "
        "Abaixo de 1 é melhor que a média; o melhor de cada linha está em negrito.",
        "",
        *_tabela(["Medicamento", "Classe", "ADI", "CV²", "Média/sem. (teste)", *METODOS], linhas),
        "Resumo por grupo (média geométrica do MAE relativo):",
        "",
        *_tabela(["Grupo", "Séries", *METODOS], linhas_resumo),
        "Vitórias por método: " + ", ".join(f"{k} {vitorias.get(k, 0)}" for k in METODOS) + ".",
        "",
    ]


def _secao_censura(meds) -> list[str]:
    linhas = []
    for med in meds:
        observado = avaliar_previsao(med)
        if not observado:
            continue
        real = avaliar_previsao(med, alvo="demanda_real", treino="demanda_real")
        nao_atendida = real.media_teste - observado.media_teste
        if nao_atendida <= 0.01:
            continue
        com_saidas = previsao_proxima_semana(med, "saidas")
        com_real = previsao_proxima_semana(med, "demanda_real")
        linhas.append([
            med.nome, _n(real.media_teste), _n(observado.media_teste),
            _pct(nao_atendida / real.media_teste),
            _n(com_saidas), _n(com_real), _pct(1 - com_saidas / com_real),
        ])
    if not linhas:
        return []
    return [
        "## 2. Demanda censurada: o que o sistema não vê",
        "",
        "Quando falta estoque, o paciente volta para casa sem o medicamento e nada é registrado. "
        f"A simulação conhece a demanda real; o sistema só vê as saídas. Médias das últimas "
        f"{SEMANAS_TESTE} semanas e previsão SBA para a próxima semana, treinada em cada fonte.",
        "",
        *_tabela(["Medicamento", "Demanda real/sem.", "Saídas/sem.", "Não atendida",
                  "Previsão com saídas", "Previsão com demanda real", "Subestimação"], linhas),
    ]


def _brier(previsoes: list[PrevisaoRisco], probabilidade) -> float:
    return float(np.mean([(probabilidade(p) - (p.perda_real > 0)) ** 2 for p in previsoes]))


def _secao_validacao_risco(meds) -> list[str]:
    previsoes = validar_risco(meds)
    if not previsoes:
        return []
    reais = np.array([p.perda_real for p in previsoes], dtype=float)
    simuladas = np.array([p.simulado.perda_esperada for p in previsoes])
    projetadas = np.array([p.projetado for p in previsoes])
    sem_modelo = np.array([p.saldo for p in previsoes], dtype=float)
    lotes = {(p.medicamento, p.lote) for p in previsoes}

    escolhidas = {}
    for p in previsoes:
        chave = (p.medicamento, p.lote)
        alvo = p.validade_dia - ANTECEDENCIA_TABELA
        if chave not in escolhidas or abs(p.corte - alvo) < abs(escolhidas[chave].corte - alvo):
            escolhidas[chave] = p
    linhas = [
        [p.medicamento, p.lote, str(p.validade_dia - p.corte), _n(p.saldo, 0),
         _pct(p.simulado.prob_perda), _n(p.simulado.perda_esperada, 0),
         _n(p.simulado.perda_p90, 0), _n(p.perda_real, 0)]
        for p in sorted(escolhidas.values(), key=lambda p: p.validade_dia)
    ]
    return [
        "## 3. Validação do risco de vencimento",
        "",
        "O modelo volta no tempo: a cada 14 dias do histórico, olha só o que se sabia naquele dia "
        "(saldos e saídas), simula 10.000 futuros de demanda com consumo FEFO e prevê quanto de cada "
        "lote vai vencer. Depois compara com o que realmente foi descartado por vencimento.",
        "",
        f"{len(previsoes)} previsões sobre {len(lotes)} lotes que venceram no histórico.",
        "",
        *_tabela(["Critério", "Monte Carlo", "Projeção linear", "Sem modelo (perde tudo)"], [
            ["Erro médio por previsão (unidades)", _n(np.mean(np.abs(simuladas - reais))),
             _n(np.mean(np.abs(projetadas - reais))), _n(np.mean(np.abs(sem_modelo - reais)))],
            ["Perda total prevista × real", f"{_n(simuladas.sum(), 0)} × {_n(reais.sum(), 0)}",
             f"{_n(projetadas.sum(), 0)} × {_n(reais.sum(), 0)}",
             f"{_n(sem_modelo.sum(), 0)} × {_n(reais.sum(), 0)}"],
            ["Brier: acerto de \"vai perder algo?\" (0 = perfeito)",
             _n(_brier(previsoes, lambda p: p.simulado.prob_perda), 3),
             _n(_brier(previsoes, lambda p: float(p.projetado > 0)), 3), "–"],
            ["Perda real ≤ p90 (ideal: perto de 90%)",
             _pct(np.mean([p.perda_real <= p.simulado.perda_p90 for p in previsoes])), "–", "–"],
        ]),
        f"Previsão de cada lote feita cerca de {ANTECEDENCIA_TABELA} dias antes do vencimento:",
        "",
        *_tabela(["Medicamento", "Lote", "Dias até vencer", "Saldo", "P(perda)",
                  "Perda esperada", "Perda p90", "Perda real"], linhas),
    ]


def _secao_risco_atual(meds, hoje: date) -> list[str]:
    rng = np.random.default_rng(0)
    riscos = [p for med in meds for p in avaliar_risco(med, 0, rng=rng)
              if p.simulado.prob_perda >= PROB_MINIMA_RISCO]
    riscos.sort(key=lambda p: -p.simulado.perda_esperada)
    linhas = [
        [p.medicamento, p.lote, f"{hoje + timedelta(days=p.validade_dia):%d/%m/%Y}", _n(p.saldo, 0),
         _pct(p.simulado.prob_perda), _n(p.simulado.perda_esperada, 0), _n(p.simulado.perda_p90, 0)]
        for p in riscos
    ]
    total = sum(p.simulado.perda_esperada for p in riscos)
    return [
        "## 4. Risco de vencimento hoje",
        "",
        f"Lotes com pelo menos {_pct(PROB_MINIMA_RISCO)} de chance de vencer com saldo. "
        f"Perda esperada somada: {_n(total, 0)} unidades.",
        "",
        *_tabela(["Medicamento", "Lote", "Validade", "Saldo", "P(perda)", "Perda esperada", "Perda p90"], linhas),
    ]


def gerar_relatorio(hoje: date) -> str:
    carga = gerar_carga(hoje, gerar_codigo)
    meds = historico(carga)
    linhas = [
        "# Previsão de demanda e risco de vencimento",
        "",
        f"Carga de demonstração com data de referência {hoje:%d/%m/%Y} e semente {SEMENTE_PADRAO}: "
        f"{len(carga.medicamentos)} medicamentos, {len(carga.pacientes)} pacientes, "
        f"{len(carga.dispensacoes)} dispensações e {len(carga.lotes)} lotes em 365 dias.",
        "",
        "Gerado por `python -m app.previsao`. O método está explicado em "
        "[`app/previsao/README.md`](README.md).",
        "",
        *_secao_previsao(meds),
        *_secao_censura(meds),
        *_secao_validacao_risco(meds),
        *_secao_risco_atual(meds, hoje),
    ]
    return "\n".join(linhas)


def main(argv: list[str] | None = None) -> int:
    args = _argumentos(argv)
    relatorio = gerar_relatorio(args.hoje or hoje_ubs())
    if args.saida:
        args.saida.write_text(relatorio, encoding="utf-8", newline="\n")
        print(f"Relatório gravado em {args.saida}")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(relatorio)
    return 0


if __name__ == "__main__":
    sys.exit(main())
