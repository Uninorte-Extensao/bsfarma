import { Component, inject, input, InputSignal, model, output } from '@angular/core';
import { TableModule } from 'primeng/table';
import { IMedicine } from '../../../shared/models/IMedicine';
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { InputText } from 'primeng/inputtext';
import { ITypeDialog } from '../../../shared/models/IGeneral';
import { Router } from '@angular/router';

@Component({
  selector: 'app-table-medicines',
  imports: [
    TableModule,
    IconField,
    InputIcon,
    InputText
  ],
  templateUrl: './table-medicines.component.html',
  styleUrl: './table-medicines.component.scss',
})
export class TableMedicinesComponent {
  listMedicine: InputSignal<IMedicine[]> = input.required();
  private router = inject(Router)

  protected goToEdit(medicine: IMedicine) {
  this.router.navigate(['/catalog/edit', medicine.id])
}
}
