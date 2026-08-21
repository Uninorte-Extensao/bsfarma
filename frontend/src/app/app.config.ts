import { APP_INITIALIZER, ApplicationConfig, DEFAULT_CURRENCY_CODE, LOCALE_ID, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, Router, withDisabledInitialNavigation } from '@angular/router';
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { ConfirmationService, MessageService } from 'primeng/api';
import { providePrimeNG } from 'primeng/config';

import { routes } from './app.routes';
import { AuthService } from './shared/services/auth.service';
import { BsFarmaTheme, BsFarmaTranslation } from './primeng.theme';
import { loadingInterceptor } from './core/loadingInterceptor';
import { authInterceptor } from './core/authInterceptor';
import { IS_MOBILE, IsMobileService } from './shared/services/is-mobile.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),

    // Segura a navegação até o APP_INITIALIZER terminar
    provideRouter(routes, withDisabledInitialNavigation()),

    provideAnimationsAsync(),
    provideHttpClient(withFetch(), withInterceptors([authInterceptor, loadingInterceptor])),

    providePrimeNG({
      ripple: true,
      theme: {
        preset: BsFarmaTheme,
        options: { prefix: 'p', cssLayer: false, darkModeSelector: '.dark' }
      },
      translation: BsFarmaTranslation
    }),
    { provide: LOCALE_ID, useValue: 'pt-BR' },
    { provide: DEFAULT_CURRENCY_CODE, useValue: 'BRL' },
    // { provide: HTTP_INTERCEPTORS, useClass: LoadingInterceptor, multi: true },
    MessageService,
    ConfirmationService,
    {
      provide: IS_MOBILE,
      useFactory: (s: IsMobileService) => s.isMobile,
      deps: [IsMobileService]
    },

    // Carrega o user antes de qualquer rota ser resolvida
    {
      provide: APP_INITIALIZER,
      useFactory: (auth: AuthService, router: Router) => async () => {
        if (localStorage.getItem('tokenBsFarma')) {
          await auth.loadUser();
        }
        console.log('[INIT] user carregado:', auth.user());
        console.log('[INIT] perfil:', auth.user()?.perfil);
        await router.initialNavigation();
        console.log('[INIT] navegação iniciada');
      },
      deps: [AuthService, Router], // ← faltava
      multi: true                  // ← faltava — esse era o erro
    },
  ]
};