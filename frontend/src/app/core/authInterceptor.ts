import { HttpInterceptorFn } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { ToastService } from '../shared/services/toast.service';

let isHandling401 = false;

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  
  const token = localStorage.getItem('tokenBsFarma');
  const router = inject(Router);
  const toastService = inject(ToastService)

  const isLoginRequest = req.url.includes('/auth/login');

  if (token && req.url.startsWith(environment.apiUrl) && !isLoginRequest) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(req).pipe(
    catchError((error) => {
      if (error.status === 401 && !isLoginRequest && !isHandling401)  {
        isHandling401 = true;
        localStorage.removeItem('tokenBsFarma');
        localStorage.removeItem('isLoggedBsFarma');

        toastService.showToastError('Sessão expirada. Faça login novamente.');

        if (router.url !== '/login') {
          router.navigate(['/login']);
        }

        setTimeout(() => isHandling401 = false, 2000);
      }

      return throwError(() => error);
    })
  );
};