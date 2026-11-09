import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CardViewComponent } from "../../shared/components/card-view/card-view.component";
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { Select } from "primeng/select";
import { Button } from "primeng/button";
import { Tag } from 'primeng/tag';
import { Paginator, PaginatorState } from 'primeng/paginator';
import { FormsModule } from '@angular/forms';
import { DatePipe } from '@angular/common';
import { InputText } from 'primeng/inputtext';
import { IBatch } from '../../shared/models/IBatch';
import { IMovimentacaoDetalhada } from '../../shared/models/IMovement';
import { ICard } from '../../shared/models/ICard';
import { MovementService } from '../../shared/services/movement.service';
import { LoteService } from '../../shared/services/batch.service';
import { LoadingService } from '../../shared/services/loading.service';
import { Router } from '@angular/router';
import { IS_MOBILE } from '../../shared/services/is-mobile.service';
import { ToastService } from '../../shared/services/toast.service';
import { AuthService } from '../../shared/services/auth.service';

type TagSeverity = 'success' | 'secondary' | 'info' | 'warn' | 'danger' | 'contrast';

@Component({
  selector: 'app-movement',
  imports: [CardViewComponent, IconField, InputIcon, Select, Button, Tag, Paginator, FormsModule, DatePipe, InputText],
  templateUrl: './movement.component.html',
  styleUrl: './movement.component.scss',
})
export class MovementComponent implements OnInit {
  protected cardItems = computed<ICard[]>(() => {
    const movimentacoes = this.movimentacoes();

    const entradas = movimentacoes.filter(
      item => item.tipo === 'entrada'
    );

    const saidas = movimentacoes.filter(
      item => item.tipo === 'saida'
    );

    const perdas = movimentacoes.filter(
      item => item.tipo === 'perda'
    );

    const ajustes = movimentacoes.filter(
      item => item.tipo === 'ajuste'
    );

    const totalEntradas = entradas.reduce(
      (acc, item) => acc + item.quantidade,
      0
    );

    const totalSaidas = saidas.reduce(
      (acc, item) => acc + item.quantidade,
      0
    );

    const totalPerdas = perdas.reduce(
      (acc, item) => acc + item.quantidade,
      0
    );

    const totalAjustes = ajustes.reduce(
      (acc, item) => acc + item.quantidade,
      0
    );

    return [
      {
        title: 'TOTAL ENTRADAS',
        value: `${totalEntradas}`,
        subtitle: `${entradas.length} movimentações`,
        icon: 'pi pi-arrow-down-left',
        variant: 'success'
      },

      {
        title: 'TOTAL SAÍDAS',
        value: `${totalSaidas}`,
        subtitle: `${saidas.length} movimentações`,
        icon: 'pi pi-arrow-up-right',
        variant: 'danger'
      },

      {
        title: 'PERDAS',
        value: `${totalPerdas}`,
        subtitle: `${perdas.length} registros`,
        icon: 'pi pi-exclamation-triangle',
        variant: 'warning'
      },

      {
        title: 'AJUSTES',
        value: `${totalAjustes}`,
        subtitle: `${ajustes.length} ajustes realizados`,
        icon: 'pi pi-sync',
        variant: 'primary'
      }
    ];
  });
  protected movimentacoes = signal<IMovimentacaoDetalhada[]>([])
  protected lotes = signal<IBatch[]>([])
  protected loteId: string | null = null

  private service = inject(MovementService)
  private LoteService = inject(LoteService)
  private loading = inject(LoadingService)
  private router = inject(Router)
  private toast = inject(ToastService)

  protected isMobile = inject(IS_MOBILE)
  protected authService = inject(AuthService)
  protected isCreate = signal(this.authService.hasPermission('movement.create'));
  protected isEdit = signal(this.authService.hasPermission('movement.update'));

  protected searchTerm = signal('');
  protected first = signal(0);
  protected rows = signal(8);

  protected filteredList = computed(() => {
    const term = this.searchTerm().trim().toLowerCase();
    const list = this.movimentacoes();

    if (!term) return list;

    return list.filter(item =>
      item.lote.numero_lote.toLowerCase().includes(term) ||
      item.tipo.toLowerCase().includes(term) ||
      item.usuario.nome.toLowerCase().includes(term) ||
      (item.justificativa ?? '').toLowerCase().includes(term)
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

  protected getTipoSeverity(tipo: string): TagSeverity {
    switch (tipo) {
      case 'entrada':
        return 'success';
      case 'saida':
        return 'danger';
      case 'perda':
        return 'warn';
      case 'ajuste':
        return 'info';
      default:
        return 'secondary';
    }
  }

  ngOnInit() {
    this.getMovimentacoes()
    this.getLotes()
  }

  goToCreate() {
    this.router.navigate(['/movement/create'])
  }

  goToEdit(item: string) {
    this.router.navigate(['/movement/edit', item])
  }

  onChangeLote(loteId: string | null) {
    this.loteId = loteId
    this.first.set(0)

    this.getMovimentacoes(this.loteId ?? undefined)
  }

  private getMovimentacoes(loteId?: string) {
    this.loading.show()
    this.service.getMovimentacao(loteId)
      .then((res: IMovimentacaoDetalhada[]) => {
        this.movimentacoes.set(res)
      })
      .catch(() => {
        this.toast.showToastError('Erro ao buscar movimentacções.')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  private getLotes() {
    this.loading.show()
    this.LoteService.getLotes()
      .then((res: IBatch[]) => {
        this.lotes.set(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }
}
