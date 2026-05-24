import { Component, inject, signal, OnInit } from '@angular/core';
import { ReportService } from '../../shared/services/report.service';
import { CardViewComponent } from "../../shared/components/card-view/card-view.component";
import { DashboardMovementComponent } from "./dashboard-movement/dashboard-movement.component";
import { IItemCritico, IMovimentacaoRelatorio, IRelatorioDispensacao } from '../../shared/models/IReport';
import { DashboardAlertComponent } from "./dashboard-alert/dashboard-alert.component";
import { DashboardMonthlyConsumptionComponent } from './dashboard-monthly-consumption/dashboard-monthly-consumption.component';
import { LoadingService } from '../../shared/services/loading.service';
import { Button } from "primeng/button";
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Dialog } from "primeng/dialog";
import { DatePicker } from 'primeng/datepicker';
import { ITypeMovimentacao } from '../../shared/models/IMovement';
import { Select } from 'primeng/select';

@Component({
  selector: 'app-report',
  imports: [CardViewComponent, ReactiveFormsModule, DashboardMovementComponent, DashboardAlertComponent, DashboardMonthlyConsumptionComponent, Button, Dialog, DatePicker, Select],
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

  protected exportDialogVisible = false;
  protected exportForm: FormGroup;
  protected typeDialog = ''


  public listTipoMovimentacao = signal([
    {
      label: 'Entrada',
      value: ITypeMovimentacao.ENTRADA
    },
    {
      label: 'Saída',
      value: ITypeMovimentacao.SAIDA
    },
    {
      label: 'Perda',
      value: ITypeMovimentacao.PERDA
    },
    {
      label: 'Ajuste',
      value: ITypeMovimentacao.AJUSTE
    }
  ]);

  constructor() {
    const fb = new FormBuilder()
    this.exportForm = fb.group({
      periodo: [[] as Date[]],
      tipo: ['']
    });
  }

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
        subtitle: 'Abaixo do estoque mín.',
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

  private getPeriodoSelecionado() {

    const periodo = this.exportForm.value.periodo;

    if (!periodo || periodo.length < 2) {
      throw new Error('Selecione um período');
    }

    const dataInicio = periodo[0]
      .toISOString()
      .split('T')[0];

    const dataFim = periodo[1]
      .toISOString()
      .split('T')[0];

    return {
      dataInicio,
      dataFim
    };
  }

  async exportarConsumoCsv() {

    try {

      const {
        dataInicio,
        dataFim
      } = this.getPeriodoSelecionado();

      const blob =
        await this.reportService.exportarConsumoCsv(
          dataInicio,
          dataFim
        );

      this.downloadFile(
        blob,
        `consumo_${dataInicio}_${dataFim}.csv`
      );
      
      this.exportForm.reset()

    } catch (error) {
      console.error(error);
    } 
  }

  async exportarConsumoXlsx() {

    try {

      const {
        dataInicio,
        dataFim
      } = this.getPeriodoSelecionado();

      const blob =
        await this.reportService.exportarConsumoXlsx(
          dataInicio,
          dataFim
        );

      this.downloadFile(
        blob,
        `consumo_${dataInicio}_${dataFim}.xlsx`
      );

      this.exportForm.reset()

    } catch (error) {
      console.error(error);
    }
  }

  async exportarMovimentacoesCsv() {

    try {

      const {
        dataInicio,
        dataFim
      } = this.getPeriodoSelecionado();

      const tipo = this.exportForm.value.tipo

      const blob =
        await this.reportService.exportarMovimentacoesCsv(
          dataInicio,
          dataFim,
          tipo
        );

      this.downloadFile(
        blob,
        `movimentacoes_${dataInicio}_${dataFim}.csv`
      );

    this.exportForm.reset()

    } catch (error) {
      console.error(error);
    }
  }

  async exportarEstoqueXlsx() {
    try {
      const blob = await this.reportService.exportarEstoqueXlsx();

      this.downloadFile(
        blob,
        `estoque_atual.xlsx`
      );

    } catch (error) {
      console.error(error);
    }
  }


  private downloadFile(
    blob: Blob,
    fileName: string
  ) {
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;

    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  showModal(type: string) {
    this.exportDialogVisible = true
    this.typeDialog = type
  }

  closeModal() {
    this.exportDialogVisible = false
    this.exportForm.reset()
  }
}
