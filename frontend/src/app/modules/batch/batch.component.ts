import { Component, inject, signal, OnInit } from '@angular/core';
import { TableModule } from 'primeng/table';
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { InputText } from 'primeng/inputtext';
import { DatePipe } from '@angular/common';
import { Button } from 'primeng/button';
import { IBatch } from '../../shared/models/IBatch';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { LoteService } from '../../shared/services/batch.service';
import { LoadingService } from '../../shared/services/loading.service';
import { ToastService } from '../../shared/services/toast.service';
@Component({
  selector: 'app-batch',
  imports: [
    TableModule,
    IconField,
    InputIcon,
    InputText,
    DatePipe,
    Button,
    FormsModule,
  ],
  templateUrl: './batch.component.html',
  styleUrl: './batch.component.scss',
})
export class BatchComponent implements OnInit {
  listLote = signal<IBatch[]>([]);

  private router = inject(Router)
  private service = inject(LoteService)
  private loading = inject(LoadingService)
  private toast = inject(ToastService)

  ngOnInit() {
    this.getAllLotes()
  }


  goToCreate() {
    this.router.navigate(['batch/create'])
  }

  goToEdit(lote: IBatch) {
    this.router.navigate(['batch/edit', lote.id])
  }

  getAllLotes() {
    this.loading.show()
    this.service.getLotes()
      .then((res: IBatch[]) => {
        this.listLote.set(res)
      })
      .catch(() => {
        this.toast.showToastError('Erro ao buscar medicamentos.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

}
