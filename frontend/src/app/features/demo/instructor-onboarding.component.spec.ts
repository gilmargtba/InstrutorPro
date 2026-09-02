import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { InstructorOnboardingComponent } from './instructor-onboarding.component';

describe('InstructorOnboardingComponent',()=>{
  beforeEach(()=>TestBed.configureTestingModule({imports:[InstructorOnboardingComponent],providers:[provideHttpClient(),provideHttpClientTesting(),provideRouter([])]}));
  it('mantém sete etapas e persiste localização antes de avançar',()=>{
    const component=TestBed.createComponent(InstructorOnboardingComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);http.expectOne('/demo/instructor-onboarding/draft/').flush({}, {status:404,statusText:'Not found'});
    expect(component.labels).toEqual(['Dados','Foto','Atendimento','Veículo','Localização','Documentos','Revisão']);
    component.step=5;component.form.city='Porto Alegre';component.form.location_authorized=false;component.next();
    expect(component.step).toBe(5);expect(component.error).toContain('obrigatórios');
    component.form.location_authorized=true;component.next();
    const request=http.expectOne('/demo/instructor-onboarding/draft/');expect(request.request.body instanceof FormData).toBeTrue();
    request.flush({current_step:6,display_name:'Alex Demo',email:'alex@example.invalid',transmissions:['MANUAL'],vehicle_available:false,photo_present:false,document_types:[],profile_status:'DRAFT'});
    expect(component.step).toBe(6);
  });
  it('submete o rascunho persistido sem publicar',()=>{
    const component=TestBed.createComponent(InstructorOnboardingComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);http.expectOne('/demo/instructor-onboarding/draft/').flush({}, {status:404,statusText:'Not found'});
    component.step=7;component.form.synthetic_data_confirmed=true;component.send();
    const request=http.expectOne('/demo/instructor-onboarding/submit/');request.flush({profile_status:'SUBMITTED'});
    expect(component.submitted).toBeTrue();
  });
});
