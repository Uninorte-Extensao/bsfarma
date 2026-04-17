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
  activeItem: MenuItem | null = null;
  isCollapsed = false;
  readonly user: WritableSignal<IUser | undefined> = signal(undefined);

  ngOnInit() {
    this.user.set({
      nome: 'Juliana Salgado',
      perfil: 'Administrador',
      image: 'assets/profile.jpg'
    })

    this.items = [
        { label: 'Controle', icon: 'pi pi-th-large', routerLink: '/control' },
        {
          label: 'Inventário',
          icon: 'pi pi-inbox',
          routerLink: '/home',
          // items: [
          //   { label: 'Medicamentos', icon: 'pi pi-inbox' },
          //   { label: 'Grupo de Medicamentos', icon: 'pi pi-inbox' },
          // ],
        },
        {
          label: 'Relatórios',
          icon: 'pi pi-chart-line',
          routerLink: '/home',
          // items: [
          //   { label: 'Mensal', icon: 'pi pi-calendar' },
          //   { label: 'Anual', icon: 'pi pi-chart-bar' },
          // ],
        },
        { label: 'Configurações', icon: 'pi pi-sliders-h', routerLink: '/home' },
        { label: 'Contactar Gerência', icon: 'pi pi-users', routerLink: '/home' },
        { label: 'Notificações', icon: 'pi pi-bell', routerLink: '/home' },
        { label: 'Fornecedores', icon: 'pi pi-comment', routerLink: '/home' },
        { label: 'Configurações do aplicativo', icon: 'pi pi-cog', routerLink: '/home' },
        { label: 'Covid 19', icon: 'pi pi-asterisk', routerLink: '/home' },
        { label: 'Contactar Suport', icon: 'pi pi-question-circle', routerLink: '/home' },
      ];
  }

  selectItem(item: MenuItem) {
    if (item.items?.length) return;
    this.activeItem = item;
    this.router.navigate([item.routerLink])
  }

  isActive(item: MenuItem): boolean {
    return this.activeItem === item;
  }

  toggleMenu() {
    this.isCollapsed = !this.isCollapsed;
  }

  toggleAll() {
    const expanded = !this.areAllItemsExpanded();
    this.items = this.toggleAllRecursive(this.items, expanded);
  }

  private toggleAllRecursive(items: MenuItem[], expanded: boolean): MenuItem[] {
    return items.map((menuItem) => {
      menuItem.expanded = expanded;
      if (menuItem.items) {
        menuItem.items = this.toggleAllRecursive(menuItem.items, expanded);
      }
      return menuItem;
    });
  }

  private areAllItemsExpanded(): boolean {
    return this.items.every((menuItem) => menuItem.expanded);
  }
}