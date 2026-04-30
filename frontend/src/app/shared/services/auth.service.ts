import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { lastValueFrom, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ICreateUser, IResponseCreateUser, IResponseLogin, IUserLogin } from '../models/IUser';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  public isLogged = signal(!!localStorage.getItem('isLoggedBsFarma'));
  public emailUser = signal('');

  constructor() { }
async login(credentials: IUserLogin) {
  const body = new URLSearchParams();

  body.set('username', credentials.username)
  body.set('password', credentials.password)

  return lastValueFrom(
    this.http.post<IResponseLogin>(
      `${environment.apiUrl}/auth/login`,
      body.toString(),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
  ).then(res => {
    localStorage.setItem('isLoggedBsFarma', 'true');
    this.isLogged.set(true)
    return res;
  })
}

  register(data: ICreateUser) {
    return lastValueFrom(
      this.http.post<IResponseCreateUser>(`${environment.apiUrl}/usuarios`, data, {
        withCredentials: true,
      })
    );
  }


  logout() {
    return lastValueFrom(
      this.http.post(`${environment.apiUrl}/logout`, {}, {
        withCredentials: true,
        responseType: 'text'
      })
    ).then(res => {
      localStorage.removeItem('isLogged');
      this.isLogged.set(false);
      return res;
    });
  }

  isLoggedIn(): boolean {
    return localStorage.getItem('isLoggedBsFarma') === 'true';
  }
}
