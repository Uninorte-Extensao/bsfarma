import { Component, inject, model, OnInit, signal, WritableSignal } from '@angular/core';
import { MenuModule } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { Router, RouterModule } from '@angular/router';
import { IUser } from '../../models/IUser';
import { Badge } from "primeng/badge";
import { AuthService } from '../../services/auth.service';
import { TitleCasePipe, UpperCasePipe, NgClass } from '@angular/common';
import { getInitials } from '../../utils/initialsName';

@Component({
  selector: 'app-menu',
  imports: [
    MenuModule,
    RouterModule,
    Badge,
    TitleCasePipe,
    UpperCasePipe,
    NgClass
  ],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss',
})
export class MenuComponent implements OnInit {
  private router = inject(Router);
  private authService = inject(AuthService)

  protected items: MenuItem[] = [];
  protected isCollapsed = false;
  protected itemsProfile: MenuItem[] = []
  readonly user = this.authService.user;

  ngOnInit() {
    const stored = localStorage.getItem('isCollapsed');
    this.isCollapsed = stored === 'true';

    this.items = [
      {
        label: 'Catálogo',
        items: [
          {
            label: 'Medicamentos',
            icon: 'pi pi-inbox',
            routerLink: '/catalog',
            visible: this.authService.hasPermission('catalog.view')
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
            visible: this.authService.hasPermission('batch.view')
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
            visible: this.authService.hasPermission('dispensation.view')
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
            visible: this.authService.hasPermission('alerts.view')
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
            visible: this.authService.hasPermission('management.view')
          }
        ]
      }
    ];

    this.itemsProfile = [
      {
        label: 'Opções',
        items: [
          {
            label: 'Ver Perfil',
            icon: 'pi pi-user'
          },
          {
            label: 'Sair',
            icon: 'pi pi-sign-out',
            // adicionar um confirmpopup
            command: () => this.logout()
          }
        ]
      }
    ];

    this.items = this.items
      .map(group => ({
        ...group,
        items: group.items?.filter(item => item.visible !== false)
      }))
      .filter(group => group.items && group.items.length > 0);

  }

  toggleMenu() {
    this.isCollapsed = !this.isCollapsed;
    localStorage.setItem('isCollapsed', String(this.isCollapsed));
  }

  private logout() {
    this.authService.logout()
  }

  protected inititalName(name: string): string {
    return getInitials(name)
  }

  getProfileClass(profile: string | undefined) {
    return {
      gestor: profile === 'gestor',
      farmaceutico: profile === 'farmaceutico',
      atendente: profile === 'atendente'
    };
  }

  getTextClass(profile: string | undefined) {
    return {
      textYellow: profile === 'gestor',
      textRed: profile === 'farmaceutico',
      textBlue: profile === 'atendente'
    };
  }
}