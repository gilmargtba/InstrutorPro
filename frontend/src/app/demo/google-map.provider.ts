import { Injectable } from '@angular/core';
import { publicMediaUrl } from '../core/api-url';
import { loadGoogleMaps } from './google-maps-loader';
import { MapProvider } from './map.provider';
import { SearchInstructor } from './instructor-search.provider';

@Injectable({ providedIn: 'root' })
export class GoogleMapProvider implements MapProvider {
  private map?: google.maps.Map;
  private host?: HTMLElement;
  private markerClass?: typeof google.maps.marker.AdvancedMarkerElement;
  private markers = new Map<string, google.maps.marker.AdvancedMarkerElement>();
  private onSelect: (id: string) => void = () => undefined;
  private generation = 0;

  async mountReady(element: HTMLElement, onSelect: (id: string) => void, key: string, mapId: string): Promise<void> {
    this.destroy();
    const generation = this.generation;
    this.host = element;
    this.onSelect = onSelect;
    const [{ Map }, { AdvancedMarkerElement }] = await loadGoogleMaps(key, mapId);
    if (generation !== this.generation) return;
    this.markerClass = AdvancedMarkerElement;
    element.replaceChildren();
    this.map = new Map(element, {
      center: { lat: -14.2, lng: -51.9 }, zoom: 4, mapId,
      clickableIcons: false, mapTypeControl: false, streetViewControl: false,
    });
  }

  mount(_element: HTMLElement, _onSelect: (id: string) => void): void {
    throw new Error('Google Maps requires browser configuration before mounting.');
  }

  focus(latitude: number, longitude: number, zoom = 12): void {
    this.map?.setCenter({ lat: latitude, lng: longitude });
    this.map?.setZoom(zoom);
  }

  render(items: SearchInstructor[], selectedId: string | null): void {
    if (!this.map || !this.markerClass) return;
    for (const marker of this.markers.values()) marker.map = null;
    this.markers.clear();
    const bounds = new google.maps.LatLngBounds();
    for (const item of items) {
      const content = document.createElement('span');
      content.className = 'google-instructor-marker';
      const photo = publicMediaUrl(item.profile_photo_url);
      if (photo) {
        const image = document.createElement('img');
        image.src = photo;
        image.alt = '';
        image.onerror = () => { image.remove(); content.textContent = this.initials(item.display_name); };
        content.appendChild(image);
      } else {
        content.textContent = this.initials(item.display_name);
      }
      const position = { lat: item.latitude, lng: item.longitude };
      const marker = new this.markerClass({ map: this.map, position, title: item.display_name, content });
      marker.addListener('click', () => this.onSelect(item.id));
      this.markers.set(item.id, marker);
      bounds.extend(position);
    }
    if (items.length === 1) this.focus(items[0].latitude, items[0].longitude, 13);
    else if (items.length > 1) {
      this.map.fitBounds(bounds, 60);
      google.maps.event.addListenerOnce(this.map, 'idle', () => {
        if (this.map && (this.map.getZoom() ?? 0) > 14) this.map.setZoom(14);
      });
    }
    if (selectedId) this.select(selectedId);
  }

  select(id: string): void {
    for (const [markerId, marker] of this.markers) {
      (marker.content as HTMLElement | null)?.classList.toggle('selected', markerId === id);
    }
    const marker = this.markers.get(id);
    const position = marker?.position;
    if (position) {
      this.map?.panTo(position);
      if ((this.map?.getZoom() ?? 0) < 15) this.map?.setZoom(15);
    }
  }

  refresh(): void {
    const center = this.map?.getCenter();
    if (center) this.map?.setCenter(center);
  }

  destroy(): void {
    this.generation++;
    for (const marker of this.markers.values()) marker.map = null;
    this.markers.clear();
    this.map = undefined;
    this.markerClass = undefined;
    this.host?.replaceChildren();
    this.host = undefined;
  }

  private initials(name: string): string {
    return name.split(' ').slice(0, 2)
      .map(part => part.match(/[\p{L}\p{N}]/u)?.[0] ?? '').join('').toUpperCase() || 'IP';
  }
}
