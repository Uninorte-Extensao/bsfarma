import { Component, inject } from '@angular/core';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { LoadingService } from '../../services/loading.service';
import { CommonModule } from '@angular/common';
import { BlockUIModule } from 'primeng/blockui';

@Component({
  selector: 'app-loading',
  imports: [
    ProgressSpinnerModule,
    CommonModule,
    BlockUIModule
  ],
  templateUrl: './loading.component.html',
  styleUrl: './loading.component.scss'
})
export class LoadingComponent {
  private loadingService = inject(LoadingService);
  public loading$ = this.loadingService.loading$
}
