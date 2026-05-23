import { isPlatformBrowser } from '@angular/common';
import {
  ChangeDetectorRef,
  Component,
  inject,
  input,
  OnChanges,
  OnInit,
  PLATFORM_ID,
  SimpleChanges
} from '@angular/core';
import { UIChart } from 'primeng/chart';
import { IRelatorioDispensacao } from '../../../shared/models/IReport';

@Component({
  selector: 'app-dashboard-monthly-consumption',
  imports: [UIChart],
  templateUrl: './dashboard-monthly-consumption.component.html',
  styleUrl: './dashboard-monthly-consumption.component.scss',
})
export class DashboardMonthlyConsumptionComponent implements OnInit, OnChanges {

  data: any;

  options: any;

  consumoMensal = input<IRelatorioDispensacao[]>([]);

  platformId = inject(PLATFORM_ID);

  constructor(private cd: ChangeDetectorRef) { }

  ngOnInit() {
    this.initChart();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['consumoMensal']) {
      this.initChart();
    }
  }

  initChart() {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    const documentStyle = getComputedStyle(document.documentElement);

    const textColor = documentStyle.getPropertyValue('--p-text-color');
    const textColorSecondary = documentStyle.getPropertyValue('--p-text-muted-color');
    const surfaceBorder = documentStyle.getPropertyValue('--p-content-border-color');

    const topMedicamentos = [...this.consumoMensal()]
      .sort((a, b) => b.total_dispensado - a.total_dispensado)
      .slice(0, 5);

    const labels = topMedicamentos.map(
      item => `${item.nome_generico} ${item.concentracao}`
    );

    const consumo = topMedicamentos.map(
      item => item.total_dispensado
    );

    this.data = {
      labels,
      datasets: [
        {
          label: 'Quantidade dispensada',
          data: consumo,

          backgroundColor: [
            '#2563eb',
            '#3b82f6',
            '#60a5fa',
            '#93c5fd',
            '#bfdbfe'
          ],

          borderRadius: 12,
          borderSkipped: false,
          barThickness: 24,
          maxBarThickness: 30
        }
      ]
    };

    this.options = {
      indexAxis: 'y',

      maintainAspectRatio: false,

      responsive: true,

      plugins: {
        legend: {
          display: false
        },

        tooltip: {
          backgroundColor: '#111827',

          padding: 12,

          displayColors: false,

          callbacks: {
            label: (context: any) =>
              `${context.raw} unidades dispensadas`
          }
        }
      },

      layout: {
        padding: 0
      },

      scales: {
        x: {
          beginAtZero: true,

          ticks: {
            color: textColorSecondary
          },

          grid: {
            color: `${surfaceBorder}40`,
            drawBorder: false
          },

          border: {
            display: false
          }
        },

        y: {
          ticks: {
            color: textColor,

            font: {
              size: 13,
              weight: 500
            }
          },

          grid: {
            display: false
          },

          border: {
            display: false
          }
        }
      }
    };

    this.cd.markForCheck();
  }
}