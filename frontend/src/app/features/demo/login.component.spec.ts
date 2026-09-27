import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideZonelessChangeDetection } from '@angular/core';
import { provideRouter, Router } from '@angular/router';
import { LoginComponent } from './marketplace-entry.component';

describe('LoginComponent feedback', () => {
  let fixture: ComponentFixture<LoginComponent>;
  let http: HttpTestingController;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [provideZonelessChangeDetection(), provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    });
    fixture = TestBed.createComponent(LoginComponent);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    await fixture.whenStable();
  });

  afterEach(() => http.verify());

  async function submit(email = 'pessoa@example.com', password = 'synthetic-password') {
    for (const [name, value] of [['email', email], ['password', password]]) {
      const input = fixture.nativeElement.querySelector(`[name="${name}"]`) as HTMLInputElement;
      input.value = value;
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
    await fixture.whenStable();
    fixture.nativeElement.querySelector('form').dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    await fixture.whenStable();
  }

  it('renders asynchronous credential errors and re-enables submission without another click', async () => {
    await submit();
    const button = fixture.nativeElement.querySelector('button') as HTMLButtonElement;
    expect(button.disabled).toBeTrue();
    expect(button.textContent).toContain('Entrando');
    fixture.nativeElement.querySelector('form').dispatchEvent(new Event('submit'));
    const request = http.expectOne('/marketplace/session/login/');
    request.flush({ detail: 'Credenciais inválidas' }, { status: 400, statusText: 'Bad Request' });
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('E-mail ou senha inválidos');
    expect(button.disabled).toBeFalse();
    expect(fixture.nativeElement.querySelector('a[href="/recuperar-senha"]')).not.toBeNull();
  });

  it('rejects invalid fields locally with visible feedback', async () => {
    await submit('not-an-email', '');
    http.expectNone('/marketplace/session/login/');
    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('Informe um e-mail válido');
  });

  for (const [status, message] of [[429, 'Muitas tentativas'], [503, 'Não foi possível entrar agora']] as const) {
    it(`shows safe feedback for HTTP ${status}`, async () => {
      await submit();
      http.expectOne('/marketplace/session/login/').flush({ detail: 'internal-sensitive-detail' }, { status, statusText: 'Failure' });
      await fixture.whenStable();
      const text = fixture.nativeElement.querySelector('[role="alert"]').textContent;
      expect(text).toContain(message);
      expect(text).not.toContain('internal-sensitive-detail');
      expect(fixture.nativeElement.querySelector('button').disabled).toBeFalse();
    });
  }

  it('shows network failures and clears the old error on a successful retry', async () => {
    const navigate = spyOn(TestBed.inject(Router), 'navigate').and.resolveTo(true);
    await submit();
    http.expectOne('/marketplace/session/login/').error(new ProgressEvent('error'));
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('[role="alert"]').textContent).toContain('Não foi possível entrar agora');
    await submit();
    expect(fixture.nativeElement.querySelector('[role="alert"]')).toBeNull();
    http.expectOne('/marketplace/session/login/').flush({ roles: ['INSTRUCTOR'], is_staff: false });
    await fixture.whenStable();
    expect(navigate).toHaveBeenCalledWith(['/instrutor']);
  });
});
