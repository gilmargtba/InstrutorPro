import { Injectable, signal } from '@angular/core';
import { Capacitor } from '@capacitor/core';
import { environment } from '../../environments/environment';

export function supportsPwaRegistration(): boolean {
  return environment.production && !Capacitor.isNativePlatform() &&
    typeof window !== 'undefined' && window.isSecureContext && 'serviceWorker' in navigator;
}

@Injectable({ providedIn: 'root' })
export class PwaUpdateService {
  readonly updateAvailable = signal(false);
  private registration?: ServiceWorkerRegistration;
  private initialized = false;
  private reloading = false;
  private activatingUpdate = false;

  init(): void {
    if (this.initialized || !supportsPwaRegistration()) return;
    this.initialized = true;
    const register = () => {
      navigator.serviceWorker.register('/sw.js', { scope: '/' }).then((registration) => {
        this.registration = registration;
        this.updateAvailable.set(Boolean(registration.waiting && navigator.serviceWorker.controller));
        registration.addEventListener('updatefound', () => {
          const installing = registration.installing;
          installing?.addEventListener('statechange', () => {
            if (installing.state === 'installed' && navigator.serviceWorker.controller) {
              this.updateAvailable.set(true);
            }
          });
        });
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          // Initial installation must not reload and discard an unfinished form.
          if (!this.activatingUpdate || this.reloading) return;
          this.reloading = true;
          window.location.reload();
        });
      }).catch(() => {
        // A failed service worker must never block a live, network-backed session.
      });
    };
    if (document.readyState === 'complete') register();
    else window.addEventListener('load', register, { once: true });
  }

  activateUpdate(): void {
    if (!this.registration?.waiting) return;
    this.activatingUpdate = true;
    this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
  }
}
