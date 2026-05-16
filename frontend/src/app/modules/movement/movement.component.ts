import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CardViewComponent } from "../../shared/components/card-view/card-view.component";
import { TableModule } from "primeng/table";
import { IconField } from "primeng/iconfield";
import { InputIcon } from "primeng/inputicon";
import { Select } from "primeng/select";
import { Button } from "primeng/button";
import { FormsModule } from '@angular/forms';
import { DatePipe, NgClass } from '@angular/common';
import { InputText } from 'primeng/inputtext';
import { IBatch } from '../../shared/models/IBatch';
import { IMovimentacao } from '../../shared/models/IMovement';
import { MovementService } from '../../shared/services/movement.service';
import { LoteService } from '../../shared/services/batch.service';
import { LoadingService } from '../../shared/services/loading.service';
import { Router } from '@angular/router';
import { IS_MOBILE } from '../../shared/services/is-mobile.service';
import { ToastService } from '../../shared/services/toast.service';
import { UserService } from '../../shared/services/user.service';
import { IUser } from '../../shared/models/IUser';

@Component({
  selector: 'app-movement',
  imports: [CardViewComponent, TableModule, IconField, InputIcon, Select, Button, FormsModule, DatePipe, InputText, NgClass],
  templateUrl: './movement.component.html',
  styleUrl: './movement.component.scss',
})
export class MovementComponent implements OnInit {
  protected cardItems = computed<any[]>(() => {
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
        value: `${totalEntradas} un.`,
        subtitle: `${entradas.length} movimentações`,
        icon: 'pi pi-arrow-down-left',
        variant: 'success'
      },

      {
        title: 'TOTAL SAÍDAS',
        value: `${totalSaidas} un.`,
        subtitle: `${saidas.length} movimentações`,
        icon: 'pi pi-arrow-up-right',
        variant: 'danger'
      },

      {
        title: 'PERDAS',
        value: `${totalPerdas} un.`,
        subtitle: `${perdas.length} registros`,
        icon: 'pi pi-exclamation-triangle',
        variant: 'warning'
      },

      {
        title: 'AJUSTES',
        value: `${totalAjustes} un.`,
        subtitle: `${ajustes.length} ajustes realizados`,
        icon: 'pi pi-sync',
        variant: 'primary'
      }
    ];
  });
  protected movimentacoes = signal<IMovimentacao[]>([])
  protected lotes = signal<IBatch[]>([])
  protected loteId: string | null = null
  protected users = signal<IUser[]>([])

  private service = inject(MovementService)
  private LoteService = inject(LoteService)
  private loading = inject(LoadingService)
  private router = inject(Router)
  private toast = inject(ToastService)
  private userService = inject(UserService)

  protected isMobile = inject(IS_MOBILE)

  protected movimentacoesComUsuario = computed(() => {
    return this.movimentacoes().map(mov => ({
      ...mov,
      usuario: this.users().find(user => user.id === mov.usuario_id)
    }));
  });

  ngOnInit() {
    this.getMovimentacoes()
    this.getLotes()
    this.getUsers()
  }

  goToCreate() {
    this.router.navigate(['/movement/create'])
  }

  goToEdit(item: string) {
    this.router.navigate(['/movement/edit', item])
  }

  onChangeLote(loteId: string | null) {
    this.loteId = loteId

    this.getMovimentacoes(this.loteId ?? undefined)
  }

  private getMovimentacoes(loteId?: string) {
    this.loading.show()
    this.service.getMovimentacao(loteId)
      .then((res: IMovimentacao[]) => {
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

  private getUsers() {
    this.loading.show()
    this.userService.getAllUsers()
      .then((res: IUser[]) => {
        this.users.set(res)
      })
      .finally(() => {
        this.loading.hide()
      })
  }
}
