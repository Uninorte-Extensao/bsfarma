import { Routes } from '@angular/router';
import { authGuard, homeRedirectGuard, permissionGuard } from './core/authGuard';
import { HomeComponent } from './modules/home/home.component';

export const routes: Routes = [
    {
        path: 'auth',
        loadComponent: () =>
            import('./modules/auth/auth/auth.component').then(r => r.AuthComponent)
    },
    {
        path: '',
        canActivate: [authGuard],
        canActivateChild: [permissionGuard],
        loadComponent: () =>
            import('./modules/home/home.component').then(r => r.HomeComponent),
        children: [
            {
                path: '',
                pathMatch: 'full',
                canActivate: [homeRedirectGuard],
                component: HomeComponent
            },
            {
                path: 'report',
                data: { breadcrumb: 'Painel de Controle', subLabel: 'Visão Geral do Inventário', permission: 'report.view' },
                loadComponent: () =>
                    import('./modules/report/report.component').then(r => r.ReportComponent)
            },
            {
                path: 'catalog',
                data: { breadcrumb: 'Medicamentos', subLabel: 'Lista de medicamentos.', permission: 'catalog.view' },
                loadComponent: () =>
                    import('./modules/catalog/catalog.component').then(r => r.CatalogComponent)
            },
            {
                path: 'catalog/create',
                data: { breadcrumb: 'Cadastro de medicamento', subLabel: 'Cadastro de medicamento.', permission: 'catalog.create' },
                loadComponent: () =>
                    import('./modules/catalog/form-medicine/form-medicine.component').then(r => r.FormMedicineComponent)
            },
            {
                path: 'catalog/edit/:id',
                data: { breadcrumb: 'Edição de medicamento', subLabel: 'Cadastro de medicamento.', permission: 'catalog.update' },
                loadComponent: () =>
                    import('./modules/catalog/form-medicine/form-medicine.component').then(r => r.FormMedicineComponent)
            },
            {
                path: 'batch',
                data: { breadcrumb: 'Lote', subLabel: 'Lista de Lotes', permission: 'batch.view' },
                loadComponent: () =>
                    import('./modules/batch/batch.component').then(r => r.BatchComponent)
            },
            {
                path: 'batch/create',
                data: { breadcrumb: 'Entrada de Lote', subLabel: 'Registre a entrada de novos medicamentos no estoque.', permission: 'batch.create' },
                loadComponent: () =>
                    import('./modules/batch/form-batch/form-batch.component').then(r => r.FormBatchComponent)
            },
            {
                path: 'batch/edit/:id',
                data: { breadcrumb: 'Edição de Lote', subLabel: 'Registre a entrada de novos medicamentos no estoque.', permission: 'batch.update' },
                loadComponent: () =>
                    import('./modules/batch/form-batch/form-batch.component').then(r => r.FormBatchComponent)
            },
            {
                path: 'movement',
                data: { breadcrumb: 'Movimentação de Lote', subLabel: 'Novo Atendimento.', permission: 'movement.view' },
                loadComponent: () =>
                    import('./modules/movement/movement.component').then(r => r.MovementComponent)
            },
            {
                path: 'movement/create',
                data: { breadcrumb: 'Criar Movimentação', subLabel: 'Registre movimentações de estoque.', permission: 'movement.create' },
                loadComponent: () =>
                    import('./modules/movement/form-movement/form-movement.component').then(r => r.FormMovementComponent)
            },
            {
                path: 'movement/edit/:id',
                data: { breadcrumb: 'Editar Movimentação', subLabel: 'Registre movimentações de estoque.', permission: 'movement.update' },
                loadComponent: () =>
                    import('./modules/movement/form-movement/form-movement.component').then(r => r.FormMovementComponent)
            },
            {
                path: 'dispersation',
                data: { breadcrumb: 'Atendimentos Realizados', subLabel: 'Histórico de dispersação de medicamentos na unidade.', permission: 'dispersation.view' },
                loadComponent: () =>
                    import('./modules/dispersation/dispersation.component').then(r => r.DispersationComponent)
            },
            {
                path: 'dispersation/create',
                data: { breadcrumb: 'Novo Atendimento', subLabel: 'Registro dispersação de medicamentos para pacientes cadastrados.', permission: 'dispersation.create' },
                loadComponent: () =>
                    import('./modules/dispersation/form-dispersation/form-dispersation.component').then(r => r.FormDispersationComponent)
            },
            {
                path: 'dispersation/edit',
                data: { breadcrumb: 'Editar Atendimento', subLabel: 'Registro dispersação de medicamentos para pacientes cadastrados.', permission: 'dispersation.update' },
                loadComponent: () =>
                    import('./modules/dispersation/form-dispersation/form-dispersation.component').then(r => r.FormDispersationComponent)
            },
            {
                path: 'alerts',
                data: { breadcrumb: 'Notificações', subLabel: 'Lista de Alertas', permission: 'alerts.view' },
                loadComponent: () =>
                    import('./modules/alerts/alerts.component').then(r => r.AlertsComponent)
            },
            {
                path: 'management',
                data: { breadcrumb: 'Usuários', subLabel: 'Lista de usuários.', permission: 'management.view' },
                loadComponent: () =>
                    import('./modules/management/management.component').then(r => r.ManagementComponent)
            },
            {
                path: 'management/create',
                data: { breadcrumb: 'Adicionar Usuário', permission: 'management.create' },
                loadComponent: () =>
                    import('./modules/management/form-user/form-user.component').then(r => r.FormUserComponent)
            },
            {
                path: 'management/edit/:id',
                data: { breadcrumb: 'Editar Usuário', permission: 'management.update' },
                loadComponent: () =>
                    import('./modules/management/form-user/form-user.component').then(r => r.FormUserComponent)
            },
            {
                path: 'patient',
                data: { breadcrumb: 'Pacientes', subLabel: 'Lista de pacientes.', permission: 'patient.view' },
                loadComponent: () =>
                    import('./modules/patient/patient.component').then(r => r.PatientComponent)
            }
        ]
    },
    { path: '**', redirectTo: 'auth' }
];
