import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { LessonPackagesComponent } from './lesson-packages.component';

describe('LessonPackagesComponent', () => {
  beforeEach(() => TestBed.configureTestingModule({
    imports: [LessonPackagesComponent],
    providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
  }));

  it('shows the effective Free limit and never starts an upgrade automatically', () => {
    const fixture = TestBed.createComponent(LessonPackagesComponent);
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/marketplace/instructor/packages/').flush({
      plan_code: 'FREE', active_count: 1, active_limit: 1,
      available_categories: ['A', 'B'], vehicle_available: true,
      packages: [{ id: 'one', name: 'Pacote inicial', category: 'B', categories: ['B'], lesson_count: 2,
        price_amount: 170, price_per_lesson: 85, vehicle_included: false,
        description: '', is_active: true, visible: true }],
    });
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent;
    expect(text).toContain('1 de 1');
    expect(text).toContain('Pacote inicial');
    expect(text).toContain('conhecer os planos superiores');
    http.expectNone('/marketplace/instructor/upgrade/');
  });

  it('sends the instructor-defined total and shows a clear backend limit error', () => {
    const fixture = TestBed.createComponent(LessonPackagesComponent);
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/marketplace/instructor/packages/').flush({
      plan_code: 'FREE', active_count: 0, active_limit: 1,
      available_categories: ['A'], vehicle_available: true, packages: [],
    });
    fixture.componentInstance.draft = { name: 'Cinco aulas', categories: ['A'], lesson_count: 5,
      price_amount: 420, vehicle_included: true, description: '', is_active: true };
    fixture.componentInstance.save(true);
    const request = http.expectOne('/marketplace/instructor/packages/');
    expect(request.request.method).toBe('POST');
    expect(request.request.body.price_amount).toBe(420);
    expect(request.request.body.lesson_count).toBe(5);
    request.flush({ code: 'package_limit_reached', detail: 'Limite do plano atingido.' },
      { status: 400, statusText: 'Bad Request' });
    expect(fixture.componentInstance.error()).toContain('Limite do plano atingido');
  });

  it('selects only the categories on the profile and defaults to the first one', async () => {
    const fixture = TestBed.createComponent(LessonPackagesComponent);
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/marketplace/instructor/packages/').flush({
      plan_code: 'FREE', active_count: 0, active_limit: 1,
      available_categories: ['A'], vehicle_available: false, packages: [],
    });
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
    const categoryOptions = fixture.nativeElement.querySelectorAll('fieldset input[type="checkbox"]') as NodeListOf<HTMLInputElement>;
    expect(fixture.componentInstance.draft.categories).toEqual(['A']);
    expect(categoryOptions.length).toBe(1);
    expect(categoryOptions[0].checked).toBeTrue();
    expect((fixture.nativeElement.querySelector('input[name="vehicle"]') as HTMLInputElement).disabled).toBeTrue();
    fixture.componentInstance.draft = { ...fixture.componentInstance.draft, name: 'Cinco aulas', categories: ['B'], price_amount: 300 };
    fixture.componentInstance.save(true);
    expect(fixture.componentInstance.error()).toContain('categorias cadastradas');
    http.expectNone('/marketplace/instructor/packages/');
  });

  it('submits A and B together as one package', () => {
    const fixture = TestBed.createComponent(LessonPackagesComponent);
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/marketplace/instructor/packages/').flush({
      plan_code: 'FREE', active_count: 0, active_limit: 1,
      available_categories: ['A', 'B'], vehicle_available: true, packages: [],
    });
    fixture.detectChanges();
    const options = fixture.nativeElement.querySelectorAll('fieldset input[type="checkbox"]') as NodeListOf<HTMLInputElement>;
    options[1].click();
    fixture.componentInstance.draft.name = 'Pacote A e B';
    fixture.componentInstance.draft.price_amount = 300;
    fixture.componentInstance.save(true);
    const request = http.expectOne('/marketplace/instructor/packages/');
    expect(request.request.body.categories).toEqual(['A', 'B']);
    expect(request.request.body.category).toBeUndefined();
    request.flush({ id: 'one' });
    http.expectOne('/marketplace/instructor/packages/').flush({
      plan_code: 'FREE', active_count: 1, active_limit: 1,
      available_categories: ['A', 'B'], vehicle_available: true, packages: [],
    });
  });

  it('explains how to register a category instead of submitting without one', () => {
    const fixture = TestBed.createComponent(LessonPackagesComponent);
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/marketplace/instructor/packages/').flush({
      plan_code: 'FREE', active_count: 0, active_limit: 1,
      available_categories: [], vehicle_available: false, packages: [],
    });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Cadastre primeiro uma categoria');
    expect((fixture.nativeElement.querySelector('button.button.primary') as HTMLButtonElement).disabled).toBeTrue();
    expect(fixture.nativeElement.querySelector('a[href="/profissional/instrutor/onboarding"]')).not.toBeNull();
  });
});
