export interface ICreateDispensacao {
    paciente_id: string,
    lote_id: string,
    quantidade: number
}

export interface IDispensacao {
    id: string,
    paciente_id: string,
    movimentacao_id: string;
    dispensado_em: Date
}

