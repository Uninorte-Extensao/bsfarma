import math
import random
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from typing import Callable

from app.movimentacao.model import TipoMovimentacao
from app.seed.catalogo import (
    DESABASTECIMENTOS,
    LOTES_AVULSOS,
    MEDICAMENTOS,
    PERFIS_CLINICOS,
    USUARIOS,
    MedicamentoDemo,
    Uso,
)
from app.usuario.model import PerfilUsuario

FUSO_UBS = timezone(timedelta(hours=-5))
JANELA_DIAS = 365
CICLO_PEDIDO = 60
ESTOQUE_SEGURANCA_DIAS = 25
DIAS_ESTOQUE_MINIMO = 20
MESES_SAZONAIS = {7, 8, 9, 10}
FATOR_SAZONAL = 2.2
PROB_INICIO_NA_JANELA = 0.12
PROB_ABANDONO = 0.08
PROB_DOSE_DOBRADA = 0.05
PROB_MES_PERDIDO = 0.07
PROB_AVARIA_DIA = 0.0025
PROB_AJUSTE_INVENTARIO = 0.3
DIAS_INVENTARIO = (-270, -180, -90)
SEMENTE_PADRAO = 20261023


@dataclass
class Pedido:
    dia: int
    minuto: int
    quantidade: int
    paciente_id: str


@dataclass
class LoteSimulado:
    registro: dict
    validade_dia: int
    descarte_dia: int
    saldo: int


@dataclass
class CargaDemo:
    hoje: date
    usuarios: list[dict] = field(default_factory=list)
    medicamentos: list[dict] = field(default_factory=list)
    pacientes: list[dict] = field(default_factory=list)
    lotes: list[dict] = field(default_factory=list)
    movimentacoes: list[dict] = field(default_factory=list)
    dispensacoes: list[dict] = field(default_factory=list)
    demanda_nao_atendida: dict[str, int] = field(default_factory=dict)
    pacientes_exemplo: list[tuple[str, str]] = field(default_factory=list)


def gerar_carga(
    hoje: date,
    gerar_codigo: Callable[[str], str],
    semente: int = SEMENTE_PADRAO,
) -> CargaDemo:
    return _Gerador(hoje, gerar_codigo, semente).gerar()


