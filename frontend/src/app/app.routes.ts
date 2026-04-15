import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: 'home',
        loadComponent: () =>
            import('./modules/home/home.component')
                .then(r => r.HomeComponent)
    },

    {
        path: 'control',
        loadComponent: () =>
            import('./modules/control/control.component')
                .then(r => r.ControlComponent)
    }
];
