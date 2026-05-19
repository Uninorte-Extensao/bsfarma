import { Routes } from '@angular/router';
import { AuthGuard } from './core/authGuard';
import { permissionGuard } from './core/permissionGuard';

export const routes: Routes = [
    {
        path: 'auth',
        loadComponent: () =>
            import('./modules/auth/auth/auth.component')
                .then(r => r.AuthComponent)
    },

    {
        path: '',
        canActivate: [AuthGuard],
        canActivateChild: [permissionGuard],
        loadComponent: () =>
            import('./modules/home/home.component')
                .then(r => r.HomeComponent),
        children: [

            // MEDICAMENTOS
            {
                path: '',
                redirectTo: 'catalog',
                pathMatch: 'full'
            },
            {

                path: 'catalog',
                data: {
                    breadcrumb: 'Medicamentos',
                    permission: 'catalog.view'
                },
                loadComponent: () =>
                    import('./modules/catalog/catalog.component')
                        .then(r => r.CatalogComponent)
            },
            {
                path: 'catalog/create',
                data: { 
                    breadcrumb: 'Cadastro de medicamento',
                    permission: 'catalog.create'
                 },
                loadComponent: () =>
                    import('./modules/catalog/form-medicine/form-medicine.component')
                        .then(r => r.FormMedicineComponent)
            },

            {
                path: 'catalog/edit/:id',
                data: { 
                    breadcrumb: 'Edição de medicamento',
                    permission: 'catalog.update'
                 },
                loadComponent: () =>
                    import('./modules/catalog/form-medicine/form-medicine.component')
                        .then(r => r.FormMedicineComponent)
            },

            // LOTE

            {
                path: 'batch',
                data: { 
                    breadcrumb: 'Lote',
                    permission: 'batch.view'
                 },
                loadComponent: () =>
                    import('./modules/batch/batch.component')
                        .then(r => r.BatchComponent)
            },

            {
                path: 'batch/create',
                data: { 
                    breadcrumb: 'Entrada de Lote',
                    permission: 'batch.create'
                 },
                loadComponent: () =>
                    import('./modules/batch/form-batch/form-batch.component')
                        .then(r => r.FormBatchComponent)

            },

            {
                path: 'batch/edit/:id',
                data: { 
                    breadcrumb: 'Edição de Lote',
                    permission: 'batch.update'
                },
                loadComponent: () =>
                    import('./modules/batch/form-batch/form-batch.component')
                        .then(r => r.FormBatchComponent)

            },

            // MOVIMENTACAO

            {
                path: 'movement',
                data: { 
                    breadcrumb: 'Movimentação de Lote',
                    permission: 'movement.view'
                },
                loadComponent: () =>
                    import('./modules/movement/movement.component')
                        .then(r => r.MovementComponent)

            },

            {
                path: 'movement/create',
                data: { 
                    breadcrumb: 'Criar Movimentação',
                    permission: 'movement.create'
                 },
                loadComponent: () =>
                    import('./modules/movement/form-movement/form-movement.component')
                        .then(r => r.FormMovementComponent)
            },
            {
                path: 'movement/edit/:id',
                data: { 
                    breadcrumb: 'Editar Movimentação',
                    permission: 'movement.update'
                },
                loadComponent: () =>
                    import('./modules/movement/form-movement/form-movement.component')
                        .then(r => r.FormMovementComponent)
            },

            // DISPERSACAO

            {
                path: 'dispersation',
                data: {
                    breadcrumb: 'Atendimento',
                    permission: 'dispersation.view'
                },
                loadComponent: () =>
                    import('./modules/dispersation/dispersation.component')
                        .then(r => r.DispersationComponent)
            },

            // ALERTAS

            {
                path: 'alerts',
                data: {
                    breadcrumb: 'Notificações',
                    permission: 'alerts.view'
                },
                loadComponent: () =>
                    import('./modules//alerts/alerts.component')
                        .then(r => r.AlertsComponent)
            },

            // GESTAO

            {
                path: 'management',
                data: {
                    breadcrumb: 'Usuários',
                    permission: 'management.view'
                },
                loadComponent: () =>
                    import('./modules//management/management.component')
                        .then(r => r.ManagementComponent)
            },
            {
                path: 'management/create',
                data: {
                    breadcrumb: 'Adicionar Usuário',
                    permission: 'management.create'
                },
                loadComponent: () =>
                    import('./modules/management/form-user/form-user.component')
                        .then(r => r.FormUserComponent)
            },

            {
                path: 'management/edit/:id',
                data: {
                    breadcrumb: 'Editar Usuário',
                    permission: 'management.update'
                },
                loadComponent: () =>
                    import('./modules/management/form-user/form-user.component')
                        .then(r => r.FormUserComponent)
            },

            {
                path: 'patient',
                data: {
                    breadcrumb: 'Pacientes',
                    permission: 'patient.view'
                },
                loadComponent: () =>
                    import('./modules/patient/patient.component')
                        .then(r => r.PatientComponent)
            }

        ]
    },

    { path: '**', redirectTo: 'auth' },

];
