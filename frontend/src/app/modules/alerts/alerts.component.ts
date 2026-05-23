import { Component, inject, signal, OnInit } from '@angular/core';
import { TabsModule } from 'primeng/tabs';
import { TableAlertsComponent } from "./table-alerts/table-alerts.component";
import { CardViewComponent } from "../../shared/components/card-view/card-view.component";
import { IAlertaValidade } from '../../shared/models/IAlert';
import { AlertService } from '../../shared/services/alert.service';
import { ToastService } from '../../shared/services/toast.service';
import { LoadingService } from '../../shared/services/loading.service';

@Component({
  selector: 'app-alerts',
  imports: [TabsModule, TableAlertsComponent, CardViewComponent],
  templateUrl: './alerts.component.html',
  styleUrl: './alerts.component.scss',
})
export class AlertsComponent implements OnInit {
  cards = signal<any[]>([
    {
      title: 'VENCIMENTO PRÓXIMO',
      value: '3 alertas',
      subtitle: 'Lotes próximos do vencimento',
      icon: 'pi pi-calendar',
      variant: 'danger'
    },

    {
      title: 'ESTOQUE MÍNIMO',
      value: '3 itens',
      subtitle: 'Necessitam reposição',
      icon: 'pi pi-exclamation-triangle',
      variant: 'warning'
    },

    {
      title: 'RESOLVIDOS HOJE',
      value: '0 alertas',
      subtitle: 'Nenhuma pendência resolvida',
      icon: 'pi pi-check-circle',
      variant: 'success'
    }
  ]);

  listAlerts = signal<IAlertaValidade[]>([])
  listAlertsAbertos = signal<IAlertaValidade[]>([])
  listAlertsResolvidos = signal<IAlertaValidade[]>([])

  private alertService = inject(AlertService)
  private toastService = inject(ToastService)
  private loadingService = inject(LoadingService)

  selectedTab = signal<string | number | undefined>('0');

  constructor() {
  }

  ngOnInit() {
    this.loadAbertos()
    this.loadCards()
  }

  changeTab(tab: string | number | undefined) {
    this.selectedTab.set(tab);

    switch (tab) {

      case '0':
        this.loadAbertos();
        break;

      case '1':
        this.loadResolvidos();
        break;

      case '2':
        this.loadTodos();
        break;
    }
  }

  loadAbertos() {
    this.loadingService.show()

    this.alertService
      .getAlertas(
        undefined,
        undefined,
        undefined,
        true
      )
    this.alertService.getAlertas()
      .then((res: IAlertaValidade[]) => {
        this.listAlerts.set(res)
      })
      .catch(() => {
        this.toastService.showToastError('Erro ao buscar alertas')
      })
      .finally(() => {
        this.loadingService.hide()
      })
  }

  loadResolvidos() {
    this.loadingService.show();

    this.alertService
      .getAlertas(
        'Resolvido',
        undefined,
        undefined,
        false
      )
      .then(res => {
        this.listAlerts.set(res);
      })
      .finally(() => {
        this.loadingService.hide();
      });
  }

  loadTodos() {
    this.loadingService.show();

    this.alertService
      .getAlertas(
        undefined,
        undefined,
        undefined,
        false
      )
      .then(res => {
        this.listAlerts.set(res);
      })
      .finally(() => {
        this.loadingService.hide();
      });
  }

  private loadCards() {

    this.alertService
      .getAlertas(
        undefined,
        undefined,
        undefined,
        false
      )
      .then((res) => {

        const vencimento30 = res.filter(
          item => item.tipo_alerta === '30 dias para vencimento'
        ).length;

        const vencimento15 = res.filter(
          item => item.tipo_alerta === '15 dias para vencimento'
        ).length;

        const vencimento7 = res.filter(
          item => item.tipo_alerta === '7 dias para vencimento'
        ).length;

        const estoqueCritico = res.filter(
          item => item.tipo_alerta === 'Estoque Crítico'
        ).length;

        const resolvidos = res.filter(
          item => item.status_alerta === 'Resolvido'
        ).length;

        this.cards.set([
          {
            title: 'VENCIMENTOS',
            value: `${vencimento30 + vencimento15 + vencimento7} alertas`,
            subtitle: `${vencimento7} críticos, ${vencimento15} médios e ${vencimento30} leves`,
            icon: 'pi pi-calendar',
            variant: 'primary'
          },

          {
            title: 'ESTOQUE CRÍTICO',
            value: `${estoqueCritico} itens`,
            subtitle: 'Necessitam reposição',
            icon: 'pi pi-exclamation-triangle',
            variant: 'warning'
          },

          {
            title: 'RESOLVIDOS',
            value: `${resolvidos} alertas`,
            subtitle: 'Alertas finalizados',
            icon: 'pi pi-check-circle',
            variant: 'success'
          }
        ]);
      });
  }

  reloadCurrentTab() {

    switch (this.selectedTab()) {

      case '0':
        this.loadAbertos();
        break;

      case '1':
        this.loadResolvidos();
        break;

      case '2':
        this.loadTodos();
        break;
    }

    this.loadCards();
  }

  // verificarAgora() {
  //   this.alertService.verificarAlertas()
  //     .then((resultado: any) => {
  //       // aqui você usa o resultado pra mostrar pro usuário
  //       console.log(`Criados: ${resultado.alertas_criados}`);
  //       console.log(`Escalados: ${resultado.alertas_escalados}`);
  //       console.log(`Expirados: ${resultado.alertas_expirados}`);

  //       // depois recarrega a lista pra refletir os novos alertas
  //       // this.carregar();
  //     })
  //     .catch((err) => {
  //       console.error('Erro ao verificar alertas', err);
  //     })
  // }
}
