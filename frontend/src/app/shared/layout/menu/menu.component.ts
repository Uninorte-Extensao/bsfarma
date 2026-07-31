import { Component, computed, inject, OnInit } from '@angular/core';
import { MenuModule } from 'primeng/menu';
import { RouterModule } from '@angular/router';
import { Badge } from "primeng/badge";
import { AuthService } from '../../services/auth.service';
import { buildMenuItems } from './menu.config';
import { AlertService } from '../../services/alert.service';

@Component({
  selector: 'app-menu',
  imports: [
    MenuModule,
    RouterModule,
    Badge
  ],
  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss',
})
export class MenuComponent implements OnInit {
  private authService = inject(AuthService)
  protected isCollapsed = false;
  private alertService = inject(AlertService)
  protected qtd = computed(() => {
    return this.alertService.quantidadeAlertas()
  })

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
  }

  protected toggleMenu() {
    this.isCollapsed = !this.isCollapsed;
    localStorage.setItem('isCollapsed', String(this.isCollapsed));
  }
}