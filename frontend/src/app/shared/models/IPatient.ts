export interface IPaciente {
    codigo: string;
    condicao_clinica: string;
    ativo: boolean;
    criado_em: Date;
    atualizado_em: Date;
}

export interface ICreatePaciente {
    cpf: string,
    condicao_clinica: string
}

export interface IUpdatePaciente {
    condicao_clinica: string
}

export interface IRecuperarPaciente {
    cpf: string
}