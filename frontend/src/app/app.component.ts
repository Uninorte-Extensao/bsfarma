import { Component, inject } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { LoadingComponent } from "./shared/components/loading/loading.component";
import { Toast } from "primeng/toast"
import { filter } from 'rxjs';
@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    LoadingComponent,
    Toast
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
