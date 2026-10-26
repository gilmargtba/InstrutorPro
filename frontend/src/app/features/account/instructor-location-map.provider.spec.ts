import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { InstructorLocationMapProvider } from './instructor-location-map.provider';

describe('InstructorLocationMapProvider', () => {
  beforeEach(() => TestBed.configureTestingModule({
    providers: [provideHttpClient(), provideHttpClientTesting(), InstructorLocationMapProvider],
  }));

  it('uses the browser Google configuration without embedding a key in the page', () => {
    const provider = TestBed.inject(InstructorLocationMapProvider);
    const mountGoogle = spyOn<any>(provider, 'mountGoogle').and.returnValue(Promise.resolve());
    const host = document.createElement('div');
    provider.mount(host, () => undefined);
    TestBed.inject(HttpTestingController).expectOne('/map/browser-config/').flush({
      provider: 'google', api_key: 'restricted-browser-key', map_id: 'configured-map-id',
    });
    expect(mountGoogle).toHaveBeenCalledWith(jasmine.any(Number), 'restricted-browser-key', 'configured-map-id');
    expect(provider.source()).toBe('loading');
    provider.destroy();
  });

  it('falls back to Leaflet only when Google is not configured', () => {
    const provider = TestBed.inject(InstructorLocationMapProvider);
    const host = document.createElement('div');
    document.body.append(host);
    provider.mount(host, () => undefined);
    provider.setPoint(-18.01, -49.35);
    TestBed.inject(HttpTestingController).expectOne('/map/browser-config/').flush({ provider: 'maptiler' });
    expect(provider.source()).toBe('maptiler');
    expect(host.querySelector('.leaflet-container')).toBeNull();
    expect(host.querySelector('.leaflet-pane')).not.toBeNull();
    provider.clearPoint();
    provider.destroy();
    host.remove();
  });

  it('ignores a configuration response after the map is destroyed', () => {
    const provider = TestBed.inject(InstructorLocationMapProvider);
    const host = document.createElement('div');
    provider.mount(host, () => undefined);
    const request = TestBed.inject(HttpTestingController).expectOne('/map/browser-config/');
    provider.destroy();
    expect(request.cancelled).toBeTrue();
    expect(provider.source()).toBe('loading');
  });
});
