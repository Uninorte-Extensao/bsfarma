import { Component, effect, input, model, output, OutputEmitterRef } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from 'primeng/button';
import { InputMask } from 'primeng/inputmask';
import { Textarea } from 'primeng/textarea';
import { DatePipe } from '@angular/common';
import {
  ICreatePaciente,
  IPaciente,
  IRecuperarPaciente,
  IUpdatePaciente
} from '../../../shared/models/IPatient';

type ITypeDialog = 'criar' | 'recuperar' | 'editar';

@Component({
  selector: 'app-form-patient',
  imports: [
    ReactiveFormsModule,
    Button,
    InputMask,
    Textarea,
    DatePipe
  ],
  templateUrl: './form-patient.component.html',
  styleUrl: './form-patient.component.scss',
})
export class FormPatientComponent {
  protected form: FormGroup;

  public isVisible = model(false);
  public typeDialog = model<ITypeDialog>('criar');
  public paciente = input<IPaciente | null>(null);
  public dadosRecuperados = input<IPaciente | null>(null);

  public onChangeCreate: OutputEmitterRef<ICreatePaciente> = output();
  public onChangeRecuperar: OutputEmitterRef<IRecuperarPaciente> = output();
  public onChangeEditar: OutputEmitterRef<IUpdatePaciente> = output();
  public onInvalid: OutputEmitterRef<void> = output();

  constructor() {
    const fb = new FormBuilder();

    this.form = fb.group({
      cpf: [null, Validators.required],
      condicaoClinica: [null, Validators.required]
    });

    effect(() => {
      const type = this.typeDialog();
      const paciente = this.paciente();

      if (!this.isVisible()) return;

      this.form.reset();
      this.updateValidators(type);

      if (type === 'editar' && paciente) {
        this.form.patchValue({
          condicaoClinica: paciente.condicao_clinica
        });
      }
    });
  }

  private updateValidators(type: ITypeDialog) {
    const cpf = this.form.get('cpf');
    const condicaoClinica = this.form.get('condicaoClinica');

    if (type === 'editar') {
      cpf?.clearValidators();
    } else {
      cpf?.setValidators(Validators.required);
    }
    cpf?.updateValueAndValidity();

    if (type === 'recuperar') {
      condicaoClinica?.clearValidators();
    } else {
      condicaoClinica?.setValidators(Validators.required);
    }
    condicaoClinica?.updateValueAndValidity();
  }

  close() {
    this.isVisible.set(false);
  }

  submit() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.onInvalid.emit();
      return;
    }

    const value = this.form.getRawValue();

    switch (this.typeDialog()) {
      case 'criar':
        this.onChangeCreate.emit({
          cpf: value.cpf.replace(/\D/g, ''),
          condicao_clinica: value.condicaoClinica
        });
        break;

      case 'recuperar':
        this.onChangeRecuperar.emit({
          cpf: value.cpf
        });
        break;

      case 'editar':
        this.onChangeEditar.emit({
          condicao_clinica: value.condicaoClinica
        });
        break;
    }
  }
}
