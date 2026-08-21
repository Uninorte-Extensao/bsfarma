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
  protected subLabel: string | null = null;

  ngOnInit() {
    this.build();

    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.build();
      });
  }

  private build() {
    const url = this.router.url.split('?')[0];
    const segments = url.split('/').filter(Boolean);
    const breadcrumbs: MenuItem[] = [];
    let currentPath = '';
    let subLabel: string | null = null;

    segments.forEach(segment => {
      currentPath += `/${segment}`;

      const data = this.findRouteData(
        this.router.config,
        currentPath.replace(/^\//, '')
      );

      if (data?.['breadcrumb']) {
        breadcrumbs.push({ label: data['breadcrumb'], routerLink: currentPath });
        subLabel = data['subLabel'] ?? null;
      }
    });

    this.items = breadcrumbs;
    this.subLabel = subLabel;
  }

  private findRouteData(routes: Route[], fullPath: string): { [key: string]: any } | null {
    for (const route of routes) {
      const routePath = route.path ?? '';

      if (this.matchPath(routePath, fullPath) && route.data?.['breadcrumb']) {
        return route.data;
      }

      if (route.children) {
        const found = this.findRouteData(route.children, fullPath);
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