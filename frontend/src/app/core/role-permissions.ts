import { IProfileEnum } from "../shared/models/IUser";
import { Permission } from "./permissions.enum";


// ATENDENTE = REGISTRAR DISPENSAÇÕES, CONSULTAR ESTOQUE
// FARMACEUTICO = TUDO DO ATENDENTE + GERENCIAR LOTES E ALERTAS
// GESTOR = ACESSO TOTAL, INCLUINDO USUÁRIOS E RELATÓRIO

export const ROLE_PERMISSIONS: Record<IProfileEnum, Permission[]> = {
    atendente: [
        'catalog.view',
        
        'batch.view',
  
        'dispersation.view',
        'dispersation.create',
    ],

    farmaceutico: [
        'catalog.view',
        'catalog.create',
        'catalog.update',

        'batch.view',
        'batch.create',
        'batch.update',
        'batch.delete',

        'dispersation.view',
        'dispersation.create',

        'alerts.view'
    ],

    gestor: [
        'catalog.view',
        'catalog.create',
        'catalog.update',
        'catalog.delete',

        'batch.view',
        'batch.create',
        'batch.update',
        'batch.delete',

        'dispersation.view',
        'dispersation.create',
        'dispersation.update',
        'dispersation.delete',

        'alerts.view',

        'management.view',
        'management.create',
        'management.update',
        'management.delete'
    ]
}