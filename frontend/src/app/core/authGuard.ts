import { inject } from '@angular/core';
import { CanActivateFn, ActivatedRouteSnapshot, Router } from '@angular/router';
import { AuthService } from '../shared/services/auth.service';
import { ToastService } from '../shared/services/toast.service';
import { Permission } from './permissions.enum';

// Mapa de home por perfil — fonte única da verdade
export const HOME_BY_PROFILE: Record<string, string> = {
    atendente:    '/catalog',
    farmaceutico: '/catalog',
    gestor:       '/report'
};

// Verifica se está autenticado
export const authGuard: CanActivateFn = () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    if (!auth.isLoggedIn()) {
        router.navigate(['/auth']);
        return false;
    }

    return true;
};

// Redireciona para a home do perfil (usado na rota raiz '')
// Síncrono pois o APP_INITIALIZER já garantiu que o user está carregado
// homeRedirectGuard em auth.guards.ts
export const homeRedirectGuard: CanActivateFn = () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    console.log('[HOME GUARD] rodando, perfil:', auth.user()?.perfil);
    const home = HOME_BY_PROFILE[auth.user()?.perfil ?? ''] ?? '/catalog';
    console.log('[HOME GUARD] redirecionando para:', home);
    return router.parseUrl(home);
};

// Verifica permissão da rota — síncrono pelo mesmo motivo
export const permissionGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
    const auth = inject(AuthService);
    const router = inject(Router);
    const toast = inject(ToastService);

    const permission = getPermission(route);
    if (!permission) return true;

    if (!auth.hasPermission(permission)) {
        toast.showToastError('Você não tem permissão para acessar este módulo.');
        const fallback = HOME_BY_PROFILE[auth.user()?.perfil ?? ''] ?? '/catalog';
        return router.parseUrl(fallback);
    }

    return true;
};

function getPermission(route: ActivatedRouteSnapshot): Permission | null {
    let current: ActivatedRouteSnapshot | null = route;
    while (current) {
        if (current.data?.['permission']) return current.data['permission'];
        current = current.parent;
    }
    return null;
}