import { Component, OnInit, WritableSignal, inject, signal } from '@angular/core';
import { TableMedicinesComponent } from './table-medicines/table-medicines.component';
import { IMedicine } from '../../shared/models/IMedicine';
import { MedicineService } from '../../shared/services/medicine.service';
import { ToastService } from '../../shared/services/toast.service';
import { LoadingService } from '../../shared/services/loading.service';
@Component({
  selector: 'app-catalog',
  imports: [
    TableMedicinesComponent
  ],
  templateUrl: './catalog.component.html',
  styleUrl: './catalog.component.scss',
})
export class CatalogComponent implements OnInit {
  listMedicine: WritableSignal<IMedicine[]> = signal([]);

  private service = inject(MedicineService)
  private toast = inject(ToastService)
  private loading = inject(LoadingService)

  ngOnInit() {
    this.getAllMedicamentos()
  }

  getAllMedicamentos() {
    this.loading.show()
    this.service.getMedicamentos()
      .then((res: IMedicine[]) => {
        this.listMedicine.set(res)
      })
      .catch(() => {
        this.toast.showToastError('Erro ao buscar medicamentos.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  public delete(medicamento: IMedicine) {
    this.loading.show()

    this.service.deleteMedicamento(medicamento.id)
      .then(() => {
        this.listMedicine.update(list =>
          list.filter(item => item.id !== medicamento.id)
        )

        this.toast.showToastSuccess('Medicamento removido com sucesso.')
      })
      .catch(() => {
        this.toast.showToastError('Erro ao remover medicamento.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

}
