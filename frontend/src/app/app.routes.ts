import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: 'home',
        loadComponent: () =>
            import('./modules/home/home.component')
                .then(r => r.HomeComponent)
    },

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
    }

];
