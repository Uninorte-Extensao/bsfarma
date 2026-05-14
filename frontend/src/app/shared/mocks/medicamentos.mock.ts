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
  { label: 'Cápsula', value: 'Cápsula' },
  { label: 'Solução oral', value: 'Solução oral' },
  { label: 'Injetável', value: 'Injetável' },
  { label: 'Pomada', value: 'Pomada' },
  { label: 'Suspensão', value: 'Suspensão' },
  { label: 'Xarope', value: 'Xarope' },
  { label: 'Supositório', value: 'Supositório' }
];

export const VIA_ADMINISTRACAO = [
  { label: 'Oral', value: 'Oral' },
  { label: 'Intravenosa', value: 'Intravenosa' },
  { label: 'Intramuscular', value: 'Intramuscular' },
  { label: 'Subcutânea', value: 'Subcutânea' },
  { label: 'Tópica', value: 'Tópica' },
  { label: 'Inalatória', value: 'Inalatória' },
  { label: 'Retal', value: 'Retal' },
  { label: 'Sublingual', value: 'Sublingual' }
];

export const UNIDADE_CONCENTRACAO = [
    { label: 'mg', value: 'mg' },
    { label: 'g', value: 'g' },
    { label: 'mcg', value: 'mcg' },
    { label: 'mg/mL', value: 'mg/mL' },
    { label: 'g/mL', value: 'g/mL' },
    { label: '%', value: '%' },
    { label: 'UI/mL', value: 'UI/mL' }
  ];