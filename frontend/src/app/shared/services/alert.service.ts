import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { IAlertaValidade, IUpdateStatusAlerta, IVerificacaoAlerta } from '../models/IAlert';

@Injectable({
  providedIn: 'root',
})
export class AlertService {
  private http = inject(HttpClient);

  getAlertas(
    status?: string,
    tipo_alerta?: string,
    medicamento_id?: string,
    apenas_ativos?: boolean
  ): Promise<IAlertaValidade[]> {

    let params = new HttpParams();

    if (status) {
      params = params.set('status', status);
    }

    if (tipo_alerta) {
      params = params.set('tipo_alerta', tipo_alerta);
    }

    if (medicamento_id) {
      params = params.set('medicamento_id', medicamento_id);
    }

    if (apenas_ativos !== undefined) {
      params = params.set('apenas_ativos', apenas_ativos);
    }

    return firstValueFrom(
      this.http.get<IAlertaValidade[]>(
        `${environment.apiUrl}/alertas`,
        { params }
      )
    );
  }

  getAlertaById(alertaId: string): Promise<IAlertaValidade> {
    return firstValueFrom(
      this.http.get<IAlertaValidade>(
        `${environment.apiUrl}/alertas/${alertaId}`
      )
    );
  }

  updateStatusAlerta(
    alertaId: string,
    payload: IUpdateStatusAlerta
  ): Promise<IAlertaValidade> {
    return firstValueFrom(
      this.http.patch<IAlertaValidade>(
        `${environment.apiUrl}/alertas/${alertaId}/status_alerta`,
        payload
      )
    );
  }


  verificarAlertas(): Promise<IVerificacaoAlerta> {
    return firstValueFrom(
      this.http.post<IVerificacaoAlerta>(
        `${environment.apiUrl}/alertas/verificar`,
        {}
      )
    );
  }

  async getQuantidadeAlertasAbertos(): Promise<number> {
    return this.getAlertas(
      undefined,
      undefined,
      undefined,
      true
    ).then(alertas => alertas.length);
  }

  quantidadeAlertas = signal(0);

  atualizarQuantidadeAlertas() {
    this.getQuantidadeAlertasAbertos()
      .then(qtd => {
        this.quantidadeAlertas.set(qtd);
      })
      .catch(() => {
        this.quantidadeAlertas.set(0);
      });
  }
}