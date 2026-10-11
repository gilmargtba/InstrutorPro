import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { RealRegistrationComponent } from './real-registration.component';

describe('RealRegistrationComponent',()=>{
  const router={navigateByUrl:jasmine.createSpy('navigateByUrl')};
  beforeEach(()=>TestBed.configureTestingModule({imports:[RealRegistrationComponent],providers:[provideHttpClient(),provideHttpClientTesting(),{provide:ActivatedRoute,useValue:{snapshot:{data:{role:'INSTRUCTOR'}}}},{provide:Router,useValue:router}]}));
  it('shows the specific API field validation instead of a generic error',()=>{
    const fixture=TestBed.createComponent(RealRegistrationComponent);const component=fixture.componentInstance;const http=TestBed.inject(HttpTestingController);
    http.expectOne('/legal/documents/instructor/').flush({version:'TERMS-1'});http.expectOne('/privacy/notice/').flush({version:'PRIVACY-1'});
    component.submit({invalid:false} as NgForm);
    http.expectOne('/marketplace/accounts/register/').flush({error:{code:'INVALID',message:'Entrada inválida',details:{password:['A senha deve ter pelo menos 10 caracteres.']}}},{status:400,statusText:'Bad Request'});
    expect(component.message()).toContain('pelo menos 10 caracteres');
  });
  it('does not send blank student location fields for an instructor',()=>{
    const fixture=TestBed.createComponent(RealRegistrationComponent);const component=fixture.componentInstance;const http=TestBed.inject(HttpTestingController);
    http.expectOne('/legal/documents/instructor/').flush({version:'TERMS-1'});http.expectOne('/privacy/notice/').flush({version:'PRIVACY-1'});
    component.submit({invalid:false} as NgForm);
    const request=http.expectOne('/marketplace/accounts/register/');
    expect(request.request.body.city).toBeUndefined();expect(request.request.body.uf).toBeUndefined();
    request.flush({id:'account-id',role:'INSTRUCTOR'});
  });
  it('explains invalid fields when the user clicks Criar conta instead of silently disabling the button',async()=>{
    const fixture=TestBed.createComponent(RealRegistrationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/legal/documents/instructor/').flush({version:'TERMS-1'});http.expectOne('/privacy/notice/').flush({version:'PRIVACY-1'});
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
    const button=fixture.nativeElement.querySelector('button.button.primary') as HTMLButtonElement;
    expect(button.disabled).toBeFalse();
    button.click();fixture.detectChanges();
    expect(fixture.componentInstance.message()).toContain('Nome');
    expect(fixture.componentInstance.message()).toContain('Senha');
    http.expectNone('/marketplace/accounts/register/');
  });
  it('shows a loading error if the legal version cannot be retrieved',()=>{
    const fixture=TestBed.createComponent(RealRegistrationComponent);const http=TestBed.inject(HttpTestingController);
    http.expectOne('/legal/documents/instructor/').flush({}, {status:503,statusText:'Unavailable'});
    http.expectOne('/privacy/notice/').flush({version:'PRIVACY-1'});
    fixture.detectChanges();
    expect(fixture.componentInstance.message()).toContain('Termos de Uso');
    expect((fixture.nativeElement.querySelector('button.button.primary') as HTMLButtonElement).disabled).toBeTrue();
  });
});
