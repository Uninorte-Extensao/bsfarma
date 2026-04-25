import { inject, Injectable } from '@angular/core';
import {
    HttpInterceptor,
    HttpRequest,
    HttpHandler,
    HttpEvent
} from '@angular/common/http';
import { Observable } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { LoadingService } from '../shared/services/loading.service';

@Injectable()

export class LoadingInterceptor implements HttpInterceptor {
    private loadingService = inject(LoadingService);

    intercept(
        req: HttpRequest<any>,
        next: HttpHandler
    ): Observable<HttpEvent<any>> {
        this.loadingService.show();

        return next.handle(req).pipe(
            finalize(() => {
                this.loadingService.hide()
            })
        )
    }
}