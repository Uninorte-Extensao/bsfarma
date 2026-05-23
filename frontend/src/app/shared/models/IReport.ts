export interface IGestaoDashboard {
    alertas: {
        '30_dias': number;
        '15_dias': number;
        '7_dias': number;
        estoque_critico: number;
        total: number;
    };

    estoque: {
        total_medicamentos: number;
        medicamentos_ok: number;
        medicamentos_criticos: number;
    };

    itens_criticos: IItemCritico[];
}

export interface IRelatorioDispensacao {
    periodo: string,
    ano: number,
    mes: number,
    nome_generico: string,
    concentracao: string,
    total_dispensado: number,
    num_dispensacoes: number
}

export interface IEstoqueMedicamento {
    medicamento_id: string;
    nome_generico: string;
    concentracao: string;
    forma_farmaceutica: string;
    via_administracao: string;
    indicacao_farmacia_popular: string;
    estoque_minimo: number;
    saldo_total: number;
    num_lotes: number;
    proximo_vencimento: Date;
    status: string;
}

export interface IItemCritico {
    lote_id: string;
    numero_lote: string;
    validade: string;
    quantidade_atual: number;
    estoque_minimo: number;
    medicamento_id: string;
    nome_generico: string;
    concentracao: string;
    motivo: string;
}

export interface IPaginacao<IMovimentacaoRelatorio> {
    data: IMovimentacaoRelatorio[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export interface IMovimentacaoRelatorio {
    id: string;
    tipo: 'entrada' | 'saida' | 'perda' | 'ajuste';
    quantidade: number;
    justificativa: string;
    ocorrido_em: string;
    numero_lote: string;
    validade: string;
    medicamento_id: string;
    nome_generico: string;
    concentracao: string;
}