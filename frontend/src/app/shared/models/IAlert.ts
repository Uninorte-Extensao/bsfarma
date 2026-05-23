export interface IAlertaValidade {
  id: string;
  tipo_alerta: string;
  status_alerta: string;
  gerado_em: Date;
  resolvido_em: Date | null;
  lote: ILoteAlerta;
  medicamento: IMedicamentoAlerta;
}

export interface ILoteAlerta {
  id: string;
  numero_lote: string;
  validade: Date;
  quantidade_atual: number;
  quantidade_inicial: number;
}

export interface IMedicamentoAlerta {
  id: string;
  nome_generico: string;
  concentracao: string;
  forma_farmaceutica: string;
  estoque_minimo: number;
}

export interface IUpdateStatusAlerta {
  status_alerta:
    | 'Pendente'
    | 'Em andamento'
    | 'Resolvido'
    | 'Expirado';
}

export interface IVerificacaoAlerta {
  data_verificacao: string;
  alertas_criados: number;
  alertas_escalados: number;
  alertas_expirados: number;
}