import { Component, WritableSignal, signal } from '@angular/core';
import { TabsModule } from 'primeng/tabs';
import { TableMedicinesComponent } from './table-medicines/table-medicines.component';

@Component({
  selector: 'app-catalog',
  imports: [
    TabsModule, 
    TableMedicinesComponent
  ],
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.scss',
})
export class CatalogComponent {
  // listMedicines: WritableSignal<Medicamento[]> = signal(MEDICAMENTOS)
}
