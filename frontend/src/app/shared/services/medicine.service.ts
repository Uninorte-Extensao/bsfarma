import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { lastValueFrom } from 'rxjs';
import { ICreateMedicine, IMedicine } from '../models/IMedicine';
import { environment } from '../../../environments/environment';
@Injectable({
  providedIn: 'root',
})
export class MedicineService {
  private http = inject(HttpClient);

  public getMedicamentos() {
    return lastValueFrom(this.http.get<IMedicine[]>(`${environment.apiUrl}/medicamentos`))
  }

  public createMedicamentos(data: ICreateMedicine) {
    return lastValueFrom(this.http.post<IMedicine>(`${environment.apiUrl}/medicamentos`, data))
  }

  public getMedicamentoById(medicamentoId: string) {
    return lastValueFrom(this.http.get<IMedicine>(`${environment.apiUrl}/medicamentos/${medicamentoId}`))
  }

  public updateMedicamento(medicamentoId: string, data: ICreateMedicine) {
    return lastValueFrom(this.http.patch<IMedicine>(`${environment.apiUrl}/medicamentos/${medicamentoId}`, data))
  }

  public deleteMedicamento(medicamentoId: string) {
    return lastValueFrom(this.http.delete<IMedicine>(`${environment.apiUrl}/medicamentos/${medicamentoId}`))
  }
}
