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
            routerLink: '/catalog'
          },
        ]
      },
      {
        label: 'Lote',
        items: [
          {
            label: 'Movimentação',
            icon: 'pi pi-chart-line',
            routerLink: '/batch'
          },
        ],
      },
      {
        label: 'Dispensação',
        items: [
          {
            label: 'Atendimento',
            icon: 'pi pi-receipt',
            routerLink: '/dispensation'
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
            routerLink: '/management'
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
            icon: 'pi pi-person'
          },
          {
            label: 'Sair',
            icon: 'pi pi-logout',
            // adicionar um confirmpopup
            command: () => this.logout()
          }
        ]
      }
    ];

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
}