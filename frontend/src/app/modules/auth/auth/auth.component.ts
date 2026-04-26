import { Component, inject } from '@angular/core';
import { LoginComponent } from "../login/login.component";
import { Button } from "primeng/button";
import { SelectButton } from 'primeng/selectbutton';
import { FormsModule } from '@angular/forms';
import { RegisterComponent } from "../register/register.component";
import { IResponseLogin, IUserLogin } from '../../../shared/models/IUser';
import { AuthService } from '../../../shared/services/auth.service';
import { LoadingService } from '../../../shared/services/loading.service';
import { ToastService } from '../../../shared/services/toast.service';

@Component({
  selector: 'app-auth',
  imports: [LoginComponent, SelectButton, FormsModule, RegisterComponent],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.scss',
})
export class AuthComponent {
  readonly stateOptions: any[] = [
    { label: 'Entrar', value: 'login' }, 
    { label: 'Criar Conta', value: 'register' }];

  protected value: string = 'login';

  private authService = inject(AuthService)
  private loadingService = inject(LoadingService)
  private toastService = inject(ToastService)

  submit(event: IUserLogin) {
    this.loadingService.show()
    this.authService.login(event)
    .then((res: IResponseLogin) => {
      console.log(res)
      // TODO AO INVÉS DE UM TOAST, CRIAR UMA TELA DO TIPO BEM VINDO
      this.toastService.showToastSuccess('Usuario logado com sucesso')
    })
    .catch((err) => {
      console.log(err)
      this.toastService.showToastError('Erro ao logar.')
    })
    .finally(() => {
      this.loadingService.hide()
    })
  }
}
