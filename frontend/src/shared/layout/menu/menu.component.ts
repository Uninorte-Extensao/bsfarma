import { Component, inject, model, OnInit, signal, WritableSignal } from '@angular/core';
import { MenuModule } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { Router, RouterModule } from '@angular/router';
import { IUser } from '../../models/IUser';

@Component({
  selector: 'app-menu',
  imports: [MenuModule, RouterModule],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss',
})
export class MenuComponent implements OnInit {
  private router = inject(Router);

  items: MenuItem[] = [];
  isCollapsed = false;
  readonly user: WritableSignal<IUser | undefined> = signal(undefined);

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
            icon: 'pi pi-inbox',
            routerLink: '/lote'
          },
        ],
      },
      {
        label: 'Dispensação',
        items: [
          {
            label: 'Atendimento',
            icon: 'pi pi-chart-line',
            routerLink: '/atendimento'
          },
        ],
      },
      {
        label: 'Alertas',
        items: [
          {
            label: 'Notificações',
            icon: 'pi pi-bell',
            routerLink: '/notificacoes'
          }
        ]
      },
      {
        label: 'Administração',
        items: [
          {
            label: 'Usuários internos',
            icon: 'pi pi-users',
            routerLink: '/users'
          }
        ]
      }
    ];
  }

  toggleMenu() {
    this.isCollapsed = !this.isCollapsed;
    localStorage.setItem('isCollapsed', String(this.isCollapsed));
  }
}