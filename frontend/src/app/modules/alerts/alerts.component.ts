import { Component, signal } from '@angular/core';

@Component({
  selector: 'app-alerts',
  imports: [],
  templateUrl: './alerts.component.html',
  styleUrl: './alerts.component.scss',
})
export class AlertsComponent {
  cards = signal<any[]>([
    {
      icon: 'pi pi-calendar',
      label: 'Vencimento próximo',
      valor: 3,
      color: 'red'
    },

    {
      icon: 'pi pi-home',
      label: 'Estoque mínimo',
      valor: 3,
      color: 'yellow'
    },

    {
      icon: 'pi pi-check',
      label: 'Resolvidos hoje',
      valor: 0,
      color: 'green'
    }
  ])
}
