import { ApplicationConfig, DEFAULT_CURRENCY_CODE, LOCALE_ID, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { HTTP_INTERCEPTORS, provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { IS_MOBILE, IsMobileService } from './shared/services/is-mobile.service';
import { MessageService } from 'primeng/api';
import { BsFarmaTheme, BsFarmaTranslation } from './primeng.theme';
import { LoadingInterceptor } from './core/loadingInterceptor';
import { providePrimeNG } from 'primeng/config';
import { authInterceptor } from './core/authInterceptor';

export const appConfig: ApplicationConfig = {
  // providers: [
  //   provideZoneChangeDetection({ eventCoalescing: true }), 
  //   provideRouter(routes),

  //   // se der erro futuramente, remover withFetch
  //   provideHttpClient(withFetch()),
  //   provideAnimationsAsync()
  // ]

   providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideAnimationsAsync(),
    provideHttpClient(withFetch(), withInterceptors([authInterceptor])),
    providePrimeNG({
      ripple: true,
      theme: {
        preset: BsFarmaTheme,
        options: {
          prefix: 'p',
          cssLayer: false,
          darkModeSelector: 'off',
        }
      },
      translation: BsFarmaTranslation
    }),
    {
      provide: LOCALE_ID,
      useValue: 'pt-BR'
    },
    {
      provide: DEFAULT_CURRENCY_CODE,
      useValue: 'BRL'
    },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: LoadingInterceptor,
      multi: true
    },
    MessageService,
    {
      provide: IS_MOBILE,
      useFactory: (mobileService: IsMobileService) => {
        return mobileService.isMobile;
      },
      deps: [IsMobileService]
    }
  ]
};
