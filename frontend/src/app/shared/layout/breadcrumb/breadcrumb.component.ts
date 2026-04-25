import { Component, inject } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Breadcrumb } from 'primeng/breadcrumb';
import { ActivatedRoute, NavigationEnd, Router, RouterModule } from '@angular/router';
import { filter } from 'rxjs';

@Component({
  selector: 'app-breadcrumb',
  imports: [
    Breadcrumb,
    RouterModule
  ],
  templateUrl: './breadcrumb.component.html',
  styleUrl: './breadcrumb.component.scss',
})
export class BreadcrumbComponent {
  private router = inject(Router);
  protected items: MenuItem[] = [];

  ngOnInit() {
    this.items = this.buildBreadcrumb();

    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.items = this.buildBreadcrumb();
      });
  }

  private buildBreadcrumb(): MenuItem[] {
    const url = this.router.url;
    const breadcrumbs: MenuItem[] = [];

    const routes = this.router.config;

    const segments = url.split('/').filter(Boolean);
    let currentPath = '';

    segments.forEach(segment => {
      currentPath += `/${segment}`;

      const route = routes.find(r => `/${r.path}` === currentPath);

      if (route?.data?.['breadcrumb']) {
        breadcrumbs.push({
          label: route.data['breadcrumb'],
          routerLink: currentPath
        });
      }
    });

    return breadcrumbs;
  }
}
