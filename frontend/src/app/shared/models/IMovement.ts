export interface ICreateMovimentacao {
    lote_id: string,
    usuario_id: string,
    tipo: ITypeMovimentacao,
    quantidade: number,
    justificativa: string
}

export enum ITypeMovimentacao {
    ENTRADA = "entrada",
    SAIDA = "saida",
    PERDA = "perda",
    AJUSTE = "ajuste"
} 

export interface IMovimentacao {
    id: string,
    lote_id: string,
    usuario_id: string,
    tipo: ITypeMovimentacao,
    quantidade: number,
    justificativa: string,
    ocorrido_em: Date
}

export interface IMovimentacaoDetalhada extends IMovimentacao {
    lote: { id: string, numero_lote: string },
    usuario: { id: string, nome: string }
}

export interface IUpdateMovimentacao {
    justificativa: string
}
