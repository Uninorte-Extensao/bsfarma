import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { lastValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';
import { IUser } from '../models/IUser'
@Injectable({
  providedIn: 'root',
})
export class UserService {
  private http = inject(HttpClient);

  public getAllUsers() {
    return lastValueFrom(this.http.get<IUser[]>(`${environment.apiUrl}/usuarios`))
  }
}
