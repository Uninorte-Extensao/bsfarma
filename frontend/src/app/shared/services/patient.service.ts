import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { ICreatePaciente, IPaciente, IRecuperarPaciente, IUpdatePaciente } from '../models/IPatient';
import { lastValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class PatientService {
  private http = inject(HttpClient)

  createPaciente(paciente: ICreatePaciente) {
    return lastValueFrom(this.http.post<IPaciente>(`${environment.apiUrl}/pacientes`, paciente))
  }

  getPacientes(ativo?: boolean) {

    let params = new HttpParams();

    if (ativo !== undefined) {
      params = params.set('apenas_ativos', ativo.toString())
    }

    return lastValueFrom(this.http.get<IPaciente[]>(`${environment.apiUrl}/pacientes`, { params }));
  }

  getPacienteById(pacienteId: string) {
    return lastValueFrom(this.http.get<IPaciente>(`${environment.apiUrl}/pacientes/${pacienteId}`))
  }

  updatePaciente(pacienteId: string, paciente: IUpdatePaciente) {
    return lastValueFrom(this.http.patch<IPaciente>(`${environment.apiUrl}/pacientes/${pacienteId}`, paciente))
  }

  recuperarPaciente(paciente: IRecuperarPaciente) {
    return lastValueFrom(this.http.post<IPaciente>(`${environment.apiUrl}/pacientes/recuperar`, paciente))
  }

  deletePaciente(pacienteId: string) {
    return lastValueFrom(this.http.delete<IPaciente>(`${environment.apiUrl}/pacientes/${pacienteId}/inativar`))
  }
}
