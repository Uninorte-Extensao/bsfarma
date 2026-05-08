import { Component, inject, OnInit } from '@angular/core';
import { MenuItem } from 'primeng/api';
import { Breadcrumb } from 'primeng/breadcrumb';
import { NavigationEnd, Router, RouterModule, Route } from '@angular/router';
import { filter } from 'rxjs';

@Component({
  selector: 'app-breadcrumb',
  imports: [Breadcrumb, RouterModule],
  templateUrl: './breadcrumb.component.html',
  styleUrl: './breadcrumb.component.scss',
})
export class BreadcrumbComponent implements OnInit {
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
    const url = this.router.url.split('?')[0];
    const segments = url.split('/').filter(Boolean);
    const breadcrumbs: MenuItem[] = [];
    let currentPath = '';

    segments.forEach(segment => {
      currentPath += `/${segment}`;

      const label = this.findBreadcrumbLabel(
        this.router.config,
        currentPath.replace(/^\//, '') 
      );

      if (label) {
        breadcrumbs.push({ label, routerLink: currentPath });
      }
    });

    return breadcrumbs;
  }

  private findBreadcrumbLabel(routes: Route[], fullPath: string): string | null {
    for (const route of routes) {
      const routePath = route.path ?? '';

      if (this.matchPath(routePath, fullPath) && route.data?.['breadcrumb']) {
        return route.data['breadcrumb'];
      }

      if (route.children) {
        const found = this.findBreadcrumbLabel(route.children, fullPath);
        if (found) return found;
      }
    }

    return null;
  }

  private matchPath(routePath: string, urlPath: string): boolean {
    const routeSegments = routePath.split('/');
    const urlSegments = urlPath.split('/');

    if (routeSegments.length !== urlSegments.length) return false;

    return routeSegments.every((seg, i) =>
      seg.startsWith(':') || seg === urlSegments[i]
    );
  }
}