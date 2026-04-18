import { Component, WritableSignal, computed, signal } from '@angular/core';
import { TabsModule } from 'primeng/tabs';
import { TableMedicinesComponent } from './table-medicines/table-medicines.component';
import { IMedicine } from '../../../shared/models/IMedicine';
import { MEDICAMENTOS } from '../../../shared/mocks/medicamentos.mock';
import { Button } from 'primeng/button';
import { RouterLink } from "@angular/router";

@Component({
  selector: 'app-catalog',
  imports: [
    TabsModule,
    TableMedicinesComponent,
    Button,
    RouterLink
  ],
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.scss',
})
export class CatalogComponent {
  listMedicine: WritableSignal<IMedicine[]> = signal(MEDICAMENTOS);
  listActive = computed(() => {
    return this.listMedicine().filter(m => m.ativo === true)
  })
  listInactive = computed(() => {
    return this.listMedicine().filter(m => m.ativo === false);
  })
}
