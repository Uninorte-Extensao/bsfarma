import { Component, OnInit, PLATFORM_ID, ChangeDetectorRef, inject, effect, input, SimpleChanges, OnChanges } from '@angular/core';
import { ChartModule } from 'primeng/chart';
import { isPlatformBrowser } from '@angular/common';
import { IMovimentacaoRelatorio } from '../../../shared/models/IReport';
import { Button } from "primeng/button";
@Component({
  selector: 'app-dashboard-movement',
  imports: [ChartModule, Button],
  templateUrl: './dashboard-movement.component.html',
  styleUrl: './dashboard-movement.component.scss',
})
export class DashboardMovementComponent implements OnInit, OnChanges {
  data: any;

  options: any;

  platformId = inject(PLATFORM_ID);

  movimentacoes = input<IMovimentacaoRelatorio[]>([]);


  constructor(private cd: ChangeDetectorRef) { }

  ngOnChanges(changes: SimpleChanges) {

    if (changes['movimentacoes']) {
      this.initChart();
    }

  }

  ngOnInit() {
    this.initChart();
  }

  initChart() {
    if (isPlatformBrowser(this.platformId)) {
      const documentStyle = getComputedStyle(document.documentElement);
      const textColor = documentStyle.getPropertyValue('--p-text-color');


      const diasSemana = [
        'Dom',
        'Seg',
        'Ter',
        'Qua',
        'Qui',
        'Sex',
        'Sáb'
      ];

      const agrupado = new Map<
        string,
        {
          entrada: number;
          saida: number;
          perda: number;
          ajuste: number;
        }
      >();

      // cria os últimos 7 dias já zerados
      for (let i = 6; i >= 0; i--) {
        const data = new Date();

        data.setHours(0, 0, 0, 0);
        data.setDate(data.getDate() - i);

        const chave = data.toISOString().split('T')[0];

        agrupado.set(chave, {
          entrada: 0,
          saida: 0,
          perda: 0,
          ajuste: 0
        });
      }

      this.movimentacoes().forEach(mov => {

        const dataMov = new Date(mov.ocorrido_em);

        dataMov.setHours(0, 0, 0, 0);

        const chave = dataMov.toISOString().split('T')[0];

        const item = agrupado.get(chave);

        if (!item) {
          return;
        }

        switch (mov.tipo) {

          case 'entrada':
            item.entrada += mov.quantidade;
            break;

          case 'saida':
            item.saida += mov.quantidade;
            break;

          case 'perda':
            item.perda += mov.quantidade;
            break;

          case 'ajuste':
            item.ajuste += mov.quantidade;
            break;
        }

      });


      const labels: string[] = [];

      const entradas: number[] = [];
      const saidas: number[] = [];
      const perdas: number[] = [];
      const ajustes: number[] = [];

      agrupado.forEach((valor, chave) => {

        const data = new Date(`${chave}T00:00:00`);

        labels.push(
          `${diasSemana[data.getDay()]} ${data.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit'
          })}`
        );

        entradas.push(valor.entrada);
        saidas.push(valor.saida);
        perdas.push(valor.perda);
        ajustes.push(valor.ajuste);

      });

      this.data = {
        labels,
        datasets: [
          {
            label: 'Entrada',
            backgroundColor: '#22c55e',
            data: entradas,
            borderRadius: 8
          },
          {
            label: 'Saída',
            backgroundColor: '#3b82f6',
            data: saidas,
            borderRadius: 8
          },
          {
            label: 'Perda',
            backgroundColor: '#ef4444',
            data: perdas,
            borderRadius: 8
          },
          {
            label: 'Ajuste',
            backgroundColor: '#f59e0b',
            data: ajustes,
            borderRadius: 8
          }
        ]
      };

      this.options = {
        maintainAspectRatio: false,
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: textColor
            }
          }
        },
        scales: {
          x: {
            stacked: false
          },
          y: {
            beginAtZero: true
          }
        }
      };
      this.cd.markForCheck()
    }
  }
}
