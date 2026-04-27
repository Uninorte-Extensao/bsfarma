import { Component, signal } from '@angular/core';
import { MenuComponent } from '../../shared/layout/menu/menu.component';
import { HeaderComponent } from '../../shared/layout/header/header.component';
import { BreadcrumbComponent } from '../../shared/layout/breadcrumb/breadcrumb.component';
import { RouterOutlet } from "@angular/router";
@Component({
  selector: 'app-home',
  imports: [
    MenuComponent,
    HeaderComponent,
    BreadcrumbComponent,
    RouterOutlet,
],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent {
}
