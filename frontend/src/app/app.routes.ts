import { Routes } from '@angular/router';
import { AuthGuard } from './core/authGuard';

export const routes: Routes = [
    {
        path: '',
        loadComponent: () =>
            import('./modules/auth/auth/auth.component')
                .then(r => r.AuthComponent)
    },

    {
        path: '',
        loadComponent: () =>
            import('./modules/home/home.component')
                .then(r => r.HomeComponent), canActivate: [AuthGuard]
    },

    // CATALOGO DE MEDICAMENTOS

    {

        path: 'catalog',
        data: { breadcrumb: 'Medicamentos' },
        loadComponent: () =>
            import('./modules/catalog/catalog.component')
                .then(r => r.CatalogComponent), canActivate: [AuthGuard]
    },
    {
        path: 'catalog/form-medicine',
        data: { breadcrumb: 'Cadastro de medicamentos' },
        loadComponent: () =>
            import('./modules/catalog/form-medicine/form-medicine.component')
                .then(r => r.FormMedicineComponent), canActivate: [AuthGuard]
    },

    {
        path: 'catalog/:id',
        data: { breadcrumb: 'Cadastro de medicamentos' },
        loadComponent: () =>
            import('./modules/catalog/form-medicine/form-medicine.component')
                .then(r => r.FormMedicineComponent), canActivate: [AuthGuard]
    },

    // LOTE

    {
        path: 'batch',
        data: { breadcrumb: 'Movimentação' },
        loadComponent: () =>
            import('./modules/batch/batch.component')
                .then(r => r.BatchComponent), canActivate: [AuthGuard]
    },

    // DISPENSACAO

    {
        path: 'dispensation',
        data: { breadcrumb: 'Atendimento' },
        loadComponent: () =>
            import('./modules/dispensation/dispensation.component')
                .then(r => r.DispensationComponent), canActivate: [AuthGuard]
    },

    // ALERTAS

    {
        path: 'alerts',
        data: { breadcrumb: 'Notificações' },
        loadComponent: () =>
            import('./modules//alerts/alerts.component')
                .then(r => r.AlertsComponent), canActivate: [AuthGuard]
    },

    // GESTAO

    {
        path: 'management',
        data: { breadcrumb: 'Usuários Internos' },
        loadComponent: () =>
            import('./modules//management/management.component')
                .then(r => r.ManagementComponent), canActivate: [AuthGuard]
    },

    { path: '**', redirectTo: '' },

];
