import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { lastValueFrom, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ICreateUser, IResponseCreateUser, IResponseLogin, IUserLogin } from '../models/IUser';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  public isLogged = signal(!!localStorage.getItem('isLoggedBsFarma'));
  public emailUser = signal('');
  private router = inject(Router)

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
      localStorage.setItem('tokenBsFarma', res.access_token)
      return res;
    })
  }

  logout() {
    localStorage.removeItem('isLoggedBsFarma');
    localStorage.removeItem('tokenBsFarma')
    this.isLogged.set(false);
    this.router.navigate(['auth'])
  }

  isLoggedIn(): boolean {
    return localStorage.getItem('isLoggedBsFarma') === 'true';
  }
}
