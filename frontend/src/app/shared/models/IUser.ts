export interface IUser {
    id: string,
    nome: string,
    login: string,
    perfil: IProfileEnum
}

export interface IUserLogin {
    username: string,
    password: string
}

export interface IResponseLogin {
    access_token: string,
    token_type: string
}

export interface ICreateUser {
    nome: string,
    login: string,
    senha: string,
    perfil: 'atendente' | 'farmaceutico' | 'gestor'
}

export interface IResponseCreateUser extends ICreateUser {
    ativo: boolean,
    criado_em: Date,
    ultimo_acesso: Date
}

export enum IProfileEnum {
    ATENDENTE = "atendente",
    FARMACEUTICO = "farmaceutico",
    GESTOR = "gestor"
}