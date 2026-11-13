import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { AppComponent } from './app.component';
import { routes } from './app.routes';

describe('InstrutorProCNH shell', () => {
  beforeEach(async () => TestBed.configureTestingModule({
    imports: [AppComponent],
    providers: [provideRouter(routes)],
  }).compileComponents());

  it('renders the InstrutorProCNH identity and logo', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const root = fixture.nativeElement as HTMLElement;
    expect(root.textContent).toContain('InstrutorProCNH');
    expect(root.textContent).not.toContain('EMBREA');
    expect(root.querySelector('.brand img')?.getAttribute('src')).toBe('/logo-cnh.svg');
  });

  it('keeps instructor search available while hiding the paused CFC entry', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const hrefs = [...(fixture.nativeElement as HTMLElement).querySelectorAll('nav a')]
      .map(a => a.getAttribute('href'));
    expect(hrefs).toContain('/aluno/instrutores');
    expect(hrefs).toContain('/aluno/sem-instrutor');
    expect(hrefs).toContain('/profissional/instrutor/entrada');
    expect(hrefs).toContain('/cadastro/aluno');
    expect(hrefs).not.toContain('/cfc/cadastro');
  });
});
