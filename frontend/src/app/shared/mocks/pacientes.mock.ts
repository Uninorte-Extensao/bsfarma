import { IPaciente } from "../models/IPatient";

export const PACIENTE: IPaciente[] = [
    {
        codigo: 'PAC-0001',
        condicao_clinica: 'Diabetes Tipo 2',
        ativo: true,
        criado_em: new Date('2026-01-10T08:30:00'),
        atualizado_em: new Date()
    },
    {
        codigo: 'PAC-0002',
        condicao_clinica: 'Diabetes Tipo 2',
        ativo: true,
        criado_em: new Date('2026-01-15T10:20:00'),
        atualizado_em: new Date()
    },
    {
        codigo: 'PAC-0003',
        condicao_clinica: 'Diabetes Tipo 2',
        ativo: false,
        criado_em: new Date('2026-02-01T14:45:00'),
        atualizado_em: new Date()
    },
    {
        codigo: 'PAC-0004',
        condicao_clinica: 'Diabetes Tipo 2',
        ativo: true,
        criado_em: new Date('2026-02-18T09:10:00'),
        atualizado_em: new Date()
    },
    {
        codigo: 'PAC-0005',
        condicao_clinica: 'Diabetes Tipo 2',
        ativo: true,
        criado_em: new Date('2026-03-05T16:00:00'),
        atualizado_em: new Date()
    }

]