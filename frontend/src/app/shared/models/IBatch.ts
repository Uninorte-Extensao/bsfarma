export interface IBatch {
    id: string;
    medicamento_id: string;
    // Nulos de verdade na API: registrado_por vira null quando o usuário que
    // registrou a entrada é apagado, e fabricante é opcional (ver LoteResponse
    // no backend). Os formulários de criação/edição continuam exigindo os dois.
    registrado_por: string | null;
    numero_lote: string;
    fabricante: string | null;
    validade: Date;
    quantidade_inicial: number;
    quantidade_atual: number;
    entrada_em: Date;
}

export interface ICreateLote {
    medicamento_id: string;
    registrado_por: string;
    numero_lote: string;
    fabricante: string;
    validade: string;
    quantidade_inicial: number;
}

export interface IUpdateLote {
    numero_lote: string;
    fabricante: string;
    validade: Date;
}