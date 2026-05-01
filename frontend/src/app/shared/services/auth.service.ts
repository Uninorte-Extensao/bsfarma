import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { lastValueFrom, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ICreateUser, IResponseUser, IResponseLogin, IUserLogin, IUser } from '../models/IUser';
import { Router } from '@angular/router';
import { UserService } from './user.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  public isLogged = signal(!!localStorage.getItem('isLoggedBsFarma'));
  public emailUser = signal('');
  private router = inject(Router);
  public user = signal<IResponseUser | null>(null);
  private userService = inject(UserService);

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
    ).then(async res => {
      localStorage.setItem('isLoggedBsFarma', 'true');
      localStorage.setItem('tokenBsFarma', res.access_token)
      localStorage.setItem('UserIdBSFarma', res.id_user)
      this.isLogged.set(true)

      const user = await this.userService.getUserById(res.id_user);
      this.user.set(user);
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

  async loadUser() {
    try {
      const userId = this.getUserIdFromToken();

      if (!userId) {
        this.logout();
        return;
      }

      const user = await this.userService.getUserById(userId);
      this.user.set(user);

    } catch (err) {
      console.error('Erro loadUser:', err);
      this.logout();
    }
  }

  getUserIdFromToken(): string {
    const token = localStorage.getItem('tokenBsFarma');

    if (!token) return '';

    const payload = JSON.parse(atob(token.split('.')[1]));

    console.log('JWT payload:', payload);

    return payload.sub;
  }
}
