export type FormaFarmaceutica =
  | 'Comprimido'
  | 'Cápsula'
  | 'Solução oral'
  | 'Injetável'
  | 'Pomada'
  | 'Suspensão'
  | 'Xarope'
  | 'Supositório'
  | 'Outros'

  | 'Comprimido revestido'
  | 'Comprimido mastigável'
  | 'Comprimido efervescente'
  | 'Comprimido sublingual'
  | 'Drágea'
  | 'Cápsula gelatinosa'
  | 'Pó'
  | 'Granulado'
  | 'Sachê'
  | 'Suspensão oral'
  | 'Emulsão'
  | 'Elixir'
  | 'Gotas'
  | 'Spray'
  | 'Aerossol'
  | 'Ampola'
  | 'Frasco-ampola'
  | 'Bolsa para infusão'
  | 'Creme'
  | 'Gel'
  | 'Loção'
  | 'Pasta'
  | 'Unguento'
  | 'Adesivo transdérmico'
  | 'Óvulo'
  | 'Enema'
  | 'Colírio'
  | 'Pomada oftálmica'
  | 'Solução nasal'
  | 'Spray nasal'
  | 'Inalador'
  | 'Nebulização'
  | 'Implante'
  | 'Sistema transdérmico'
  | 'Shampoo'
  | 'Sabonete medicinal'
  | 'Tintura'
  | 'Extrato';

export type ViaAdministracao =
  | 'Oral'
  | 'Intravenosa'
  | 'Intramuscular'
  | 'Subcutânea'
  | 'Tópica'
  | 'Inalatória'
  | 'Retal'
  | 'Sublingual'

  | 'Bucal'
  | 'Enteral'
  | 'Vaginal'
  | 'Cutânea'
  | 'Transdérmica'
  | 'Oftálmica'
  | 'Otológica'
  | 'Nasal'
  | 'Pulmonar'
  | 'Intradérmica'
  | 'Intratecal'
  | 'Epidural'
  | 'Intraóssea'
  | 'Intraperitoneal'
  | 'Intra-articular'
  | 'Intravesical'
  | 'Intracardíaca'
  | 'Intracavernosa'
  | 'Intravitreal'
  | 'Uretral'
  | 'Implantável';

export interface IMedicine {
  id: string;
  nome_generico: string;
  nome_comercial: string;
  concentracao: string;
  forma_farmaceutica: string;
  via_administracao: string;
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

