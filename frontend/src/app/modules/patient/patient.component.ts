import {
  Component,
  inject,
  model,
  signal,
  WritableSignal,
  OnInit
} from '@angular/core';

import { TabsModule } from 'primeng/tabs';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { Textarea } from 'primeng/textarea';
import { InputMask } from 'primeng/inputmask';

import {
  FormBuilder,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';

import { TablePatientComponent } from './table-patient/table-patient.component';
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
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-patient',
  imports: [
    TabsModule,
    Button,
    TablePatientComponent,
    Dialog,
    Textarea,
    InputMask,
    ReactiveFormsModule,
    DatePipe
  ],
  templateUrl: './patient.component.html',
  styleUrl: './patient.component.scss',
})
export class PatientComponent implements OnInit {

  protected isMobile = inject(IS_MOBILE);

  private patientService = inject(PatientService);
  private toast = inject(ToastService);
  private loading = inject(LoadingService);
  private fb = inject(FormBuilder);

  public pacientes = signal<IPaciente[]>([]);
  public pacientesAtivos = signal<IPaciente[]>([]);
  public pacientesInativos = signal<IPaciente[]>([]);

  public isVisible = model<boolean>(false);
  public typeDialog = signal<string>('criar');

  public codigo = model<string>('');

  public form = this.fb.group({
    cpf: ['', Validators.required],
    condicaoClinica: ['', Validators.required]
  });

  public dadosRecuperados = signal<IPaciente | null>(null)

  ngOnInit() {
    this.loadPacientes();
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

  delete(item: IPaciente) {

    this.loading.show();

    this.patientService.deletePaciente(item.codigo)
      .then(() => {

        this.pacientes.update(
          pacientes =>
            pacientes.filter(
              p => p.codigo !== item.codigo
            )
        );

        this.pacientesAtivos.update(
          pacientes =>
            pacientes.filter(
              p => p.codigo !== item.codigo
            )
        );

        this.pacientesInativos.update(
          pacientes => [
            ...pacientes,
            {
              ...item,
              ativo: false
            }
          ]
        );

        this.toast.showToastSuccess(
          'Paciente inativado com sucesso.'
        );
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

  showModal(type: string) {
    this.typeDialog.set(type);

    this.form.reset();

    if (type === 'recuperar') {
      this.form.get('condicaoClinica')?.clearValidators();
      this.form.get('condicaoClinica')?.updateValueAndValidity();
    } else {
      this.form.get('condicaoClinica')?.setValidators(Validators.required);
      this.form.get('condicaoClinica')?.updateValueAndValidity();
    }

    if (type === 'editar') {
      this.form.get('cpf')?.clearValidators();
      this.form.get('cpf')?.updateValueAndValidity();
    } else {
      this.form.get('cpf')?.setValidators(Validators.required);
      this.form.get('cpf')?.updateValueAndValidity();
    }

    this.isVisible.set(true);
  }

  closeModal() {
    this.isVisible.set(false);
    this.form.reset();
    this.dadosRecuperados.set(null)
  }

  submit() {

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.toast.showToastWarn(
        'Por favor, preencha todos os campos.'
      );
      return;
    }

    this.loading.show();

    if (this.typeDialog() === 'criar') {
      this.criarPaciente();
    } else if (this.typeDialog() === 'recuperar') {
      this.recuperarPaciente();
    } else {
      this.editarPaciente();
    }
  }

  private criarPaciente() {

    const formValue = this.form.getRawValue();

    const form: ICreatePaciente = {
      cpf: formValue.cpf!.replace(/\D/g, ''),
      condicao_clinica: formValue.condicaoClinica!
    };

    this.patientService.createPaciente(form)
      .then((res: IPaciente) => {

        this.pacientes.update(
          pacientes => [...pacientes, res]
        );

        this.pacientesAtivos.update(
          pacientes => [...pacientes, res]
        );

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

  private recuperarPaciente() {

    const formValue = this.form.getRawValue();

    const form: IRecuperarPaciente = {
      cpf: formValue.cpf!
    };

    this.loading.show();

    this.patientService.recuperarPaciente(form)
      .then((res: IPaciente) => {

        // LISTA GERAL
        this.pacientes.update((pacientes) => {

          const exists = pacientes.some(
            p => p.codigo === res.codigo
          );

          if (exists) {
            return pacientes.map(
              p => p.codigo === res.codigo ? res : p
            );
          }

          return [...pacientes, res];
        });

        // LISTA ATIVOS
        this.pacientesAtivos.update((pacientes) => {

          const exists = pacientes.some(
            p => p.codigo === res.codigo
          );

          if (exists) {
            return pacientes.map(
              p => p.codigo === res.codigo ? res : p
            );
          }

          return [...pacientes, res];
        });

        // REMOVE DOS INATIVOS
        this.pacientesInativos.update((pacientes) =>
          pacientes.filter(
            p => p.codigo !== res.codigo
          )
        );

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

  private editarPaciente() {

    const formValue = this.form.getRawValue();

    const form: IUpdatePaciente = {
      condicao_clinica: formValue.condicaoClinica!
    };

    this.loading.show();

    this.patientService.updatePaciente(
      this.codigo(),
      form
    )
      .then((res: IPaciente) => {

        this.pacientes.update(
          pacientes =>
            pacientes.map(p =>
              p.codigo === res.codigo ? res : p
            )
        );

        this.pacientesAtivos.update(
          pacientes =>
            pacientes.map(p =>
              p.codigo === res.codigo ? res : p
            )
        );

        this.toast.showToastSuccess(
          'Paciente atualizado com sucesso.'
        );

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

    this.form.patchValue({
      condicaoClinica: item.condicao_clinica
    });

    this.form.get('cpf')?.clearValidators();
    this.form.get('cpf')?.updateValueAndValidity();

    this.form.get('condicaoClinica')?.setValidators(
      Validators.required
    );

    this.form.get('condicaoClinica')?.updateValueAndValidity();

    this.isVisible.set(true);
  }
}