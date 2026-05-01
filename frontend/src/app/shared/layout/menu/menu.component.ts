import { Component, inject, model, OnInit, signal, WritableSignal } from '@angular/core';
import { MenuModule } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { Router, RouterModule } from '@angular/router';
import { IUser } from '../../models/IUser';
import { Badge } from "primeng/badge";
import { AuthService } from '../../services/auth.service';
import { Button } from 'primeng/button';

@Component({
  selector: 'app-menu',
  imports: [MenuModule, RouterModule, Badge, Button],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss',
})
export class MenuComponent implements OnInit {
  private router = inject(Router);
  private authService = inject(AuthService)

  items: MenuItem[] = [];
  isCollapsed = false;
  readonly user: WritableSignal<any | undefined> = signal(undefined);
  protected itemsProfile: MenuItem[] = []
  ngOnInit() {
    const stored = localStorage.getItem('isCollapsed');
    this.isCollapsed = stored === 'true';

    this.user.set({
      nome: 'Juliana Salgado',
      perfil: 'Administrador',
      image: 'assets/profile.jpg'
    });

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
            badge: '3'
          }
        ]
      },
      {
        label: 'Gestão',
        items: [
          {
            label: 'Usuários internos',
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
}