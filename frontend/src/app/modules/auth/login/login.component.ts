import { Component, output, OutputEmitterRef } from '@angular/core';
import { InputText } from 'primeng/inputtext';
import { Password } from 'primeng/password'
import { Button } from "primeng/button";
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { IUserLogin } from '../../../shared/models/IUser';
@Component({
  selector: 'app-login',
  imports: [
    InputText,
    Password,
    Button,
    ReactiveFormsModule
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  protected form: FormGroup;
  public onChangeLogin: OutputEmitterRef<IUserLogin> = output()

  constructor() {
    const fb = new FormBuilder
    this.form = fb.group({
      username: [null, [Validators.required]],
      password: [null, [Validators.required]]
    })
  }

  protected saveData() {
    this.onChangeLogin.emit(this.form.value)
  }
}