class _Gerador:
    def __init__(self, hoje: date, gerar_codigo: Callable[[str], str], semente: int) -> None:
        self.hoje = hoje
        self.gerar_codigo = gerar_codigo
        self.rng = random.Random(semente)
        self.carga = CargaDemo(hoje=hoje)
        self.usuario_id: dict[PerfilUsuario, str] = {}
        self.numeros_lote: set[str] = set()

    def gerar(self) -> CargaDemo:
        self._usuarios()
        demanda = self._pacientes_e_demanda()
        avulsos = {a.medicamento: a for a in LOTES_AVULSOS}
        desabastecimentos = {d.medicamento: d for d in DESABASTECIMENTOS}
        for med in MEDICAMENTOS:
            pedidos = sorted(demanda[med.chave], key=lambda p: (p.dia, p.minuto))
            self._simular_estoque(med, pedidos, avulsos.get(med.chave), desabastecimentos.get(med.chave))
        return self.carga

    def _uuid(self) -> str:
        return str(uuid.UUID(int=self.rng.getrandbits(128), version=4))

    def _data(self, dia: int) -> date:
        return self.hoje + timedelta(days=dia)

    def _dia_util(self, dia: int) -> int:
        while self._data(dia).weekday() >= 5:
            dia += 1
        return dia

    def _instante(self, dia: int, minuto: int) -> datetime:
        local = datetime.combine(self._data(dia), time(minuto // 60, minuto % 60), tzinfo=FUSO_UBS)
        return local.astimezone(timezone.utc)

    def _minuto_expediente(self) -> int:
        return self.rng.randint(7 * 60 + 30, 16 * 60 + 30)

    def _escolher(self, opcoes):
        valores, pesos = zip(*opcoes)
        return self.rng.choices(valores, weights=pesos, k=1)[0]

    def _cpf(self) -> str:
        while True:
            base = [self.rng.randint(0, 9) for _ in range(9)]
            if len(set(base)) > 1:
                break
        for tamanho in (9, 10):
            soma = sum(d * p for d, p in zip(base, range(tamanho + 1, 1, -1)))
            resto = (soma * 10) % 11
            base.append(0 if resto == 10 else resto)
        return "".join(map(str, base))

    def _usuarios(self) -> None:
        criado_em = self._instante(-JANELA_DIAS - 30, 9 * 60)
        for u in USUARIOS:
            uid = self._uuid()
            self.usuario_id[u.perfil] = uid
            self.carga.usuarios.append({
                "id": uid,
                "nome": u.nome,
                "login": u.login,
                "perfil": u.perfil,
                "ativo": True,
                "criado_em": criado_em,
            })

    def _pacientes_e_demanda(self) -> dict[str, list[Pedido]]:
        demanda: dict[str, list[Pedido]] = defaultdict(list)
        codigos: set[str] = set()
        for perfil in PERFIS_CLINICOS:
            for _ in range(perfil.pacientes):
                codigo = self.gerar_codigo(self._cpf())
                while codigo in codigos:
                    codigo = self.gerar_codigo(self._cpf())
                codigos.add(codigo)

                esquema = self._escolher(perfil.esquemas)
                if self.rng.random() < PROB_INICIO_NA_JANELA:
                    inicio = self.rng.randint(-300, -30)
                else:
                    inicio = -JANELA_DIAS - self.rng.randint(0, 400)
                fim = 0
                if self.rng.random() < PROB_ABANDONO:
                    fim = self.rng.randint(max(inicio, -JANELA_DIAS) + 60, -20)

                pid = self._uuid()
                self.carga.pacientes.append({
                    "id": pid,
                    "codigo": codigo,
                    "condicao_clinica": perfil.condicao,
                    "ativo": True,
                    "criado_em": self._instante(max(inicio, -JANELA_DIAS), self._minuto_expediente()),
                })
                if len(self.carga.pacientes_exemplo) < len(PERFIS_CLINICOS) and fim == 0 and inicio < -JANELA_DIAS:
                    if perfil.condicao not in {c for _, c in self.carga.pacientes_exemplo}:
                        self.carga.pacientes_exemplo.append((codigo, perfil.condicao))

                for uso in esquema:
                    for dia, quantidade in self._eventos(uso, inicio, fim):
                        demanda[uso.medicamento].append(
                            Pedido(dia, self._minuto_expediente(), quantidade, pid)
                        )
        return demanda

    def _eventos(self, uso: Uso, inicio: int, fim: int) -> list[tuple[int, int]]:
        dose = self._escolher(uso.quantidades)
        comeco = max(inicio, -JANELA_DIAS)
        eventos: list[tuple[int, int]] = []

        if uso.eventual:
            ultimo = -10_000
            for dia in range(comeco, fim):
                fator = FATOR_SAZONAL if uso.sazonal and self._data(dia).month in MESES_SAZONAIS else 1.0
                if dia - ultimo >= 15 and self.rng.random() < fator / uso.intervalo:
                    eventos.append((dia, dose))
                    ultimo = dia
        else:
            dia = comeco + (self.rng.randint(0, uso.intervalo - 1) if inicio < -JANELA_DIAS else 0)
            while dia < fim:
                quantidade, intervalo = dose, uso.intervalo
                if self.rng.random() < PROB_DOSE_DOBRADA:
                    quantidade, intervalo = dose * 2, uso.intervalo * 2
                eventos.append((dia, quantidade))
                atraso = round(self.rng.gauss(2, 4))
                if self.rng.random() < PROB_MES_PERDIDO:
                    atraso += uso.intervalo
                dia += max(intervalo + atraso, uso.intervalo // 2)

        uteis = []
        for dia, quantidade in eventos:
            dia = self._dia_util(dia)
            if dia <= -1:
                uteis.append((dia, quantidade))
        return uteis

    def _numero_lote(self, med: MedicamentoDemo, validade: date) -> str:
        prefixo = "".join(p[0] for p in med.campos["fabricante"].split()[:2]).upper()
        while True:
            numero = f"{prefixo}{(validade.year - 2) % 100:02d}{self.rng.randint(0, 9999):04d}"
            if numero not in self.numeros_lote:
                self.numeros_lote.add(numero)
                return numero

    def _novo_lote(self, med: MedicamentoDemo, med_id: str, chegada: int, validade_dia: int, quantidade: int) -> LoteSimulado:
        validade = self._data(validade_dia)
        registro = {
            "id": self._uuid(),
            "medicamento_id": med_id,
            "registrado_por": self.usuario_id[PerfilUsuario.FARMACEUTICO],
            "numero_lote": self._numero_lote(med, validade),
            "fabricante": med.campos["fabricante"],
            "validade": validade,
            "quantidade_inicial": quantidade,
            "quantidade_atual": quantidade,
            "entrada_em": self._instante(chegada, self.rng.randint(7 * 60, 9 * 60)),
        }
        self.carga.lotes.append(registro)
        descarte = self._dia_util(validade_dia + self.rng.randint(1, 6))
        return LoteSimulado(registro, validade_dia, descarte, quantidade)

    def _movimentacao(self, lote: LoteSimulado, tipo: TipoMovimentacao, quantidade: int,
                      justificativa: str, dia: int, minuto: int, perfil: PerfilUsuario) -> dict:
        lote.saldo -= quantidade
        mov = {
            "id": self._uuid(),
            "lote_id": lote.registro["id"],
            "usuario_id": self.usuario_id[perfil],
            "tipo": tipo,
            "quantidade": quantidade,
            "justificativa": justificativa,
            "ocorrido_em": self._instante(dia, minuto),
        }
        self.carga.movimentacoes.append(mov)
        return mov

    def _simular_estoque(self, med: MedicamentoDemo, pedidos: list[Pedido], avulso, desabastecimento) -> None:
        consumo_diario = max(sum(p.quantidade for p in pedidos) / JANELA_DIAS, 0.05)
        estoque_minimo = math.ceil(consumo_diario * DIAS_ESTOQUE_MINIMO)
        if estoque_minimo > 50:
            estoque_minimo = math.ceil(estoque_minimo / 10) * 10

        med_id = self._uuid()
        self.carga.medicamentos.append({
            "id": med_id,
            **med.campos,
            "estoque_minimo": estoque_minimo,
            "ativo": True,
            "criado_em": self._instante(-JANELA_DIAS - 30, 9 * 60),
        })

        def arredondar(qtd: float) -> int:
            return max(med.embalagem, math.ceil(qtd / med.embalagem) * med.embalagem)

        def validade_regular(chegada: int) -> int:
            return chegada + med.validade_meses * 30 - self.rng.randint(60, 240)

        lotes: list[LoteSimulado] = []
        chegadas: dict[int, list[tuple[int, int]]] = defaultdict(list)

        implantacao = arredondar(consumo_diario * (CICLO_PEDIDO / 2 + ESTOQUE_SEGURANCA_DIAS + 10))
        partes = [implantacao] if self.rng.random() < 0.5 else [
            arredondar(implantacao * 0.4), arredondar(implantacao * 0.6)
        ]
        for qtd in partes:
            lotes.append(self._novo_lote(med, med_id, -JANELA_DIAS, -JANELA_DIAS + self.rng.randint(90, 600), qtd))

        revisoes = {}
        dia = -JANELA_DIAS + 30
        while dia <= -10:
            revisao = dia + self.rng.randint(-5, 5)
            revisoes[revisao] = self._dia_util(revisao + self.rng.randint(5, 12))
            dia += CICLO_PEDIDO

        dia_avulso = self._dia_util(avulso.chegada) if avulso else None
        inventarios = {self._dia_util(d) for d in DIAS_INVENTARIO}
        nao_atendida = 0
        indice = 0

        for dia in range(-JANELA_DIAS, 0):
            if dia in revisoes:
                chegada = revisoes[dia]
                disponivel = sum(l.saldo for l in lotes if l.saldo > 0 and l.validade_dia > dia + CICLO_PEDIDO)
                lead = chegada - dia
                alvo = consumo_diario * (CICLO_PEDIDO + lead + ESTOQUE_SEGURANCA_DIAS)
                falta = alvo - disponivel
                if chegada <= -1 and falta >= consumo_diario * 10:
                    quantidade = arredondar(falta)
                    if desabastecimento and dia >= desabastecimento.desde:
                        quantidade = math.floor(quantidade * desabastecimento.fator / med.embalagem) * med.embalagem
                    if quantidade > 0:
                        chegadas[chegada].append((quantidade, validade_regular(chegada)))

            for quantidade, validade_dia in chegadas.pop(dia, []):
                lotes.append(self._novo_lote(med, med_id, dia, validade_dia, quantidade))

            if dia == dia_avulso:
                ultimo_dia = min(avulso.validade, -1)
                demanda = sum(p.quantidade for p in pedidos if dia <= p.dia <= ultimo_dia)
                quantidade = demanda + math.ceil(consumo_diario * avulso.sobra_dias)
                lotes.append(self._novo_lote(med, med_id, dia, avulso.validade, quantidade))

            for lote in lotes:
                if lote.descarte_dia == dia and lote.saldo > 0:
                    self._movimentacao(
                        lote, TipoMovimentacao.PERDA, lote.saldo,
                        f"Descarte por vencimento — lote vencido em {self._data(lote.validade_dia):%d/%m/%Y}",
                        dia, self.rng.randint(10 * 60, 11 * 60), PerfilUsuario.FARMACEUTICO,
                    )

            utilizaveis = sorted(
                (l for l in lotes if l.saldo > 0 and l.validade_dia >= dia),
                key=lambda l: (l.validade_dia, l.registro["entrada_em"]),
            )

            while indice < len(pedidos) and pedidos[indice].dia == dia:
                pedido = pedidos[indice]
                indice += 1
                restante = pedido.quantidade
                for lote in utilizaveis:
                    if restante == 0:
                        break
                    if lote.saldo == 0:
                        continue
                    retirada = min(restante, lote.saldo)
                    perfil = PerfilUsuario.ATENDENTE if self.rng.random() < 0.8 else PerfilUsuario.FARMACEUTICO
                    mov = self._movimentacao(
                        lote, TipoMovimentacao.SAIDA, retirada, "Dispensação direta ao paciente",
                        dia, pedido.minuto, perfil,
                    )
                    self.carga.dispensacoes.append({
                        "id": self._uuid(),
                        "paciente_id": pedido.paciente_id,
                        "movimentacao_id": mov["id"],
                        "dispensado_em": mov["ocorrido_em"],
                    })
                    restante -= retirada
                nao_atendida += restante

            utilizaveis = [l for l in utilizaveis if l.saldo > 0]
            if utilizaveis and self.rng.random() < PROB_AVARIA_DIA and self._data(dia).weekday() < 5:
                lote = self.rng.choice(utilizaveis)
                self._movimentacao(
                    lote, TipoMovimentacao.PERDA, min(lote.saldo, self.rng.randint(1, 3)),
                    self._motivo_avaria(med), dia, self._minuto_expediente(), PerfilUsuario.FARMACEUTICO,
                )

            if dia in inventarios and utilizaveis and self.rng.random() < PROB_AJUSTE_INVENTARIO:
                lote = self.rng.choice(utilizaveis)
                self._movimentacao(
                    lote, TipoMovimentacao.AJUSTE, min(lote.saldo, self.rng.randint(1, 6)),
                    "Inventário trimestral — contagem física abaixo do saldo do sistema",
                    dia, 16 * 60 + 45, PerfilUsuario.FARMACEUTICO,
                )

        for lote in lotes:
            lote.registro["quantidade_atual"] = lote.saldo
        if nao_atendida:
            self.carga.demanda_nao_atendida[med.chave] = nao_atendida

    def _motivo_avaria(self, med: MedicamentoDemo) -> str:
        forma = med.campos["forma_farmaceutica"].lower()
        if "injetável" in forma and med.campos["via_administracao"] == "Parenteral" and "insulina" in med.campos["nome_generico"].lower():
            return "Quebra da cadeia de frio — frasco descartado"
        if "aerossol" in forma or "solução" in forma or "suspensão" in forma:
            return "Frasco danificado no manuseio"
        return "Blister danificado — unidades impróprias para dispensação"
