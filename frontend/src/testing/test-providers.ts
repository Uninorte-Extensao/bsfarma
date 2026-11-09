import { EnvironmentProviders, Provider, signal } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { ConfirmationService, MessageService } from 'primeng/api';
import { providePrimeNG } from 'primeng/config';
import { IS_MOBILE } from '../app/shared/services/is-mobile.service';

// Providers comuns aos specs: HTTP simulado (nenhuma requisição sai de fato),
// router vazio e os serviços globais que o app.config registra.
export const testProviders: (Provider | EnvironmentProviders)[] = [
  provideHttpClient(),
  provideHttpClientTesting(),
  provideRouter([]),
  provideAnimationsAsync('noop'),
  providePrimeNG(),
  MessageService,
  ConfirmationService,
  { provide: IS_MOBILE, useValue: signal(false) },
];
