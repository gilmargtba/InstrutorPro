import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { apiInterceptor } from '../core/api.interceptor';
import { GoogleMapProvider } from './google-map.provider';
import { LeafletMapProvider } from './map.provider';
import { SearchMapProvider } from './search-map.provider';

describe('SearchMapProvider', () => {
  let map: SearchMapProvider;
  let http: HttpTestingController;
  let leaflet: jasmine.SpyObj<LeafletMapProvider>;
  let google: jasmine.SpyObj<GoogleMapProvider>;
  let host: HTMLElement;

  beforeEach(() => {
    leaflet = jasmine.createSpyObj('LeafletMapProvider', ['mount', 'focus', 'render', 'select', 'refresh', 'destroy']);
    google = jasmine.createSpyObj('GoogleMapProvider', ['mountReady', 'focus', 'render', 'select', 'refresh', 'destroy']);
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([apiInterceptor])), provideHttpClientTesting(),
        { provide: LeafletMapProvider, useValue: leaflet },
        { provide: GoogleMapProvider, useValue: google },
      ],
    });
    map = TestBed.inject(SearchMapProvider);
    http = TestBed.inject(HttpTestingController);
    host = document.createElement('div');
  });

  afterEach(() => { map.destroy(); http.verify(); });

  it('keeps Leaflet when Google Maps is not enabled and replays the queued center', () => {
    const onSelect = jasmine.createSpy('onSelect');
    map.mount(host, onSelect);
    map.focus(-18, -49, 11);
    http.expectOne('/api/v1/map/browser-config/').flush({ provider: 'maptiler' });
    expect(leaflet.mount).toHaveBeenCalledWith(host, onSelect);
    expect(leaflet.focus).toHaveBeenCalledWith(-18, -49, 11);
    expect(google.mountReady).not.toHaveBeenCalled();
    expect(map.source()).toBe('maptiler');
  });

  it('uses Google only with an enabled key and map ID', async () => {
    google.mountReady.and.resolveTo();
    map.mount(host, () => undefined);
    http.expectOne('/api/v1/map/browser-config/').flush({
      provider: 'google', api_key: 'restricted-browser-key', map_id: 'approved-map-id',
    });
    await Promise.resolve();
    expect(google.mountReady).toHaveBeenCalledWith(host, jasmine.any(Function), 'restricted-browser-key', 'approved-map-id');
    expect(map.source()).toBe('google');
    expect(leaflet.mount).not.toHaveBeenCalled();
  });

  it('falls back to Leaflet if Google fails to load', async () => {
    google.mountReady.and.rejectWith(new Error('unavailable'));
    map.mount(host, () => undefined);
    http.expectOne('/api/v1/map/browser-config/').flush({
      provider: 'google', api_key: 'restricted-browser-key', map_id: 'approved-map-id',
    });
    await Promise.resolve();
    await Promise.resolve();
    expect(leaflet.mount).toHaveBeenCalled();
    expect(map.source()).toBe('maptiler');
  });

  it('falls back to Leaflet when browser configuration is unavailable', () => {
    map.mount(host, () => undefined);
    http.expectOne('/api/v1/map/browser-config/').flush({}, { status: 503, statusText: 'Unavailable' });
    expect(leaflet.mount).toHaveBeenCalled();
  });

  it('does not destroy a newer Google map when an older load finishes late', async () => {
    let finishFirst!: () => void;
    let finishSecond!: () => void;
    google.mountReady.and.returnValues(
      new Promise<void>(resolve => { finishFirst = resolve; }),
      new Promise<void>(resolve => { finishSecond = resolve; }),
    );
    const config = { provider: 'google', api_key: 'restricted-browser-key', map_id: 'approved-map-id' };
    map.mount(host, () => undefined);
    http.expectOne('/api/v1/map/browser-config/').flush(config);
    map.mount(host, () => undefined);
    http.expectOne('/api/v1/map/browser-config/').flush(config);
    finishSecond();
    await Promise.resolve();
    const destroyedBeforeStaleLoad = google.destroy.calls.count();
    finishFirst();
    await Promise.resolve();
    expect(google.destroy.calls.count()).toBe(destroyedBeforeStaleLoad);
    expect(map.source()).toBe('google');
  });
});
