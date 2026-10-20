import { ActivatedRoute, Router } from '@angular/router';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { InstructorSearchProvider, SearchInstructor } from '../../demo/instructor-search.provider';
import { LeafletMapProvider } from '../../demo/map.provider';
import { InstructorMapComponent } from './instructor-map.component';

describe('InstructorMapComponent geolocation', () => {
  const result = {count: 0, results: []};
  let getCurrentPosition: jasmine.Spy;

  beforeEach(async () => {
    getCurrentPosition = jasmine.createSpy('getCurrentPosition');
    Object.defineProperty(navigator, 'geolocation', {
      configurable: true,
      value: {getCurrentPosition},
    });
    await TestBed.configureTestingModule({
      imports: [InstructorMapComponent],
      providers: [
        {provide: InstructorSearchProvider, useValue: {geocode: () => of({results: []}), search: () => of(result)}},
        {provide: LeafletMapProvider, useValue: {mount: () => undefined, focus: () => undefined, render: () => undefined, select: () => undefined, refresh: () => undefined, destroy: () => undefined}},
        {provide: ActivatedRoute, useValue: {snapshot: {queryParamMap: {get: () => null}}}},
        {provide: Router, useValue: {navigate: () => Promise.resolve(true)}},
      ],
    }).compileComponents();
  });

  it('defaults to a countrywide search without an implicit vehicle filter', () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    fixture.detectChanges();
    expect(fixture.componentInstance.anyDistance).toBeTrue();
    expect(fixture.componentInstance.filters.radius).toBeNull();
    expect(fixture.componentInstance.filters.vehicleAvailable).toBeNull();
  });

  it('searches with coordinates only after explicit permission', async () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    const api = TestBed.inject(InstructorSearchProvider);
    const search = spyOn(api, 'search').and.returnValue(of(result));
    fixture.detectChanges();
    fixture.componentInstance.useMyLocation();
    const success = getCurrentPosition.calls.mostRecent().args[0];
    success({coords: {latitude: -30.0346, longitude: -51.2177}});
    await fixture.whenStable();
    expect(search).toHaveBeenCalledWith(-30.0346, -51.2177, fixture.componentInstance.filters);
    expect(fixture.componentInstance.locationMessage).toContain('localização autorizada');
  });

  it('keeps manual search usable when permission is denied', async () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    fixture.detectChanges();
    fixture.componentInstance.useMyLocation();
    const denied = getCurrentPosition.calls.mostRecent().args[1];
    denied({code: 1});
    await fixture.whenStable();
    expect(fixture.componentInstance.locationMessage).toContain('busca manual');
    expect(getCurrentPosition.calls.mostRecent().args[2]).toEqual(jasmine.objectContaining({
      enableHighAccuracy: false,
      timeout: 10000,
    }));
  });

  it('passes resolved Brasília/DF and coordinates to the search', () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    const api = TestBed.inject(InstructorSearchProvider);
    spyOn(api, 'geocode').and.returnValue(of({provider:'MAPTILER',results:[{
      id:'place.5139760',label:'Brasília, Brasil',city:'Brasília',uf:'DF',
      uf_resolution:'RESOLVED',latitude:-15.79,longitude:-47.88,place_type:'place',bbox:null,
    }]}));
    const search = spyOn(api, 'search').and.returnValue(of(result));
    fixture.detectChanges();
    fixture.componentInstance.filters.location = 'Brasília';
    fixture.componentInstance.search();
    expect(search).toHaveBeenCalledWith(-15.79, -47.88, fixture.componentInstance.filters);
  });

  it('keeps the UF from the selected autocomplete suggestion', () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    const api = TestBed.inject(InstructorSearchProvider);
    const geocode = spyOn(api, 'geocode');
    const search = spyOn(api, 'search').and.returnValue(of(result));
    fixture.detectChanges();
    fixture.componentInstance.choose({
      id:'place.5139760',label:'Brasília, Brasil',city:'Brasília',uf:'DF',
      uf_resolution:'RESOLVED',latitude:-15.79,longitude:-47.88,place_type:'place',bbox:null,
    });
    expect(geocode).not.toHaveBeenCalled();
    expect(search).toHaveBeenCalledWith(-15.79, -47.88, fixture.componentInstance.filters);
  });

  it('requires explicit UF confirmation when the provider cannot resolve it', () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    const api = TestBed.inject(InstructorSearchProvider);
    spyOn(api, 'geocode').and.returnValue(of({provider:'MAPTILER',results:[{
      id:'place.1',label:'Localidade, Brasil',city:'Localidade',uf:'',
      uf_resolution:'NEEDS_CONFIRMATION',latitude:-15.79,longitude:-47.88,
      place_type:'place',bbox:null,
    }]}));
    const search = spyOn(api, 'search').and.returnValue(of(result));
    fixture.detectChanges();
    fixture.componentInstance.filters.location = 'Localidade';
    fixture.componentInstance.search();
    expect(search).not.toHaveBeenCalled();
    expect(fixture.componentInstance.pendingLocation).not.toBeNull();
    fixture.componentInstance.confirmedUf = 'DF';
    fixture.componentInstance.confirmLocationUf();
    expect(search).toHaveBeenCalledWith(-15.79, -47.88, fixture.componentInstance.filters);
  });

  it('allows an unrestricted distance without inventing an instructor category', () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    const component = fixture.componentInstance;
    component.setAnyDistance(true);
    expect(component.filters.radius).toBeNull();
    expect(component.anyDistance).toBeTrue();
    expect(component.filters.category).toBe('');
    component.setAnyDistance(false);
    expect(component.filters.radius).toBe(10);
  });

  it('does not turn an empty radius input into an unrestricted search', () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    const component = fixture.componentInstance;
    const search = spyOn(TestBed.inject(InstructorSearchProvider), 'search');
    component.filters.location = 'Goiatuba';
    component.setAnyDistance(false);
    component.filters.radius = null;
    component.search();
    expect(search).not.toHaveBeenCalled();
    expect(component.locationMessage).toContain('Informe um raio');
  });

  it('restores a custom radius from a search link', () => {
    const route = TestBed.inject(ActivatedRoute);
    spyOn(route.snapshot.queryParamMap, 'get').and.callFake(key => key === 'raio' ? '137' : null);
    const fixture = TestBed.createComponent(InstructorMapComponent);
    fixture.detectChanges();
    expect(fixture.componentInstance.filters.radius).toBe(137);
    expect(fixture.componentInstance.anyDistance).toBeFalse();
  });

  it('restores category A from a search link', () => {
    const route = TestBed.inject(ActivatedRoute);
    spyOn(route.snapshot.queryParamMap, 'get').and.callFake(key => key === 'categoria' ? 'A' : null);
    const fixture = TestBed.createComponent(InstructorMapComponent);
    fixture.detectChanges();
    expect(fixture.componentInstance.filters.category).toBe('A');
    expect(fixture.componentInstance.filters.radius).toBeNull();
  });

  it('restores unlimited distance from a search link', () => {
    const route = TestBed.inject(ActivatedRoute);
    spyOn(route.snapshot.queryParamMap, 'get').and.callFake(key => key === 'raio' ? 'todos' : null);
    const fixture = TestBed.createComponent(InstructorMapComponent);
    fixture.detectChanges();
    expect(fixture.componentInstance.filters.radius).toBeNull();
    expect(fixture.componentInstance.anyDistance).toBeTrue();
  });

  it('opens a clicked city with an explicit city and UF search', () => {
    const route = TestBed.inject(ActivatedRoute);
    spyOn(route.snapshot.queryParamMap, 'get').and.callFake(key => ({
      local: 'Goiatuba, GO', cidade: 'Goiatuba', uf: 'GO',
    })[key as 'local' | 'cidade' | 'uf'] ?? null);
    const api = TestBed.inject(InstructorSearchProvider);
    spyOn(api, 'geocode').and.returnValue(of({provider: 'MAPTILER', results: [{
      id: 'place.1', label: 'Goiatuba, Goiás, Brasil', city: 'Goiatuba', uf: 'GO',
      uf_resolution: 'RESOLVED', latitude: -18.01, longitude: -49.37,
      place_type: 'place', bbox: null,
    }]}));
    const search = spyOn(api, 'search').and.returnValue(of(result));
    const fixture = TestBed.createComponent(InstructorMapComponent);
    fixture.detectChanges();
    expect(search).toHaveBeenCalledWith(-18.01, -49.37, fixture.componentInstance.filters, 'GO', 'Goiatuba');
    fixture.componentInstance.filters.location = 'Brasília';
    fixture.componentInstance.search();
    expect(search).toHaveBeenCalledWith(-18.01, -49.37, fixture.componentInstance.filters);
  });

  it('does not widen a clicked city search when geocoding resolves another UF', () => {
    const route = TestBed.inject(ActivatedRoute);
    spyOn(route.snapshot.queryParamMap, 'get').and.callFake(key => ({
      local: 'Goiatuba, GO', cidade: 'Goiatuba', uf: 'GO',
    })[key as 'local' | 'cidade' | 'uf'] ?? null);
    const api = TestBed.inject(InstructorSearchProvider);
    spyOn(api, 'geocode').and.returnValue(of({provider: 'MAPTILER', results: [{
      id: 'place.2', label: 'Goiatuba, MG', city: 'Goiatuba', uf: 'MG',
      uf_resolution: 'RESOLVED', latitude: -18, longitude: -49,
      place_type: 'place', bbox: null,
    }]}));
    const search = spyOn(api, 'search').and.returnValue(of(result));
    const fixture = TestBed.createComponent(InstructorMapComponent);
    fixture.detectChanges();
    expect(search).not.toHaveBeenCalled();
    expect(fixture.componentInstance.error).toBeTrue();
  });

  it('keeps the map unobstructed after search and opens the selected marker details', () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    const component = fixture.componentInstance;
    const api = TestBed.inject(InstructorSearchProvider);
    const instructor = (id: string, display_name: string): SearchInstructor => ({
      id, display_name, latitude: -18.01, longitude: -49.37, distance_km: 1,
      categories: ['B'], offer_category: 'B', transmission: 'MANUAL',
      vehicle_available: true, price_amount: 90, price_from: false,
      duration_minutes: 60, vehicle: null, availability_summary: '', demo: false,
      profile_photo_url: null, verified_claims: [], city: 'Goiatuba', uf: 'GO',
    });
    const first = instructor('first', 'Primeiro');
    const second = instructor('second', 'Segundo');
    spyOn(api, 'geocode').and.returnValue(of({provider: 'MAPTILER', results: [{
      id: 'place.1', label: 'Goiatuba, GO', city: 'Goiatuba', uf: 'GO',
      uf_resolution: 'RESOLVED', latitude: -18.01, longitude: -49.37,
      place_type: 'place', bbox: null,
    }]}));
    spyOn(api, 'search').and.returnValue(of({count: 2, results: [first, second]}));
    fixture.detectChanges();
    component.filters.location = 'Goiatuba';
    component.search();
    expect(component.drawerOpen).toBeFalse();
    expect(component.visibleItems).toEqual([first, second]);

    component.select(second);
    expect(component.drawerOpen).toBeTrue();
    expect(component.visibleItems).toEqual([second]);
    component.openResultList();
    expect(component.visibleItems).toEqual([first, second]);
  });
});
