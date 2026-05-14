import { Component, OnInit, WritableSignal, inject, signal } from '@angular/core';
import { TabsModule } from 'primeng/tabs';
import { TableMedicinesComponent } from './table-medicines/table-medicines.component';
import { IMedicine } from '../../shared/models/IMedicine';
import { Button } from 'primeng/button';
import { MedicineService } from '../../shared/services/medicine.service';
import { ToastService } from '../../shared/services/toast.service';
import { LoadingService } from '../../shared/services/loading.service';
import { Router } from '@angular/router';
@Component({
  selector: 'app-catalog',
  imports: [
    TabsModule,
    TableMedicinesComponent,
    Button
  ],
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.scss',
})
export class CatalogComponent implements OnInit{
  listMedicine: WritableSignal<IMedicine[]> = signal([]);
  listActive: WritableSignal<IMedicine[]> = signal([]);
  listInactive: WritableSignal<IMedicine[]> = signal([]);

  private service = inject(MedicineService)
  private toast = inject(ToastService)
  private loading = inject(LoadingService)
  private router = inject(Router)

  ngOnInit() {
    this.getAllMedicamentos()
  }

  getAllMedicamentos() {
    this.loading.show()
    this.service.getMedicamentos()
      .then((res: IMedicine[]) => {
        this.listMedicine.set(res)
        this.listActive.set(res.filter(item => item.ativo === true))
        this.listInactive.set(res.filter(item => item.ativo === false))
      })
      .catch(() => {
        this.toast.showToastError('Erro ao buscar medicamentos.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  protected goToCreate() {
    this.router.navigate(['/catalog/create'])
  }

}
