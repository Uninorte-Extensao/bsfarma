import { DatePipe } from '@angular/common';
import { Component, input } from '@angular/core';
import { Button } from "primeng/button";

@Component({
  selector: 'app-table-alerts',
  imports: [Button, DatePipe],
  templateUrl: './table-alerts.component.html',
  styleUrl: './table-alerts.component.scss',
})
export class TableAlertsComponent {
  item = input.required<any>()
}
