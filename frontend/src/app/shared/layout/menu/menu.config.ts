import { MenuItem } from 'primeng/api';
import { AuthService } from '../../services/auth.service';

export function buildMenuItems(authService: AuthService, quantidadeAlertas: number): MenuItem[] {
    return [
        {
            // label: 'Menu',
            items: [
                {
                    label: 'Painel de Controle',
                    icon: 'pi pi-chart-bar',
                    routerLink: '/report',
                    visible: authService.hasPermission('report.view')
                },
                {
                    label: 'Medicamentos',
                    icon: 'pi pi-inbox',
                    routerLink: '/catalog',
                    visible: authService.hasPermission('catalog.view')
                },

                {
                    label: 'Lote',
                    icon: 'pi pi-box',
                    routerLink: '/batch',
                    visible: authService.hasPermission('batch.view')
                },
                {
                    label: 'Movimentações',
                    icon: 'pi pi-arrow-right-arrow-left',
                    routerLink: '/movement',
                    visible: authService.hasPermission('movement.view')
                },


                {
                    label: 'Atendimento',
                    icon: 'pi pi-receipt',
                    routerLink: '/dispersation',
                    visible: authService.hasPermission('dispersation.view')

                },



                {
                    label: 'Notificações',
                    icon: 'pi pi-bell',
                    routerLink: '/alerts',
                    visible: authService.hasPermission('alerts.view'),
                    badge: quantidadeAlertas > 0
                        ? String(quantidadeAlertas)
                        : undefined

                },

                {

                    label: 'Usuários',
                    icon: 'pi pi-users',
                    routerLink: '/management',
                    visible: authService.hasPermission('management.view')
                },
                {
                    label: 'Pacientes',
                    icon: 'pi pi-user',
                    routerLink: '/patient',
                    visible: authService.hasPermission('patient.view')
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