import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { InstructorPerformanceComponent, InstructorPlanComponent, InstructorSaasDashboardComponent, SaasSummary } from './saas-pages.component';

const summary: SaasSummary = {
  display_name:'Carlos', profile_status:'APPROVED', publication_status:'APPROVED',
  plan:{code:'FREE',name:'Free',entitlements:['PUBLIC_PROFILE','WHATSAPP_CONTACT','BASIC_ANALYTICS']},
  metrics:{days:30,search_impressions:0,profile_views:0,whatsapp_contacts:0,conversion_percent:0,timeline:[]},
};

describe('professional SaaS pages',()=>{
  beforeEach(()=>TestBed.configureTestingModule({providers:[provideHttpClient(),provideHttpClientTesting(),provideRouter([])]}));

  it('shows dashboard, FREE plan, metrics and zero state',()=>{
    const fixture=TestBed.createComponent(InstructorSaasDashboardComponent);
    TestBed.inject(HttpTestingController).expectOne('/marketplace/instructor/saas-summary/?days=30').flush(summary);
    fixture.detectChanges();
    const text=fixture.nativeElement.textContent;
    expect(text).toContain('Olá, Carlos'); expect(text).toContain('Plano Free');
    expect(text).toContain('Aparições nas buscas'); expect(text).toContain('ainda não recebeu contatos');
  });

  it('switches among 7, 30 and 90 day periods',()=>{
    const fixture=TestBed.createComponent(InstructorPerformanceComponent); const http=TestBed.inject(HttpTestingController);
    http.expectOne('/marketplace/instructor/saas-summary/?days=30').flush(summary);
    fixture.componentInstance.load(7); http.expectOne('/marketplace/instructor/saas-summary/?days=7').flush({...summary,metrics:{...summary.metrics,days:7}});
    fixture.componentInstance.load(90); http.expectOne('/marketplace/instructor/saas-summary/?days=90').flush({...summary,metrics:{...summary.metrics,days:90}});
    expect(fixture.componentInstance.periods).toEqual([7,30,90]);
  });

  it('shows PRO as coming soon without checkout or price',()=>{
    const fixture=TestBed.createComponent(InstructorPlanComponent);
    TestBed.inject(HttpTestingController).expectOne('/marketplace/instructor/saas-summary/?days=30').flush(summary);
    fixture.detectChanges(); const text=fixture.nativeElement.textContent;
    expect(text).toContain('Plano atual: FREE'); expect(text).toContain('EM BREVE');
    expect(text).not.toContain('Comprar agora'); expect(text).not.toContain('R$');
  });
});
