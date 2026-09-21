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
    expect(component.form.service_latitude).toBe(-18.01);expect(component.form.service_longitude).toBe(-49.35);expect(component.locationMessage()).toContain('Goiatuba');
  });
  it('searches an optional public neighborhood or landmark without storing the query',()=>{
    const component=TestBed.createComponent(RealInstructorOnboardingComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);
    http.expectOne('/account/me/').flush({instructor:{display_name:'Instrutora Piloto'}});
    component.form.instructor_city='Goiatuba';component.form.instructor_uf='GO';component.publicLocationQuery='Praça da Matriz';component.findPublicLocation();
    const request=http.expectOne(req=>req.url==='/geocoding/search/'&&req.params.get('q')==='Praça da Matriz, Goiatuba, GO, Brasil');
    request.flush({provider:'maptiler',results:[{id:'poi.1',label:'Praça da Matriz, Goiatuba, Goiás, Brasil',latitude:-18.0154,longitude:-49.364,place_type:'poi',city:'Goiatuba',uf:'GO',bbox:null}]});
    expect(component.form.service_latitude).toBe(-18.02);expect(component.form.service_longitude).toBe(-49.36);component.submit();
    const update=http.expectOne('/account/me/');expect(update.request.body.publicLocationQuery).toBeUndefined();expect(update.request.body.service_latitude).toBe(-18.02);update.flush({});
  });
  it('does not accept a geocoding result from another UF',()=>{
    const component=TestBed.createComponent(RealInstructorOnboardingComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);
    http.expectOne('/account/me/').flush({instructor:{display_name:'Instrutora Piloto'}});
    component.form.instructor_city='Goiatuba';component.form.instructor_uf='GO';component.findPublicLocation();
    http.expectOne(req=>req.url==='/geocoding/search/'&&req.params.get('q')==='Goiatuba, GO, Brasil').flush({provider:'maptiler',results:[{id:'municipality.2',label:'Outra cidade',latitude:-23,longitude:-46,place_type:'municipality',city:'Outra',uf:'SP',bbox:null}]});
    expect(component.form.service_latitude).toBeNull();expect(component.locationMessage()).toContain('não encontrada');
  });
  it('loads every editable field from the saved instructor profile',()=>{
    const component=TestBed.createComponent(RealInstructorOnboardingComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);
    http.expectOne('/account/me/').flush({instructor:{display_name:'Instrutora Piloto',bio:'Experiência profissional',categories:['B'],transmission_options:['AUTOMATIC'],whatsapp:'+5564999990001',price_amount:'120.00',duration_minutes:90,city:'Goiatuba',uf:'GO',service_latitude:-18.0125,service_longitude:-49.3547,service_radius_km:20,service_location_authorized:true,vehicle:{category:'B',make:'Marca',model:'Modelo',year:2024,transmission:'AUTOMATIC',ownership_type:'OWNED',verification_status:'PENDING'}}});
    expect(component.category).toBe('B');expect(component.transmission).toBe('AUTOMATIC');expect(component.form.bio).toBe('Experiência profissional');expect(component.form.whatsapp).toBe('+5564999990001');expect(component.form.price_amount).toBe(120);expect(component.form.instructor_city).toBe('Goiatuba');expect(component.form.instructor_uf).toBe('GO');expect(component.form.service_latitude).toBe(-18.0125);expect(component.form.service_location_authorized).toBeTrue();expect(component.form.vehicle).toEqual({category:'B',make:'Marca',model:'Modelo',year:2024,transmission:'AUTOMATIC',ownership_type:'OWNED'});expect(component.form.vehicle.verification_status).toBeUndefined();expect(component.locationMessage()).toContain('Goiatuba/GO');
  });
});
