import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { lastValueFrom } from 'rxjs';
import { ICreateDispensacao, IDispensacao } from '../models/IDispersation';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class DispersationService {
  private http = inject(HttpClient)

  getAllDispersacoes(pacienteId?: string) {
    let params = new HttpParams()

    if (pacienteId) {
      params = params.set('paciente_id', pacienteId)
    }
    return lastValueFrom(this.http.get<IDispensacao[]>(`${environment.apiUrl}/dispensacoes`, { params }))
  }

  createDispensacao(dispensacao: ICreateDispensacao) {
    return lastValueFrom(this.http.post<IDispensacao>(`${environment.apiUrl}/dispensacoes`, dispensacao))
  }

  getDispensacoesById(dispensacaoId: string) {
    return lastValueFrom(this.http.get<IDispensacao>(`${environment.apiUrl}/dispensacoes/${dispensacaoId}`))
  }
}
