export type FormaFarmaceutica =
  | 'Comprimido'
  | 'Cápsula'
  | 'Solução oral'
  | 'Injetável'
  | 'Pomada'
  | 'Suspensão'
  | 'Xarope'
  | 'Supositório';

export type ViaAdministracao =
  | 'Oral'
  | 'Intravenosa'
  | 'Intramuscular'
  | 'Subcutânea'
  | 'Tópica'
  | 'Inalatória'
  | 'Retal'
  | 'Sublingual';

export interface IMedicine{
  id: number;
  nomeGenerico: string;
  nomeComercial: string;
  formaFarmaceutica: FormaFarmaceutica;
  concentracao: string;
  viaAdministracao: ViaAdministracao;
  estoqueMinimo: number;
  ativo: boolean;
  criadoEm: Date;
  atualizadoEm: Date;
}

export type CriarMedicamentoDTO = Omit<
  IMedicine,
  'id' | 'criadoEm' | 'atualizadoEm'
>;

export type AtualizarMedicamentoDTO = Partial<CriarMedicamentoDTO>;

export type MedicamentoResumo = Pick<
  IMedicine,
  | 'id'
  | 'nomeGenerico'
  | 'nomeComercial'
  | 'formaFarmaceutica'
  | 'concentracao'
  | 'viaAdministracao'
  | 'ativo'
>;

export interface FiltroMedicamento {
  busca?: string;
  formaFarmaceutica?: FormaFarmaceutica;
  ativo?: boolean;
}
