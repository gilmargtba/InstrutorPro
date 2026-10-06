import { ActivatedRoute, Router } from '@angular/router';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { InstructorSearchProvider } from '../../demo/instructor-search.provider';
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

  it('searches with coordinates only after explicit permission', () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    const api = TestBed.inject(InstructorSearchProvider);
    const search = spyOn(api, 'search').and.returnValue(of(result));
    fixture.detectChanges();
    fixture.componentInstance.useMyLocation();
    const success = getCurrentPosition.calls.mostRecent().args[0];
    success({coords: {latitude: -30.0346, longitude: -51.2177}});
    expect(search).toHaveBeenCalledWith(-30.0346, -51.2177, fixture.componentInstance.filters);
    expect(fixture.componentInstance.locationMessage).toContain('localização autorizada');
  });

  it('keeps manual search usable when permission is denied', () => {
    const fixture = TestBed.createComponent(InstructorMapComponent);
    fixture.detectChanges();
    fixture.componentInstance.useMyLocation();
    const denied = getCurrentPosition.calls.mostRecent().args[1];
    denied({code: 1});
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
});
