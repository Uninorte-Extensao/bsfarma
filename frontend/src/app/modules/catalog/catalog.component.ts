import { Component, WritableSignal, computed, model, signal } from '@angular/core';
import { TabsModule } from 'primeng/tabs';
import { TableMedicinesComponent } from './table-medicines/table-medicines.component';
import { IMedicine } from '../../shared/models/IMedicine';
import { MEDICAMENTOS } from '../../shared/mocks/medicamentos.mock';
import { Button } from 'primeng/button';
import { RouterLink } from "@angular/router";
import { Dialog } from "primeng/dialog";
import { FormMedicineComponent } from "./form-medicine/form-medicine.component";

type ITypeDialog = 'create' | 'update'
@Component({
  selector: 'app-catalog',
  imports: [
    TabsModule,
    TableMedicinesComponent,
    Button,
    RouterLink,
    Dialog,
    FormMedicineComponent
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

  public isVisible = model(false)
  public typeDialog = model<ITypeDialog>('create')
  public viewMedicine = model<any | null>(null)

  protected showDialog(type: ITypeDialog, medicine?: IMedicine) {
    this.isVisible.set(true)
  }

  protected closeModal() {
    this.isVisible.set(false)
  }

  submit(medicine: any){}

  update(medicine: any) {}
}
