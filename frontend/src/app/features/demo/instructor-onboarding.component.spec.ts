import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { InstructorOnboardingComponent } from './instructor-onboarding.component';

describe('InstructorOnboardingComponent',()=>{
  beforeEach(()=>TestBed.configureTestingModule({imports:[InstructorOnboardingComponent],providers:[provideHttpClient(),provideHttpClientTesting(),provideRouter([])]}));
  it('mantém as seis etapas e valida consentimento de localização',()=>{
    const component=TestBed.createComponent(InstructorOnboardingComponent).componentInstance;
    expect(component.labels).toEqual(['Dados','Atendimento','Veículo','Localização','Documentos','Revisão']);
    component.step=4;component.form.location_authorized=false;component.next();
    expect(component.step).toBe(4);expect(component.error).toContain('obrigatórios');
    component.form.location_authorized=true;component.next();expect(component.step).toBe(5);
  });
  it('envia o workflow DEMO e apresenta confirmação sem publicar',()=>{
    const component=TestBed.createComponent(InstructorOnboardingComponent).componentInstance;
    component.step=6;component.form.location_authorized=true;component.form.synthetic_data_confirmed=true;component.send();
    const request=TestBed.inject(HttpTestingController).expectOne('/demo/instructor-onboarding/');
    expect(request.request.body instanceof FormData).toBeTrue();
    expect((request.request.body as FormData).getAll('transmissions')).toEqual(['MANUAL']);request.flush({display_name:'Alex Demo'});
    expect(component.submitted).toBeTrue();expect(component.responseName).toBe('Alex Demo');
  });
});
