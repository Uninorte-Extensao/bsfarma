import { IMedicine } from "../models/IMedicine";

export const MEDICAMENTOS: IMedicine[] = [
  {
    id: '2a7d88c3-5a21-4f1e-b8b3-6d2f9a8f3001',
    nome_generico: 'Paracetamol',
    nome_comercial: 'Tylenol',
    concentracao: '500 mg',
    forma_farmaceutica: 'Comprimido',
    via_administracao: 'Oral',
    ativo: true,
    estoque_minimo: 50,
    criado_em: new Date(),
    atualizado_em: new Date()
  },
  {
    id: '1f8d72c9-7b32-4f2e-a9d3-5b1e7f9a4002',
    nome_generico: 'Ibuprofeno',
    nome_comercial: 'Advil',
    concentracao: '400 mg',
    forma_farmaceutica: 'Cápsula',
    via_administracao: 'Oral',
    ativo: true,
    estoque_minimo: 30,
    criado_em: new Date(),
    atualizado_em: new Date()
  },
  {
    id: '3b7f61d2-8c44-4d9f-b7a1-7e2f8a9c5003',
    nome_generico: 'Amoxicilina',
    nome_comercial: 'Amoxil',
    concentracao: '250 mg/5ml',
    forma_farmaceutica: 'Suspensão',
    via_administracao: 'Oral',
    ativo: true,
    estoque_minimo: 20,
    criado_em: new Date(),
    atualizado_em: new Date()
  },
  {
    id: '4c8e52b1-9d55-4a8f-c6b2-8f3a7d1e6004',
    nome_generico: 'Dipirona',
    nome_comercial: 'Novalgina',
    concentracao: '500 mg/ml',
    forma_farmaceutica: 'Solução oral',
    via_administracao: 'Oral',
    ativo: true,
    estoque_minimo: 40,
    criado_em: new Date(),
    atualizado_em: new Date()
  },
  {
    id: '5d9f43a2-1e66-4b7d-d5c3-9a4f8b2d7005',
    nome_generico: 'Heparina',
    nome_comercial: 'Liquemine',
    concentracao: '5000 UI/ml',
    forma_farmaceutica: 'Injetável',
    via_administracao: 'Subcutânea',
    ativo: true,
    estoque_minimo: 15,
    criado_em: new Date(),
    atualizado_em: new Date()
  }
];


export const FORMA_FARMACEUTICA = [
  { label: 'Comprimido', value: 'Comprimido' },
  { label: 'Comprimido revestido', value: 'Comprimido revestido' },
  { label: 'Comprimido mastigável', value: 'Comprimido mastigável' },
  { label: 'Comprimido efervescente', value: 'Comprimido efervescente' },
  { label: 'Comprimido sublingual', value: 'Comprimido sublingual' },
  { label: 'Drágea', value: 'Drágea' },
  { label: 'Cápsula', value: 'Cápsula' },
  { label: 'Cápsula gelatinosa', value: 'Cápsula gelatinosa' },
  { label: 'Pó', value: 'Pó' },
  { label: 'Granulado', value: 'Granulado' },
  { label: 'Sachê', value: 'Sachê' },
  { label: 'Solução oral', value: 'Solução oral' },
  { label: 'Suspensão', value: 'Suspensão' },
  { label: 'Suspensão oral', value: 'Suspensão oral' },
  { label: 'Emulsão', value: 'Emulsão' },
  { label: 'Xarope', value: 'Xarope' },
  { label: 'Elixir', value: 'Elixir' },
  { label: 'Gotas', value: 'Gotas' },
  { label: 'Spray', value: 'Spray' },
  { label: 'Aerossol', value: 'Aerossol' },
  { label: 'Injetável', value: 'Injetável' },
  { label: 'Ampola', value: 'Ampola' },
  { label: 'Frasco-ampola', value: 'Frasco-ampola' },
  { label: 'Bolsa para infusão', value: 'Bolsa para infusão' },
  { label: 'Pomada', value: 'Pomada' },
  { label: 'Creme', value: 'Creme' },
  { label: 'Gel', value: 'Gel' },
  { label: 'Loção', value: 'Loção' },
  { label: 'Pasta', value: 'Pasta' },
  { label: 'Unguento', value: 'Unguento' },
  { label: 'Adesivo transdérmico', value: 'Adesivo transdérmico' },
  { label: 'Supositório', value: 'Supositório' },
  { label: 'Óvulo', value: 'Óvulo' },
  { label: 'Enema', value: 'Enema' },
  { label: 'Colírio', value: 'Colírio' },
  { label: 'Pomada oftálmica', value: 'Pomada oftálmica' },
  { label: 'Solução nasal', value: 'Solução nasal' },
  { label: 'Spray nasal', value: 'Spray nasal' },
  { label: 'Inalador', value: 'Inalador' },
  { label: 'Nebulização', value: 'Nebulização' },
  { label: 'Implante', value: 'Implante' },
  { label: 'Sistema transdérmico', value: 'Sistema transdérmico' },
  { label: 'Shampoo medicinal', value: 'Shampoo medicinal' },
  { label: 'Sabonete medicinal', value: 'Sabonete medicinal' },
  { label: 'Tintura', value: 'Tintura' },
  { label: 'Extrato', value: 'Extrato' },
  { label: 'Outros', value: 'Outros' }
];

