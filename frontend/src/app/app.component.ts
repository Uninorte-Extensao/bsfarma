import { Component, inject } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { MenuComponent } from '../app/shared/layout/menu/menu.component';
import { HeaderComponent } from '../app/shared/layout/header/header.component';
import { BreadcrumbComponent } from "../app/shared/layout/breadcrumb/breadcrumb.component";
import { LoadingComponent } from "./shared/components/loading/loading.component";
import { Toast } from "primeng/toast"
import { HomeComponent } from "./modules/home/home.component";
import { filter } from 'rxjs';
@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    LoadingComponent,
    Toast,
    MenuComponent,
    HeaderComponent,
    BreadcrumbComponent,
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'bsfarma';

  router = inject(Router);

  isAuthRoute = false;

  constructor() {

    this.router.events
      .pipe(
        filter(event => event instanceof NavigationEnd)
      )
      .subscribe(() => {
        this.isAuthRoute =
          this.router.url === '/auth';
      });
  }
}
