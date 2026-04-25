export interface IUser {
    id?: number,
    nome: string,
    perfil: 'Administrador' | 'Funcionário'
    image: string
}
