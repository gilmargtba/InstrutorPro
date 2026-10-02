import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { InstructorStatusComponent } from './marketplace-entry.component';

describe('InstructorStatusComponent',()=>{
  beforeEach(()=>TestBed.configureTestingModule({imports:[InstructorStatusComponent],providers:[provideHttpClient(),provideHttpClientTesting(),provideRouter([])]}));

  it('opens the populated real profile editor',()=>{
    const fixture=TestBed.createComponent(InstructorStatusComponent);
    const http=TestBed.inject(HttpTestingController);
    http.expectOne('/account/me/').flush({instructor:{display_name:'Instrutora Piloto',profile_status:'DRAFT',verification_status:'NOT_STARTED',publication_status:'UNPUBLISHED'}});
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('consulte a verificação profissional para ver anexos');
    expect(fixture.nativeElement.textContent).not.toContain('Documentos ainda não solicitados');
    const link=fixture.nativeElement.querySelector('a.button.secondary') as HTMLAnchorElement;
    expect(link.textContent?.trim()).toBe('Editar perfil');
    expect(link.getAttribute('href')).toBe('/profissional/instrutor/onboarding');
  });

  it('explains that a completed verification cannot receive new attachments',()=>{
    const fixture=TestBed.createComponent(InstructorStatusComponent);
    const http=TestBed.inject(HttpTestingController);
    http.expectOne('/account/me/').flush({instructor:{display_name:'Instrutor Real',profile_status:'UNDER_REVIEW',verification_status:'VERIFIED',publication_status:'UNPUBLISHED'}});
    fixture.detectChanges();
    const text=fixture.nativeElement.textContent as string;
    expect(text).toContain('não é possível acrescentar anexos a essa solicitação');
    expect(text).toContain('Ver verificação concluída');
    expect(text).not.toContain('Solicitar verificação profissional');
    const link=fixture.nativeElement.querySelector('a.button.primary') as HTMLAnchorElement;
    expect(link.getAttribute('href')).toBe('/profissional/instrutor/verificacao');
  });

  it('explains when the current session has no instructor profile',()=>{
    const fixture=TestBed.createComponent(InstructorStatusComponent);
    const http=TestBed.inject(HttpTestingController);
    http.expectOne('/account/me/').flush({instructor:null});
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Perfil de instrutor não encontrado');
    expect(fixture.nativeElement.textContent).not.toContain('Carregando cadastro');
    const link=fixture.nativeElement.querySelector('a.button.primary') as HTMLAnchorElement;
    expect(link.getAttribute('href')).toBe('/entrar');
  });
});
