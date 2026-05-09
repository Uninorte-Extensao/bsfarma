export interface IPatient {
    id: string;
    id_interno: string;
    condicao_cronica: string;
    ativo: boolean;
    criado_em: Date;
}

export interface ICreatePAtient {
    id_interno: string;
    condicao_cronica: boolean;
}