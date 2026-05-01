import { Component, inject, OnInit } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { LoadingComponent } from "./shared/components/loading/loading.component";
import { Toast } from "primeng/toast"
import { filter } from 'rxjs';
import { AuthService } from './shared/services/auth.service';
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
export class AppComponent implements OnInit {
  title = 'bsfarma';
  isAuthRoute = false;

  private router = inject(Router);
  private authService = inject(AuthService);

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

  ngOnInit() {
    const token = localStorage.getItem('tokenBsFarma')

    if(token) {
      this.authService.loadUser()
    }
  }
}
