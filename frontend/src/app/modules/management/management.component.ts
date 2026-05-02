import { Component, inject, model, signal, OnInit } from '@angular/core';
import { Button } from "primeng/button";
import { UserService } from '../../shared/services/user.service';
import { LoadingService } from '../../shared/services/loading.service';
import { ToastService } from '../../shared/services/toast.service';
import { ICreateUser, IResponseUser, IUpdateUser, IUser } from '../../shared/models/IUser';
import { TableModule } from 'primeng/table';
import { InputIcon } from 'primeng/inputicon';
import { IconField } from 'primeng/iconfield';
import { InputText } from 'primeng/inputtext';
import { DatePipe } from '@angular/common';
import { Dialog } from 'primeng/dialog'
import { FormUserComponent } from "./form-user/form-user.component";

type ITypeDialog = 'create' | 'update'
@Component({
  selector: 'app-management',
  imports: [
    Button,
    TableModule,
    InputIcon,
    IconField,
    InputText,
    DatePipe,
    Dialog,
    FormUserComponent
  ],
  templateUrl: './management.component.html',
  styleUrl: './management.component.scss',
})
export class ManagementComponent implements OnInit {
  private userService = inject(UserService);
  private loadingService = inject(LoadingService);
  private toastService = inject(ToastService);
  readonly listUsers = signal<IResponseUser[]>([]);
  protected isVisible = model(false);
  protected typeDialog = model<ITypeDialog>('create');
  public viewUser = model<IResponseUser | null>(null);
  private userId = signal('')

  ngOnInit() {
    this.getUsers()
  }

  private getUsers() {
    this.loadingService.show()
    this.userService.getAllUsers()
      .then((res: IResponseUser[]) => {
        this.listUsers.set(res)
      })
      .catch(() => {
        this.toastService.showToastError('Erro ao buscar lista de usuários.')
      })
      .finally(() => {
        this.loadingService.hide()
      })
  }

  protected showDialog(type: ITypeDialog, user?: IResponseUser) {
    this.isVisible.set(true)
    this.typeDialog.set(type)
    if (user) {
      this.viewUser.set(user)
      this.userId.set(user.id)
    }
  }

  protected closeModal() {
    this.isVisible.set(false)
  }

  protected submit(user: ICreateUser) {
    console.log('senha enviada', user)
    this.loadingService.show()
    this.userService.createUser(user)
      .then((res: IResponseUser) => {
        this.listUsers.update(users => [...users, res]);
        this.toastService.showToastSuccess('Usuário adicionado com sucesso.')
        this.closeModal()
      })
      .catch(() => {
        this.toastService.showToastError('Erro ao adicionar usuário.')
      })
      .finally(() => {
        this.loadingService.hide()
      })
  }

  protected update(user: IUpdateUser) {
    this.loadingService.show();
    this.userService.updateUser(this.userId(), user)
      .then((res: IResponseUser) => {
        this.listUsers.update(users =>
          users.map(u => u.id === res.id ? res : u)
        );
        this.toastService.showToastSuccess('Dados do usuário atualizados com sucesso.')
        this.closeModal()
      })
      .catch(() => {
        this.toastService.showToastError('Erro ao atualizar dados do usuário.')
      })
      .finally(() => {
        this.loadingService.hide()
      })
  }
}
