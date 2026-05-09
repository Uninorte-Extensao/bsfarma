export interface ILote {
    id: string;
    medicamento_id: string;
    numero_lote: string;
    fabricante: string;
    validade: Date;
    quantidade_inicial: number;
    quantidade_atual: number;
    entrada_em: Date;
    registrado_por: string;
}

export interface ICreateLote {
    medicamento_id: string;
    numero_lote: string;
    fabricante: string;
    validade: Date;
    quantidade_inicial: number;
    quantidade_atual: number;
    registrado_por: string;
}

export interface IUpdateLote {
    numero_lote?: string;
    fabricante?: string;
    validade?: Date;
    quantidade_inicial?: number;
    quantidade_atual?: number;
}