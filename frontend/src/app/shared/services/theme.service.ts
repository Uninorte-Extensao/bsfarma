import { Injectable, signal } from '@angular/core';

const STORAGE_KEY = 'bsfarma-theme';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  readonly isDark = signal(this.getInitialTheme());

  constructor() {
    this.applyTheme(this.isDark());
  }

  toggle(): void {
    this.setTheme(!this.isDark());
  }

  setTheme(isDark: boolean): void {
    this.isDark.set(isDark);
    this.applyTheme(isDark);
    localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light');
  }

  private applyTheme(isDark: boolean): void {
    document.documentElement.classList.toggle('dark', isDark);
  }

  private getInitialTheme(): boolean {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'dark') return true;
    if (stored === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
}
