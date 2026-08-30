import { TestBed } from '@angular/core/testing';

import { BrazilDemandMapComponent } from './brazil-demand-map.component';

describe('BrazilDemandMapComponent',()=>{
  const states=[
    {uf:'RS',total:184,cities:[['Porto Alegre',58]] as [string,number][]},
    {uf:'SC',total:146,cities:[['Florianópolis',42]] as [string,number][]},
    {uf:'SP',total:418,cities:[['São Paulo',136]] as [string,number][]},
    {uf:'RJ',total:237,cities:[['Rio de Janeiro',91]] as [string,number][]},
    {uf:'ES',total:112,cities:[['Vitória',36]] as [string,number][]},
  ];
  const geoJson={type:'FeatureCollection',features:[{type:'Feature',properties:{codarea:'43'},geometry:{type:'Polygon',coordinates:[[[-57,-34],[-49,-34],[-49,-27],[-57,-27],[-57,-34]]]}}]};

  it('shows counts only for active states and emits the selected UF',async()=>{
    spyOn(globalThis,'fetch').and.resolveTo(new Response(JSON.stringify(geoJson),{status:200}));
    await TestBed.configureTestingModule({imports:[BrazilDemandMapComponent]}).compileComponents();
    const fixture=TestBed.createComponent(BrazilDemandMapComponent);
    fixture.componentRef.setInput('states',states);
    fixture.componentRef.setInput('selectedUf','RS');
    const selected=jasmine.createSpy('selected');
    fixture.componentInstance.stateSelected.subscribe(selected);
    fixture.detectChanges();
    await fixture.whenStable();
    await new Promise(resolve=>setTimeout(resolve,50));
    fixture.detectChanges();

    const labels=fixture.nativeElement.querySelectorAll('.brazil-map-count');
    expect(labels.length).toBe(5);
    expect(fixture.nativeElement.textContent).not.toContain('RO 0');
    (labels[2] as HTMLElement).click();
    expect(selected).toHaveBeenCalledWith('SP');
    fixture.destroy();
  });
});
