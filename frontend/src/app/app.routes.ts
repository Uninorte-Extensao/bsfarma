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
                path: 'catalog/form-medicine',
                data: { breadcrumb: 'Cadastro de medicamentos' },
                loadComponent: () =>
                    import('./modules/catalog/form-medicine/form-medicine.component')
                        .then(r => r.FormMedicineComponent)
            },

            // {
            //     path: 'catalog/:id',
            //     data: { breadcrumb: 'Cadastro de medicamentos' },
            //     loadComponent: () =>
            //         import('./modules/catalog/form-medicine/form-medicine.component')
            //             .then(r => r.FormMedicineComponent)
            // },

            // LOTE

            {
                path: 'batch',
                data: { breadcrumb: 'Movimentação' },
                loadComponent: () =>
                    import('./modules/batch/batch.component')
                        .then(r => r.BatchComponent)
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
                    permission: 'alert.view' 
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

        ]
    },

    { path: '**', redirectTo: 'auth' },

];
