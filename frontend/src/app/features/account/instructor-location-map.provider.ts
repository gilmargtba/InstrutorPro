import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import L from 'leaflet';
import { Subscription, timeout } from 'rxjs';

import { loadGoogleMaps } from '../../demo/google-maps-loader';
import { environment } from '../../../environments/environment';

interface BrowserMapConfig {
  provider: 'google' | 'maptiler';
  api_key?: string;
  map_id?: string;
}

@Injectable({ providedIn: 'root' })
export class InstructorLocationMapProvider {
  private readonly http = inject(HttpClient);
  private host?: HTMLElement;
  private leaflet?: L.Map;
  private leafletMarker?: L.CircleMarker;
  private googleMap?: google.maps.Map;
  private googleMarker?: google.maps.marker.AdvancedMarkerElement;
  private googleMarkerClass?: typeof google.maps.marker.AdvancedMarkerElement;
  private configRequest?: Subscription;
  private onSelect: (point: L.LatLng) => void = () => undefined;
  private point?: L.LatLng;
  private generation = 0;
  readonly source = signal<'loading' | 'google' | 'maptiler'>('loading');

  mount(element: HTMLElement, onSelect: (point: L.LatLng) => void): void {
    this.destroy();
    const generation = this.generation;
    this.host = element;
    this.onSelect = onSelect;
    if (environment.mobile) { this.activateLeaflet(generation); return; }
    this.configRequest = this.http.get<BrowserMapConfig>('/map/browser-config/')
      .pipe(timeout(3000)).subscribe({
        next: config => {
          if (generation !== this.generation) return;
          if (config.provider !== 'google' || !config.api_key || !config.map_id) {
            this.activateLeaflet(generation);
            return;
          }
          void this.mountGoogle(generation, config.api_key, config.map_id)
            .catch(() => this.activateLeaflet(generation));
        },
        error: () => this.activateLeaflet(generation),
      });
  }

  setPoint(latitude: number, longitude: number): void {
    this.point = L.latLng(latitude, longitude);
    this.renderPoint();
  }

  clearPoint(): void {
    this.point = undefined;
    if (this.leaflet && this.leafletMarker) this.leaflet.removeLayer(this.leafletMarker);
    this.leafletMarker = undefined;
    if (this.googleMarker) this.googleMarker.map = null;
    this.googleMarker = undefined;
  }

  destroy(): void {
    this.generation++;
    this.configRequest?.unsubscribe();
    this.configRequest = undefined;
    this.leaflet?.remove();
    this.leaflet = undefined;
    this.leafletMarker = undefined;
    if (this.googleMarker) this.googleMarker.map = null;
    this.googleMarker = undefined;
    if (this.googleMap) google.maps.event.clearInstanceListeners(this.googleMap);
    this.googleMap = undefined;
    this.googleMarkerClass = undefined;
    this.host?.replaceChildren();
    this.host = undefined;
    this.point = undefined;
    this.source.set('loading');
  }

  private async mountGoogle(generation: number, key: string, mapId: string): Promise<void> {
    const [{ Map }, { AdvancedMarkerElement }] = await loadGoogleMaps(key, mapId);
    if (generation !== this.generation || !this.host) return;
    this.googleMarkerClass = AdvancedMarkerElement;
    this.host.replaceChildren();
    this.googleMap = new Map(this.host, {
      center: { lat: -14.2, lng: -51.9 }, zoom: 4, mapId,
      clickableIcons: false, mapTypeControl: false, streetViewControl: false,
    });
    this.googleMap.addListener('click', (event: google.maps.MapMouseEvent) => {
      if (event.latLng) this.onSelect(L.latLng(event.latLng.lat(), event.latLng.lng()));
    });
    this.source.set('google');
    this.renderPoint();
  }

  private activateLeaflet(generation: number): void {
    if (generation !== this.generation || !this.host) return;
    this.leaflet = L.map(this.host, { zoomControl: true }).setView([-14.2, -51.9], 4);
    L.tileLayer('/api/v1/map/tiles/{z}/{x}/{y}.png', {
      attribution: '&copy; MapTiler &copy; OpenStreetMap contributors', maxZoom: 19,
    }).addTo(this.leaflet);
    this.leaflet.on('click', event => this.onSelect(event.latlng));
    this.source.set('maptiler');
    this.renderPoint();
    setTimeout(() => this.leaflet?.invalidateSize(), 0);
  }

  private renderPoint(): void {
    if (!this.point) return;
    if (this.leaflet) {
      if (this.leafletMarker) this.leafletMarker.setLatLng(this.point);
      else this.leafletMarker = L.circleMarker(this.point, {
        radius: 11, color: '#fff', weight: 3, fillColor: '#f97316', fillOpacity: 1,
        className: 'public-location-pin',
      }).addTo(this.leaflet);
      this.leaflet.setView(this.point, 13);
    }
    if (this.googleMap && this.googleMarkerClass) {
      const position = { lat: this.point.lat, lng: this.point.lng };
      if (this.googleMarker) this.googleMarker.position = position;
      else {
        const pin = document.createElement('span');
        pin.setAttribute('aria-label', 'Área pública aproximada de atendimento');
        pin.style.cssText = 'display:block;width:22px;height:22px;border:3px solid #fff;border-radius:50%;background:#f97316;box-shadow:0 2px 8px #0006';
        this.googleMarker = new this.googleMarkerClass({ map: this.googleMap, position, content: pin });
      }
      this.googleMap.setCenter(position);
      this.googleMap.setZoom(13);
    }
  }
}
