import { Component, computed, inject, signal, OnInit } from '@angular/core';
import { TableModule } from "primeng/table";
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { Button } from "primeng/button";
import { IPaciente } from '../../shared/models/IPatient';
import { PACIENTE } from '../../shared/mocks/pacientes.mock';
import { DatePipe } from '@angular/common';
import { InputText } from 'primeng/inputtext';
import { IS_MOBILE } from '../../shared/services/is-mobile.service';
import { Router } from '@angular/router';
import { LoadingService } from '../../shared/services/loading.service';
import { DispersationService } from '../../shared/services/dispersation.service';
import { ToastService } from '../../shared/services/toast.service';
import { IDispensacao } from '../../shared/models/IDispersation';
import { MovementService } from '../../shared/services/movement.service';
import { IMovimentacao } from '../../shared/models/IMovement';
import { LoteService } from '../../shared/services/batch.service';
import { IBatch } from '../../shared/models/IBatch';
@Component({
  selector: 'app-dispersation',
  imports: [
    TableModule,
    IconField,
    InputIcon,
    Button,
    DatePipe,
    InputText
  ],
  templateUrl: './dispersation.component.html',
  styleUrl: './dispersation.component.scss',
})
export class DispersationComponent implements OnInit {
  protected isMobile = inject(IS_MOBILE)
  private router = inject(Router)

  private loading = inject(LoadingService)
  private service = inject(DispersationService)
  private toast = inject(ToastService)
  private movimentacaoService = inject(MovementService)
  private loteService = inject(LoteService)

  protected lotes = signal<IBatch[]>([])
  protected dispensacoes = signal<IDispensacao[]>([])
  protected dispensacoesComputed = computed(() => {
    return this.dispensacoes().map((dispensacao) => {

      const movimentacao = this.movimentacoes().find(
        item => item.id === dispensacao.movimentacao_id
      );

      const lote = this.lotes().find(
        item => item.id === movimentacao?.lote_id
      );

      return {
        ...dispensacao,

        numero_lote: lote?.numero_lote,

        quantidade: movimentacao?.quantidade,

      };
    });
  });
  protected movimentacoes = signal<IMovimentacao[]>([])

  goToAdd() {
    this.router.navigate(['/dispersation/create'])
  }

  ngOnInit() {
    this.getDispensacoes()
    this.getMovimentacoes()
    this.getLotes()
  }

  private getDispensacoes(pacienteId?: string) {
    this.loading.show()
    this.service.getAllDispersacoes(pacienteId)
      .then((res: IDispensacao[]) => {
        this.dispensacoes.set(res)
      })
      .catch(() => {
        this.toast.showToastError('Erro ao buscar dispensações')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  private getMovimentacoes() {
    this.loading.show()
    this.movimentacaoService.getMovimentacao()
      .then((res: IMovimentacao[]) => {
        this.movimentacoes.set(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  private getLotes() {
    this.loading.show()
    this.loteService.getLotes()
      .then((res: IBatch[]) => {
        this.lotes.set(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }

}
