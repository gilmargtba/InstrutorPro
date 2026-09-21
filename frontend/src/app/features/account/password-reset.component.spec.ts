import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { PasswordResetConfirmComponent, PasswordResetRequestComponent } from './password-reset.component';

describe('PasswordResetComponents',()=>{
  it('requests recovery without exposing whether the account exists',()=>{
    TestBed.configureTestingModule({imports:[PasswordResetRequestComponent],providers:[provideHttpClient(),provideHttpClientTesting(),provideRouter([])]});
    const component=TestBed.createComponent(PasswordResetRequestComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);component.email='pessoa@example.com';component.submit();
    const request=http.expectOne('/marketplace/password-reset/request/');expect(request.request.body).toEqual({email:'pessoa@example.com'});request.flush({detail:'Se existir uma conta ativa para esse e-mail, enviaremos as instruções.'});
    expect(component.message()).toContain('Se existir');
  });

  it('confirms a token with a password of at least ten characters',()=>{
    TestBed.resetTestingModule();TestBed.configureTestingModule({imports:[PasswordResetConfirmComponent],providers:[provideHttpClient(),provideHttpClientTesting(),{provide:ActivatedRoute,useValue:{snapshot:{queryParamMap:{get:(name:string)=>name==='uid'?'uid-value':'token-value'}}}}]});
    const component=TestBed.createComponent(PasswordResetConfirmComponent).componentInstance;
    const http=TestBed.inject(HttpTestingController);component.password='senha-nova-123';component.confirmation='senha-nova-123';component.submit();
    const request=http.expectOne('/marketplace/password-reset/confirm/');expect(request.request.body.uid).toBe('uid-value');expect(request.request.body.token).toBe('token-value');request.flush({detail:'Senha redefinida com sucesso.'});
    expect(component.done()).toBeTrue();
  });
});
