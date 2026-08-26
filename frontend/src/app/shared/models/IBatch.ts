export interface IBatch {
    id: string;
    medicamento_id: string;
    registrado_por: string;
    numero_lote: string;
    fabricante: string;
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