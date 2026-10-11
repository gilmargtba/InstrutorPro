import { Injectable } from '@angular/core';
import { Capacitor } from '@capacitor/core';
import { AppLauncher } from '@capacitor/app-launcher';
import { Browser } from '@capacitor/browser';

@Injectable({ providedIn: 'root' })
export class WhatsappLinkService {
  async open(destination: string): Promise<void> {
    const url = new URL(destination);
    if (url.protocol !== 'https:' || url.hostname !== 'wa.me' || !/^\/\d{10,15}$/.test(url.pathname)) {
      throw new Error('Destino de contato inválido');
    }
    if (!Capacitor.isNativePlatform()) { window.location.assign(url.toString()); return; }
    const nativeUrl = `whatsapp://send?phone=${url.pathname.slice(1)}&text=${encodeURIComponent(url.searchParams.get('text') ?? '')}`;
    try {
      if ((await AppLauncher.canOpenUrl({ url: nativeUrl })).value) {
        await AppLauncher.openUrl({ url: nativeUrl });
        return;
      }
    } catch { /* WhatsApp absent: use the verified HTTPS destination. */ }
    await Browser.open({ url: url.toString() });
  }
}
