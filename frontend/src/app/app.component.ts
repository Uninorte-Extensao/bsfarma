import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MenuComponent } from '../app/shared/layout/menu/menu.component';
import { HeaderComponent } from  '../app/shared/layout/header/header.component';
import { BreadcrumbComponent } from "../app/shared/layout/breadcrumb/breadcrumb.component";
import { LoadingComponent } from "./shared/components/loading/loading.component";
import {Toast} from "primeng/toast"
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
}
