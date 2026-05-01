import { Component, inject, signal } from '@angular/core';
import { Button } from "primeng/button";
import { UserService } from '../../shared/services/user.service';
import { LoadingService } from '../../shared/services/loading.service';
import { ToastService } from '../../shared/services/toast.service';
import { IUser } from '../../shared/models/IUser';
import { TableModule } from 'primeng/table';
import { InputIcon } from 'primeng/inputicon';
import { IconField } from 'primeng/iconfield';
import { InputText } from 'primeng/inputtext';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-management',
  imports: [
    Button,
    TableModule,
    InputIcon,
    IconField,
    InputText,
    DatePipe
],
  templateUrl: './management.component.html',
  styleUrl: './management.component.scss',
})
export class ManagementComponent {
  private userService = inject(UserService);
  private loadingService = inject(LoadingService);
  private toastService = inject(ToastService);
  readonly listUsers = signal<IUser[]>([])

  ngOnInit() {
    this.getUsers()
  }

  private getUsers() {
    this.loadingService.show()
    this.userService.getAllUsers()
    .then((res: IUser[]) => {
      this.listUsers.set(res)
    })
    .catch(() => {
      this.toastService.showToastError('Erro ao buscar lista de usuários.')
    })
    .finally(() => {
      this.loadingService.hide()
    })
  }
}
