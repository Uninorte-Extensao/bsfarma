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

  export type Tarja =
  | 'Sem Tarja'
  | 'Tarja Vermelha'
  | 'Tarja Preta';

export interface IMedicine {
  id: number;
  nomeGenerico: string;
  nomeComercial: string;
  concentracao: string;
  formaFarmaceutica: FormaFarmaceutica;
  viaAdministracao: ViaAdministracao;
  ativo: boolean;
  estoqueMinimo: number;
  fabricantePadrao: string;
  apresentacaoOriginal: string;
  codGgrem: number;
  registro: number;
  codigoBarras: number;
  classeTerapeutica: string;
  tipoProduto: string;
  restricaoHospitalar: boolean;
  tarja: Tarja;
  criadoEm: Date;
  atualizadoEm: Date;
}
