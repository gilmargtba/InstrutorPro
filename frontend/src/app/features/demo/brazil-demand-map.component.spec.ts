import { TestBed } from '@angular/core/testing';

import { BrazilDemandMapComponent } from './brazil-demand-map.component';

describe('BrazilDemandMapComponent',()=>{
  const states=[
    {uf:'RS',total:184,searchLocation:'Porto Alegre',cities:[['Porto Alegre',58]] as [string,number][]},
    {uf:'SC',total:146,searchLocation:'Florianópolis',cities:[['Florianópolis',42]] as [string,number][]},
    {uf:'SP',total:418,searchLocation:'São Paulo',cities:[['São Paulo',136]] as [string,number][]},
    {uf:'RJ',total:237,searchLocation:'Rio de Janeiro',cities:[['Rio de Janeiro',91]] as [string,number][]},
    {uf:'ES',total:112,searchLocation:'Vitória',cities:[['Vitória',36]] as [string,number][]},
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

  it('refreshes the map when states arrive after the GeoJSON and labels an active GO',async()=>{
    const goGeoJson={type:'FeatureCollection',features:[{type:'Feature',properties:{codarea:'52'},geometry:{type:'Polygon',coordinates:[[[-53,-19],[-46,-19],[-46,-13],[-53,-13],[-53,-19]]]}}]};
    spyOn(globalThis,'fetch').and.resolveTo(new Response(JSON.stringify(goGeoJson),{status:200}));
    await TestBed.configureTestingModule({imports:[BrazilDemandMapComponent]}).compileComponents();
    const fixture=TestBed.createComponent(BrazilDemandMapComponent);
    fixture.componentRef.setInput('states',[]);
    const selected=jasmine.createSpy('selected');
    fixture.componentInstance.stateSelected.subscribe(selected);
    fixture.detectChanges();
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelectorAll('.brazil-map-count').length).toBe(0);

    fixture.componentRef.setInput('states',[{uf:'GO',total:2,searchLocation:'Formosa',cities:[['Formosa',1],['Goiatuba',1]]}]);
    fixture.detectChanges();
    await new Promise(resolve=>setTimeout(resolve,50));
    const label=fixture.nativeElement.querySelector('.brazil-map-count') as HTMLElement;
    expect(label?.textContent).toContain('GO');
    label.click();
    expect(selected).toHaveBeenCalledWith('GO');
    fixture.destroy();
  });
});
