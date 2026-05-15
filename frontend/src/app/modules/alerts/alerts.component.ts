import { Component, effect, signal } from '@angular/core';
import { TabsModule } from 'primeng/tabs';
import { TableAlertsComponent } from "./table-alerts/table-alerts.component";
import { ALERTAS } from '../../shared/mocks/alerts.mock';
import { CardViewComponent } from "../../shared/components/card-view/card-view.component";

@Component({
  selector: 'app-alerts',
  imports: [TabsModule, TableAlertsComponent, CardViewComponent],
  templateUrl: './alerts.component.html',
  styleUrl: './alerts.component.scss',
})
export class AlertsComponent {
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

  listAlerts = signal(ALERTAS)

  constructor() {
    effect(() => {
      console.log('list alert', this.listAlerts())
    })
  }
}
