import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { lastValueFrom } from 'rxjs';
import { Router } from '@angular/router';

import { environment } from '../../../environments/environment';
import { IResponseUser, IResponseLogin, IUserLogin } from '../models/IUser';
import { UserService } from './user.service';
import { Permission } from '../../core/permissions.enum';
import { ROLE_PERMISSIONS } from '../../core/role-permissions';
import { HOME_BY_PROFILE } from '../../core/authGuard';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private userService = inject(UserService);

  public user = signal<IResponseUser | null>(null);
  public isLogged = signal(!!localStorage.getItem('isLoggedBsFarma'));

  async login(credentials: IUserLogin): Promise<IResponseLogin> {
    const body = new URLSearchParams();
    body.set('username', credentials.username);
    body.set('password', credentials.password);

    const res = await lastValueFrom(
      this.http.post<IResponseLogin>(
        `${environment.apiUrl}/auth/login`,
        body.toString(),
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
      )
    );

    localStorage.setItem('isLoggedBsFarma', 'true');
    localStorage.setItem('tokenBsFarma', res.access_token);
    localStorage.setItem('UserIdBSFarma', res.id_user);
    this.isLogged.set(true);

    const user = await this.userService.getUserById(res.id_user);
    this.user.set(user);

    // Redireciona para a home do perfil
    this.router.navigate([HOME_BY_PROFILE[user.perfil] ?? '/catalog']);

    return res;
  }

  async loadUser(): Promise<void> {
    const userId = this.getUserIdFromToken();
    if (!userId) { this.logout(); return; }

    try {
      const user = await this.userService.getUserById(userId);
      this.user.set(user);
    } catch {
      this.logout();
    }
  }

  logout(): void {
    localStorage.removeItem('isLoggedBsFarma');
    localStorage.removeItem('tokenBsFarma');
    localStorage.removeItem('UserIdBSFarma');
    this.user.set(null);
    this.isLogged.set(false);
    this.router.navigate(['/auth']);
  }

  isLoggedIn(): boolean {
    return localStorage.getItem('isLoggedBsFarma') === 'true';
  }

  hasPermission(permission: Permission): boolean {
    const user = this.user();
    if (!user) return false;
    return ROLE_PERMISSIONS[user.perfil]?.includes(permission) ?? false;
  }

  private getUserIdFromToken(): string {
    const token = localStorage.getItem('tokenBsFarma');
    if (!token) return '';
    try {
      return JSON.parse(atob(token.split('.')[1])).sub;
    } catch {
      return '';
    }
  }
}