export const VIA_ADMINISTRACAO = [
  { label: 'Oral', value: 'Oral' },
  { label: 'Bucal', value: 'Bucal' },
  { label: 'Sublingual', value: 'Sublingual' },
  { label: 'Enteral', value: 'Enteral' },
  { label: 'Retal', value: 'Retal' },
  { label: 'Vaginal', value: 'Vaginal' },
  { label: 'Tópica', value: 'Tópica' },
  { label: 'Cutânea', value: 'Cutânea' },
  { label: 'Transdérmica', value: 'Transdérmica' },
  { label: 'Oftálmica', value: 'Oftálmica' },
  { label: 'Otológica', value: 'Otológica' },
  { label: 'Nasal', value: 'Nasal' },
  { label: 'Inalatória', value: 'Inalatória' },
  { label: 'Pulmonar', value: 'Pulmonar' },
  { label: 'Intravenosa', value: 'Intravenosa' },
  { label: 'Intramuscular', value: 'Intramuscular' },
  { label: 'Subcutânea', value: 'Subcutânea' },
  { label: 'Intradérmica', value: 'Intradérmica' },
  { label: 'Intratecal', value: 'Intratecal' },
  { label: 'Epidural', value: 'Epidural' },
  { label: 'Intraóssea', value: 'Intraóssea' },
  { label: 'Intraperitoneal', value: 'Intraperitoneal' },
  { label: 'Intra-articular', value: 'Intra-articular' },
  { label: 'Intravesical', value: 'Intravesical' },
  { label: 'Intracardíaca', value: 'Intracardíaca' },
  { label: 'Intracavernosa', value: 'Intracavernosa' },
  { label: 'Intravitreal', value: 'Intravitreal' },
  { label: 'Uretral', value: 'Uretral' },
  { label: 'Implantável', value: 'Implantável' }
];

export const UNIDADE_CONCENTRACAO = [
  { label: 'mg', value: 'mg' },
  { label: 'g', value: 'g' },
  { label: 'mcg', value: 'mcg' },
  { label: 'kg', value: 'kg' },

  { label: 'mg/mL', value: 'mg/mL' },
  { label: 'g/mL', value: 'g/mL' },
  { label: 'mcg/mL', value: 'mcg/mL' },

  { label: 'mg/L', value: 'mg/L' },
  { label: 'g/L', value: 'g/L' },

  { label: '%', value: '%' },

  { label: 'UI', value: 'UI' },
  { label: 'UI/mL', value: 'UI/mL' },

  { label: 'mEq', value: 'mEq' },
  { label: 'mmol', value: 'mmol' },
  { label: 'mol', value: 'mol' },

  { label: 'mL', value: 'mL' },
  { label: 'L', value: 'L' },

  { label: 'gotas', value: 'gotas' },
  { label: 'comprimidos', value: 'comprimidos' },
  { label: 'cápsulas', value: 'cápsulas' },

  { label: 'ampolas', value: 'ampolas' },
  { label: 'frascos', value: 'frascos' }
];