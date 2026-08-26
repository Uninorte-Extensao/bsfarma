import { NgClass } from '@angular/common';
import { Component, input } from '@angular/core';
@Component({
  selector: 'app-card-view',
  imports: [
    NgClass
  ],
  templateUrl: './card-view.component.html',
  styleUrl: './card-view.component.scss',
})
export class CardViewComponent {
  title = input.required<string>();
  value = input.required<string>();
  subtitle = input<string>('');
  icon = input<string>('pi pi-chart-line');

  variant = input<'primary' | 'success' | 'danger' | 'warning'>('primary');
}
