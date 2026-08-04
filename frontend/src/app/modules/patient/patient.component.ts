import {
  Component,
  inject,
  model,
  signal,
  OnInit
} from '@angular/core';

import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';

import { TablePatientComponent } from './table-patient/table-patient.component';
import { FormPatientComponent } from './form-patient/form-patient.component';
import { IS_MOBILE } from '../../shared/services/is-mobile.service';
import { PatientService } from '../../shared/services/patient.service';
import { ToastService } from '../../shared/services/toast.service';
import { LoadingService } from '../../shared/services/loading.service';

import {
  ICreatePaciente,
  IPaciente,
  IRecuperarPaciente,
  IUpdatePaciente
} from '../../shared/models/IPatient';

type ITypeDialog = 'criar' | 'recuperar' | 'editar';

@Component({
  selector: 'app-patient',
  imports: [
    Button,
    TablePatientComponent,
    FormPatientComponent,
    Dialog
  ],
  templateUrl: './patient.component.html',
  styleUrl: './patient.component.scss',
})
export class PatientComponent implements OnInit {

  protected isMobile = inject(IS_MOBILE);

  private patientService = inject(PatientService);
  private toast = inject(ToastService);
  private loading = inject(LoadingService);

  public pacientes = signal<IPaciente[]>([]);

  private currentFilter: boolean | undefined = undefined;

  public isVisible = model<boolean>(false);
  public typeDialog = signal<ITypeDialog>('criar');

  public codigo = model<string>('');
  public pacienteSelecionado = signal<IPaciente | null>(null);
  public dadosRecuperados = signal<IPaciente | null>(null);

  ngOnInit() {
    this.loadPacientes();
  }

  public onFilter(filter: boolean | undefined) {
    this.currentFilter = filter;
    this.loadPacientes();
  }

  private loadPacientes(): void {

    this.loading.show();

    this.patientService.getPacientes(this.currentFilter)
      .then((res: IPaciente[]) => {
        this.pacientes.set(res);
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

  delete(item: IPaciente) {

    this.loading.show();

    this.patientService.deletePaciente(item.codigo)
      .then(() => {

        this.toast.showToastSuccess(
          'Paciente inativado com sucesso.'
        );

        this.loadPacientes();
      })
      .catch(() => {
        this.toast.showToastError(
          'Erro ao inativar paciente.'
        );
      })
      .finally(() => {
        this.loading.hide();
      });
  }

  showModal(type: ITypeDialog) {
    this.typeDialog.set(type);
    this.pacienteSelecionado.set(null);
    this.dadosRecuperados.set(null);
    this.isVisible.set(true);
  }

  closeModal() {
    this.isVisible.set(false);
    this.dadosRecuperados.set(null);
  }

  onInvalidForm() {
    this.toast.showToastWarn(
      'Por favor, preencha todos os campos.'
    );
  }

  criarPaciente(form: ICreatePaciente) {

    this.loading.show();

    this.patientService.createPaciente(form)
      .then(() => {

        this.toast.showToastSuccess(
          'Paciente cadastrado com sucesso.'
        );

        this.loadPacientes();

        this.closeModal();
      })
      .catch(() => {
        this.toast.showToastError(
          'Erro ao cadastrar novo paciente'
        );
      })
      .finally(() => {
        this.loading.hide();
      });
  }

  recuperarPaciente(form: IRecuperarPaciente) {

    this.loading.show();

    this.patientService.recuperarPaciente(form)
      .then((res: IPaciente) => {

        this.loadPacientes();

        this.toast.showToastSuccess(
          'Paciente recuperado com sucesso.'
        );

        this.dadosRecuperados.set(res)
      })
      .catch(() => {
        this.toast.showToastError(
          'Erro ao recuperar cadastro do paciente'
        );
      })
      .finally(() => {
        this.loading.hide();
      });
  }

  editarPaciente(form: IUpdatePaciente) {

    this.loading.show();

    this.patientService.updatePaciente(
      this.codigo(),
      form
    )
      .then(() => {

        this.toast.showToastSuccess(
          'Paciente atualizado com sucesso.'
        );

        this.loadPacientes();

        this.closeModal();
      })
      .catch(() => {
        this.toast.showToastError(
          'Erro ao editar paciente'
        );
      })
      .finally(() => {
        this.loading.hide();
      });
  }

  handleEdit(item: IPaciente) {

    this.typeDialog.set('editar');

    this.codigo.set(item.codigo);

    this.pacienteSelecionado.set(item);

    this.dadosRecuperados.set(null);

    this.isVisible.set(true);
  }
}
