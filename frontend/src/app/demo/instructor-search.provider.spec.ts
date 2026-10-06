import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { InstructorSearchProvider, SearchFilters } from './instructor-search.provider';

describe('InstructorSearchProvider radius', () => {
  beforeEach(() => TestBed.configureTestingModule({
    providers: [provideHttpClient(), provideHttpClientTesting()],
  }));

  const filters: SearchFilters = {
    location: 'Goiatuba', radius: null, category: 'B', transmission: '',
    vehicleAvailable: true, maxPrice: null, ordering: 'distance',
  };

  it('omits radius and state for a countrywide search', () => {
    TestBed.inject(InstructorSearchProvider).search(-18, -49, filters).subscribe();
    const request = TestBed.inject(HttpTestingController).expectOne(request =>
      request.url === '/instructors/search/');
    expect(request.request.params.has('radius_km')).toBeFalse();
    expect(request.request.params.has('uf')).toBeFalse();
    expect(request.request.params.get('category')).toBe('B');
    request.flush({count: 0, results: []});
  });

  it('sends any valid chosen radius', () => {
    TestBed.inject(InstructorSearchProvider).search(-18, -49, {...filters, radius: 137}).subscribe();
    const request = TestBed.inject(HttpTestingController).expectOne(request =>
      request.url === '/instructors/search/');
    expect(request.request.params.get('radius_km')).toBe('137');
    request.flush({count: 0, results: []});
  });
});
