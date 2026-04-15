import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MenuComponent } from '../shared/layout/menu/menu.component';
import { HeaderComponent } from  '../shared/layout/header/header.component';

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    MenuComponent,
    HeaderComponent
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'bsfarma';
}
