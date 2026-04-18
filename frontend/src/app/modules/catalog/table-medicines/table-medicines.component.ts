import { Component, input, InputSignal } from '@angular/core';
import { TableModule } from 'primeng/table';
import { IMedicine } from '../../../../shared/models/IMedicine';

@Component({
  selector: 'app-table-medicines',
  imports: [TableModule],
  templateUrl: './table-medicines.component.html',
  styleUrl: './table-medicines.component.scss',
})
export class TableMedicinesComponent {
    listMedicine: InputSignal<IMedicine[]> = input.required();
}
