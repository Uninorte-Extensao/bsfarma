import { Injectable } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent
} from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class BasicAuthInterceptor implements HttpInterceptor {

  private username = 'user'; 
  private password = ''; 

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const credenciais = btoa(`${this.username}:${this.password}`);

    const authReq = req.clone({
      setHeaders: {
        Authorization: `Basic ${credenciais}`
      }
    });

    return next.handle(authReq);
  }
}
