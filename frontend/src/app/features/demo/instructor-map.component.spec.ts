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
});
