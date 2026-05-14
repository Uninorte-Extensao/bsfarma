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
  id: string;
  nome_generico: string;
  nome_comercial: string;
  concentracao: string;
  forma_farmaceutica: FormaFarmaceutica;
  via_administracao: ViaAdministracao;
  ativo: boolean;
  estoque_minimo: number;
  criado_em: Date;
  atualizado_em: Date;
}


export interface ICreateMedicine {
  nome_generico: string;
  nome_comercial: string;
  forma_farmaceutica: string;
  concentracao: string;
  via_administracao: string;
  estoque_minimo: number;
  ativo: boolean;
}

