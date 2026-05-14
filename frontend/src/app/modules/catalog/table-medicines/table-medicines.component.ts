import { Component, inject, input, InputSignal, output } from '@angular/core';
import { TableModule } from 'primeng/table';
import { IMedicine } from '../../../shared/models/IMedicine';
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { InputText } from 'primeng/inputtext';
import { Router } from '@angular/router';
import { Button } from "primeng/button";
import { IS_MOBILE } from '../../../shared/services/is-mobile.service';

@Component({
  selector: 'app-table-medicines',
  imports: [
    TableModule,
    IconField,
    InputIcon,
    InputText,
    Button
  ],
  templateUrl: './table-medicines.component.html',
  styleUrl: './table-medicines.component.scss',
})
export class TableMedicinesComponent {
  listMedicine: InputSignal<IMedicine[]> = input.required();
  private router = inject(Router)
  public onItemDelete = output<IMedicine>()
  public isMobile = inject(IS_MOBILE)

  protected goToEdit(medicine: IMedicine) {
    this.router.navigate(['/catalog/edit', medicine.id])
  }

  public deleteItem(medicamento: IMedicine) {
    this.onItemDelete.emit(medicamento)
  }
}
