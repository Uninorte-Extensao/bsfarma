import { Component, model, OnInit } from '@angular/core';
import { PanelMenu, PanelMenuModule } from 'primeng/panelmenu';
import { MenuItem } from 'primeng/api';
import { RouterModule } from '@angular/router';
import { Badge} from 'primeng/badge';

@Component({
  selector: 'app-menu',
  imports: [
    PanelMenuModule,
    RouterModule,
    Badge
  ],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss',
})

export class MenuComponent {
  items: MenuItem[] = [];
  activeItem: MenuItem | undefined | null = null
  imgProfile = model('assets/profile.jpg')
  isCollapsed = false;

  
  ngOnInit() {
    this.items = [
      {
        label: 'Controle',
        icon: 'pi pi-th-large',
        routerLink: '/home',
      },
      {
        label: 'Inventário',
        icon: 'pi pi-inbox',
        routerLink: '/home',
        // items: [
        //   {
        //     label: 'Upload',
        //     icon: 'pi pi-cloud-upload'
        //   },
        //   {
        //     label: 'Download',
        //     icon: 'pi pi-cloud-download'
        //   },
        //   {
        //     label: 'Sync',
        //     icon: 'pi pi-refresh'
        //   }
        // ]
      },
      {
        label: 'Relatórios',
        icon: 'pi pi-chart-line',
        routerLink: '/home',
        // items: [
        //   {
        //     label: 'Phone',
        //     icon: 'pi pi-mobile'
        //   },
        //   {
        //     label: 'Desktop',
        //     icon: 'pi pi-desktop'
        //   },
        //   {
        //     label: 'Tablet',
        //     icon: 'pi pi-tablet'
        //   }
        // ]
      },
      {
        label: 'Configurações',
        icon: 'pi pi-sliders-h',
        routerLink: '/home',
      },
      {
        label: 'Contactar Gerência',
        icon: 'pi pi-users',
        routerLink: '/home',

      },
      {
        label: 'Notificações',
        icon: 'pi pi-bell',
        routerLink: '/home',

      },
      {
        label: 'Fornecedores',
        icon: 'pi pi-comment',
        routerLink: '/home',
      },
      {
        label: 'Configurações do aplicativo',
        icon: 'pi pi-cog',
        routerLink: '/home',

      },

      {
        label: 'Covid 19',
        icon: 'pi pi-asterisk',
        routerLink: '/home',

      },

      {
        label: 'Contactar Suport',
        icon: 'pi pi-question-circle',
        routerLink: '/home',

      },
    ];
  }
  
  selectItem(item: MenuItem) {
    this.activeItem = item
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
