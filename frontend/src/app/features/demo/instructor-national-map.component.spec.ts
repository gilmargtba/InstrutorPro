import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { InstructorSearchProvider } from '../../demo/instructor-search.provider';
import { InstructorNationalMapComponent } from './instructor-national-map.component';

describe('InstructorNationalMapComponent', () => {
  it('shows database counts and routes an active state to the local map', async () => {
    const navigate = jasmine.createSpy('navigate');
    const geoJson = {type:'FeatureCollection',features:[{type:'Feature',properties:{codarea:'43'},geometry:{type:'Polygon',coordinates:[[[-57,-34],[-49,-34],[-49,-27],[-57,-27],[-57,-34]]]}}]};
    spyOn(globalThis, 'fetch').and.resolveTo(new Response(JSON.stringify(geoJson), {status: 200}));
    await TestBed.configureTestingModule({
      imports: [InstructorNationalMapComponent],
      providers: [
        {provide: InstructorSearchProvider, useValue: {states: () => of({states: [{uf:'RS', count:3, search_location:'Porto Alegre'}]})}},
        {provide: Router, useValue: {navigate}},
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(InstructorNationalMapComponent);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('3 instrutores disponíveis');
    fixture.componentInstance.openState('RS');
    expect(navigate).toHaveBeenCalledWith(['/aluno/instrutores/mapa'], {
      queryParams: {uf:'RS', local:'Porto Alegre'},
    });
    fixture.destroy();
  });
});
