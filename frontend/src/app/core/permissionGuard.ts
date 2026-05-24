import { inject } from '@angular/core';
import { CanActivateFn, ActivatedRouteSnapshot, Router } from '@angular/router';
import { AuthService } from '../shared/services/auth.service';
import { toObservable } from '@angular/core/rxjs-interop';
import { filter, firstValueFrom, timeout, catchError } from 'rxjs';
import { of } from 'rxjs';
import { Permission } from './permissions.enum';
import { ToastService } from '../shared/services/toast.service';
import { HOME_BY_PROFILE } from './authGuard';

// Guard funcional assíncrono — aguarda o user ser carregado
export const permissionGuard: CanActivateFn = (route) => {
    const auth = inject(AuthService);
    const router = inject(Router);
    const toast = inject(ToastService);

    const requiredPermission = getPermissionFromRoute(route);
    console.log('[PERMISSION GUARD] rota:', route.routeConfig?.path, '| permission:', requiredPermission, '| perfil:', auth.user()?.perfil, '| tem permissão:', auth.hasPermission(requiredPermission as any));

    if (!requiredPermission) return true;

    if (!auth.hasPermission(requiredPermission)) {
        toast.showToastError('Você não tem permissão para acessar este módulo.');
        const fallback = HOME_BY_PROFILE[auth.user()?.perfil ?? ''] ?? '/catalog';
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
        atendente: '/catalog',
        farmaceutico: '/catalog',
        gestor: '/report'
    };

    return fallbackByProfile[user?.perfil ?? ''] ?? '/catalog';
}