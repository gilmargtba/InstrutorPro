import { Injectable } from '@angular/core';
import { Capacitor } from '@capacitor/core';
import { Geolocation } from '@capacitor/geolocation';

export interface SearchPosition { latitude: number; longitude: number }

@Injectable({ providedIn: 'root' })
export class StudentLocationService {
  private pending: SearchPosition | null = null;

  async currentPosition(): Promise<SearchPosition> {
    if (Capacitor.isNativePlatform()) {
      const result = await Geolocation.getCurrentPosition({
        enableHighAccuracy: false, timeout: 10000, maximumAge: 300000,
      });
      return { latitude: result.coords.latitude, longitude: result.coords.longitude };
    }
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) { reject(new Error('Geolocalização indisponível')); return; }
      navigator.geolocation.getCurrentPosition(
        ({ coords }) => resolve({ latitude: coords.latitude, longitude: coords.longitude }),
        reject,
        { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
      );
    });
  }

  handOff(position: SearchPosition): void { this.pending = position; }
  takePending(): SearchPosition | null {
    const position = this.pending;
    this.pending = null;
    return position;
  }
}
