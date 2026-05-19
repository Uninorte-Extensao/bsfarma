"""
Schemas Pydantic do módulo alerta.

Alertas não têm schema de criação (Create) — são gerados pelo sistema.
O único payload de entrada é a atualização de status pelo operador.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.alertas.model import StatusAlerta, TipoAlerta


class LoteResumo(BaseModel):
    """Dados mínimos do lote embutidos na resposta do alerta."""
    model_config = ConfigDict(from_attributes=True)
    id: str
    numero_lote: str
    validade: datetime
    quantidade_atual: int
    quantidade_inicial: int


class MedicamentoResumo(BaseModel):
    """Dados mínimos do medicamento embutidos na resposta do alerta."""
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome_generico: str
    concentracao: str | None
    forma_farmaceutica: str | None
    estoque_minimo: int


class AlertaResponse(BaseModel):
    """Representação completa de um alerta, com lote e medicamento embutidos."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    tipo: TipoAlerta
    status: StatusAlerta
    gerado_em: datetime
    resolvido_em: datetime | None

    lote: LoteResumo
    medicamento: MedicamentoResumo


class AlertaStatusUpdate(BaseModel):
    """
    Payload para atualização de status pelo operador.

    Transições válidas:
        PENDENTE     → EM_ANDAMENTO ou RESOLVIDO
        EM_ANDAMENTO → RESOLVIDO
    """
    status: StatusAlerta


class AlertaResumoResponse(BaseModel):
    """Versão resumida para listagens — sem dados completos do lote/medicamento."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    tipo: TipoAlerta
    status: StatusAlerta
    gerado_em: datetime
    resolvido_em: datetime | None
    medicamento_nome: str | None = None   # populado manualmente no router


class VerificacaoResponse(BaseModel):
    """Resultado retornado após execução manual da verificação de alertas."""
    data_verificacao: str
    alertas_criados: int
    alertas_escalados: int
    alertas_expirados: int
