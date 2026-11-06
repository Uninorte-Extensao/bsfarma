from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime

import numpy as np

from app.core.fuso import FUSO_UBS
from app.movimentacao.model import TipoMovimentacao
from app.previsao.classificacao import Classificacao, classificar
from app.previsao.metodos import METODOS
from app.previsao.risco import DIAS_SEMANA, LoteEstoque, RiscoLote, projetar_perdas, simular_perdas
from app.seed.simulacao import CargaDemo

SEMANAS_TESTE = 13
SEMANAS_MINIMAS = 8
JANELA_TAMANHOS = 26
PREFIXO_DESCARTE = "Descarte por vencimento"


@dataclass
class LoteHistorico:
    id: str
    numero: str
    entrada_dia: int
    validade_dia: int
    quantidade_inicial: int
    movimentos: list[tuple[int, TipoMovimentacao, int, str]] = field(default_factory=list)

    def saldo_em(self, dia: int) -> int:
        return self.quantidade_inicial - sum(q for d, _, q, _ in self.movimentos if d < dia)

    def perda_por_vencimento(self) -> int:
        return sum(q for _, tipo, q, j in self.movimentos
                   if tipo == TipoMovimentacao.PERDA and j.startswith(PREFIXO_DESCARTE))


@dataclass
class MedicamentoHistorico:
    id: str
    nome: str
    inicio: int = 0
    saidas: list[tuple[int, int]] = field(default_factory=list)
    demanda_real: list[tuple[int, int]] = field(default_factory=list)
    lotes: list[LoteHistorico] = field(default_factory=list)


def dia_relativo(instante: datetime | date, hoje: date) -> int:
    if isinstance(instante, datetime):
        instante = instante.astimezone(FUSO_UBS).date()
    return (instante - hoje).days


def historico(carga: CargaDemo) -> list[MedicamentoHistorico]:
    hoje = carga.hoje
    nomes = defaultdict(list)
    for m in carga.medicamentos:
        nomes[f"{m['nome_generico']} {m['concentracao']}"].append(m)
    meds = {}
    for nome, mesmos in nomes.items():
        for m in mesmos:
            rotulo = nome if len(mesmos) == 1 else f"{nome} ({m['nome_comercial']})"
            meds[m["id"]] = MedicamentoHistorico(m["id"], rotulo)
    lotes = {}
    for l in carga.lotes:
        lote = LoteHistorico(
            l["id"], l["numero_lote"], dia_relativo(l["entrada_em"], hoje),
            dia_relativo(l["validade"], hoje), l["quantidade_inicial"],
        )
        lotes[l["id"]] = (lote, meds[l["medicamento_id"]])
        meds[l["medicamento_id"]].lotes.append(lote)
    for m in carga.movimentacoes:
        lote, med = lotes[m["lote_id"]]
        dia = dia_relativo(m["ocorrido_em"], hoje)
        lote.movimentos.append((dia, m["tipo"], m["quantidade"], m["justificativa"] or ""))
        if m["tipo"] == TipoMovimentacao.SAIDA:
            med.saidas.append((dia, m["quantidade"]))
    for d in carga.demanda:
        meds[d["medicamento_id"]].demanda_real.append((dia_relativo(d["solicitado_em"], hoje), d["quantidade"]))
    for med in meds.values():
        med.inicio = min((l.entrada_dia for l in med.lotes), default=0)
    return sorted(meds.values(), key=lambda m: m.nome)


