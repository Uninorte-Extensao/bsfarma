import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { InputText } from 'primeng/inputtext';
import { DatePipe } from '@angular/common';
import { Button } from 'primeng/button';
import { Tag } from 'primeng/tag';
import { Paginator, PaginatorState } from 'primeng/paginator';
import { IBatch } from '../../shared/models/IBatch';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { LoteService } from '../../shared/services/batch.service';
import { LoadingService } from '../../shared/services/loading.service';
import { ToastService } from '../../shared/services/toast.service';
import { Select } from "primeng/select";
import { IMedicine } from '../../shared/models/IMedicine';
import { MedicineService } from '../../shared/services/medicine.service';
import { IS_MOBILE } from '../../shared/services/is-mobile.service';
import { CardViewComponent } from "../../shared/components/card-view/card-view.component";
@Component({
  selector: 'app-batch',
  imports: [
    IconField,
    InputIcon,
    InputText,
    DatePipe,
    Button,
    Tag,
    Paginator,
    FormsModule,
    Select,
    CardViewComponent
  ],
  templateUrl: './batch.component.html',
  styleUrl: './batch.component.scss',
})
export class BatchComponent implements OnInit {
  listLote = signal<IBatch[]>([]);

  protected searchTerm = signal('');
  protected first = signal(0);
  protected rows = signal(8);

  protected filteredList = computed(() => {
    const term = this.searchTerm().trim().toLowerCase();
    const list = this.listLote();

    if (!term) return list;

    return list.filter(item =>
      item.numero_lote.toLowerCase().includes(term) ||
      item.fabricante.toLowerCase().includes(term)
    );
  });

  protected pagedList = computed(() =>
    this.filteredList().slice(this.first(), this.first() + this.rows())
  );

  protected onSearch(value: string) {
    this.searchTerm.set(value);
    this.first.set(0);
  }

  protected onPageChange(event: PaginatorState) {
    this.first.set(event.first ?? 0);
    this.rows.set(event.rows ?? 8);
  }

  private router = inject(Router)
  private loteService = inject(LoteService)
  private loading = inject(LoadingService)
  private toast = inject(ToastService)
  private medicamentoService = inject(MedicineService)
  protected isMobile = inject(IS_MOBILE)

  protected medicamentos = signal<IMedicine[]>([])
  protected checked: boolean | null = null;
  protected medicamentoId: string | null = null
  protected isSaldo = [
    { label: 'Sim', value: true },
    { label: 'Não', value: false }
  ]

  protected cards = computed<any[]>(() => [

    {
      title: 'Total de lotes',
      value: String(this.listLote().length),
      subtitle: 'Lotes cadastrados',
      icon: 'pi pi-box',
      variant: 'primary'
    },

    {
      title: 'Com saldo',
      value: String(
        this.listLote()
          .filter(item => item.quantidade_atual > 0)
          .length
      ),
      subtitle: 'Disponíveis no estoque',
      icon: 'pi pi-check-circle',
      variant: 'success'
    },

    {
      title: 'Sem saldo',
      value: String(
        this.listLote()
          .filter(item => item.quantidade_atual <= 0)
          .length
      ),
      subtitle: 'Necessitam reposição',
      icon: 'pi pi-times-circle',
      variant: 'danger'
    },

    {
      title: 'Próx. vencimento',
      value: String(
        this.listLote()
          .filter(item => {

            const hoje = new Date();

            const limite = new Date();

            limite.setDate(hoje.getDate() + 30);

            return new Date(item.validade) <= limite;

          }).length
      ),

      subtitle: 'Vencem em até 30 dias',
      icon: 'pi pi-calendar',
      variant: 'warning'
    }

  ]);

  ngOnInit() {
    this.getAllLotes()
    this.getMedicamentos()
  }


  goToCreate() {
    this.router.navigate(['batch/create'])
  }

  goToEdit(lote: IBatch) {
    this.router.navigate(['batch/edit', lote.id])
  }

  getAllLotes(medicamentoId?: string, comSaldo?: boolean) {
    this.loading.show()
    this.loteService.getLotes(medicamentoId, comSaldo)
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

  protected getMedicamentos() {
    this.loading.show()
    this.medicamentoService.getMedicamentos()
      .then((res: IMedicine[]) => {
        this.medicamentos.set(res)
      })
      .catch(() => {
        this.toast.showToastError('Erro ao buscar medicamentos.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }


  onChangeMedicamento(medicamento: string | null) {
    this.medicamentoId = medicamento
    this.first.set(0)

    this.getAllLotes(
      this.medicamentoId || undefined,
      this.checked ?? undefined
    )
  }

  onChangeSaldo(saldo: boolean | null) {
    this.checked = saldo
    this.first.set(0)

    this.getAllLotes(
      this.medicamentoId || undefined,
      this.checked ?? undefined
    )
  }

}
