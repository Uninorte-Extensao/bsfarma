import { Component, effect, model, output, OutputEmitterRef, signal } from '@angular/core';
import { InputText } from 'primeng/inputtext';
import { SelectModule } from "primeng/select";
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from "primeng/button";
import { Password } from 'primeng/password';
import { ICreateUser, IResponseUser, IUpdateUser, PROFILE_OPTIONS } from '../../../shared/models/IUser';
import { ToggleSwitch } from 'primeng/toggleswitch';

type ITypeDialog = 'create' | 'update'
@Component({
  selector: 'app-form-user',
  imports: [
    InputText,
    SelectModule,
    FormsModule,
    Button,
    Password,
    ReactiveFormsModule,
    ToggleSwitch
  ],
  templateUrl: './form-user.component.html',
  styleUrl: './form-user.component.scss',
})
export class FormUserComponent {
  checked: boolean = false;
  protected typeProfile = signal(PROFILE_OPTIONS);

  protected form: FormGroup;

  public isVisible = model(false);
  public onChangeCreate: OutputEmitterRef<ICreateUser> = output();
  public typeDialog = model<ITypeDialog>('create');
  public user = model<IResponseUser | null>(null);
  public onChangeUpdate: OutputEmitterRef<IUpdateUser> = output();

  constructor() {
    const fb = new FormBuilder
    this.form = fb.group({
      nome: [null, [Validators.required]],
      login: [null, [Validators.required]],
      senha: [null, [Validators.required, Validators.minLength(8)]],
      perfil: [null, [Validators.required]],
    })


    effect(() => {
      if (this.user()) {
        this.setValues(this.user()!)
        console.log('user', this.user())
      }

      this.typeDialog()
    })
  }

  close() {
    this.isVisible.set(false)
  }

  submit() {
    if(this.typeDialog() === 'update') {
      const form: IUpdateUser = {
        nome: this.form.value.nome,
        perfil: this.form.value.perfil,
        ativo: this.checked
      }
      this.onChangeUpdate.emit(form)


    } else if (this.typeDialog() === 'create') {
      this.onChangeCreate.emit(this.form.value)
    }
  }


  private setValues(user: IResponseUser) {
    this.form.patchValue({
      nome: user.nome,
      login: user.login,
      senha: user.senha,
      perfil: user.perfil
    })
    this.checked = user.ativo
  }
}
