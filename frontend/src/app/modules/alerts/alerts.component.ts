import { DatePipe } from '@angular/common';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { MenuModule } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { Tag } from 'primeng/tag';
import { IAlertaValidade, IUpdateStatusAlerta } from '../../shared/models/IAlert';
import { AlertService } from '../../shared/services/alert.service';
import { ToastService } from '../../shared/services/toast.service';
import { LoadingService } from '../../shared/services/loading.service';

type TagSeverity = 'success' | 'secondary' | 'info' | 'warn' | 'danger' | 'contrast';

@Component({
  selector: 'app-alerts',
  imports: [DatePipe, MenuModule, Tag],
  templateUrl: './alerts.component.html',
  styleUrl: './alerts.component.scss',
})
export class AlertsComponent implements OnInit {
  private alertService = inject(AlertService);
  private toastService = inject(ToastService);
  private loadingService = inject(LoadingService);

  private listAlertas = signal<IAlertaValidade[]>([]);

  criticos = computed(() =>
    this.listAlertas().filter(item =>
      item.tipo_alerta === 'Estoque Crítico' &&
      this.severidadeEstoque(item) === 'critico'
    )
  );

  estoqueBaixo = computed(() =>
    this.listAlertas().filter(item =>
      item.tipo_alerta === 'Estoque Crítico' &&
      this.severidadeEstoque(item) === 'baixo'
    )
  );

  validade = computed(() =>
    this.listAlertas().filter(item => item.tipo_alerta !== 'Estoque Crítico')
  );

  ngOnInit() {
    this.load();
  }

  private load() {
    this.loadingService.show();

    this.alertService
      .getAlertas(undefined, undefined, undefined, true)
      .then(res => this.listAlertas.set(res))
      .catch(() => this.toastService.showToastError('Erro ao buscar alertas'))
      .finally(() => this.loadingService.hide());
  }

  protected severidadeEstoque(item: IAlertaValidade): 'critico' | 'baixo' {
    const { estoque_minimo } = item.medicamento;

    if (!estoque_minimo) return 'critico';

    const ratio = item.lote.quantidade_atual / estoque_minimo;
    return ratio <= 0.5 ? 'critico' : 'baixo';
  }

  protected diasParaVencer(validade: Date): number {
    return Math.ceil(
      (new Date(validade).getTime() - Date.now()) /
      (1000 * 60 * 60 * 24)
    );
  }

  protected isVencido(item: IAlertaValidade): boolean {
    return this.diasParaVencer(item.lote.validade) < 0;
  }

  protected getStatusSeverity(status: string): TagSeverity {
    switch (status) {
      case 'Pendente':
        return 'secondary';
      case 'Em andamento':
        return 'info';
      case 'Resolvido':
        return 'success';
      case 'Expirado':
        return 'danger';
      default:
        return 'secondary';
    }
  }

  protected getStatusMenuItems(item: IAlertaValidade): MenuItem[] {
    const status = item.status_alerta;
    const items: MenuItem[] = [];

    if (status === 'Pendente') {
      items.push({
        label: 'Em andamento',
        icon: 'pi pi-clock',
        command: () => this.alterarStatus(item, 'Em andamento')
      });

      items.push({
        label: 'Resolver',
        icon: 'pi pi-check',
        command: () => this.alterarStatus(item, 'Resolvido')
      });
    }

    if (status === 'Em andamento') {
      items.push({
        label: 'Resolver',
        icon: 'pi pi-check',
        command: () => this.alterarStatus(item, 'Resolvido')
      });
    }

    return items;
  }

  protected alterarStatus(item: IAlertaValidade, status: IUpdateStatusAlerta['status_alerta']) {
    this.loadingService.show();

    this.alertService
      .updateStatusAlerta(item.id, { status_alerta: status })
      .then(() => {
        this.toastService.showToastSuccess(`Status alterado para ${status}`);
        this.alertService.atualizarQuantidadeAlertas();
        this.load();
      })
      .catch(() => this.toastService.showToastError('Erro ao atualizar status'))
      .finally(() => this.loadingService.hide());
  }
}
