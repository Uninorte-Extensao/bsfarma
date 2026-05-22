import { Component, computed, inject, signal } from '@angular/core';
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
export class DispersationComponent {
  protected listPacientes = signal<IPaciente[]>(PACIENTE)
  protected isMobile = inject(IS_MOBILE)
  private router = inject(Router)

  private loading = inject(LoadingService)
  private service = inject(DispersationService)
  private toast = inject(ToastService)
  private movimentacaoService = inject(MovementService)

  protected dispensacoes = signal<IDispensacao[]>([])
  protected dispensacoesComputed = computed<IDispensacao[]>(() => {
    return this.dispensacoes().map((dispensacao) => {
      const movimentacoes = this.movimentacoes().find(
        (item) => item.id === dispensacao.movimentacao_id
      );

      return {
        ...dispensacao,
        
      }
    })
  })
  protected movimentacoes = signal<IMovimentacao[]>([])

  deleteItem(_t48: any) {
    throw new Error('Method not implemented.');
  }

  goToEdit(_t48: any) {
    throw new Error('Method not implemented.');
  }

  goToAdd() {
    this.router.navigate(['/dispersation/create'])
  }
  
  ngOnInit() {
    this.getDispensacoes()
    this.getMovimentacoes()
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

}
