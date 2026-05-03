import { MenuItem } from 'primeng/api';
import { AuthService } from '../../services/auth.service';

export function buildMenuItems(authService: AuthService): MenuItem[] {
    return [
        {
            label: 'Catálogo',
            items: [
                {
                    label: 'Medicamentos',
                    icon: 'pi pi-inbox',
                    routerLink: '/catalog',
                    visible: authService.hasPermission('catalog.view')
                },
            ]
        },

        {
            label: 'Lote',
            items: [
                {
                    label: 'Movimentação',
                    icon: 'pi pi-chart-line',
                    routerLink: '/batch',
                    visible: authService.hasPermission('batch.view')
                },
            ],
        },

        {
            label: 'Dispensação',
            items: [
                {
                    label: 'Atendimento',
                    icon: 'pi pi-receipt',
                    routerLink: '/dispensation',
                    visible: authService.hasPermission('dispensation.view')
                },
            ],
        },

        {
            label: 'Alertas',
            items: [
                {
                    label: 'Notificações',
                    icon: 'pi pi-bell',
                    routerLink: '/alerts',
                    visible: authService.hasPermission('alerts.view')
                    // badge: '3'
                }
            ]
        },

        {
            label: 'Gestão',
            items: [
                {
                    label: 'Usuários',
                    icon: 'pi pi-users',
                    routerLink: '/management',
                    visible: authService.hasPermission('management.view')
                }
            ]
        }
    ];
}

export function buildProfileMenu(logout: () => void): MenuItem[] {
    return [
        {
            label: 'Opções',
            items: [
                {
                    label: 'Sair',
                    icon: 'pi pi-sign-out',
                    command: logout
                }
            ]
        }
    ];
}