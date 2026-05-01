import { Component, inject, model, output, OutputEmitterRef, signal } from '@angular/core';
import { InputText } from 'primeng/inputtext';
import { SelectModule } from "primeng/select";
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from "primeng/button";
import { Password } from 'primeng/password';
import { ICreateUser, PROFILE_OPTIONS } from '../../../shared/models/IUser';
import { UserService } from '../../../shared/services/user.service';
import { LoadingService } from '../../../shared/services/loading.service';
import { ToastService } from '../../../shared/services/toast.service';
@Component({
  selector: 'app-form-user',
  imports: [
    InputText,
    SelectModule,
    FormsModule,
    Button,
    Password,
    ReactiveFormsModule
  ],
  templateUrl: './form-user.component.html',
  styleUrl: './form-user.component.scss',
})
export class FormUserComponent {
  checked: boolean = false;
  protected typeProfile = signal(PROFILE_OPTIONS);
  private userService = inject(UserService);
  private loadingService = inject(LoadingService);
  private toastService = inject(ToastService);

  protected form: FormGroup;

  public isVisible = model(false);
  public onChangeData: OutputEmitterRef<ICreateUser> = output()

  constructor() {
    const fb = new FormBuilder
    this.form = fb.group({
      nome: [null, [Validators.required]],
      login: [null, [Validators.required]],
      senha: [null, [Validators.required, Validators.minLength(8)]],
      perfil: [null, [Validators.required]],
    })
  }

  close() {
    this.isVisible.set(false)
  }

  submit() {
    this.onChangeData.emit(this.form.value)
  }

}
