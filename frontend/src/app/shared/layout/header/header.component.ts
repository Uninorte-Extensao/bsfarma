import { Component, computed, inject, OnInit } from '@angular/core';
import { TitleCasePipe, UpperCasePipe, NgClass } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MenuModule } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { AuthService } from '../../services/auth.service';
import { AlertService } from '../../services/alert.service';
import { ThemeService } from '../../services/theme.service';
import { getInitials } from '../../utils/initialsName';
import { buildProfileMenu } from '../menu/menu.config';
import { BreadcrumbComponent } from '../breadcrumb/breadcrumb.component';

@Component({
  selector: 'app-header',
  imports: [
    TitleCasePipe,
    UpperCasePipe,
    NgClass,
    MenuModule,
    RouterLink,
    BreadcrumbComponent
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
})
export class HeaderComponent implements OnInit {
  private authService = inject(AuthService);
  private alertService = inject(AlertService);
  protected themeService = inject(ThemeService);

  readonly user = this.authService.user;
  protected itemsProfile: MenuItem[] = [];
  protected qtd = computed(() => this.alertService.quantidadeAlertas());

  ngOnInit() {
    this.itemsProfile = buildProfileMenu(() => this.logout());
  }

  protected toggleTheme() {
    this.themeService.toggle();
  }

  private logout() {
    this.authService.logout();
  }

  protected inititalName(name: string): string {
    return getInitials(name);
  }

  protected getProfileClass(profile: string | undefined) {
    return {
      gestor: profile === 'gestor',
      farmaceutico: profile === 'farmaceutico',
      atendente: profile === 'atendente'
    };
  }
}
