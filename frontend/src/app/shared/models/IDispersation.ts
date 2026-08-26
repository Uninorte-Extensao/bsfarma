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

