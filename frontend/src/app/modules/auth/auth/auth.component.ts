import { Component } from '@angular/core';
import { LoginComponent } from "../login/login.component";
import { Button } from "primeng/button";
import { SelectButton } from 'primeng/selectbutton';
import { FormsModule } from '@angular/forms';
import { RegisterComponent } from "../register/register.component";

@Component({
  selector: 'app-auth',
  imports: [LoginComponent, SelectButton, FormsModule, RegisterComponent],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.scss',
})
export class AuthComponent {
  readonly stateOptions: any[] = [
    { label: 'Entrar', value: 'login' }, 
    { label: 'Criar Conta', value: 'register' }];

  protected value: string = 'login';
}
