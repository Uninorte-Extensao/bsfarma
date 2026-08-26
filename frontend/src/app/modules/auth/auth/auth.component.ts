import { Component, inject } from '@angular/core';
import { LoginComponent } from "../login/login.component";
import { FormsModule } from '@angular/forms';
import { IResponseLogin, IUserLogin } from '../../../shared/models/IUser';
import { AuthService } from '../../../shared/services/auth.service';
import { LoadingService } from '../../../shared/services/loading.service';
import { ToastService } from '../../../shared/services/toast.service';
import { ThemeService } from '../../../shared/services/theme.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-auth',
  imports: [LoginComponent, FormsModule],
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
  private router = inject(Router)
  protected themeService = inject(ThemeService)

  toggleTheme() {
    this.themeService.toggle();
  }

  submit(event: IUserLogin) {
    this.loadingService.show()
    this.authService.login(event)
    .then((res: IResponseLogin) => {
      console.log(res)
      // TODO AO INVÉS DE UM TOAST, CRIAR UMA TELA DO TIPO BEM VINDO
      this.router.navigate(['/catalog']);
      // this.toastService.showToastSuccess('Usuario logado com sucesso')
    })
    .catch((err) => {
      console.log(err)
      this.toastService.showToastError('Não foi possível acessar o sistema, por favor, tente novamente.')
    })
    .finally(() => {
      this.loadingService.hide()
    })
  }
}
