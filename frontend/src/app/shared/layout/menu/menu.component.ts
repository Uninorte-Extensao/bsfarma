import { Component, computed, inject, OnInit } from '@angular/core';
import { MenuModule } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { RouterModule } from '@angular/router';
import { Badge } from "primeng/badge";
import { AuthService } from '../../services/auth.service';
import { TitleCasePipe, UpperCasePipe, NgClass } from '@angular/common';
import { getInitials } from '../../utils/initialsName';
import { buildMenuItems, buildProfileMenu } from './menu.config';
import { AlertService } from '../../services/alert.service';

@Component({
  selector: 'app-menu',
  imports: [
    MenuModule,
    RouterModule,
    Badge,
    TitleCasePipe,
    UpperCasePipe,
    NgClass
  ],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss',
})
export class MenuComponent implements OnInit {
  private authService = inject(AuthService)
  // protected items: MenuItem[] = [];
  protected isCollapsed = false;
  protected itemsProfile: MenuItem[] = []
  readonly user = this.authService.user;
  private alertService = inject(AlertService)

  items = computed(() => {

    const menu = buildMenuItems(
      this.authService,
      this.alertService.quantidadeAlertas()
    );

    return menu
      .map(group => ({
        ...group,
        items: group.items?.filter(
          item => item.visible !== false
        )
      }))
      .filter(
        group => group.items && group.items.length > 0
      );

  });

  ngOnInit() {
    const stored = localStorage.getItem('isCollapsed');
    this.isCollapsed = stored === 'true';

    this.alertService.atualizarQuantidadeAlertas();

    this.itemsProfile = buildProfileMenu(
      () => this.logout()
    );
  }
  protected toggleMenu() {
    this.isCollapsed = !this.isCollapsed;
    localStorage.setItem('isCollapsed', String(this.isCollapsed));
  }

  private logout() {
    this.authService.logout()
  }

  protected inititalName(name: string): string {
    return getInitials(name)
  }

  protected getProfileClass(profile: string | undefined) {
    return {
      gestor: profile === 'gestor',
      farmaceutico: profile === 'farmaceutico',
      atendente: profile === 'atendente'
    };
  }

  protected getTextClass(profile: string | undefined) {
    return {
      textYellow: profile === 'gestor',
      textRed: profile === 'farmaceutico',
      textBlue: profile === 'atendente'
    };
  }

  protected toggleProfileMenu(event: Event, menu: any) {
    menu.toggle(event);
  }
}