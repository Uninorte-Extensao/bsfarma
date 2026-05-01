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
    token_type: string,
    id_user: string
}

export interface ICreateUser {
    nome: string,
    login: string,
    senha: string,
    perfil: 'atendente' | 'farmaceutico' | 'gestor'
}

export interface IResponseUser extends ICreateUser {
    ativo: boolean,
    criado_em: Date,
    ultimo_acesso: Date,
    id: string
}

export enum IProfileEnum {
    ATENDENTE = "atendente",
    FARMACEUTICO = "farmaceutico",
    GESTOR = "gestor"
}

export const PROFILE_OPTIONS = [
  { label: 'Atendente', value: IProfileEnum.ATENDENTE },
  { label: 'Farmacêutico', value: IProfileEnum.FARMACEUTICO },
  { label: 'Gestor', value: IProfileEnum.GESTOR }
];