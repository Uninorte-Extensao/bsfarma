import { Component, computed, inject, signal, OnInit } from '@angular/core';
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { Button } from "primeng/button";
import { DatePipe } from '@angular/common';
import { InputText } from 'primeng/inputtext';
import { Paginator, PaginatorState } from 'primeng/paginator';
import { IS_MOBILE } from '../../shared/services/is-mobile.service';
import { Router } from '@angular/router';
import { LoadingService } from '../../shared/services/loading.service';
import { DispersationService } from '../../shared/services/dispersation.service';
import { ToastService } from '../../shared/services/toast.service';
import { IDispensacaoDetalhada } from '../../shared/models/IDispersation';
import { Tooltip } from "primeng/tooltip";
import { Dialog } from 'primeng/dialog';
import { AuthService } from '../../shared/services/auth.service';
@Component({
  selector: 'app-dispersation',
  imports: [
    IconField,
    InputIcon,
    Button,
    DatePipe,
    InputText,
    Paginator,
    Tooltip,
    Dialog
],
  templateUrl: './dispersation.component.html',
  styleUrl: './dispersation.component.scss',
})
export class DispersationComponent implements OnInit {
  protected isMobile = inject(IS_MOBILE)
  protected authService = inject(AuthService)
  protected isCreate = signal(this.authService.hasPermission('dispersation.create'));
  private router = inject(Router)

  private loading = inject(LoadingService)
  private service = inject(DispersationService)
  private toast = inject(ToastService)

  protected dispensacoes = signal<IDispensacaoDetalhada[]>([])
  protected dispensacaoSelecionada = signal<IDispensacaoDetalhada | null>(null)

  protected searchTerm = signal('');
  protected first = signal(0);
  protected rows = signal(12);

  protected filteredList = computed(() => {
    const term = this.searchTerm().trim().toLowerCase();
    const list = this.dispensacoes();

    if (!term) return list;

    return list.filter(item =>
      item.paciente.codigo.toLowerCase().includes(term) ||
      item.lote.numero_lote.toLowerCase().includes(term) ||
      item.medicamento.nome_generico.toLowerCase().includes(term)
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

  protected abrirResumo(dispensacao: IDispensacaoDetalhada) {
    this.dispensacaoSelecionada.set(dispensacao)
  }

  protected fecharResumo() {
    this.dispensacaoSelecionada.set(null)
  }

  goToAdd() {
    this.router.navigate(['/dispersation/create'])
  }

  ngOnInit() {
    this.getDispensacoes()
  }

  private getDispensacoes(pacienteId?: string) {
    this.loading.show()
    this.service.getAllDispersacoes(pacienteId)
      .then((res: IDispensacaoDetalhada[]) => {
        this.dispensacoes.set(res)
      })
      .catch(() => {
        this.toast.showToastError('Erro ao buscar dispensações')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

}
