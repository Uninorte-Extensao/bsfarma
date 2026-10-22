import { inject } from '@angular/core';
import { CanActivateFn, ActivatedRouteSnapshot, Router } from '@angular/router';
import { AuthService } from '../shared/services/auth.service';
import { Permission } from './permissions.enum';
import { ToastService } from '../shared/services/toast.service';
import { HOME_BY_PROFILE } from './authGuard';

// Guard funcional assíncrono — aguarda o user ser carregado
export const permissionGuard: CanActivateFn = (route) => {
    const auth = inject(AuthService);
    const router = inject(Router);
    const toast = inject(ToastService);

    const requiredPermission = getPermissionFromRoute(route);
    console.log('[PERMISSION GUARD] rota:', route.routeConfig?.path, '| permission:', requiredPermission, '| perfil:', auth.user()?.perfil, '| tem permissão:', (requiredPermission ? auth.hasPermission(requiredPermission) : true));

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

