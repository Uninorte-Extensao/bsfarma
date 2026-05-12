export interface IAlert {
    id: string,
    lote_id: string,
    medicamento_id: string,
    tipo: string,
    status: string,
    gerado_em: Date,
    resolvido_em: string | null
}