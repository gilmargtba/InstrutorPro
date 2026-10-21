import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Subscription, timeout } from 'rxjs';

import { apiUrl } from '../core/api-url';
import { environment } from '../../environments/environment';
import { GoogleMapProvider } from './google-map.provider';
import { LeafletMapProvider, MapProvider } from './map.provider';
import { SearchInstructor } from './instructor-search.provider';

interface BrowserMapConfig {
  provider: 'google' | 'maptiler';
  api_key?: string;
  map_id?: string;
}

@Injectable({ providedIn: 'root' })
export class SearchMapProvider implements MapProvider {
  private readonly http = inject(HttpClient);
  private readonly leaflet = inject(LeafletMapProvider);
  private readonly google = inject(GoogleMapProvider);
  private active?: MapProvider;
  private configRequest?: Subscription;
  private host?: HTMLElement;
  private onSelect: (id: string) => void = () => undefined;
  private generation = 0;
  private point?: { latitude: number; longitude: number; zoom: number };
  private items: SearchInstructor[] = [];
  private selectedId: string | null = null;
  readonly source = signal<'google' | 'maptiler'>('maptiler');

  mount(element: HTMLElement, onSelect: (id: string) => void): void {
    this.destroy();
    const generation = this.generation;
    this.host = element;
    this.onSelect = onSelect;
    if (environment.mobile) { this.activateLeaflet(generation); return; }
    this.configRequest = this.http.get<BrowserMapConfig>(apiUrl('/map/browser-config/'))
      .pipe(timeout(3000)).subscribe({
        next: config => {
          if (generation !== this.generation) return;
          if (config.provider !== 'google' || !config.api_key || !config.map_id) {
            this.activateLeaflet(generation);
            return;
          }
          void this.google.mountReady(element, onSelect, config.api_key, config.map_id)
            .then(() => {
              if (generation !== this.generation) return;
              this.active = this.google;
              this.source.set('google');
              this.replay();
            })
            .catch(() => {
              if (generation !== this.generation) return;
              this.google.destroy();
              this.activateLeaflet(generation);
            });
        },
        error: () => this.activateLeaflet(generation),
      });
  }

  focus(latitude: number, longitude: number, zoom = 12): void {
    this.point = { latitude, longitude, zoom };
    this.active?.focus(latitude, longitude, zoom);
  }

  render(items: SearchInstructor[], selectedId: string | null): void {
    this.items = items;
    this.selectedId = selectedId;
    this.active?.render(items, selectedId);
  }

  select(id: string): void {
    this.selectedId = id;
    this.active?.select(id);
  }

  refresh(): void { this.active?.refresh(); }

  destroy(): void {
    this.generation++;
    this.configRequest?.unsubscribe();
    this.configRequest = undefined;
    this.active?.destroy();
    if (this.active !== this.google) this.google.destroy();
    this.active = undefined;
    this.host = undefined;
    this.point = undefined;
    this.items = [];
    this.selectedId = null;
    this.source.set('maptiler');
  }

  private activateLeaflet(generation: number): void {
    if (generation !== this.generation || !this.host) return;
    this.leaflet.mount(this.host, this.onSelect);
    this.active = this.leaflet;
    this.source.set('maptiler');
    this.replay();
  }

  private replay(): void {
    if (this.point) this.active?.focus(this.point.latitude, this.point.longitude, this.point.zoom);
    this.active?.render(this.items, this.selectedId);
  }
}
