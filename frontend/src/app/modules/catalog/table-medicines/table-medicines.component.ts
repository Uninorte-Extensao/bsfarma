import { Component } from '@angular/core';
import { TableModule } from 'primeng/table';

@Component({
  selector: 'app-table-medicines',
  imports: [TableModule],
  templateUrl: './table-medicines.component.html',
  styleUrl: './table-medicines.component.scss',
})
export class TableMedicinesComponent {
    products: any = [
      {

      }
    ];
}
