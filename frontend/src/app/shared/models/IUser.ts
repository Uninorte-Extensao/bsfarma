export interface IUser {
    id?: number,
    nome: string,
    perfil: 'Administrador' | 'Funcionário'
    image: string
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