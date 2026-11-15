import { provideZonelessChangeDetection } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, provideRouter } from '@angular/router';
import { of, Subject } from 'rxjs';

import { AvailabilityInterestPolicy, InstructorSearchProvider } from '../../demo/instructor-search.provider';
import { NoInstructorComponent } from './no-instructor.component';

describe('NoInstructorComponent', () => {
  it('keeps the form closed while the privacy policy is not enabled', () => {
    TestBed.configureTestingModule({
      imports: [NoInstructorComponent],
      providers: [
        provideRouter([]),
        {provide: ActivatedRoute, useValue: {snapshot: {queryParamMap: {get: () => null}}}},
        {provide: InstructorSearchProvider, useValue: {availabilityInterestPolicy: () => of({enabled: false})}},
      ],
    });
    const fixture = TestBed.createComponent(NoInstructorComponent);
    fixture.detectChanges();
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Cadastro de interesse indisponível');
    expect((fixture.nativeElement as HTMLElement).querySelector('form')).toBeNull();
  });

  it('prefills the requested city and shows the consent form only when enabled', () => {
    TestBed.configureTestingModule({
      imports: [NoInstructorComponent],
      providers: [
        provideRouter([]),
        {provide: ActivatedRoute, useValue: {snapshot: {queryParamMap: {get: (key: string) => ({uf: 'GO', cidade: 'Goiatuba'} as Record<string, string>)[key] ?? null}}}},
        {provide: InstructorSearchProvider, useValue: {availabilityInterestPolicy: () => of({enabled: true, retention_days: 90, consent_text: 'Aceito contato manual.'})}},
      ],
    });
    const fixture = TestBed.createComponent(NoInstructorComponent);
    fixture.detectChanges();
    expect(fixture.componentInstance.scope).toBe('CITY');
    expect(fixture.componentInstance.uf).toBe('GO');
    expect(fixture.componentInstance.city).toBe('Goiatuba');
    expect((fixture.nativeElement as HTMLElement).querySelector('form')?.textContent).toContain('Aceito contato manual.');
  });

  it('renders the form when the policy request completes asynchronously', async () => {
    const response = new Subject<AvailabilityInterestPolicy>();
    TestBed.configureTestingModule({
      imports: [NoInstructorComponent],
      providers: [
        provideZonelessChangeDetection(),
        provideRouter([]),
        {provide: ActivatedRoute, useValue: {snapshot: {queryParamMap: {get: () => null}}}},
        {provide: InstructorSearchProvider, useValue: {availabilityInterestPolicy: () => response.asObservable()}},
      ],
    });
    const fixture = TestBed.createComponent(NoInstructorComponent);
    fixture.detectChanges();
    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Verificando disponibilidade');
    response.next({enabled: true, retention_days: 90, consent_text: 'Aceito contato manual.'});
    response.complete();
    await fixture.whenStable();
    expect((fixture.nativeElement as HTMLElement).querySelector('form')).not.toBeNull();
    expect((fixture.nativeElement as HTMLElement).textContent).not.toContain('Verificando disponibilidade');
  });
});
