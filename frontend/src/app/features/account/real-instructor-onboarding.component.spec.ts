import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { RealInstructorOnboardingComponent } from './real-instructor-onboarding.component';

describe('RealInstructorOnboardingComponent',()=>{
  beforeEach(()=>TestBed.configureTestingModule({imports:[RealInstructorOnboardingComponent],providers:[provideHttpClient(),provideHttpClientTesting(),provideRouter([])]}));
  it('saves only the allowed non-documental onboarding fields',()=>{
    const component=TestBed.createComponent(RealInstructorOnboardingComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);
    http.expectOne('/account/me/').flush({instructor:{display_name:'Instrutora Piloto'}});
    component.form.whatsapp='+5551999990001';component.form.price_amount=95;component.form.instructor_city='Goiânia';component.form.instructor_uf='GO';component.form.service_latitude=-16.6869;component.form.service_longitude=-49.2648;component.form.service_location_authorized=true;component.form.vehicle.make='Marca';component.form.vehicle.model='Modelo';
    component.submit();
    const request=http.expectOne('/account/me/');expect(request.request.method).toBe('PATCH');expect(request.request.body.categories).toEqual(['B']);expect(request.request.body.vehicle.transmission).toBe('MANUAL');expect(request.request.body.document).toBeUndefined();request.flush({});
  });
  it('finds and fills the public city center without manual coordinates',()=>{
    const component=TestBed.createComponent(RealInstructorOnboardingComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);
    http.expectOne('/account/me/').flush({instructor:{display_name:'Instrutora Piloto'}});
    component.form.instructor_city='Goiatuba';component.form.instructor_uf='GO';component.findPublicLocation();
    const request=http.expectOne(req=>req.url==='/geocoding/search/'&&req.params.get('q')==='Goiatuba, GO, Brasil');
    request.flush({provider:'maptiler',results:[{id:'municipality.1',label:'Goiatuba, Goiás, Brasil',latitude:-18.0125,longitude:-49.3547,place_type:'municipality',city:'Goiatuba',uf:'GO',bbox:null}]});
    expect(component.form.service_latitude).toBe(-18.0125);expect(component.form.service_longitude).toBe(-49.3547);expect(component.locationMessage()).toContain('Goiatuba');
  });
  it('does not accept a geocoding result from another UF',()=>{
    const component=TestBed.createComponent(RealInstructorOnboardingComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);
    http.expectOne('/account/me/').flush({instructor:{display_name:'Instrutora Piloto'}});
    component.form.instructor_city='Goiatuba';component.form.instructor_uf='GO';component.findPublicLocation();
    http.expectOne(req=>req.url==='/geocoding/search/'&&req.params.get('q')==='Goiatuba, GO, Brasil').flush({provider:'maptiler',results:[{id:'municipality.2',label:'Outra cidade',latitude:-23,longitude:-46,place_type:'municipality',city:'Outra',uf:'SP',bbox:null}]});
    expect(component.form.service_latitude).toBeNull();expect(component.locationMessage()).toContain('não encontrada');
  });
});
