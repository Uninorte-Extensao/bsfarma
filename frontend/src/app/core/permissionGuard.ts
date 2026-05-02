import { inject } from '@angular/core';
import { CanActivateFn, ActivatedRouteSnapshot, Router } from '@angular/router';
import { AuthService } from '../shared/services/auth.service';
import { toObservable } from '@angular/core/rxjs-interop';
import { filter, firstValueFrom, timeout, catchError } from 'rxjs';
import { of } from 'rxjs';
import { Permission } from './permissions.enum';
import { ToastService } from '../shared/services/toast.service';

// Guard funcional assíncrono — aguarda o user ser carregado
export const permissionGuard: CanActivateFn = async (route) => {
    const authService = inject(AuthService);
    const router = inject(Router);
    const toastService = inject(ToastService);

    // Se o user ainda não foi carregado, aguarda (com timeout de segurança)
    if (!authService.user()) {
        const loaded = await firstValueFrom(
            toObservable(authService.user).pipe(
                filter(user => user !== null),
                timeout(5000), // evita travar infinitamente
                catchError(() => of(null))
            )
        );

        // Se mesmo após aguardar não carregou, redireciona pro auth
        if (!loaded) {
            router.navigate(['/auth']);
            return false;
        }
    }

    const permission = getPermissionFromRoute(route);

    // Rota sem restrição de permissão — libera
    if (!permission) return true;

    if (!authService.hasPermission(permission)) {
        toastService.showToastError('Você não tem permissão para acessar este módulo.')
        const fallback = getFallbackRoute(authService);
        return router.parseUrl(fallback);
    }

    return true;
};

// Sobe na árvore de rotas até achar um data.permission definido
function getPermissionFromRoute(route: ActivatedRouteSnapshot): Permission | null {
    let current: ActivatedRouteSnapshot | null = route;
    while (current) {
        if (current.data?.['permission']) return current.data['permission'];
        current = current.parent;
    }
    return null;
}

function getFallbackRoute(authService: AuthService): string {
    const user = authService.user();

    // Cada perfil cai na primeira rota que tem permissão
    const fallbackByProfile: Record<string, string> = {
        atendente: '/batch',
        farmaceutico: '/catalog',
        gestor: '/catalog'
    };

    return fallbackByProfile[user?.perfil ?? ''] ?? '/catalog';
}