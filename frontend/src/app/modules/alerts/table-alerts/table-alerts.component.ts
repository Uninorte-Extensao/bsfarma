import { DatePipe } from '@angular/common';
import { Component, computed, inject, input, output } from '@angular/core';
import { Button } from 'primeng/button';
import { IAlertaValidade } from '../../../shared/models/IAlert';
import { AlertService } from '../../../shared/services/alert.service';
import { ToastService } from '../../../shared/services/toast.service';
import { LoadingService } from '../../../shared/services/loading.service';
import { Menu } from "primeng/menu";
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-table-alerts',
  imports: [Button, DatePipe, Menu],
  templateUrl: './table-alerts.component.html',
  styleUrl: './table-alerts.component.scss',
})
export class TableAlertsComponent {

  private alertService = inject(AlertService);
  private toast = inject(ToastService);
  private loading = inject(LoadingService);

  item = input.required<IAlertaValidade>();
  reload = output<void>();

  diasVencimento = computed(() => {
    const validade = new Date(this.item().lote.validade);

    return Math.ceil(
      (validade.getTime() - Date.now()) /
      (1000 * 60 * 60 * 24)
    );
  });

  isEstoqueCritico = computed(() =>
    this.item().tipo_alerta === 'Estoque Crítico'
  );

  resolver() {
    this.loading.show();

    this.alertService
      .updateStatusAlerta(this.item().id, {
        status_alerta: 'Resolvido'
      })
      .then(() => {

        this.toast.showToastSuccess(
          'Alerta resolvido com sucesso'
        );

        this.alertService.atualizarQuantidadeAlertas()

        this.reload.emit();

      })
      .catch(() => {

        this.toast.showToastError(
          'Erro ao atualizar alerta'
        );

      })
      .finally(() => {
        this.loading.hide();
      });
  }

  getTag(tag: string): string {

    switch (tag) {

      // tipos

      case '30 dias para vencimento':
        return 'tag-blue';

      case '15 dias para vencimento':
        return 'tag-orange';

      case '7 dias para vencimento':
        return 'tag-red';

      case 'Estoque Crítico':
        return 'tag-yellow';

      // status

      case 'Pendente':
        return 'tag-gray';

      case 'Em andamento':
        return 'tag-blue';

      case 'Resolvido':
        return 'tag-green';

      case 'Expirado':
        return 'tag-red';

      default:
        return '';
    }
  }

  getBorderClass(): string {

    switch (this.item().tipo_alerta) {

      case '30 dias para vencimento':
        return 'border-blue';

      case '15 dias para vencimento':
        return 'border-orange';

      case '7 dias para vencimento':
        return 'border-red';

      case 'Estoque Crítico':
        return 'border-yellow';

      default:
        return 'border-gray';
    }
  }

  getIconClass(): string {

    switch (this.item().tipo_alerta) {

      case '30 dias para vencimento':
        return 'box-blue';

      case '15 dias para vencimento':
        return 'box-orange';

      case '7 dias para vencimento':
        return 'box-red';

      case 'Estoque Crítico':
        return 'box-yellow';

      default:
        return 'box-gray';
    }
  }

  getStatusMenuItems(): MenuItem[] {

    const status = this.item().status_alerta;

    const items: MenuItem[] = [];

    if (status === 'Pendente') {

      items.push({
        label: 'Em andamento',
        icon: 'pi pi-clock',
        command: () => this.alterarStatus('Em andamento')
      });

      items.push({
        label: 'Resolver',
        icon: 'pi pi-check',
        command: () => this.alterarStatus('Resolvido')
      });

    }

    if (status === 'Em andamento') {

      items.push({
        label: 'Resolver',
        icon: 'pi pi-check',
        command: () => this.alterarStatus('Resolvido')
      });

    }

    return items;
  }

  alterarStatus(status: "Em andamento" | "Pendente" | "Resolvido" | "Expirado") {

    this.loading.show();

    this.alertService
      .updateStatusAlerta(
        this.item().id,
        {
          status_alerta: status
        }
      )
      .then(() => {

        this.toast.showToastSuccess(
          `Status alterado para ${status}`
        );

        this.alertService.atualizarQuantidadeAlertas();

        this.reload.emit();

      })
      .catch(() => {

        this.toast.showToastError(
          'Erro ao atualizar status'
        );

      })
      .finally(() => {

        this.loading.hide();

      });

  }
}