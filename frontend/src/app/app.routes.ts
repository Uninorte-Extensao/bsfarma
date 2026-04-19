import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: 'home',
        loadComponent: () =>
            import('./modules/home/home.component')
                .then(r => r.HomeComponent)
    },

    // CATALOGO DE MEDICAMENTOS

    {

        path: 'catalog',
        data: { breadcrumb: 'Medicamentos' },
        loadComponent: () =>
            import('./modules/catalog/catalog.component')
                .then(r => r.CatalogComponent),
    },
    {
        path: 'catalog/form-medicine',
        data: { breadcrumb: 'Cadastro de medicamentos' },
        loadComponent: () =>
            import('./modules/catalog/form-medicine/form-medicine.component')
                .then(r => r.FormMedicineComponent),
    },

    {
        path: 'catalog/:id',
        data: { breadcrumb: 'Cadastro de medicamentos' },
        loadComponent: () =>
            import('./modules/catalog/form-medicine/form-medicine.component')
                .then(r => r.FormMedicineComponent),
    },

    // LOTE

    {
        path: 'batch',
        data: { breadcrumb: 'Movimentação' },
        loadComponent: () =>
            import('./modules/batch/batch.component')
                .then(r => r.BatchComponent),
    },

    // DISPENSACAO

    {
        path: 'dispensation',
        data: { breadcrumb: 'Atendimento' },
        loadComponent: () =>
            import('./modules/dispensation/dispensation.component')
                .then(r => r.DispensationComponent),
    },

    // ALERTAS

    {
        path: 'alerts',
        data: { breadcrumb: 'Notificações' },
        loadComponent: () =>
            import('./modules//alerts/alerts.component')
                .then(r => r.AlertsComponent),
    },

    // GESTAO

    {
        path: 'management',
        data: { breadcrumb: 'Usuários Internos' },
        loadComponent: () =>
            import('./modules//management/management.component')
                .then(r => r.ManagementComponent),
    }

];
