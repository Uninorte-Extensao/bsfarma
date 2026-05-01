import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { lastValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ICreateUser, IResponseUser, IUser } from '../models/IUser'
@Injectable({
  providedIn: 'root',
})
export class UserService {
  private http = inject(HttpClient);

  public getAllUsers() {
    return lastValueFrom(this.http.get<IResponseUser[]>(`${environment.apiUrl}/usuarios`))
  }

  public getUserById(userId: string) {
    return lastValueFrom(this.http.get<IResponseUser>(`${environment.apiUrl}/usuarios/${userId}`))
  }

  public createUser(user: ICreateUser) {
    return lastValueFrom(this.http.post<IResponseUser>(`${environment.apiUrl}/usuarios`, user))
  }
}
