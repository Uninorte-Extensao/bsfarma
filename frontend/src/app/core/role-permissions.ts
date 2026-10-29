import { IProfileEnum } from "../shared/models/IUser";
import { Permission } from "./permissions.enum";


// ATENDENTE = REGISTRAR DISPENSAÇÕES, CONSULTAR ESTOQUE
// FARMACEUTICO = TUDO DO ATENDENTE + GERENCIAR LOTES E ALERTAS
// GESTOR = ACESSO TOTAL, INCLUINDO USUÁRIOS E RELATÓRIO
//
// Espelha o require_perfil() de cada router do backend: uma permissão só
// existe aqui se o backend aceitar a requisição correspondente.

export const ROLE_PERMISSIONS: Record<IProfileEnum, Permission[]> = {
    atendente: [
        'catalog.view',

        'batch.view',

        'dispersation.view',
        'dispersation.create',

        'alerts.view',

        'patient.view',
        'patient.create',
        'patient.update',
    ],

    farmaceutico: [
        'catalog.view',

        'batch.view',
        'batch.create',
        'batch.update',

        'dispersation.view',
        'dispersation.create',

        'alerts.view',

        'patient.view',
        'patient.create',
        'patient.update',

        'movement.view',
        'movement.create',
    ],

    gestor: [
        'catalog.view',
        'catalog.create',
        'catalog.update',
        'catalog.delete',

        'batch.view',
        'batch.create',
        'batch.update',

        'dispersation.view',
        'dispersation.create',

        'alerts.view',

        'management.view',
        'management.create',
        'management.update',

        'patient.view',
        'patient.create',
        'patient.update',
        'patient.delete',

        'movement.view',
        'movement.create',
        'movement.update',

        'report.view',
    ]
}
