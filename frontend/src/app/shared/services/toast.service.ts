import { inject, Injectable } from '@angular/core';
import { MessageService } from 'primeng/api';

@Injectable({
  providedIn: 'root'
})
export class ToastService {
    private messageService = inject(MessageService);

  constructor() { }

  showToastSuccess(msg: string) {
    this.messageService.add({ key: 'tc', severity: 'success', summary: 'Sucesso', detail: msg });
  }

  showToastError(msg: string) {
    this.messageService.add({ key: 'tc', severity: 'error', summary: 'Erro', detail: msg });
  }

  showToastInfo(msg: string) {
    this.messageService.add({ key: 'tc', severity: 'info', summary: 'Informação', detail: msg });
  }

  showToastWarn(msg: string) {
    this.messageService.add({ key: 'tc', severity: 'warn', summary: 'Observação', detail: msg });
  }
}
