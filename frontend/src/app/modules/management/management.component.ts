import { Component, computed, inject, model, signal, OnInit } from '@angular/core';
import { Button } from "primeng/button";
import { UserService } from '../../shared/services/user.service';
import { LoadingService } from '../../shared/services/loading.service';
import { ToastService } from '../../shared/services/toast.service';
import { ICreateUser, IResponseUser, IUpdateUser } from '../../shared/models/IUser';
import { InputIcon } from 'primeng/inputicon';
import { IconField } from 'primeng/iconfield';
import { InputText } from 'primeng/inputtext';
import { DatePipe, NgClass, TitleCasePipe, UpperCasePipe } from '@angular/common';
import { Dialog } from 'primeng/dialog'
import { Tag } from 'primeng/tag';
import { FormUserComponent } from "./form-user/form-user.component";
import { IS_MOBILE } from '../../shared/services/is-mobile.service';
import { getInitials } from '../../shared/utils/initialsName';

type ITypeDialog = 'create' | 'update'
@Component({
  selector: 'app-management',
  imports: [
    Button,
    InputIcon,
    IconField,
    InputText,
    DatePipe,
    Dialog,
    Tag,
    FormUserComponent,
    NgClass,
    TitleCasePipe,
    UpperCasePipe
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
  private userId = signal<string | null>(null)
  protected isMobile = inject(IS_MOBILE)

  protected searchTerm = signal('');

  protected filteredUsers = computed(() => {
    const term = this.searchTerm().trim().toLowerCase();
    const list = this.listUsers();

    if (!term) return list;

    return list.filter(user =>
      user.nome.toLowerCase().includes(term) ||
      user.login.toLowerCase().includes(term) ||
      user.perfil.toLowerCase().includes(term)
    );
  });

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
    } else {
      this.viewUser.set(null)
      this.userId.set(null)
    }
  }

  protected closeModal() {
    this.isVisible.set(false)
  }

  protected submit(user: ICreateUser) {
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
    this.userService.updateUser(this.userId()!, user)
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

  protected getProfileClass(perfil: string) {
    let style = ''
    if (perfil === 'gestor') style = 'box-yellow' 
    if(perfil === 'farmaceutico') style = 'box-red'
    if(perfil === 'atendente') style = 'box-blue'

    return style
  }

  protected inititalName(name: string): string {
    return getInitials(name);
  }
}