def serie_semanal(eventos: list[tuple[int, int]], inicio: int, fim: int) -> np.ndarray:
    semanas = max(0, (fim - inicio) // DIAS_SEMANA)
    serie = np.zeros(semanas)
    for dia, quantidade in eventos:
        if dia >= fim:
            continue
        indice = semanas - 1 - (fim - 1 - dia) // DIAS_SEMANA
        if indice >= 0:
            serie[indice] += quantidade
    return serie


@dataclass
class ResultadoPrevisao:
    medicamento: str
    classificacao: Classificacao
    media_teste: float
    mae: dict[str, float]
    vies: dict[str, float]


def avaliar_previsao(
    med: MedicamentoHistorico,
    alvo: str = "saidas",
    treino: str = "saidas",
    semanas_teste: int = SEMANAS_TESTE,
) -> ResultadoPrevisao | None:
    serie_treino = serie_semanal(getattr(med, treino), med.inicio, 0)
    serie_alvo = serie_semanal(getattr(med, alvo), med.inicio, 0)
    corte = len(serie_treino) - semanas_teste
    classificacao = classificar(serie_treino[:corte])
    if classificacao.eventos == 0:
        return None
    teste = serie_alvo[corte:]
    mae, vies = {}, {}
    for nome, metodo in METODOS.items():
        prev = metodo(serie_treino)[corte:-1]
        mae[nome] = float(np.mean(np.abs(prev - teste)))
        vies[nome] = float(np.mean(prev - teste))
    return ResultadoPrevisao(med.nome, classificacao, float(teste.mean()), mae, vies)


def previsao_proxima_semana(med: MedicamentoHistorico, fonte: str = "saidas", metodo: str = "SBA") -> float:
    serie = serie_semanal(getattr(med, fonte), med.inicio, 0)
    return float(METODOS[metodo](serie)[-1])


def parametros_demanda(serie: np.ndarray) -> tuple[float, np.ndarray]:
    recentes = serie[-JANELA_TAMANHOS:]
    tamanhos = recentes[recentes > 0]
    if len(tamanhos) == 0:
        tamanhos = serie[serie > 0]
    previsao = METODOS["SBA"](serie)[-1]
    if np.isnan(previsao) or len(tamanhos) == 0:
        return 0.0, tamanhos
    return min(previsao / tamanhos.mean(), 1.0), tamanhos


def estoque_em(med: MedicamentoHistorico, dia: int) -> list[LoteEstoque]:
    return [
        LoteEstoque(l.id, l.validade_dia, saldo)
        for l in med.lotes
        if l.entrada_dia < dia and l.validade_dia >= dia and (saldo := l.saldo_em(dia)) > 0
    ]


@dataclass
class PrevisaoRisco:
    medicamento: str
    lote: str
    corte: int
    saldo: int
    validade_dia: int
    simulado: RiscoLote
    projetado: float
    perda_real: int | None


def avaliar_risco(med: MedicamentoHistorico, corte: int, horizonte: int | None = None,
                  rng: np.random.Generator | None = None) -> list[PrevisaoRisco]:
    lotes = estoque_em(med, corte)
    serie = serie_semanal(med.saidas, med.inicio, corte)
    if not lotes or len(serie) < SEMANAS_MINIMAS:
        return []
    prob, tamanhos = parametros_demanda(serie)
    simulados = simular_perdas(lotes, corte, prob, tamanhos, rng=rng)
    projetados = projetar_perdas(lotes, corte, prob * (tamanhos.mean() if len(tamanhos) else 0.0))
    numeros = {l.id: l for l in med.lotes}
    resultado = []
    for lote, sim, proj in zip(lotes, simulados, projetados):
        if horizonte is not None and lote.validade_dia > corte + horizonte:
            continue
        real = numeros[lote.id].perda_por_vencimento() if corte < 0 else None
        resultado.append(PrevisaoRisco(med.nome, numeros[lote.id].numero, corte, lote.saldo,
                                       lote.validade_dia, sim, proj, real))
    return resultado


def cortes_validacao(inicio: int = -308, fim: int = -28, passo: int = 14) -> list[int]:
    return list(range(inicio, fim + 1, passo))


def validar_risco(meds: list[MedicamentoHistorico], horizonte: int = 84, folga_descarte: int = 10,
                  semente: int = 0) -> list[PrevisaoRisco]:
    rng = np.random.default_rng(semente)
    previsoes = []
    for corte in cortes_validacao():
        for med in meds:
            for p in avaliar_risco(med, corte, horizonte, rng):
                if p.validade_dia <= -folga_descarte:
                    previsoes.append(p)
    return previsoes


def resumo_por_classe(resultados: list[ResultadoPrevisao]) -> dict[str, dict[str, float]]:
    grupos: dict[str, list[ResultadoPrevisao]] = defaultdict(list)
    for r in resultados:
        grupo = "suave/errática" if r.classificacao.adi < 1.32 else "intermitente/irregular"
        grupos[grupo].append(r)
        grupos["todos"].append(r)
    resumo = {}
    for grupo, itens in grupos.items():
        resumo[grupo] = {
            nome: float(np.exp(np.mean([np.log(r.mae[nome] / r.mae["Média"]) for r in itens if r.mae["Média"] > 0])))
            for nome in METODOS
        }
        resumo[grupo]["_n"] = len(itens)
    return resumo
