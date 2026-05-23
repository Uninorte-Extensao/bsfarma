import { Component, computed, input } from '@angular/core';
import { IItemCritico } from '../../../shared/models/IReport';
import { Tag} from 'primeng/tag'
import { Button } from "primeng/button";
import { RouterLink } from "@angular/router";
@Component({
  selector: 'app-dashboard-alert',
  imports: [
    Tag,
    Button,
    RouterLink
],
  templateUrl: './dashboard-alert.component.html',
  styleUrl: './dashboard-alert.component.scss',
})
export class DashboardAlertComponent {
  alerts = input.required<IItemCritico[]>();

  totalAlertas = computed(() => this.alerts().length);

  getSeverity(motivo: string) {
    return motivo.toLowerCase().includes('estoque')
      ? 'danger'
      : 'warn';
  }
}
