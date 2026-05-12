import { Component, input, InputSignal } from '@angular/core';
import { TableModule } from 'primeng/table';
import { IMedicine } from '../../../shared/models/IMedicine';
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { InputText } from 'primeng/inputtext';

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
}
