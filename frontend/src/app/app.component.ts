import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MenuComponent } from '../app/shared/layout/menu/menu.component';
import { HeaderComponent } from  '../app/shared/layout/header/header.component';
import { BreadcrumbComponent } from "../app/shared/layout/breadcrumb/breadcrumb.component";

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    MenuComponent,
    HeaderComponent,
    BreadcrumbComponent
],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'bsfarma';
}
