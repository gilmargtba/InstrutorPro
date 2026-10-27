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
        {provide: InstructorSearchProvider, useValue: {states: () => of({states: [{uf:'RS', count:3, search_location:'Porto Alegre', cities:[
          {name:'Porto Alegre',count:2,instructors:[{id:'one',display_name:'Ana Silva',latitude:-30.03,longitude:-51.21},{id:'two',display_name:'Bia Souza',latitude:-30.04,longitude:-51.22}]},
          {name:'Caxias do Sul',count:1,instructors:[{id:'three',display_name:'Carlos Lima',latitude:-29.17,longitude:-51.18}]},
        ]}]})}},
        {provide: Router, useValue: {navigate}},
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(InstructorNationalMapComponent);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('3 instrutores disponíveis');
    expect(fixture.nativeElement.textContent).toContain('Carlos Lima');
    const cityButtons = [...fixture.nativeElement.querySelectorAll('.city-button')] as HTMLButtonElement[];
    expect(cityButtons).toHaveSize(2);
    expect(cityButtons[0].textContent).toContain('Porto Alegre');
    expect(cityButtons[1].textContent).toContain('Caxias do Sul');
    cityButtons[1].click();
    expect(navigate).toHaveBeenCalledWith(['/aluno/instrutores/mapa'], {
      queryParams: {uf:'RS', local:'Caxias do Sul, RS', cidade:'Caxias do Sul', lat:-29.17, lng:-51.18},
    });
    (fixture.nativeElement.querySelector('.instructor-button') as HTMLButtonElement).click();
    expect(navigate).toHaveBeenCalledWith(['/aluno/instrutores/mapa'], {
      queryParams: {uf:'RS', local:'Porto Alegre, RS', cidade:'Porto Alegre', lat:-30.03, lng:-51.21, instrutor:'one'},
    });
    fixture.destroy();
  });
});
