import { Component, inject, signal, OnInit } from '@angular/core';
import { ReportService } from '../../shared/services/report.service';
import { CardViewComponent } from "../../shared/components/card-view/card-view.component";
import { DashboardMovementComponent } from "./dashboard-movement/dashboard-movement.component";
import { IItemCritico, IMovimentacaoRelatorio, IRelatorioDispensacao } from '../../shared/models/IReport';
import { IMovimentacao } from '../../shared/models/IMovement';
import { DashboardAlertComponent } from "./dashboard-alert/dashboard-alert.component";
import { DashboardMonthlyConsumptionComponent } from './dashboard-monthly-consumption/dashboard-monthly-consumption.component';
import { LoadingService } from '../../shared/services/loading.service';
import { Button } from "primeng/button";

@Component({
  selector: 'app-report',
  imports: [CardViewComponent, DashboardMovementComponent, DashboardAlertComponent, DashboardMonthlyConsumptionComponent, Button],
  templateUrl: './report.component.html',
  styleUrl: './report.component.scss',
})
export class ReportComponent implements OnInit {
  private reportService = inject(ReportService)

  public cards = signal<any[]>([])

  public movimentacoes = signal<IMovimentacaoRelatorio[]>([])
  public itensCriticos = signal<IItemCritico[]>([]);
  public consumoMensal = signal<IRelatorioDispensacao[]>([])
  private loading = inject(LoadingService)

  async ngOnInit() {
    this.loading.show();

    await Promise.all([
      this.loadDashboard(),
      this.getMovimentacoes(),
      this.getItensCriticos(),
      this.getConsumoMensal()
    ]).finally(() => {
      this.loading.hide();
    });
  }

  async loadDashboard() {
    const dashboard = await this.reportService.getDashboard();

    this.cards.set([
      {
        title: 'Medicamentos cadastrados',
        value: dashboard.estoque.total_medicamentos.toString(),
        subtitle: `${dashboard.estoque.medicamentos_criticos} requerem atenção`,
        icon: 'pi pi-box',
        variant: 'primary'
      },
      {
        title: 'Alertas de vencimento',
        value: (
          dashboard.alertas['30_dias'] +
          dashboard.alertas['15_dias'] +
          dashboard.alertas['7_dias']
        ).toString(),
        subtitle: `${dashboard.alertas['30_dias']} vencem em até 30 dias`,
        icon: 'pi pi-calendar',
        variant: 'warning'
      },
      {
        title: 'Estoque crítico',
        value: dashboard.alertas.estoque_critico.toString(),
        subtitle: 'Abaixo do estoque mínimo',
        icon: 'pi pi-exclamation-triangle',
        variant: 'danger'
      },
      {
        title: 'Alertas abertos',
        value: dashboard.alertas.total.toString(),
        subtitle: 'Necessitam ação',
        icon: 'pi pi-bell',
        variant: 'teal'
      }
    ])
  }


  async getMovimentacoes() {
    const movimentacoes = await this.reportService.getMovimentacoes()
    try {
      console.log('movimentacoes', movimentacoes)
      this.movimentacoes.set(movimentacoes.data)
    }
    catch (err) {

    }

  }
  async getItensCriticos() {
    try {
      const itens = await this.reportService.getItensCriticos();

      this.itensCriticos.set(itens);

    } catch (error) {
      console.error(error);
    }
  }

  async getConsumoMensal() {
    try {

      const dataFim = new Date();

      const dataInicio = new Date();

      dataInicio.setDate(dataInicio.getDate() - 30);

      const consumo = await this.reportService.getConsumoMensal(
        dataInicio.toISOString().split('T')[0],
        dataFim.toISOString().split('T')[0]
      );

      this.consumoMensal.set(consumo);

    } catch (error) {
      console.error(error);
    }
  }
}
