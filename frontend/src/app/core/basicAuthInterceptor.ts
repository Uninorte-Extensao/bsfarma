import { Injectable } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
} from '@angular/common/http';

@Injectable()
export class BasicAuthInterceptor implements HttpInterceptor {

  private username = 'user';
  private password = '';

  intercept(req: HttpRequest<any>, next: HttpHandler) {

    if (req.url.includes('/auth/login')) {
      return next.handle(req);
    }

    const credenciais = btoa(`${this.username}:${this.password}`);

    const authReq = req.clone({
      setHeaders: {
        Authorization: `Basic ${credenciais}`
      }
    });

    return next.handle(authReq);
  }
}
