export interface ICreateDispensacao {
    codigo: string,
    lote_id: string,
    quantidade: number
}

export interface IDispensacao {
    id: string,
    paciente_id: string,
    movimentacao_id: string;
    dispensado_em: Date
}

export interface IDispensacaoDetalhada extends IDispensacao {
    paciente: { id: string, codigo: string },
    quantidade: number,
    lote: { id: string, numero_lote: string },
    medicamento: { id: string, nome_generico: string, concentracao: string }
}

