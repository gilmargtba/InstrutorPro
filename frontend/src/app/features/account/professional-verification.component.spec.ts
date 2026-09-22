import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { ProfessionalVerificationComponent } from './professional-verification.component';

describe('ProfessionalVerificationComponent',()=>{
  beforeEach(()=>TestBed.configureTestingModule({imports:[ProfessionalVerificationComponent],providers:[provideHttpClient(),provideHttpClientTesting(),provideRouter([])]}));
  it('does not send an invalid CPF',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({status:'DRAFT',cpf_masked:'',submitted_at:null,review_started_at:null,decided_at:null,message:'',can_edit:true});
    fixture.componentInstance.cpf='111.111.111-11';fixture.componentInstance.confirmed=true;fixture.componentInstance.submit();
    http.expectNone('/instructor/verification/');expect(fixture.componentInstance.error()).toContain('CPF válido');
  });
  it('saves and submits a valid CPF without retaining it',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({status:'DRAFT',cpf_masked:'',submitted_at:null,review_started_at:null,decided_at:null,message:'',can_edit:true});
    fixture.componentInstance.cpf='529.982.247-25';fixture.componentInstance.confirmed=true;fixture.componentInstance.submit();
    const save=http.expectOne('/instructor/verification/');
    expect(save.request.body).toEqual({cpf:'529.982.247-25'});
    save.flush({status:'DRAFT'});
    http.expectOne('/instructor/verification/submit/').flush({status:'SUBMITTED',cpf_masked:'***.***.***-25',submitted_at:'x',review_started_at:null,decided_at:null,message:'',can_edit:false});
    expect(fixture.componentInstance.cpf).toBe('');
  });
  it('shows a useful error instead of loading forever',()=>{
    const fixture=TestBed.createComponent(ProfessionalVerificationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/instructor/verification/').flush({detail:'Forbidden'},{status:403,statusText:'Forbidden'});
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Não foi possível carregar a verificação profissional.');
    expect(fixture.nativeElement.textContent).not.toContain('Carregando');
  });
});
