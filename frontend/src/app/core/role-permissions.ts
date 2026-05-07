import { IProfileEnum } from "../shared/models/IUser";
import { Permission } from "./permissions.enum";


// ATENDENTE = REGISTRAR DISPENSAÇÕES, CONSULTAR ESTOQUE
// FARMACEUTICO = TUDO DO ATENDENTE + GERENCIAR LOTES E ALERTAS
// GESTOR = ACESSO TOTAL, INCLUINDO USUÁRIOS E RELATÓRIO

export const ROLE_PERMISSIONS: Record<IProfileEnum, Permission[]> = {
    atendente: [
        'catalog.view',
        
        'batch.view',
  
        'dispensation.view',
        'dispensation.create',
    ],

    farmaceutico: [
        'catalog.view',
        'catalog.create',
        'catalog.update',

        'batch.view',
        'batch.create',
        'batch.update',
        'batch.delete',

        'dispensation.view',
        'dispensation.create',

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

        'dispensation.view',
        'dispensation.create',
        'dispensation.update',
        'dispensation.delete',

        'alerts.view',

        'management.view',
        'management.create',
        'management.update',
        'management.delete'
    ]
}