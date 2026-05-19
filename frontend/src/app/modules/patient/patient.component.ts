import { Component, inject, model, signal, WritableSignal, OnInit } from '@angular/core';
import { TabsModule } from "primeng/tabs";
import { Button } from "primeng/button";
import { TablePatientComponent } from './table-patient/table-patient.component';
import { IS_MOBILE } from '../../shared/services/is-mobile.service';
import { PatientService } from '../../shared/services/patient.service';
import { ToastService } from '../../shared/services/toast.service';
import { LoadingService } from '../../shared/services/loading.service';
import { ICreatePaciente, IPaciente, IRecuperarPaciente, IUpdatePaciente } from '../../shared/models/IPatient';
import { Router } from '@angular/router';
import { Dialog } from "primeng/dialog";
import { Textarea } from 'primeng/textarea';
import { InputMask } from 'primeng/inputmask'
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-patient',
  imports: [
    TabsModule,
    Button,
    TablePatientComponent,
    Dialog,
    Textarea,
    InputMask,
    FormsModule
  ],
  templateUrl: './patient.component.html',
  styleUrl: './patient.component.scss',
})
export class PatientComponent implements OnInit {
  protected isMobile = inject(IS_MOBILE)

  private patientService = inject(PatientService)
  private toast = inject(ToastService)
  private loading = inject(LoadingService)

  public pacientes = signal<IPaciente[]>([])
  public pacientesAtivos = signal<IPaciente[]>([])
  public pacientesInativos = signal<IPaciente[]>([])
  public isVisible = model<boolean>(false)
  public typeDialog = signal<string>('criar')

  protected cpf: string = ''
  protected condicaoClinica: string = ''
  public codigo = model<string>('')


  ngOnInit() {
    this.loadPacientes()
  }

  private loadPacientes(): void {
    this.fetchPacientes(this.pacientes);
    this.fetchPacientes(this.pacientesAtivos, true);
    this.fetchPacientes(this.pacientesInativos, false);
  }

  private fetchPacientes(
    state: WritableSignal<IPaciente[]>,
    ativo?: boolean
  ): void {

    this.loading.show();

    this.patientService.getPacientes(ativo)
      .then((res: IPaciente[]) => {
        state.set(res);
      })
      .catch(() => {
        this.toast.showToastError(
          'Erro ao buscar lista de pacientes.'
        );
      })
      .finally(() => {
        this.loading.hide();
      });
  }

  delete(item: any) { }


  showModal(type: string) {
    this.typeDialog.set(type)
    this.isVisible.set(true)
  }

  closeModal() {
    this.isVisible.set(false)
  }

  submit() {
    this.loading.show()
    if (this.typeDialog() === 'criar') {
      this.criarPaciente()
    } else if (this.typeDialog() === 'recuperar') {
      this.recuperarPaciente()
    } else {
      this.editarPaciente()
    }
  }

  private criarPaciente() {
    this.loading.show()

    if (this.cpf === null || this.condicaoClinica === null) {
      this.toast.showToastWarn('Por favor, preencha todos os campos.')
      return
    }
    const form: ICreatePaciente = {
      cpf: this.cpf.replace(/\D/g, ''),
      condicao_clinica: this.condicaoClinica
    }
    this.patientService.createPaciente(form)
      .then((res: IPaciente) => {
        this.pacientes.update(pacientes => [...pacientes, res])
        this.pacientesAtivos.update(pacientes => [...pacientes, res])
      })
      .catch(() => {
        this.toast.showToastError('Erro ao cadastrar novo paciente')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  private recuperarPaciente() {
    this.loading.show()

    if (this.cpf === null) {
      this.toast.showToastWarn('Por favor, preencha todos os campos.')
      return
    }
    const form: IRecuperarPaciente = {
      cpf: this.cpf
    }
    this.patientService.recuperarPaciente(form)
      .then((res: IPaciente) => {
        this.pacientes.update(pacientes => [...pacientes, res])
        this.pacientesAtivos.update(pacientes => [...pacientes, res])
      })
      .catch(() => {
        this.toast.showToastError('Erro ao recuperar cadastro do paciente')
      })
      .finally(() => {
        this.loading.hide()
      })
  }

  private editarPaciente() { 
    this.loading.show()

    if(this.condicaoClinica === null) {
      this.toast.showToastWarn('Por favor, preencha todos os campos.')
      return
    }
    const form: IUpdatePaciente = {
      condicao_clinica: this.condicaoClinica
    }
     this.patientService.updatePaciente(this.codigo(), form)
     .then((res: IPaciente) => {
      this.pacientes.update(paciente => paciente.map(p => p.codigo === res.codigo ? res : p))
      this.pacientesAtivos.update(paciente => paciente.map(p => p.codigo === res.codigo ? res : p))
     })
     .catch(() => {
      this.toast.showToastError('Erro ao editar paciente')
     })
     .finally(() => {
      this.loading.hide()
     })
  }

  private deletePaciente() {
    
  }
}
