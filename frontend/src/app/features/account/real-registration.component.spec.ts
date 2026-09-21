import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { RealRegistrationComponent } from './real-registration.component';

describe('RealRegistrationComponent',()=>{
  const router={navigateByUrl:jasmine.createSpy('navigateByUrl')};
  beforeEach(()=>TestBed.configureTestingModule({imports:[RealRegistrationComponent],providers:[provideHttpClient(),provideHttpClientTesting(),{provide:ActivatedRoute,useValue:{snapshot:{data:{role:'INSTRUCTOR'}}}},{provide:Router,useValue:router}]}));
  it('shows the specific API field validation instead of a generic error',()=>{
    const fixture=TestBed.createComponent(RealRegistrationComponent);const component=fixture.componentInstance;const http=TestBed.inject(HttpTestingController);
    http.expectOne('/legal/documents/instructor/').flush({version:'TERMS-1'});http.expectOne('/privacy/notice/').flush({version:'PRIVACY-1'});
    component.submit();
    http.expectOne('/marketplace/accounts/register/').flush({error:{code:'INVALID',message:'Entrada inválida',details:{password:['A senha deve ter pelo menos 10 caracteres.']}}},{status:400,statusText:'Bad Request'});
    expect(component.message()).toContain('pelo menos 10 caracteres');
  });
});
