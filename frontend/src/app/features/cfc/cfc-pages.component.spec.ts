import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, provideRouter, Router } from '@angular/router';
import { CFCDashboardComponent, CFCEntryComponent, CFCInstructorActivationComponent } from './cfc-pages.component';

describe('CFCEntryComponent', () => {
  it('shows the CFC access path without promising public self-registration', () => {
    TestBed.configureTestingModule({imports: [CFCEntryComponent], providers: [provideRouter([])]});
    const fixture = TestBed.createComponent(CFCEntryComponent);
    fixture.detectChanges();
    const root = fixture.nativeElement as HTMLElement;
    expect(root.textContent).toContain('O auto-cadastro público ainda não está disponível');
    expect(root.querySelector('a[href="/entrar"]')).not.toBeNull();
    expect(root.querySelector('a[href="/cfc"]')).not.toBeNull();
  });
});

describe('CFCDashboardComponent', () => {
  beforeEach(() => TestBed.configureTestingModule({
    imports: [CFCDashboardComponent],
    providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
  }));

  it('pre-registers only a name and email, without password or publication', () => {
    const component = TestBed.createComponent(CFCDashboardComponent).componentInstance;
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/cfc/memberships/').flush([{id: 'cfc-1', display_name: 'CFC Central'}]);
    http.expectOne('/cfc/cfc-1/').flush({id:'cfc-1',display_name:'CFC Central',declared_instructor_count:2,pre_registered_count:0,accepted_count:0});
    http.expectOne('/cfc/cfc-1/instructors/').flush([]);
    component.instructorName = 'Pessoa Instrutora';
    component.instructorEmail = 'person@example.invalid';
    component.invite();
    const request = http.expectOne('/cfc/cfc-1/instructors/');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({display_name:'Pessoa Instrutora',email:'person@example.invalid'});
    request.flush({id:'link-1',status:'PENDING'});
    http.expectOne('/cfc/cfc-1/').flush({id:'cfc-1',display_name:'CFC Central',declared_instructor_count:2,pre_registered_count:1,accepted_count:0});
    http.expectOne('/cfc/cfc-1/instructors/').flush([]);
    expect(component.message()).toContain('Convite enviado');
  });
});

describe('CFCInstructorActivationComponent', () => {
  const router = {navigateByUrl: jasmine.createSpy('navigateByUrl')};
  beforeEach(() => TestBed.configureTestingModule({
    imports: [CFCInstructorActivationComponent],
    providers: [
      provideHttpClient(), provideHttpClientTesting(),
      {provide: ActivatedRoute, useValue:{snapshot:{queryParamMap:{get:(key:string)=>key==='uid'?'uid-value':'token-value'}}}},
      {provide: Router, useValue: router},
    ],
  }));

  it('requires the instructor own terms and CFC-link consent before activation', () => {
    const component = TestBed.createComponent(CFCInstructorActivationComponent).componentInstance;
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/legal/documents/instructor/').flush({version:'terms-1'});
    http.expectOne('/privacy/notice/').flush({version:'notice-1'});
    component.birthDate='1990-01-01';component.password='safe-password-123';
    component.confirmation='safe-password-123';component.termsAccepted=true;
    component.privacyAcknowledged=true;
    component.activate();
    http.expectNone('/cfc/activate-instructor/');
    component.linkAccepted=true;
    component.activate();
    const request=http.expectOne('/cfc/activate-instructor/');
    expect(request.request.body.cfc_link_accepted).toBeTrue();
    expect(request.request.body.terms_version).toBe('terms-1');
    expect(request.request.body.uid).toBe('uid-value');
    request.flush({status:'ACCEPTED'});
    expect(router.navigateByUrl).toHaveBeenCalledWith('/profissional/instrutor/onboarding');
  });
});
