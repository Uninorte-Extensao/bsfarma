import { Component, signal, WritableSignal } from '@angular/core';
import { Password } from "primeng/password";
import { Button } from "primeng/button";
import { InputText } from 'primeng/inputtext';
import { Select } from "primeng/select";

@Component({
  selector: 'app-register',
  imports: [Password, Button, InputText, Select],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss',
})
export class RegisterComponent {
  readonly listProfile = signal<any[]>([
    { label: 'Farmacêutico', id: 1 },
    { label: 'Atendente', id: 2 },
    { label: 'Gestor', id: 3 }
  ])
}
