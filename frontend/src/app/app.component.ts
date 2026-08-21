import { Component, inject } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { Toast } from 'primeng/toast';
import { LoadingComponent } from './shared/components/loading/loading.component';
import { ThemeService } from './shared/services/theme.service';

@Component({
    selector: 'app-root',
    imports: [RouterOutlet, LoadingComponent, Toast],
    templateUrl: './app.component.html',
    styleUrl: './app.component.scss'
})
export class AppComponent {
    isAuthRoute = false;
    private router = inject(Router);
    private themeService = inject(ThemeService);

    constructor() {
        this.router.events
            .pipe(filter(e => e instanceof NavigationEnd))
            .subscribe(() => this.isAuthRoute = this.router.url === '/auth');
    }

    // ngOnInit removido — APP_INITIALIZER cuida do loadUser
}