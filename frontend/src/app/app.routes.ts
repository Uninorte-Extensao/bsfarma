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
        loadComponent: () =>
            import('./modules/catalog/catalog.component')
                .then(r => r.CatalogComponent)
    }
];
