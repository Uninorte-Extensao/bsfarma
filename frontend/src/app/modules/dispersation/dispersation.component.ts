import { Component, computed, inject, signal } from '@angular/core';
import { TableModule } from "primeng/table";
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { Button } from "primeng/button";
import { IPaciente } from '../../shared/models/IPatient';
import { PACIENTE } from '../../shared/mocks/pacientes.mock';
import { DatePipe } from '@angular/common';
import { InputText } from 'primeng/inputtext';
import { IS_MOBILE } from '../../shared/services/is-mobile.service';
import { Router } from '@angular/router';
@Component({
  selector: 'app-dispersation',
  imports: [
    TableModule,
    IconField,
    InputIcon,
    Button,
    DatePipe,
    InputText
  ],
  templateUrl: './dispersation.component.html',
  styleUrl: './dispersation.component.scss',
})
export class DispersationComponent {
  protected listPacientes = signal<IPaciente[]>(PACIENTE)
  protected isMobile = inject(IS_MOBILE)
  private router = inject(Router)

  deleteItem(_t48: any) {
    throw new Error('Method not implemented.');
  }

  goToEdit(_t48: any) {
    throw new Error('Method not implemented.');
  }

  goToAdd() {
    this.router.navigate(['/dispersation/create'])
  }
  
}
